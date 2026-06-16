import streamlit as st
import pandas as pd
from db_connection import get_connection

st.set_page_config(
    page_title="Clinic Dashboard Project",
    page_icon="🏥",
    layout="wide"
)

def run_query(query):
        return pd.read_sql(query, conn)

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "New Visit",
        "Purchase Stock"
    ]
)

conn = get_connection()
st.success("Connected to Oracle")

if page == "Dashboard":

    st.title("🏥 Clinic Management Dashboard")

    # all your current dashboard code
    st.sidebar.header("Filters")

    selected_date = st.sidebar.date_input(
        "Select Date",
        value=pd.to_datetime("today").normalize()
    )  
    oracle_date = selected_date.strftime("%Y-%m-%d")
    st.write(selected_date)
    # st.write(repr(selected_date))
    # st.write(oracle_date)

    st.header("💰 Revenue Summary")

    col1, col2, col3, col4 = st.columns(4)
    # CARD-1 REVENUE:

    revenue_df = run_query(f"""
    SELECT
        SUM(
            consultation_fee +
            medicine_amount +
            service_amount
        ) AS total_revenue
    FROM Visit
    WHERE TRUNC(visit_date) = DATE '{oracle_date}'
    """)
    total_revenue = revenue_df.loc[0, "TOTAL_REVENUE"]

    with col1:
        st.metric(
            "Total revenue:",
            f"₹{total_revenue:,.0f}"
        )
    # CARD 2-Consultation Revenue:

    crevenue_df = run_query(f"""
    SELECT
        SUM(consultation_fee) AS consultation_revenue
    FROM Visit
    WHERE TRUNC(visit_date)=DATE '{oracle_date}'
    """)

    consulataion_revenue = crevenue_df.loc[0, "CONSULTATION_REVENUE"]

    with col2:
        st.metric(
            "Consultation revenue today:",
            f"₹{consulataion_revenue:,.0f}"
        )

    # CARD-3 Medicine Revenue:

    mrevenue_df = run_query(f"""
    SELECT
        SUM(medicine_amount) AS medicine_revenue
    FROM Visit
    WHERE TRUNC(visit_date)=DATE '{oracle_date}'
    """)

    medicine_revenue = mrevenue_df.loc[0, "MEDICINE_REVENUE"]

    with col3:
        st.metric(
            "Medicine revenue today:",
            f"₹{medicine_revenue:,.0f}"
        )

    # CARD-4 Service Revenue:

    srevenue_df = run_query(f"""
    SELECT
        SUM(service_amount) AS service_revenue
    FROM Visit
    WHERE TRUNC(visit_date)=DATE '{oracle_date}'
    """)
    service_revenue = srevenue_df.loc[0, "SERVICE_REVENUE"]

    with col4:
        st.metric(
            "Service revenue today:",
            f"₹{service_revenue:,.0f}"
        )

    st.header("👥 Patient Statistics")

    col1, col2, col3, col4 = st.columns(4)

    patients_df = run_query(f"""
    SELECT
        COUNT(*) AS patients_today
    FROM Visit
    WHERE TRUNC(visit_date) = DATE '{oracle_date}'
    """)
    patients_today = patients_df.loc[0, "PATIENTS_TODAY"]
    with col1:
        st.metric(
            "Patients today:",
            patients_today
        )

    rpatients_df = run_query(f"""
    SELECT COUNT(*) AS repeat_patients
    FROM Visit v
    WHERE TRUNC(v.visit_date) = DATE '{oracle_date}'
    AND EXISTS (
        SELECT 1
        FROM Visit v2
        WHERE v2.p_id = v.p_id
        AND v2.visit_date < v.visit_date    
    )
    """)
    repeat_patients_today = rpatients_df.loc[0, "REPEAT_PATIENTS"]

    with col2:
        st.metric(
            "Repeat Patients today:",
            repeat_patients_today
        )

    payment_df = run_query(f"""
    SELECT
        payment_mode,
        SUM(
            consultation_fee +
            medicine_amount +
            service_amount
        ) AS revenue
    FROM Visit
    WHERE TRUNC(visit_date)=DATE '{oracle_date}'
    GROUP BY payment_mode
    """)

    cash_revenue = payment_df.loc[
        payment_df["PAYMENT_MODE"] == "CASH",
        "REVENUE"
    ].sum()

    online_revenue = payment_df.loc[
        payment_df["PAYMENT_MODE"] == "ONLINE",
        "REVENUE"
    ].sum()

    with col3:
        st.metric(
            "Cash Revenue",
            f"₹{cash_revenue:,.0f}"
        )

    with col4:
        st.metric(
            "Online Revenue",
            f"₹{online_revenue:,.0f}"
        )

    st.header("💊 Medicines Sold Today")

    medicinesold_df = run_query(f"""
    SELECT
        m.medicine_name,

        SUM(md.quantity_given) AS tablets_sold,

        CASE
            WHEN m.tablets_per_strip IS NOT NULL
            THEN ROUND(
                SUM(md.quantity_given) / m.tablets_per_strip,
                2
            )
        END AS strips_sold,

        ROUND(
            SUM(
                md.quantity_given * m.selling_price_per_unit
            ),
            2
        ) AS revenue_generated

    FROM Medicine_Dispensed md

    JOIN Visit v
    ON md.visit_id = v.visit_id

    JOIN Medicine m
    ON md.medicine_id = m.medicine_id

    WHERE TRUNC(v.visit_date) = DATE '{oracle_date}'

    GROUP BY
        m.medicine_name,
        m.tablets_per_strip,
        m.selling_price_per_unit

    ORDER BY revenue_generated DESC
    """)
    st.dataframe(
        medicinesold_df,
        use_container_width=True
    )

    st.header("📦 Inventory Status")

    inventory_df = run_query(f"""
    SELECT
        m.medicine_name,

        m.unit_type,

        CASE
            WHEN m.unit_type IN ('TABLET','CAPSULE')
            THEN ROUND(
                (
                    NVL(p.total_purchased,0)
                    - NVL(d.total_dispensed,0)
                ) / m.tablets_per_strip,
                2
            )
            ELSE
                (
                    NVL(p.total_purchased,0)
                    - NVL(d.total_dispensed,0)
                )
        END AS quantity_left,

        CASE

            WHEN (
                NVL(p.total_purchased,0)
                - NVL(d.total_dispensed,0)
            ) < 0
            THEN 'ERROR'

            WHEN m.unit_type IN ('TABLET','CAPSULE')
                 AND (
                     (
                         NVL(p.total_purchased,0)
                         - NVL(d.total_dispensed,0)
                     ) / m.tablets_per_strip
                 ) < 20
            THEN 'LOW STOCK'

            WHEN m.unit_type NOT IN ('TABLET','CAPSULE')
                 AND (
                     NVL(p.total_purchased,0)
                     - NVL(d.total_dispensed,0)
                 ) < 10
            THEN 'LOW STOCK'

            ELSE 'OK'

        END AS stock_status

    FROM Medicine m

    LEFT JOIN (
        SELECT
            medicine_id,
            SUM(quantity_purchased) total_purchased
        FROM Medicine_Purchased
        GROUP BY medicine_id
    ) p
    ON m.medicine_id = p.medicine_id

    LEFT JOIN (
        SELECT
            medicine_id,
            SUM(quantity_given) total_dispensed
        FROM Medicine_Dispensed
        GROUP BY medicine_id
    ) d
    ON m.medicine_id = d.medicine_id

    ORDER BY quantity_left
    """)

    inventory_df.columns = [
        "Medicine",
        "Unit Type",
        "Quantity Left",
        "STOCK_STATUS"
    ]

    st.dataframe(
        inventory_df,
        use_container_width=True
    )

    st.header("⚠ Low Stock Alerts")

    alerts_df = inventory_df[
        inventory_df["STOCK_STATUS"] != "OK"
    ]

    st.dataframe(
        alerts_df,
        use_container_width=True
    )

    chart_df = pd.DataFrame({
        "Revenue Type": [
            "Consultation",
            "Medicine",
            "Service"
        ],
        "Revenue": [
            consulataion_revenue,
            medicine_revenue,
            service_revenue
        ]
    })

    st.header("📊 Revenue Breakdown")

    st.bar_chart(
        chart_df.set_index("Revenue Type")
    )

    st.header("🏆 Top Medicines by Revenue")

    top_medicines = medicinesold_df.head(10)

    st.bar_chart(
        top_medicines.set_index(
            "MEDICINE_NAME"
        )["REVENUE_GENERATED"]
    )

elif page == "New Visit":

    st.title("➕ New Patient Visit")

    medicine_df = run_query("""
        SELECT
            medicine_id,
            medicine_name
        FROM Medicine
        ORDER BY medicine_name
        """
    )

    if "medicine_rows" not in st.session_state:
        st.session_state.medicine_rows = 1

    with st.form("visit_form"):

        st.subheader("Patient Information")

        patient_name = st.text_input(
            "Patient Name"
        )

        age = st.number_input(
            "Age",
            min_value=0,
            max_value=120,
            step=1
        )

        gender = st.selectbox(
            "Gender",
            [
                "M",
                "F",
                "O"
            ]
        )

        phone = st.text_input(
            "Phone Number"
        )

        st.subheader("Visit Details")

        consultation_fee = st.number_input(
            "Consultation Fee",
            min_value=0
        )

        service_fee = st.number_input(
            "Service Fee",
            min_value=0
        )

        payment_mode = st.selectbox(
            "Payment Mode",
            [
                "CASH",
                "ONLINE"
            ]
        )

        st.subheader("Medicine Dispensing")

        medicines = []

        for i in range(st.session_state.medicine_rows):

            medicine_name = st.selectbox(
                f"Medicine {i+1}",
                medicine_df["MEDICINE_NAME"],
                key=f"med_{i}"
            )

            qty = st.number_input(
                f"Quantity {i+1}",
                min_value=0,
                step=1,
                key=f"qty_{i}"
            )

            medicines.append(
                (
                    medicine_name,
                    qty
                )
            )

        submitted = st.form_submit_button(
            "Submit Visit"
        )
    if st.button("➕ Add Medicine"):
        st.session_state.medicine_rows += 1
        st.rerun()
    if st.button("➖ Remove Last Medicine"):
       if st.session_state.medicine_rows > 1:
            st.session_state.medicine_rows -= 1
            st.rerun()
    if submitted:
        # st.write(selected_medicine)
        # st.write(quantity_given)

        cursor = conn.cursor()

        # Check if patient already exists

        cursor.execute(
            """
            SELECT p_id
            FROM Patient
            WHERE mobile_number = :1
            """,
            [phone]
        )

        existing_patient = cursor.fetchone()

        # Existing Patient

        if existing_patient:

            patient_id = existing_patient[0]

        # New Patient

        else:

            cursor.execute(
                """
                INSERT INTO Patient
                (
                    p_id,
                    p_name,
                    p_age,
                    p_gender,
                    mobile_number
                )
                VALUES
                (
                    patient_seq.NEXTVAL,
                    :1,
                    :2,
                    :3,
                    :4
                )
                """,
                [
                    patient_name,
                    age,
                    gender,
                    phone
                ]
            )

            cursor.execute(
                """
                SELECT patient_seq.CURRVAL
                FROM dual
                """
            )

            patient_id = cursor.fetchone()[0]

        medicine_amount = 0

        medicine_details = []

        for medicine_name, qty in medicines:

            if qty == 0:
                continue

            cursor.execute(
                """
                SELECT
                    medicine_id,
                    selling_price_per_unit
                FROM Medicine
                WHERE medicine_name = :1
                """,
                [medicine_name]
            )

            medicine_id, selling_price = cursor.fetchone()

            medicine_amount += (
                selling_price * qty
            )

            medicine_details.append(
                (
                    medicine_id,
                    qty
                )
            )
            cursor.execute(
                """
                SELECT
                    NVL(
                        (
                            SELECT SUM(quantity_purchased)
                            FROM Medicine_Purchased
                            WHERE medicine_id = :med_id
                        ),
                        0
                    )
                    -
                    NVL(
                        (
                            SELECT SUM(quantity_given)
                            FROM Medicine_Dispensed
                            WHERE medicine_id = :med_id
                        ),
                        0
                    )
                FROM dual
                """,
                med_id=medicine_id
            )

            stock_available = cursor.fetchone()[0]

            if qty > stock_available:

                st.error(
                    f"Insufficient stock for {medicine_name}. Available: {stock_available}"
                )

                st.stop()
        if len(medicine_details) == 0:

            st.error(
                "Please select at least one medicine."
            )

            st.stop()

        # Create Visit

        cursor.execute(
            """
            INSERT INTO Visit
            (
                visit_id,
                p_id,
                visit_date,
                consultation_fee,
                medicine_amount,
                service_amount,
                payment_mode
            )
            VALUES
            (
                visit_seq.NEXTVAL,
                :1,
                SYSDATE,
                :2,
                :3,
                :4,
                :5
            )
            """,
            [
                patient_id,
                consultation_fee,
                medicine_amount,
                service_fee,
                payment_mode
            ]
        )
        cursor.execute(
            """
            SELECT visit_seq.CURRVAL
            FROM dual
            """
        )

        visit_id = cursor.fetchone()[0]

        for medicine_id, qty in medicine_details:

            cursor.execute(
                """
                INSERT INTO Medicine_Dispensed
                (
                    dispense_id,
                    visit_id,
                    medicine_id,
                    quantity_given
                )
                VALUES
                (
                    dispense_seq.NEXTVAL,
                    :1,
                    :2,
                    :3
                )
                """,
                [
                    visit_id,
                    medicine_id,
                    qty
                ]
            )



        conn.commit()

        st.success(
            f"Visit created successfully! Patient ID: {patient_id}"
        )

elif page == "Purchase Stock":

    st.title("📦 Purchase Stock")

    medicine_df = run_query(
        """
        SELECT
            medicine_id,
            medicine_name
        FROM Medicine
        ORDER BY medicine_name
        """
    )

    with st.form("purchase_form"):

        selected_medicine = st.selectbox(
            "Medicine",
            medicine_df["MEDICINE_NAME"]
        )

        quantity_purchased = st.number_input(
            "Quantity Purchased",
            min_value=1,
            step=1
        )

        submitted_purchase = st.form_submit_button(
            "Add Stock"
        )

    if submitted_purchase:

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT medicine_id
            FROM Medicine
            WHERE medicine_name = :1
            """,
            [selected_medicine]
        )

        medicine_id = cursor.fetchone()[0]

        cursor.execute(
            """
            INSERT INTO Medicine_Purchased
            (
                purchase_id,
                medicine_id,
                quantity_purchased,
                purchase_date
            )
            VALUES
            (
                purchase_seq.NEXTVAL,
                :1,
                :2,
                SYSDATE
            )
            """,
            [
                medicine_id,
                quantity_purchased
            ]
        )

        conn.commit()

        st.success(
            f"{quantity_purchased} units added to inventory."
        )