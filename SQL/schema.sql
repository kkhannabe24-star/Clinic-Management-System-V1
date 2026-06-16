CREATE TABLE Patient (
    p_id NUMBER PRIMARY KEY,

    p_name VARCHAR2(100) NOT NULL,

    p_age NUMBER(3)
        CHECK (p_age BETWEEN 0 AND 120),

    p_gender CHAR(1)
        CHECK (p_gender IN ('M','F','O')),

    mobile_number VARCHAR2(10) UNIQUE --unique because patient can revisit how do we know new patient or not
);	

CREATE TABLE Medicine (
    medicine_id NUMBER PRIMARY KEY,

    medicine_name VARCHAR2(100) NOT NULL,

    unit_type VARCHAR2(20),

    tablets_per_strip NUMBER,

    selling_price_per_unit NUMBER(10,2),

    purchase_price_per_unit NUMBER(10,2)
);
CREATE TABLE Visit (
    visit_id NUMBER PRIMARY KEY,

    p_id NUMBER NOT NULL,

    visit_date DATE NOT NULL,

    consultation_fee NUMBER(10,2) DEFAULT 400,

    medicine_amount NUMBER(10,2) DEFAULT 0,

    service_amount NUMBER(10,2) DEFAULT 0,

    payment_mode VARCHAR2(10)
        CHECK (payment_mode IN ('CASH','ONLINE')),

    CONSTRAINT fk_visit_patient
        FOREIGN KEY (p_id)
        REFERENCES Patient(p_id)
);
CREATE TABLE Medicine_Purchased (
    purchase_id NUMBER PRIMARY KEY,

    medicine_id NUMBER NOT NULL,

    purchase_date DATE NOT NULL,

    quantity_purchased NUMBER NOT NULL,

    total_purchase_cost NUMBER(10,2),

    vendor_name VARCHAR2(100),

    CONSTRAINT fk_purchase_medicine
        FOREIGN KEY (medicine_id)
        REFERENCES Medicine(medicine_id)
);
CREATE TABLE Medicine_Dispensed (
    dispense_id NUMBER PRIMARY KEY,

    visit_id NUMBER NOT NULL,

    medicine_id NUMBER NOT NULL,

    quantity_given NUMBER NOT NULL,

    CONSTRAINT fk_dispense_visit
        FOREIGN KEY (visit_id)
        REFERENCES Visit(visit_id),

    CONSTRAINT fk_dispense_medicine
        FOREIGN KEY (medicine_id)
        REFERENCES Medicine(medicine_id)
);
