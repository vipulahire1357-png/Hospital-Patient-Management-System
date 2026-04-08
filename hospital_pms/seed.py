"""
seed.py
=======
Inserts sample data into the Hospital PMS database.
Run once after init_db() to populate the system with realistic demo records.

Usage:  python seed.py
"""

import sqlite3
import os

DB_PATH     = os.path.join(os.path.dirname(__file__), 'hospital.db')
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), 'schema.sql')


def get_conn():
    """Opens a connection with row-factory and FK support."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_schema(conn):
    """Creates all tables from schema.sql if they don't exist yet."""
    with open(SCHEMA_PATH) as f:
        conn.executescript(f.read())
    conn.commit()


def seed_patients(conn):
    """Inserts 5 sample patients with varied demographics."""
    patients = [
        ('Arjun Mehta',    32, 'Male',   '9876543210', '12 MG Road, Bengaluru',       'B+'),
        ('Priya Sharma',   28, 'Female', '9123456780', '45 Park Street, Kolkata',     'A+'),
        ('Rajesh Kumar',   55, 'Male',   '9001234567', '7 Civil Lines, Lucknow',      'O-'),
        ('Sunita Patel',   41, 'Female', '8888123456', '23 Shivaji Nagar, Pune',      'AB+'),
        ('Mohammed Irfan', 19, 'Male',   '7776543210', '5 Banjara Hills, Hyderabad',  'O+'),
    ]
    conn.executemany(
        """INSERT OR IGNORE INTO patients
           (name, age, gender, phone, address, blood_group)
           VALUES (?, ?, ?, ?, ?, ?)""",
        patients
    )
    conn.commit()
    print(f"  ✓ Inserted {len(patients)} patients")


def seed_doctors(conn):
    """Inserts 5 sample doctors across different specializations."""
    doctors = [
        ('Dr. Anjali Singh',    'Cardiology',      '9990001111',
         'anjali.singh@hospital.com',   'Mon-Fri 09:00-13:00', 800.0),
        ('Dr. Ramesh Iyer',     'Neurology',       '9990002222',
         'ramesh.iyer@hospital.com',    'Mon-Wed 10:00-14:00', 1000.0),
        ('Dr. Pooja Nair',      'Orthopedics',     '9990003333',
         'pooja.nair@hospital.com',     'Tue-Sat 08:00-12:00', 700.0),
        ('Dr. Suresh Gupta',    'General Medicine','9990004444',
         'suresh.gupta@hospital.com',   'Mon-Sat 09:00-17:00', 500.0),
        ('Dr. Kavitha Reddy',   'Dermatology',     '9990005555',
         'kavitha.reddy@hospital.com',  'Wed-Fri 11:00-15:00', 600.0),
    ]
    conn.executemany(
        """INSERT OR IGNORE INTO doctors
           (name, specialization, phone, email, schedule, consultation_fee)
           VALUES (?, ?, ?, ?, ?, ?)""",
        doctors
    )
    conn.commit()
    print(f"  ✓ Inserted {len(doctors)} doctors")


def seed_appointments(conn):
    """Inserts 10 sample appointments with various statuses."""
    # fetch first 5 patient_ids and first 5 doctor_ids
    pids = [r['patient_id'] for r in conn.execute(
        "SELECT patient_id FROM patients ORDER BY patient_id LIMIT 5").fetchall()]
    dids = [r['doctor_id'] for r in conn.execute(
        "SELECT doctor_id FROM doctors ORDER BY doctor_id LIMIT 5").fetchall()]

    appointments = [
        (pids[0], dids[0], '2025-04-01', '09:00', 'completed', 'Chest pain evaluation'),
        (pids[1], dids[1], '2025-04-02', '10:00', 'completed', 'Migraine consultation'),
        (pids[2], dids[2], '2025-04-03', '08:00', 'completed', 'Knee pain follow-up'),
        (pids[3], dids[3], '2025-04-04', '09:00', 'completed', 'Routine check-up'),
        (pids[4], dids[4], '2025-04-05', '11:00', 'completed', 'Skin allergy treatment'),
        (pids[0], dids[3], '2025-04-10', '10:00', 'scheduled', 'Fever and fatigue'),
        (pids[1], dids[0], '2025-04-11', '09:00', 'scheduled', 'Blood pressure monitoring'),
        (pids[2], dids[1], '2025-04-12', '10:00', 'cancelled', 'Headache assessment'),
        (pids[3], dids[2], '2025-04-13', '08:00', 'scheduled', 'Post-surgery review'),
        (pids[4], dids[3], '2025-04-14', '09:00', 'scheduled', 'Diabetes management'),
    ]
    conn.executemany(
        """INSERT OR IGNORE INTO appointments
           (patient_id, doctor_id, appointment_date, time_slot, status, reason)
           VALUES (?, ?, ?, ?, ?, ?)""",
        appointments
    )
    conn.commit()
    print(f"  ✓ Inserted {len(appointments)} appointments")


def seed_prescriptions(conn):
    """Inserts 5 prescriptions for completed appointments."""
    # get the first 5 completed appointment_ids
    completed = [r['appointment_id'] for r in conn.execute(
        """SELECT appointment_id FROM appointments
           WHERE status='completed' ORDER BY appointment_id LIMIT 5"""
    ).fetchall()]

    prescriptions = [
        (completed[0], 'Aspirin 75mg, Atorvastatin 20mg',
         'Aspirin: 1 tablet after breakfast\nAtorvastatin: 1 tablet at night',
         'Avoid spicy food. Return in 4 weeks.'),
        (completed[1], 'Sumatriptan 50mg, Ibuprofen 400mg',
         'Sumatriptan: 1 tablet at onset of migraine\nIbuprofen: 1 tablet twice daily',
         'Rest in a dark room during attacks.'),
        (completed[2], 'Diclofenac 50mg, Pantoprazole 40mg, Calcium + D3',
         'Diclofenac: 1 tablet twice daily with food\nPantoprazole: 1 before breakfast',
         'Apply ice pack 3x daily. Physiotherapy recommended.'),
        (completed[3], 'Paracetamol 500mg, Zinc 50mg, Vitamin C 1000mg',
         'Paracetamol: 1 tablet every 6 hrs if fever > 38°C',
         'Drink 3L water daily. Monitor temperature.'),
        (completed[4], 'Cetirizine 10mg, Betamethasone cream',
         'Cetirizine: 1 tablet at bedtime\nApply cream to affected area twice daily',
         'Avoid direct sunlight. No soap on affected skin.'),
    ]
    conn.executemany(
        """INSERT OR IGNORE INTO prescriptions
           (appointment_id, medicines, dosage, instructions)
           VALUES (?, ?, ?, ?)""",
        prescriptions
    )
    conn.commit()
    print(f"  ✓ Inserted {len(prescriptions)} prescriptions")


def seed_bills(conn):
    """Inserts 5 bills for completed appointments with varied payment statuses."""
    completed = conn.execute(
        """SELECT a.appointment_id, a.patient_id, d.consultation_fee
           FROM appointments a
           JOIN doctors d ON d.doctor_id = a.doctor_id
           WHERE a.status = 'completed'
           ORDER BY a.appointment_id LIMIT 5"""
    ).fetchall()

    statuses = ['paid', 'paid', 'pending', 'paid', 'pending']
    extra    = [(150, 100), (200, 50), (300, 75), (0, 200), (100, 150)]

    for i, appt in enumerate(completed):
        med_c, oth_c = extra[i]
        total = appt['consultation_fee'] + med_c + oth_c
        conn.execute(
            """INSERT OR IGNORE INTO bills
               (patient_id, appointment_id, consultation_fee,
                medicine_charges, other_charges, total_amount, payment_status)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (appt['patient_id'], appt['appointment_id'],
             appt['consultation_fee'], med_c, oth_c, total, statuses[i])
        )
    conn.commit()
    print(f"  ✓ Inserted {len(completed)} bills")


def main():
    """Runs the full seeding pipeline."""
    print("\n=== Hospital PMS – Database Seeder ===\n")
    conn = get_conn()
    init_schema(conn)
    print("Schema initialised.")
    seed_patients(conn)
    seed_doctors(conn)
    seed_appointments(conn)
    seed_prescriptions(conn)
    seed_bills(conn)
    conn.close()
    print("\n✅ All seed data inserted successfully!\n")
    print("Run:  python app.py   to start the server.")


if __name__ == '__main__':
    main()
