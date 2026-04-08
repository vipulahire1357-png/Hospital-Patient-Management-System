"""
app.py
======
Flask entry point and route controllers for the Hospital PMS.
Follows MVC pattern: views in /templates, logic here, data in database.py.
"""

from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, jsonify, abort
)
import database as db

# ── App setup ─────────────────────────────────────────────────────────────────

app = Flask(__name__)
app.secret_key = 'hospital_pms_secret_key_2024'   # required for flash messages


# ══════════════════════════════════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════

@app.route('/')
def index():
    """
    Renders the main dashboard with live aggregate stats
    and the 5 most recent appointments.
    """
    stats  = db.get_dashboard_stats()
    recent = db.get_recent_appointments(5)
    return render_template('index.html', stats=stats, recent=recent)


# ══════════════════════════════════════════════════════════════════════════════
# PATIENTS
# ══════════════════════════════════════════════════════════════════════════════

@app.route('/patients')
def patients():
    """Lists all registered patients."""
    all_patients = db.get_all_patients()
    return render_template('patients.html', patients=all_patients)


@app.route('/patients/add', methods=['POST'])
def add_patient():
    """
    Processes the patient registration form.
    Validates required fields and inserts a new patient record.
    """
    name        = request.form.get('name', '').strip()
    age         = request.form.get('age', '').strip()
    gender      = request.form.get('gender', '').strip()
    phone       = request.form.get('phone', '').strip()
    address     = request.form.get('address', '').strip()
    blood_group = request.form.get('blood_group', '').strip()

    if not all([name, age, gender, phone, address, blood_group]):
        flash('All fields are required.', 'error')
        return redirect(url_for('patients'))

    pid = db.add_patient(name, int(age), gender, phone, address, blood_group)
    if pid:
        flash(f'Patient "{name}" registered successfully (ID: {pid}).', 'success')
    else:
        flash('Phone number already exists. Try a different number.', 'error')
    return redirect(url_for('patients'))


@app.route('/patients/edit/<int:patient_id>', methods=['GET', 'POST'])
def edit_patient(patient_id):
    """
    GET  – renders the edit form prefilled with the patient's current data.
    POST – processes the updated fields and saves them.
    """
    patient = db.get_patient_by_id(patient_id)
    if not patient:
        abort(404)

    if request.method == 'POST':
        name        = request.form.get('name', '').strip()
        age         = request.form.get('age', '').strip()
        gender      = request.form.get('gender', '').strip()
        phone       = request.form.get('phone', '').strip()
        address     = request.form.get('address', '').strip()
        blood_group = request.form.get('blood_group', '').strip()

        ok = db.update_patient(patient_id, name, int(age), gender,
                               phone, address, blood_group)
        if ok:
            flash('Patient updated successfully.', 'success')
        else:
            flash('Update failed. Phone number may already be in use.', 'error')
        return redirect(url_for('patients'))

    return render_template('edit_patient.html', patient=patient)


@app.route('/patients/delete/<int:patient_id>', methods=['POST'])
def delete_patient(patient_id):
    """
    Deletes a patient and all cascaded records (appointments, bills, etc.).
    """
    patient = db.get_patient_by_id(patient_id)
    if not patient:
        abort(404)
    db.delete_patient(patient_id)
    flash(f'Patient "{patient["name"]}" deleted.', 'success')
    return redirect(url_for('patients'))


@app.route('/patients/<int:patient_id>/history')
def patient_history(patient_id):
    """
    Shows the full medical history of a patient:
    appointments, prescriptions, and bills.
    """
    patient = db.get_patient_by_id(patient_id)
    if not patient:
        abort(404)
    history = db.get_patient_medical_history(patient_id)
    return render_template('patient_history.html', patient=patient, history=history)


# ══════════════════════════════════════════════════════════════════════════════
# DOCTORS
# ══════════════════════════════════════════════════════════════════════════════

@app.route('/doctors')
def doctors():
    """Lists all registered doctors."""
    all_doctors = db.get_all_doctors()
    return render_template('doctors.html', doctors=all_doctors)


@app.route('/doctors/add', methods=['POST'])
def add_doctor():
    """
    Processes the doctor registration form.
    Inserts a new doctor record.
    """
    name             = request.form.get('name', '').strip()
    specialization   = request.form.get('specialization', '').strip()
    phone            = request.form.get('phone', '').strip()
    email            = request.form.get('email', '').strip()
    schedule         = request.form.get('schedule', '').strip()
    consultation_fee = request.form.get('consultation_fee', '0').strip()

    if not all([name, specialization, phone, email, schedule, consultation_fee]):
        flash('All fields are required.', 'error')
        return redirect(url_for('doctors'))

    did = db.add_doctor(name, specialization, phone, email,
                        schedule, float(consultation_fee))
    if did:
        flash(f'Dr. {name} added successfully.', 'success')
    else:
        flash('Phone or email already in use.', 'error')
    return redirect(url_for('doctors'))


@app.route('/doctors/edit/<int:doctor_id>', methods=['GET', 'POST'])
def edit_doctor(doctor_id):
    """
    GET  – renders the edit form with existing doctor data.
    POST – saves the updated doctor record.
    """
    doctor = db.get_doctor_by_id(doctor_id)
    if not doctor:
        abort(404)

    if request.method == 'POST':
        name             = request.form.get('name', '').strip()
        specialization   = request.form.get('specialization', '').strip()
        phone            = request.form.get('phone', '').strip()
        email            = request.form.get('email', '').strip()
        schedule         = request.form.get('schedule', '').strip()
        consultation_fee = request.form.get('consultation_fee', '0').strip()

        ok = db.update_doctor(doctor_id, name, specialization, phone,
                              email, schedule, float(consultation_fee))
        if ok:
            flash('Doctor updated successfully.', 'success')
        else:
            flash('Update failed. Phone or email may already be in use.', 'error')
        return redirect(url_for('doctors'))

    return render_template('edit_doctor.html', doctor=doctor)


@app.route('/doctors/delete/<int:doctor_id>', methods=['POST'])
def delete_doctor(doctor_id):
    """Deletes a doctor and all cascaded appointment records."""
    doctor = db.get_doctor_by_id(doctor_id)
    if not doctor:
        abort(404)
    db.delete_doctor(doctor_id)
    flash(f'Dr. {doctor["name"]} deleted.', 'success')
    return redirect(url_for('doctors'))


@app.route('/doctors/<int:doctor_id>/schedule')
def doctor_schedule(doctor_id):
    """Shows all appointments for a specific doctor."""
    doctor   = db.get_doctor_by_id(doctor_id)
    if not doctor:
        abort(404)
    schedule = db.get_doctor_schedule(doctor_id)
    return render_template('doctor_schedule.html', doctor=doctor, schedule=schedule)


# ── AJAX endpoint ─────────────────────────────────────────────────────────────

@app.route('/api/doctors_by_spec')
def api_doctors_by_spec():
    """
    AJAX endpoint – returns doctors filtered by specialization as JSON.
    Called by the appointment booking form when the user picks a specialization.
    """
    spec = request.args.get('specialization', '')
    rows = db.get_doctors_by_specialization(spec)
    return jsonify([dict(r) for r in rows])


@app.route('/api/booked_slots')
def api_booked_slots():
    """
    AJAX endpoint – returns already-booked time slots for a doctor on a date.
    Called by the appointment booking form to disable unavailable slots.
    """
    doctor_id = request.args.get('doctor_id', type=int)
    date      = request.args.get('date', '')
    slots     = db.get_booked_slots(doctor_id, date)
    return jsonify(slots)


# ══════════════════════════════════════════════════════════════════════════════
# APPOINTMENTS
# ══════════════════════════════════════════════════════════════════════════════

@app.route('/appointments')
def appointments():
    """Lists all appointments with patient and doctor info."""
    all_appts = db.get_all_appointments()
    patients  = db.get_all_patients()
    specs     = db.get_all_specializations()
    return render_template('appointments.html',
                           appointments=all_appts,
                           patients=patients,
                           specializations=specs)


@app.route('/appointments/book', methods=['POST'])
def book_appointment():
    """
    Books a new appointment.  The DB enforces no-double-booking via UNIQUE
    constraint; if violated we show an error flash message.
    """
    patient_id       = request.form.get('patient_id', type=int)
    doctor_id        = request.form.get('doctor_id', type=int)
    appointment_date = request.form.get('appointment_date', '').strip()
    time_slot        = request.form.get('time_slot', '').strip()
    reason           = request.form.get('reason', '').strip()

    if not all([patient_id, doctor_id, appointment_date, time_slot, reason]):
        flash('All fields are required.', 'error')
        return redirect(url_for('appointments'))

    aid = db.book_appointment(patient_id, doctor_id,
                              appointment_date, time_slot, reason)
    if aid:
        flash(f'Appointment booked successfully (ID: {aid}).', 'success')
    else:
        flash('That time slot is already booked for this doctor. '
              'Please choose a different slot.', 'error')
    return redirect(url_for('appointments'))


@app.route('/appointments/<int:appointment_id>/cancel', methods=['POST'])
def cancel_appointment(appointment_id):
    """Marks an appointment as cancelled."""
    db.update_appointment_status(appointment_id, 'cancelled')
    flash('Appointment cancelled.', 'success')
    return redirect(url_for('appointments'))


@app.route('/appointments/<int:appointment_id>/complete', methods=['POST'])
def complete_appointment(appointment_id):
    """Marks an appointment as completed."""
    db.update_appointment_status(appointment_id, 'completed')
    flash('Appointment marked as completed.', 'success')
    return redirect(url_for('appointments'))


@app.route('/appointments/<int:appointment_id>/reschedule', methods=['POST'])
def reschedule_appointment(appointment_id):
    """
    Reschedules an appointment to a new date/time_slot.
    Validates against double-booking.
    """
    new_date = request.form.get('new_date', '').strip()
    new_slot = request.form.get('new_slot', '').strip()

    if not new_date or not new_slot:
        flash('Please provide both date and time slot.', 'error')
        return redirect(url_for('appointments'))

    result = db.reschedule_appointment(appointment_id, new_date, new_slot)
    if result:
        flash('Appointment rescheduled successfully.', 'success')
    elif result is None:
        flash('That time slot is already booked. Choose a different slot.', 'error')
    else:
        flash('Reschedule failed.', 'error')
    return redirect(url_for('appointments'))


# ══════════════════════════════════════════════════════════════════════════════
# PRESCRIPTIONS
# ══════════════════════════════════════════════════════════════════════════════

@app.route('/prescriptions')
def prescriptions():
    """Lists all prescriptions; provides dropdown of eligible appointments."""
    all_rx      = db.get_all_prescriptions()
    eligible    = db.get_completed_appointments_without_prescription()
    all_patients = db.get_all_patients()
    return render_template('prescriptions.html',
                           prescriptions=all_rx,
                           eligible_appointments=eligible,
                           patients=all_patients)


@app.route('/prescriptions/add', methods=['POST'])
def add_prescription():
    """
    Adds a new prescription linked to a completed appointment.
    Only appointments without an existing prescription are eligible.
    """
    appointment_id = request.form.get('appointment_id', type=int)
    medicines      = request.form.get('medicines', '').strip()
    dosage         = request.form.get('dosage', '').strip()
    instructions   = request.form.get('instructions', '').strip()

    if not all([appointment_id, medicines, dosage]):
        flash('Appointment, medicines, and dosage are required.', 'error')
        return redirect(url_for('prescriptions'))

    pid = db.add_prescription(appointment_id, medicines, dosage, instructions)
    if pid:
        flash('Prescription added successfully.', 'success')
    else:
        flash('A prescription already exists for this appointment.', 'error')
    return redirect(url_for('prescriptions'))


@app.route('/prescriptions/patient/<int:patient_id>')
def prescriptions_by_patient(patient_id):
    """Returns prescriptions filtered to one patient (AJAX JSON response)."""
    rows = db.get_prescriptions_by_patient(patient_id)
    return jsonify([dict(r) for r in rows])


# ══════════════════════════════════════════════════════════════════════════════
# BILLING
# ══════════════════════════════════════════════════════════════════════════════

@app.route('/billing')
def billing():
    """Lists all bills; provides dropdown for generating new bills."""
    all_bills   = db.get_all_bills()
    unbilled    = db.get_appointments_without_bill()
    return render_template('billing.html',
                           bills=all_bills,
                           unbilled_appointments=unbilled)


@app.route('/billing/generate', methods=['POST'])
def generate_bill():
    """
    Generates a bill for a completed appointment.
    Auto-populates consultation_fee from the doctor's record.
    """
    appointment_id   = request.form.get('appointment_id', type=int)
    medicine_charges = float(request.form.get('medicine_charges', 0) or 0)
    other_charges    = float(request.form.get('other_charges', 0) or 0)

    if not appointment_id:
        flash('Please select an appointment.', 'error')
        return redirect(url_for('billing'))

    appt = db.get_appointment_by_id(appointment_id)
    if not appt:
        flash('Appointment not found.', 'error')
        return redirect(url_for('billing'))

    consultation_fee = appt['consultation_fee']
    bid = db.generate_bill(appt['patient_id'], appointment_id,
                           consultation_fee, medicine_charges, other_charges)
    if bid:
        flash(f'Bill generated successfully (Bill ID: {bid}).', 'success')
    else:
        flash('A bill already exists for this appointment.', 'error')
    return redirect(url_for('billing'))


@app.route('/billing/<int:bill_id>/pay', methods=['POST'])
def mark_paid(bill_id):
    """Marks a bill's payment_status as 'paid'."""
    db.update_payment_status(bill_id, 'paid')
    flash('Bill marked as paid.', 'success')
    return redirect(url_for('billing'))


@app.route('/billing/<int:bill_id>/cancel', methods=['POST'])
def cancel_bill(bill_id):
    """Marks a bill's payment_status as 'cancelled'."""
    db.update_payment_status(bill_id, 'cancelled')
    flash('Bill cancelled.', 'success')
    return redirect(url_for('billing'))


@app.route('/billing/<int:bill_id>/view')
def view_bill(bill_id):
    """Renders a printable bill detail page."""
    bill = db.get_bill_by_id(bill_id)
    if not bill:
        abort(404)
    return render_template('bill_detail.html', bill=bill)


# ══════════════════════════════════════════════════════════════════════════════
# ERROR HANDLERS
# ══════════════════════════════════════════════════════════════════════════════

@app.errorhandler(404)
def not_found(e):
    """Custom 404 page."""
    return render_template('404.html'), 404


# ══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    db.init_db()          # create tables if they don't exist
    app.run(debug=True, port=5000)
