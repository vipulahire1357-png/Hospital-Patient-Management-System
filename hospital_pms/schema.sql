-- ============================================================
-- Hospital Patient Management System - Database Schema
-- SQLite compatible with full relational integrity
-- ============================================================

PRAGMA foreign_keys = ON;

-- ============================================================
-- TABLE: patients
-- Stores all registered patient records
-- ============================================================
CREATE TABLE IF NOT EXISTS patients (
    patient_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name         TEXT    NOT NULL,
    age          INTEGER NOT NULL CHECK (age > 0 AND age < 150),
    gender       TEXT    NOT NULL CHECK (gender IN ('Male', 'Female', 'Other')),
    phone        TEXT    NOT NULL UNIQUE,
    address      TEXT    NOT NULL,
    blood_group  TEXT    NOT NULL CHECK (blood_group IN ('A+','A-','B+','B-','AB+','AB-','O+','O-')),
    created_at   TEXT    NOT NULL DEFAULT (datetime('now','localtime'))
);

-- ============================================================
-- TABLE: doctors
-- Stores all registered doctor records
-- ============================================================
CREATE TABLE IF NOT EXISTS doctors (
    doctor_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    name             TEXT    NOT NULL,
    specialization   TEXT    NOT NULL,
    phone            TEXT    NOT NULL UNIQUE,
    email            TEXT    NOT NULL UNIQUE,
    schedule         TEXT    NOT NULL,
    consultation_fee REAL    NOT NULL CHECK (consultation_fee >= 0)
);

-- ============================================================
-- TABLE: appointments
-- Links patients to doctors with date/time and status tracking
-- Prevents double-booking via UNIQUE constraint on (doctor_id, appointment_date, time_slot)
-- ============================================================
CREATE TABLE IF NOT EXISTS appointments (
    appointment_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id       INTEGER NOT NULL,
    doctor_id        INTEGER NOT NULL,
    appointment_date TEXT    NOT NULL,
    time_slot        TEXT    NOT NULL,
    status           TEXT    NOT NULL DEFAULT 'scheduled'
                             CHECK (status IN ('scheduled','cancelled','completed')),
    reason           TEXT    NOT NULL,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id)  REFERENCES doctors(doctor_id)   ON DELETE CASCADE,
    UNIQUE (doctor_id, appointment_date, time_slot)
);

-- ============================================================
-- TABLE: prescriptions
-- Linked to a completed appointment; stores medicine details
-- ============================================================
CREATE TABLE IF NOT EXISTS prescriptions (
    prescription_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    appointment_id   INTEGER NOT NULL UNIQUE,
    medicines        TEXT    NOT NULL,
    dosage           TEXT    NOT NULL,
    instructions     TEXT,
    prescribed_date  TEXT    NOT NULL DEFAULT (date('now','localtime')),
    FOREIGN KEY (appointment_id) REFERENCES appointments(appointment_id) ON DELETE CASCADE
);

-- ============================================================
-- TABLE: bills
-- Auto-generated billing linked to appointment; tracks payments
-- ============================================================
CREATE TABLE IF NOT EXISTS bills (
    bill_id           INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id        INTEGER NOT NULL,
    appointment_id    INTEGER NOT NULL UNIQUE,
    consultation_fee  REAL    NOT NULL DEFAULT 0 CHECK (consultation_fee >= 0),
    medicine_charges  REAL    NOT NULL DEFAULT 0 CHECK (medicine_charges >= 0),
    other_charges     REAL    NOT NULL DEFAULT 0 CHECK (other_charges >= 0),
    total_amount      REAL    NOT NULL DEFAULT 0 CHECK (total_amount >= 0),
    payment_status    TEXT    NOT NULL DEFAULT 'pending'
                              CHECK (payment_status IN ('paid','pending','cancelled')),
    bill_date         TEXT    NOT NULL DEFAULT (date('now','localtime')),
    FOREIGN KEY (patient_id)     REFERENCES patients(patient_id)         ON DELETE CASCADE,
    FOREIGN KEY (appointment_id) REFERENCES appointments(appointment_id) ON DELETE CASCADE
);
