Clinic Management System
Overview
A full-stack Clinic Management System developed using Oracle SQL, Python, Streamlit, and Pandas. The application helps manage patient visits, medicine inventory, revenue tracking, and operational analytics through an interactive dashboard.
The system was designed to simulate real-world clinic workflows, including patient registration, repeat patient detection, medicine dispensing, inventory management, stock purchases, and business reporting.
________________________________________
Features
Patient Management
•	New patient registration
•	Repeat patient detection using mobile number
•	Automatic patient reuse for returning visits
Visit Management
•	Consultation fee tracking
•	Service fee tracking
•	Cash and online payment support
•	Visit history storage
Medicine Dispensing
•	Multiple medicines per visit
•	Dynamic medicine selection
•	Automatic medicine revenue calculation
•	Inventory validation before dispensing
Inventory Management
•	Stock purchase entry
•	Real-time inventory updates
•	Low stock alerts
•	Inventory monitoring dashboard
Dashboard Analytics
•	Total revenue
•	Consultation revenue
•	Medicine revenue
•	Service revenue
•	Daily patient count
•	Repeat patient count
•	Payment mode analysis
•	Medicines sold report
•	Inventory status report
•	Low stock alerts
________________________________________
Database Design
Tables
•	Patient
•	Visit
•	Medicine
•	Medicine_Purchased
•	Medicine_Dispensed
Relationships
•	One Patient → Many Visits
•	One Visit → Many Dispensed Medicines
•	One Medicine → Many Purchases
•	One Medicine → Many Dispensing Records

![alt text](<DOCS/ER DIAGRAM/ER_Clinic.png>)
________________________________________
Technology Stack
Backend
•	Python
•	Oracle Database
•	Oracle SQL
Frontend
•	Streamlit
Data Processing
•	Pandas
Visualization
•	Plotly
________________________________________
Screenshots
Dashboard
![alt text](<DOCS/Test_Screenshots/Screenshot 2026-06-16 014532.png>)

New Visit Form
![alt text](<DOCS/Test_Screenshots/Screenshot 2026-06-16 014954.png>)
![alt text](<DOCS/Test_Screenshots/Screenshot 2026-06-16 015010.png>)
 
Multiple Medicine Dispensing
![alt text](<DOCS/Test_Screenshots/Screenshot 2026-06-16 015033.png>)
Inventory Status
![alt text](<DOCS/Test_Screenshots/Screenshot 2026-06-16 014635.png>)
Low Stock Alerts
![alt text](<DOCS/Test_Screenshots/Screenshot 2026-06-16 014650.png>)
________________________________________
Future Roadmap
Version 2
•	Inventory forecasting
•	Revenue forecasting
•	AI/ML recommendations
•	Business analytics
Version 3
•	Cloud deployment
•	Multi-user support
•	Remote database access
•	Scalable architecture
________________________________________
Author
Kavya Khanna
Built as a practical DBMS + Data Analytics project for real-world clinic operations.
