# 🏥 MediCare — Hospital Patient Management System

> A fully functional **DBMS Academic Project** built with **Python Flask**, **SQLite**, and **Vanilla JS**.

---

## 📌 Project Overview

MediCare PMS is a web-based Hospital Patient Management System that demonstrates key Database Management System concepts including:

- **Normalized relational schema** (1NF, 2NF, 3NF)
- **Referential integrity** via FOREIGN KEY constraints with CASCADE
- **Parameterized queries** to prevent SQL injection
- **Transaction-like operations** (bill generation, prescription linking)
- **MVC architecture** separating concerns cleanly

---

## 🛠️ Tech Stack

| Layer     | Technology               |
|-----------|--------------------------|
| Backend   | Python 3.8+ · Flask 3.x  |
| Database  | SQLite 3 (file-based)    |
| Frontend  | HTML5 · CSS3 · Vanilla JS |
| Fonts     | Google Fonts (Inter)     |
| Pattern   | MVC (Model-View-Controller) |

---

## 📂 Project Structure

```
hospital_pms/
├── app.py                   # Flask entry point + all route controllers
├── database.py              # DB connection, init, all SQL query functions
├── schema.sql               # CREATE TABLE statements with all constraints
├── seed.py                  # Sample data insertion script
├── hospital.db              # SQLite database (auto-created on first run)
├── README.md                # This file
├── ER_DIAGRAM.md            # Entity-Relationship diagram
├── setup_and_run.md         # Detailed setup instructions
├── static/
│   ├── style.css            # Complete UI stylesheet
│   └── script.js            # Form validation, AJAX, modals
└── templates/
    ├── base.html            # Base layout with sidebar navigation
    ├── index.html           # Dashboard with stats cards
    ├── patients.html        # Patient list + register form
    ├── edit_patient.html    # Edit patient form
    ├── patient_history.html # Full medical history timeline
    ├── doctors.html         # Doctor list + add form
    ├── edit_doctor.html     # Edit doctor form
    ├── doctor_schedule.html # Doctor's appointment schedule
    ├── appointments.html    # Book/view/cancel/reschedule appointments
    ├── prescriptions.html   # Add/view prescriptions
    ├── billing.html         # Generate bills + payment status
    ├── bill_detail.html     # Printable bill view
    └── 404.html             # Custom 404 error page
```

---

## 🗃️ Database Schema — 5 Normalized Tables

### `patients`
| Column      | Type    | Constraints                        |
|-------------|---------|------------------------------------|
| patient_id  | INTEGER | PRIMARY KEY AUTOINCREMENT          |
| name        | TEXT    | NOT NULL                           |
| age         | INTEGER | NOT NULL, CHECK (1–149)            |
| gender      | TEXT    | CHECK IN ('Male','Female','Other') |
| phone       | TEXT    | NOT NULL, UNIQUE                   |
| address     | TEXT    | NOT NULL                           |
| blood_group | TEXT    | CHECK IN ('A+','A-','B+',…)        |
| created_at  | TEXT    | DEFAULT datetime('now','localtime')|

### `doctors`
| Column           | Type    | Constraints               |
|------------------|---------|---------------------------|
| doctor_id        | INTEGER | PRIMARY KEY AUTOINCREMENT |
| name             | TEXT    | NOT NULL                  |
| specialization   | TEXT    | NOT NULL                  |
| phone            | TEXT    | NOT NULL, UNIQUE          |
| email            | TEXT    | NOT NULL, UNIQUE          |
| schedule         | TEXT    | NOT NULL                  |
| consultation_fee | REAL    | NOT NULL, CHECK (≥ 0)     |

### `appointments`
| Column           | Type    | Constraints                                     |
|------------------|---------|-------------------------------------------------|
| appointment_id   | INTEGER | PRIMARY KEY AUTOINCREMENT                       |
| patient_id       | INTEGER | FK → patients, ON DELETE CASCADE                |
| doctor_id        | INTEGER | FK → doctors, ON DELETE CASCADE                 |
| appointment_date | TEXT    | NOT NULL                                        |
| time_slot        | TEXT    | NOT NULL                                        |
| status           | TEXT    | CHECK IN ('scheduled','cancelled','completed')  |
| reason           | TEXT    | NOT NULL                                        |
|                  |         | UNIQUE (doctor_id, appointment_date, time_slot) |

### `prescriptions`
| Column          | Type    | Constraints                              |
|-----------------|---------|------------------------------------------|
| prescription_id | INTEGER | PRIMARY KEY AUTOINCREMENT                |
| appointment_id  | INTEGER | FK → appointments UNIQUE, CASCADE        |
| medicines       | TEXT    | NOT NULL                                 |
| dosage          | TEXT    | NOT NULL                                 |
| instructions    | TEXT    |                                          |
| prescribed_date | TEXT    | DEFAULT date('now','localtime')          |

### `bills`
| Column           | Type    | Constraints                                    |
|------------------|---------|------------------------------------------------|
| bill_id          | INTEGER | PRIMARY KEY AUTOINCREMENT                      |
| patient_id       | INTEGER | FK → patients, CASCADE                         |
| appointment_id   | INTEGER | FK → appointments UNIQUE, CASCADE              |
| consultation_fee | REAL    | NOT NULL DEFAULT 0, CHECK (≥ 0)               |
| medicine_charges | REAL    | NOT NULL DEFAULT 0, CHECK (≥ 0)               |
| other_charges    | REAL    | NOT NULL DEFAULT 0, CHECK (≥ 0)               |
| total_amount     | REAL    | NOT NULL DEFAULT 0, CHECK (≥ 0)               |
| payment_status   | TEXT    | CHECK IN ('paid','pending','cancelled')        |
| bill_date        | TEXT    | DEFAULT date('now','localtime')                |

---

## ✨ Features

### Dashboard
- Live counts: total patients, doctors, today's appointments, pending bills
- Recent appointments widget
- Quick-action shortcut buttons

### Patients Module
- ✅ Register new patient with full validation
- ✅ List all patients with sortable table
- ✅ Edit patient details
- ✅ Delete patient (cascades all related records)
- ✅ View complete medical history (appointments + prescriptions + bills)

### Doctors Module
- ✅ Add new doctor with specialization autocomplete
- ✅ List all doctors with fee and schedule
- ✅ Edit doctor details
- ✅ Delete doctor
- ✅ View doctor's full appointment schedule

### Appointments Module
- ✅ Book appointment with AJAX-powered cascading dropdowns (specialty → doctor → available slots)
- ✅ Double-booking prevention (DB UNIQUE constraint)
- ✅ Cancel appointment
- ✅ Mark appointment as completed
- ✅ Reschedule to new date/time via modal

### Prescriptions Module
- ✅ Add prescription linked only to completed appointments
- ✅ Each appointment can have exactly one prescription (enforced by DB)
- ✅ Filter prescriptions by patient via AJAX
- ✅ View all prescriptions

### Billing Module
- ✅ Auto-generate bill from completed appointment
- ✅ Auto-fill consultation fee from doctor record
- ✅ Live total calculation on form
- ✅ Add medicine and other charges
- ✅ Mark bill as paid / cancel
- ✅ Printable bill detail page

---

## 🔒 Security Features

- All SQL queries use **parameterized statements** (no string interpolation)
- **FOREIGN KEY constraints** with `ON DELETE CASCADE` for referential integrity
- **CHECK constraints** for domain validation at the DB layer
- **UNIQUE constraints** prevent duplicate phone, email, and appointment slots
- Flash messages for all user feedback

---

## 🚀 Quick Start

See **`setup_and_run.md`** for full step-by-step instructions.

```bash
cd hospital_pms
pip install flask
python seed.py       # Initialize DB + insert sample data
python app.py        # Start the server
# Visit: http://127.0.0.1:5000
```

---

## 📊 DBMS Concepts Demonstrated

| Concept              | Where Used                                         |
|----------------------|----------------------------------------------------|
| Primary Keys         | All 5 tables                                       |
| Foreign Keys         | appointments, prescriptions, bills                 |
| NOT NULL constraints | All required columns                               |
| CHECK constraints    | age, gender, blood_group, status, payment_status   |
| DEFAULT values       | created_at, bill_date, payment_status, total_amount|
| UNIQUE constraints   | phone, email, (doctor_id, date, slot)              |
| CASCADE DELETE       | appointments → prescriptions → bills               |
| Parameterized SQL    | All queries in database.py                         |
| Joins                | Multi-table SELECT across all modules              |
| Aggregation          | COUNT(*) for dashboard stats                       |
| Subqueries           | Filtering unbilled/unprescribed appointments       |

---

## 👥 Team / Author

- **Author**: [Your Name]  
- **Roll No**: [Your Roll Number]  
- **Subject**: Database Management Systems  
- **Academic Year**: 2024–25
