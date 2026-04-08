# 🔗 ER Diagram — Hospital Patient Management System

## Entity-Relationship Overview

This document describes all entities, attributes, and relationships in the MediCare PMS database.

---

## Entities & Attributes

```
┌─────────────────────────────────────────────┐
│                  PATIENTS                   │
├─────────────────────────────────────────────┤
│ PK  patient_id     INTEGER (AUTOINCREMENT)  │
│     name           TEXT    NOT NULL         │
│     age            INTEGER CHECK(1–149)     │
│     gender         TEXT    CHECK(enum)      │
│     phone          TEXT    UNIQUE           │
│     address        TEXT    NOT NULL         │
│     blood_group    TEXT    CHECK(enum)      │
│     created_at     TEXT    DEFAULT now()    │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│                  DOCTORS                    │
├─────────────────────────────────────────────┤
│ PK  doctor_id        INTEGER (AUTOINCREMENT)│
│     name             TEXT    NOT NULL       │
│     specialization   TEXT    NOT NULL       │
│     phone            TEXT    UNIQUE         │
│     email            TEXT    UNIQUE         │
│     schedule         TEXT    NOT NULL       │
│     consultation_fee REAL    CHECK(≥0)      │
└─────────────────────────────────────────────┘

┌──────────────────────────────────────────────────┐
│                  APPOINTMENTS                    │
├──────────────────────────────────────────────────┤
│ PK  appointment_id   INTEGER (AUTOINCREMENT)     │
│ FK  patient_id       → patients(patient_id)      │
│ FK  doctor_id        → doctors(doctor_id)        │
│     appointment_date TEXT    NOT NULL            │
│     time_slot        TEXT    NOT NULL            │
│     status           TEXT    CHECK(enum)         │
│     reason           TEXT    NOT NULL            │
│ UQ  (doctor_id, appointment_date, time_slot)     │
└──────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│                PRESCRIPTIONS                    │
├─────────────────────────────────────────────────┤
│ PK  prescription_id  INTEGER (AUTOINCREMENT)    │
│ FK  appointment_id   → appointments (UNIQUE)    │
│     medicines        TEXT    NOT NULL           │
│     dosage           TEXT    NOT NULL           │
│     instructions     TEXT                       │
│     prescribed_date  TEXT    DEFAULT today()    │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│                    BILLS                        │
├─────────────────────────────────────────────────┤
│ PK  bill_id          INTEGER (AUTOINCREMENT)    │
│ FK  patient_id       → patients(patient_id)     │
│ FK  appointment_id   → appointments (UNIQUE)    │
│     consultation_fee REAL    CHECK(≥0)          │
│     medicine_charges REAL    CHECK(≥0)          │
│     other_charges    REAL    CHECK(≥0)          │
│     total_amount     REAL    CHECK(≥0)          │
│     payment_status   TEXT    CHECK(enum)        │
│     bill_date        TEXT    DEFAULT today()    │
└─────────────────────────────────────────────────┘
```

---

## Relationships Diagram

```
PATIENTS ──────────────────────────────────────────────────────────┐
│                                                                   │
│  1                                                               MANY
│                                                                   │
└──── books ──── APPOINTMENTS ──── has ──── PRESCRIPTIONS          │
       MANY         │   │  1                    1               MANY│
                    │   │                                           │
                    │   └──── generates ──────────── BILLS ────────┘
                 1  │             MANY              1
                    │
               MANY │
                    │
                 DOCTORS
```

---

## Relationship Details

### 1. PATIENTS → APPOINTMENTS (One-to-Many)
- **Cardinality**: 1 Patient can have MANY Appointments
- **FK**: `appointments.patient_id` → `patients.patient_id`
- **Delete Rule**: ON DELETE CASCADE (deleting a patient removes all their appointments)
- **Business Rule**: A patient must exist before booking an appointment

```
PATIENTS ──< APPOINTMENTS
  1             MANY
```

---

### 2. DOCTORS → APPOINTMENTS (One-to-Many)
- **Cardinality**: 1 Doctor can have MANY Appointments
- **FK**: `appointments.doctor_id` → `doctors.doctor_id`
- **Delete Rule**: ON DELETE CASCADE
- **Business Rule**: A doctor must exist before an appointment can be booked with them
- **Special Constraint**: `UNIQUE(doctor_id, appointment_date, time_slot)` prevents double-booking

```
DOCTORS ──< APPOINTMENTS
  1            MANY
```

---

### 3. APPOINTMENTS → PRESCRIPTIONS (One-to-One)
- **Cardinality**: 1 Appointment can have at most 1 Prescription
- **FK**: `prescriptions.appointment_id` → `appointments.appointment_id` (UNIQUE)
- **Delete Rule**: ON DELETE CASCADE
- **Business Rule**: Only completed appointments may have a prescription

```
APPOINTMENTS ──|| PRESCRIPTIONS
     1              0 or 1
```

---

### 4. APPOINTMENTS → BILLS (One-to-One)
- **Cardinality**: 1 Appointment can have at most 1 Bill
- **FK**: `bills.appointment_id` → `appointments.appointment_id` (UNIQUE)
- **Delete Rule**: ON DELETE CASCADE
- **Business Rule**: Only completed appointments may be billed

```
APPOINTMENTS ──|| BILLS
     1           0 or 1
```

---

### 5. PATIENTS → BILLS (One-to-Many)
- **Cardinality**: 1 Patient can have MANY Bills (one per appointment)
- **FK**: `bills.patient_id` → `patients.patient_id`
- **Delete Rule**: ON DELETE CASCADE

```
PATIENTS ──< BILLS
   1          MANY
```

---

## Full ER Diagram (Text-Based)

```
                    ┌──────────────┐
                    │   PATIENTS   │
                    │──────────────│
                    │PK patient_id │──────────────────────────────┐
                    │   name       │                              │
                    │   age        │                              │ 1:M
                    │   gender     │                              │
                    │   phone      │                              ▼
                    │   address    │     ┌──────────────────────────────┐
                    │   blood_group│     │        APPOINTMENTS          │
                    │   created_at │     │──────────────────────────────│
                    └──────────────┘     │PK appointment_id             │
                           │            │FK patient_id    ←────────────┘
                           │            │FK doctor_id     ←────────────┐
                           │ 1:M        │   appointment_date            │
                           │            │   time_slot                  │
                           ▼            │   status                     │
                    ┌──────────────┐    │   reason                     │
                    │    BILLS     │    │ UQ(doctor_id,date,time_slot)  │
                    │──────────────│    └──────────────────────────────┘
                    │PK bill_id    │          │              │
                    │FK patient_id │          │ 1:1          │ 1:1
                    │FK appt_id   ←┘          ▼              ▼
                    │   cons_fee   │  ┌──────────────┐  ┌──────────────┐
                    │   med_charges│  │PRESCRIPTIONS │  │   (linked    │
                    │   oth_charges│  │──────────────│  │  via BILLS   │
                    │   total      │  │PK rx_id      │  │  table ←──) │
                    │   pay_status │  │FK appt_id    │  └──────────────┘
                    │   bill_date  │  │   medicines  │
                    └──────────────┘  │   dosage     │
                                      │   instruc.   │
               ┌──────────────┐       │   rx_date    │
               │   DOCTORS    │       └──────────────┘
               │──────────────│
               │PK doctor_id  │──────────────────────────────────────┐
               │   name       │                                      │ 1:M
               │   speciali.  │                                      │
               │   phone      │                                      ▼
               │   email      │             (To APPOINTMENTS.doctor_id)
               │   schedule   │
               │   cons_fee   │
               └──────────────┘
```

---

## Cardinality Summary Table

| Relationship                         | Type      | Enforced By                     |
|--------------------------------------|-----------|---------------------------------|
| Patient → Appointments               | 1 : Many  | FK patient_id + CASCADE         |
| Doctor → Appointments                | 1 : Many  | FK doctor_id + CASCADE          |
| Appointment → Prescription           | 1 : 0..1  | FK + UNIQUE on appointment_id   |
| Appointment → Bill                   | 1 : 0..1  | FK + UNIQUE on appointment_id   |
| Patient → Bills (via appointments)   | 1 : Many  | FK patient_id + CASCADE         |

---

## Normalization Analysis

### First Normal Form (1NF) ✅
- All attributes contain atomic (indivisible) values
- No repeating groups or arrays
- Each row is uniquely identified by its primary key

### Second Normal Form (2NF) ✅
- Every 1NF table where all non-key attributes are fully functionally dependent on the entire primary key
- No partial dependencies (each table has a single-column PK)

### Third Normal Form (3NF) ✅
- No transitive dependencies
- `total_amount` in `bills` is derived but stored for query performance (acceptable in OLTP)
- `doctor_name` / `patient_name` are NOT stored redundantly — they are always joined from the source tables
