"""
database.py
===========
Handles all database operations for the Hospital PMS.
Provides connection management, schema initialization, and
parameterized SQL query functions for each model.
"""

import sqlite3
import os

# Path to the SQLite database file
DB_PATH = os.path.join(os.path.dirname(__file__), 'hospital.db')
# Path to the SQL schema file
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), 'schema.sql')


# ── Connection ────────────────────────────────────────────────────────────────

def get_connection():
    """
    Opens and returns a new SQLite connection with:
      - Row factory set so results behave like dicts
      - Foreign-key enforcement enabled
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row        # access columns by name
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """
    Reads schema.sql and executes it against the database.
    Safe to call multiple times (uses CREATE TABLE IF NOT EXISTS).
    """
    with open(SCHEMA_PATH, 'r') as f:
        schema = f.read()
    conn = get_connection()
    conn.executescript(schema)
    conn.commit()
    conn.close()


# ══════════════════════════════════════════════════════════════════════════════
# PATIENTS
# ══════════════════════════════════════════════════════════════════════════════

def get_all_patients():
    """Returns a list of all patients ordered by creation date descending."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM patients ORDER BY created_at DESC"
    ).fetchall()
    conn.close()
    return rows


def get_patient_by_id(patient_id):
    """Returns a single patient row matching the given patient_id."""
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM patients WHERE patient_id = ?", (patient_id,)
    ).fetchone()
    conn.close()
    return row


def add_patient(name, age, gender, phone, address, blood_group):
    """
    Inserts a new patient record.
    Returns the newly created patient_id on success, None on failure.
    """
    conn = get_connection()
    try:
        cur = conn.execute(
            """INSERT INTO patients (name, age, gender, phone, address, blood_group)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (name, age, gender, phone, address, blood_group)
        )
        conn.commit()
        return cur.lastrowid
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()


def update_patient(patient_id, name, age, gender, phone, address, blood_group):
    """
    Updates an existing patient's details.
    Returns True if exactly one row was updated, False otherwise.
    """
    conn = get_connection()
    try:
        cur = conn.execute(
            """UPDATE patients
               SET name=?, age=?, gender=?, phone=?, address=?, blood_group=?
               WHERE patient_id=?""",
            (name, age, gender, phone, address, blood_group, patient_id)
        )
        conn.commit()
        return cur.rowcount == 1
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def delete_patient(patient_id):
    """
    Deletes a patient and all related records (CASCADE).
    Returns True if the patient was found and deleted.
    """
    conn = get_connection()
    cur = conn.execute(
        "DELETE FROM patients WHERE patient_id = ?", (patient_id,)
    )
    conn.commit()
    conn.close()
    return cur.rowcount == 1


def get_patient_medical_history(patient_id):
    """
    Returns all appointments, prescriptions, and bills for a patient,
    joined together for the medical-history view.
    """
    conn = get_connection()
    rows = conn.execute(
        """SELECT
               a.appointment_id,
               a.appointment_date,
               a.time_slot,
               a.status,
               a.reason,
               d.name       AS doctor_name,
               d.specialization,
               p.medicines,
               p.dosage,
               p.instructions,
               p.prescribed_date,
               b.total_amount,
               b.payment_status
           FROM appointments a
           JOIN doctors d ON d.doctor_id = a.doctor_id
           LEFT JOIN prescriptions p ON p.appointment_id = a.appointment_id
           LEFT JOIN bills         b ON b.appointment_id = a.appointment_id
           WHERE a.patient_id = ?
           ORDER BY a.appointment_date DESC""",
        (patient_id,)
    ).fetchall()
    conn.close()
    return rows


# ══════════════════════════════════════════════════════════════════════════════
# DOCTORS
# ══════════════════════════════════════════════════════════════════════════════

def get_all_doctors():
    """Returns a list of all doctors ordered by name."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM doctors ORDER BY name"
    ).fetchall()
    conn.close()
    return rows


def get_doctor_by_id(doctor_id):
    """Returns a single doctor row matching the given doctor_id."""
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM doctors WHERE doctor_id = ?", (doctor_id,)
    ).fetchone()
    conn.close()
    return row


def get_doctors_by_specialization(specialization):
    """
    Returns doctors filtered by specialization.
    Used for AJAX dropdown population when booking appointments.
    """
    conn = get_connection()
    rows = conn.execute(
        "SELECT doctor_id, name, consultation_fee FROM doctors WHERE specialization = ? ORDER BY name",
        (specialization,)
    ).fetchall()
    conn.close()
    return rows


def get_all_specializations():
    """Returns a distinct list of all specializations available."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT DISTINCT specialization FROM doctors ORDER BY specialization"
    ).fetchall()
    conn.close()
    return [r['specialization'] for r in rows]


def add_doctor(name, specialization, phone, email, schedule, consultation_fee):
    """
    Inserts a new doctor record.
    Returns the new doctor_id on success, None on unique-constraint failure.
    """
    conn = get_connection()
    try:
        cur = conn.execute(
            """INSERT INTO doctors (name, specialization, phone, email, schedule, consultation_fee)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (name, specialization, phone, email, schedule, consultation_fee)
        )
        conn.commit()
        return cur.lastrowid
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()


def update_doctor(doctor_id, name, specialization, phone, email, schedule, consultation_fee):
    """
    Updates an existing doctor's details.
    Returns True if exactly one row was updated.
    """
    conn = get_connection()
    try:
        cur = conn.execute(
            """UPDATE doctors
               SET name=?, specialization=?, phone=?, email=?, schedule=?, consultation_fee=?
               WHERE doctor_id=?""",
            (name, specialization, phone, email, schedule, consultation_fee, doctor_id)
        )
        conn.commit()
        return cur.rowcount == 1
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def delete_doctor(doctor_id):
    """
    Deletes a doctor and all related records (CASCADE).
    Returns True if the doctor was found and deleted.
    """
    conn = get_connection()
    cur = conn.execute(
        "DELETE FROM doctors WHERE doctor_id = ?", (doctor_id,)
    )
    conn.commit()
    conn.close()
    return cur.rowcount == 1


def get_doctor_schedule(doctor_id):
    """
    Returns all appointments for a specific doctor,
    joined with patient info for the schedule view.
    """
    conn = get_connection()
    rows = conn.execute(
        """SELECT
               a.appointment_id,
               a.appointment_date,
               a.time_slot,
               a.status,
               a.reason,
               p.name   AS patient_name,
               p.age,
               p.gender,
               p.phone  AS patient_phone
           FROM appointments a
           JOIN patients p ON p.patient_id = a.patient_id
           WHERE a.doctor_id = ?
           ORDER BY a.appointment_date DESC, a.time_slot""",
        (doctor_id,)
    ).fetchall()
    conn.close()
    return rows


# ══════════════════════════════════════════════════════════════════════════════
# APPOINTMENTS
# ══════════════════════════════════════════════════════════════════════════════

def get_all_appointments():
    """
    Returns all appointments with patient and doctor names joined,
    ordered by date descending.
    """
    conn = get_connection()
    rows = conn.execute(
        """SELECT
               a.*,
               p.name AS patient_name,
               d.name AS doctor_name,
               d.specialization
           FROM appointments a
           JOIN patients p ON p.patient_id = a.patient_id
           JOIN doctors  d ON d.doctor_id  = a.doctor_id
           ORDER BY a.appointment_date DESC, a.time_slot"""
    ).fetchall()
    conn.close()
    return rows


def get_appointment_by_id(appointment_id):
    """Returns a single appointment with patient and doctor details."""
    conn = get_connection()
    row = conn.execute(
        """SELECT
               a.*,
               p.name AS patient_name,
               d.name AS doctor_name,
               d.consultation_fee,
               d.specialization
           FROM appointments a
           JOIN patients p ON p.patient_id = a.patient_id
           JOIN doctors  d ON d.doctor_id  = a.doctor_id
           WHERE a.appointment_id = ?""",
        (appointment_id,)
    ).fetchone()
    conn.close()
    return row


def get_todays_appointments():
    """
    Returns all appointments scheduled for today's date.
    Used for the dashboard live count.
    """
    conn = get_connection()
    rows = conn.execute(
        """SELECT COUNT(*) as cnt FROM appointments
           WHERE appointment_date = date('now','localtime')
           AND status = 'scheduled'"""
    ).fetchone()
    conn.close()
    return rows['cnt'] if rows else 0


def book_appointment(patient_id, doctor_id, appointment_date, time_slot, reason):
    """
    Books a new appointment.
    The UNIQUE constraint on (doctor_id, appointment_date, time_slot)
    prevents double-booking at the database level.
    Returns the new appointment_id, or None on conflict.
    """
    conn = get_connection()
    try:
        cur = conn.execute(
            """INSERT INTO appointments
               (patient_id, doctor_id, appointment_date, time_slot, reason)
               VALUES (?, ?, ?, ?, ?)""",
            (patient_id, doctor_id, appointment_date, time_slot, reason)
        )
        conn.commit()
        return cur.lastrowid
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()


def update_appointment_status(appointment_id, status):
    """
    Updates the status of an appointment (scheduled / cancelled / completed).
    Returns True if the update succeeded.
    """
    conn = get_connection()
    cur = conn.execute(
        "UPDATE appointments SET status=? WHERE appointment_id=?",
        (status, appointment_id)
    )
    conn.commit()
    conn.close()
    return cur.rowcount == 1


def reschedule_appointment(appointment_id, new_date, new_slot):
    """
    Changes the date and time_slot of an existing scheduled appointment.
    Returns True on success, None on double-booking conflict.
    """
    conn = get_connection()
    try:
        cur = conn.execute(
            """UPDATE appointments
               SET appointment_date=?, time_slot=?, status='scheduled'
               WHERE appointment_id=?""",
            (new_date, new_slot, appointment_id)
        )
        conn.commit()
        return cur.rowcount == 1
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()


def get_booked_slots(doctor_id, appointment_date):
    """
    Returns list of already-booked time slots for a doctor on a given date.
    Used by the frontend to grey-out unavailable slots.
    """
    conn = get_connection()
    rows = conn.execute(
        """SELECT time_slot FROM appointments
           WHERE doctor_id=? AND appointment_date=? AND status != 'cancelled'""",
        (doctor_id, appointment_date)
    ).fetchall()
    conn.close()
    return [r['time_slot'] for r in rows]


# ══════════════════════════════════════════════════════════════════════════════
# PRESCRIPTIONS
# ══════════════════════════════════════════════════════════════════════════════

def get_all_prescriptions():
    """
    Returns all prescriptions with patient name, doctor name,
    and appointment date joined for the prescriptions list view.
    """
    conn = get_connection()
    rows = conn.execute(
        """SELECT
               pr.*,
               p.name  AS patient_name,
               d.name  AS doctor_name,
               a.appointment_date
           FROM prescriptions pr
           JOIN appointments a ON a.appointment_id = pr.appointment_id
           JOIN patients     p ON p.patient_id     = a.patient_id
           JOIN doctors      d ON d.doctor_id      = a.doctor_id
           ORDER BY pr.prescribed_date DESC"""
    ).fetchall()
    conn.close()
    return rows


def get_prescriptions_by_patient(patient_id):
    """
    Returns all prescriptions for a specific patient,
    ordered by prescribed date descending.
    """
    conn = get_connection()
    rows = conn.execute(
        """SELECT
               pr.*,
               d.name  AS doctor_name,
               a.appointment_date
           FROM prescriptions pr
           JOIN appointments a ON a.appointment_id = pr.appointment_id
           JOIN doctors      d ON d.doctor_id      = a.doctor_id
           WHERE a.patient_id = ?
           ORDER BY pr.prescribed_date DESC""",
        (patient_id,)
    ).fetchall()
    conn.close()
    return rows


def get_completed_appointments_without_prescription():
    """
    Returns completed appointments that do NOT yet have a prescription.
    Used to populate the 'Add Prescription' dropdown.
    """
    conn = get_connection()
    rows = conn.execute(
        """SELECT
               a.appointment_id,
               a.appointment_date,
               p.name AS patient_name,
               d.name AS doctor_name
           FROM appointments a
           JOIN patients p ON p.patient_id = a.patient_id
           JOIN doctors  d ON d.doctor_id  = a.doctor_id
           WHERE a.status = 'completed'
             AND a.appointment_id NOT IN (
                 SELECT appointment_id FROM prescriptions
             )
           ORDER BY a.appointment_date DESC"""
    ).fetchall()
    conn.close()
    return rows


def add_prescription(appointment_id, medicines, dosage, instructions):
    """
    Inserts a new prescription linked to a completed appointment.
    Returns the new prescription_id, or None if already exists.
    """
    conn = get_connection()
    try:
        cur = conn.execute(
            """INSERT INTO prescriptions (appointment_id, medicines, dosage, instructions)
               VALUES (?, ?, ?, ?)""",
            (appointment_id, medicines, dosage, instructions)
        )
        conn.commit()
        return cur.lastrowid
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()


# ══════════════════════════════════════════════════════════════════════════════
# BILLING
# ══════════════════════════════════════════════════════════════════════════════

def get_all_bills():
    """
    Returns all bills with patient name and doctor name joined,
    ordered by bill date descending.
    """
    conn = get_connection()
    rows = conn.execute(
        """SELECT
               b.*,
               p.name AS patient_name,
               d.name AS doctor_name,
               a.appointment_date
           FROM bills b
           JOIN patients     p ON p.patient_id     = b.patient_id
           JOIN appointments a ON a.appointment_id = b.appointment_id
           JOIN doctors      d ON d.doctor_id      = a.doctor_id
           ORDER BY b.bill_date DESC"""
    ).fetchall()
    conn.close()
    return rows


def get_bill_by_id(bill_id):
    """Returns a single bill with full patient, doctor, and appointment details."""
    conn = get_connection()
    row = conn.execute(
        """SELECT
               b.*,
               p.name    AS patient_name,
               p.phone   AS patient_phone,
               p.address AS patient_address,
               d.name    AS doctor_name,
               d.specialization,
               a.appointment_date,
               a.time_slot,
               a.reason
           FROM bills b
           JOIN patients     p ON p.patient_id     = b.patient_id
           JOIN appointments a ON a.appointment_id = b.appointment_id
           JOIN doctors      d ON d.doctor_id      = a.doctor_id
           WHERE b.bill_id = ?""",
        (bill_id,)
    ).fetchone()
    conn.close()
    return row


def get_pending_bills_count():
    """Returns the count of bills with payment_status = 'pending'."""
    conn = get_connection()
    row = conn.execute(
        "SELECT COUNT(*) as cnt FROM bills WHERE payment_status = 'pending'"
    ).fetchone()
    conn.close()
    return row['cnt'] if row else 0


def get_appointments_without_bill():
    """
    Returns completed appointments that do NOT yet have a bill.
    Used to populate the 'Generate Bill' dropdown.
    """
    conn = get_connection()
    rows = conn.execute(
        """SELECT
               a.appointment_id,
               a.appointment_date,
               p.name  AS patient_name,
               d.name  AS doctor_name,
               d.consultation_fee
           FROM appointments a
           JOIN patients p ON p.patient_id = a.patient_id
           JOIN doctors  d ON d.doctor_id  = a.doctor_id
           WHERE a.status = 'completed'
             AND a.appointment_id NOT IN (
                 SELECT appointment_id FROM bills
             )
           ORDER BY a.appointment_date DESC"""
    ).fetchall()
    conn.close()
    return rows


def generate_bill(patient_id, appointment_id, consultation_fee,
                  medicine_charges, other_charges):
    """
    Creates a new bill record.
    Calculates total_amount as sum of all charge components.
    Returns the new bill_id, or None if a bill already exists for this appointment.
    """
    total = consultation_fee + medicine_charges + other_charges
    conn = get_connection()
    try:
        cur = conn.execute(
            """INSERT INTO bills
               (patient_id, appointment_id, consultation_fee,
                medicine_charges, other_charges, total_amount)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (patient_id, appointment_id, consultation_fee,
             medicine_charges, other_charges, total)
        )
        conn.commit()
        return cur.lastrowid
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()


def update_payment_status(bill_id, status):
    """
    Updates the payment_status of a bill to paid / pending / cancelled.
    Returns True if the update succeeded.
    """
    conn = get_connection()
    cur = conn.execute(
        "UPDATE bills SET payment_status=? WHERE bill_id=?",
        (status, bill_id)
    )
    conn.commit()
    conn.close()
    return cur.rowcount == 1


# ══════════════════════════════════════════════════════════════════════════════
# DASHBOARD STATS
# ══════════════════════════════════════════════════════════════════════════════

def get_dashboard_stats():
    """
    Returns a dict with aggregate counts used on the dashboard:
      - total_patients
      - total_doctors
      - todays_appointments
      - pending_bills
    """
    conn = get_connection()
    stats = {}
    stats['total_patients'] = conn.execute(
        "SELECT COUNT(*) as cnt FROM patients"
    ).fetchone()['cnt']
    stats['total_doctors'] = conn.execute(
        "SELECT COUNT(*) as cnt FROM doctors"
    ).fetchone()['cnt']
    stats['todays_appointments'] = conn.execute(
        """SELECT COUNT(*) as cnt FROM appointments
           WHERE appointment_date = date('now','localtime') AND status='scheduled'"""
    ).fetchone()['cnt']
    stats['pending_bills'] = conn.execute(
        "SELECT COUNT(*) as cnt FROM bills WHERE payment_status='pending'"
    ).fetchone()['cnt']
    conn.close()
    return stats


def get_recent_appointments(limit=5):
    """Returns the most recent `limit` appointments for the dashboard widget."""
    conn = get_connection()
    rows = conn.execute(
        """SELECT
               a.appointment_date,
               a.time_slot,
               a.status,
               p.name AS patient_name,
               d.name AS doctor_name
           FROM appointments a
           JOIN patients p ON p.patient_id = a.patient_id
           JOIN doctors  d ON d.doctor_id  = a.doctor_id
           ORDER BY a.appointment_id DESC
           LIMIT ?""",
        (limit,)
    ).fetchall()
    conn.close()
    return rows
