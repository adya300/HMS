# 🏥 Hospital Management System (Flask)

A role-based **Hospital Management System** built using **Flask and SQLite**, designed to model real-world hospital workflows with separate access levels for **Patients, Doctors, and Admin**.

This project focuses on backend development, authentication, and relational database design.

---

## 📌 Features

### 🧑‍⚕️ Patient
- Register and log in
- Book doctor appointments
- View appointment status and medical history

### 👨‍⚕️ Doctor
- View assigned appointments
- Update diagnosis, prescriptions, and treatment details
- Maintain patient visit records

### 🛠️ Admin
- Manage doctors and patients
- Monitor appointments
- Centralized control over system data

---

## 🏗️ System Architecture
- Backend built using **Flask**
- Frontend rendered using **Jinja2 templates**
- **Role-based routing and access control**
- Session-based authentication
- Modular project structure

---

## 🗄️ Database Design
- Database: **SQLite**
- Implemented **manual SQL queries (without ORM)**
- Tables:
  - Patient
  - Doctor
  - Department
  - Appointments
  - Treatment

**Relationships:**
- One-to-Many → Patient → Appointments  
- One-to-Many → Doctor → Appointments  
- One-to-One → Appointment → Treatment  
- One-to-Many → Department → Doctor  

SQL JOINs are used to fetch complete patient visit history and related records.

---

## 🔧 Tech Stack
- **Backend:** Flask (Python)
- **Frontend:** HTML, CSS, Jinja2
- **Database:** SQLite
- **Authentication:** Session-based login

---

## 🎯 Key Learnings
- Role-Based Access Control (RBAC)
- Relational database design
- SQL JOIN operations
- Backend routing and session handling
- CRUD operations
- Debugging and structuring backend applications

---

## ▶️ Demo
- 📹 Demo video shared on LinkedIn  
- 📁 Source code available in this repository

---

## 🚀 Future Improvements
- Password hashing and improved security
- REST API implementation
- Vue.js integration for dynamic frontend
- UI/UX enhancements
