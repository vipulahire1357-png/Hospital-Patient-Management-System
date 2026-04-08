/**
 * script.js
 * =========
 * Frontend logic for Hospital PMS.
 * Handles:
 *   - Flash message auto-dismiss
 *   - Client-side form validation
 *   - AJAX dynamic doctor dropdown
 *   - AJAX booked-slot highlighting
 *   - Reschedule & confirmation modals
 *   - Date header display
 */

'use strict';

/* ── DOMContentLoaded ───────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  initFlashMessages();
  initDateDisplay();
  initFormValidation();
  initAppointmentForm();
  initModals();
  highlightActiveNav();
});


/* ══════════════════════════════════════════════════════════════
   FLASH MESSAGES
   ════════════════════════════════════════════════════════════ */

/**
 * Auto-dismiss flash messages after 4 seconds.
 * Also wires up the × close button.
 */
function initFlashMessages() {
  document.querySelectorAll('.flash').forEach(flash => {
    // Auto-hide after 4 s
    setTimeout(() => dismissFlash(flash), 4000);

    // Manual close button
    const closeBtn = flash.querySelector('.flash-close');
    if (closeBtn) closeBtn.addEventListener('click', () => dismissFlash(flash));
  });
}

/**
 * Animates a flash message out and removes it from the DOM.
 * @param {HTMLElement} flash
 */
function dismissFlash(flash) {
  flash.style.transition = 'opacity .3s, transform .3s';
  flash.style.opacity    = '0';
  flash.style.transform  = 'translateY(-8px)';
  setTimeout(() => flash.remove(), 300);
}


/* ══════════════════════════════════════════════════════════════
   DATE DISPLAY
   ════════════════════════════════════════════════════════════ */

/**
 * Injects the current date into elements with class .js-date.
 */
function initDateDisplay() {
  const els = document.querySelectorAll('.js-date');
  if (!els.length) return;
  const opts = { weekday: 'short', year: 'numeric', month: 'short', day: 'numeric' };
  const today = new Date().toLocaleDateString('en-IN', opts);
  els.forEach(el => { el.textContent = today; });
}


/* ══════════════════════════════════════════════════════════════
   ACTIVE NAV HIGHLIGHT
   ════════════════════════════════════════════════════════════ */

/**
 * Adds the 'active' class to the sidebar nav item whose
 * href matches the current page path.
 */
function highlightActiveNav() {
  const path = window.location.pathname.split('/')[1] || '';
  document.querySelectorAll('.nav-item').forEach(item => {
    const href = item.getAttribute('href') || '';
    const segment = href.replace('/', '');
    if ((path === '' && segment === '') || (segment && path.startsWith(segment))) {
      item.classList.add('active');
    }
  });
}


/* ══════════════════════════════════════════════════════════════
   GENERIC FORM VALIDATION
   ════════════════════════════════════════════════════════════ */

/**
 * Validates all forms marked with data-validate="true".
 * Checks required fields, phone format, and email format.
 */
function initFormValidation() {
  document.querySelectorAll('form[data-validate="true"]').forEach(form => {
    form.addEventListener('submit', e => {
      if (!validateForm(form)) e.preventDefault();
    });

    // Live validation on blur
    form.querySelectorAll('input, select, textarea').forEach(field => {
      field.addEventListener('blur', () => validateField(field));
      field.addEventListener('input', () => clearFieldError(field));
    });
  });
}

/**
 * Validates every required field in the given form.
 * @param {HTMLFormElement} form
 * @returns {boolean} true if all fields valid
 */
function validateForm(form) {
  let valid = true;
  form.querySelectorAll('[required]').forEach(field => {
    if (!validateField(field)) valid = false;
  });
  return valid;
}

/**
 * Validates a single form field and shows inline error.
 * @param {HTMLElement} field
 * @returns {boolean}
 */
function validateField(field) {
  clearFieldError(field);
  const val = field.value.trim();

  // Required check
  if (field.hasAttribute('required') && !val) {
    showFieldError(field, 'This field is required.');
    return false;
  }

  // Phone: 10-digit Indian mobile
  if (field.dataset.type === 'phone' && val) {
    if (!/^[6-9]\d{9}$/.test(val)) {
      showFieldError(field, 'Enter a valid 10-digit mobile number.');
      return false;
    }
  }

  // Email format
  if (field.type === 'email' && val) {
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(val)) {
      showFieldError(field, 'Enter a valid email address.');
      return false;
    }
  }

  // Positive number
  if (field.dataset.type === 'positive' && val) {
    if (isNaN(val) || parseFloat(val) < 0) {
      showFieldError(field, 'Enter a valid non-negative number.');
      return false;
    }
  }

  // Age range
  if (field.dataset.type === 'age' && val) {
    const age = parseInt(val);
    if (age < 1 || age > 149) {
      showFieldError(field, 'Age must be between 1 and 149.');
      return false;
    }
  }

  // Future date (appointment booking)
  if (field.dataset.type === 'future-date' && val) {
    const chosen = new Date(val);
    const today  = new Date(); today.setHours(0,0,0,0);
    if (chosen < today) {
      showFieldError(field, 'Appointment date must be today or in the future.');
      return false;
    }
  }

  return true;
}

/** Shows an inline error message below the field. */
function showFieldError(field, msg) {
  field.classList.add('error');
  let err = field.parentElement.querySelector('.field-error');
  if (!err) {
    err = document.createElement('div');
    err.className = 'field-error';
    field.parentElement.appendChild(err);
  }
  err.textContent = msg;
  err.style.display = 'block';
}

/** Clears the inline error for a field. */
function clearFieldError(field) {
  field.classList.remove('error');
  const err = field.parentElement.querySelector('.field-error');
  if (err) err.style.display = 'none';
}


/* ══════════════════════════════════════════════════════════════
   APPOINTMENT BOOKING FORM (AJAX)
   ════════════════════════════════════════════════════════════ */

/** All time slots available in the system */
const ALL_SLOTS = [
  '08:00','08:30','09:00','09:30','10:00','10:30',
  '11:00','11:30','12:00','12:30','13:00','13:30',
  '14:00','14:30','15:00','15:30','16:00','16:30',
  '17:00','17:30',
];

/**
 * Wires up the appointment booking form:
 *  1. Specialization → fetch doctors by AJAX
 *  2. Doctor + date → fetch booked slots by AJAX and disable them
 */
function initAppointmentForm() {
  const specSelect   = document.getElementById('specialization');
  const doctorSelect = document.getElementById('doctor_id');
  const dateInput    = document.getElementById('appointment_date');
  const slotSelect   = document.getElementById('time_slot');

  if (!specSelect) return;   // not on appointments page

  /**
   * Fetches doctors for the selected specialization via AJAX.
   * Populates the doctor dropdown dynamically.
   */
  async function fetchDoctors() {
    const spec = specSelect.value;
    doctorSelect.innerHTML = '<option value="">Loading…</option>';
    slotSelect.innerHTML   = '<option value="">Select doctor & date first</option>';

    if (!spec) {
      doctorSelect.innerHTML = '<option value="">Select specialization first</option>';
      return;
    }

    try {
      const res  = await fetch(`/api/doctors_by_spec?specialization=${encodeURIComponent(spec)}`);
      const docs = await res.json();

      if (docs.length === 0) {
        doctorSelect.innerHTML = '<option value="">No doctors available</option>';
        return;
      }

      doctorSelect.innerHTML = '<option value="">-- Select Doctor --</option>';
      docs.forEach(d => {
        const opt = document.createElement('option');
        opt.value = d.doctor_id;
        opt.textContent = `${d.name}  (₹${d.consultation_fee})`;
        doctorSelect.appendChild(opt);
      });
    } catch (err) {
      doctorSelect.innerHTML = '<option value="">Error loading doctors</option>';
    }
  }

  /**
   * Fetches already-booked slots for the selected doctor on the chosen date.
   * Disables those options in the slot dropdown.
   */
  async function fetchBookedSlots() {
    const doctorId = doctorSelect.value;
    const date     = dateInput ? dateInput.value : '';

    slotSelect.innerHTML = '';

    if (!doctorId || !date) {
      slotSelect.innerHTML = '<option value="">Select doctor & date first</option>';
      return;
    }

    let booked = [];
    try {
      const res = await fetch(`/api/booked_slots?doctor_id=${doctorId}&date=${date}`);
      booked = await res.json();
    } catch (_) {}

    // Default placeholder
    const placeholder = document.createElement('option');
    placeholder.value = ''; placeholder.textContent = '-- Select Time Slot --';
    slotSelect.appendChild(placeholder);

    ALL_SLOTS.forEach(slot => {
      const opt = document.createElement('option');
      opt.value = slot;
      if (booked.includes(slot)) {
        opt.textContent = `${slot} — Booked`;
        opt.disabled = true;
        opt.style.color = '#9ca3af';
      } else {
        opt.textContent = slot;
      }
      slotSelect.appendChild(opt);
    });
  }

  specSelect.addEventListener('change', fetchDoctors);
  doctorSelect.addEventListener('change', fetchBookedSlots);
  if (dateInput) dateInput.addEventListener('change', fetchBookedSlots);
}


/* ══════════════════════════════════════════════════════════════
   MODALS
   ════════════════════════════════════════════════════════════ */

/**
 * Generic modal system.
 * - data-modal-open="<id>"  → opens that modal
 * - data-modal-close        → closes parent modal
 * - Clicking backdrop       → closes
 */
function initModals() {
  // Open buttons
  document.querySelectorAll('[data-modal-open]').forEach(btn => {
    btn.addEventListener('click', () => {
      const id = btn.dataset.modalOpen;
      openModal(id, btn.dataset);
    });
  });

  // Close buttons
  document.querySelectorAll('[data-modal-close]').forEach(btn => {
    btn.addEventListener('click', () => {
      const modal = btn.closest('.modal-overlay');
      if (modal) closeModal(modal.id);
    });
  });

  // Backdrop click
  document.querySelectorAll('.modal-overlay').forEach(overlay => {
    overlay.addEventListener('click', e => {
      if (e.target === overlay) closeModal(overlay.id);
    });
  });

  // ESC key
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape') {
      document.querySelectorAll('.modal-overlay.open').forEach(m => closeModal(m.id));
    }
  });
}

/**
 * Opens a modal and populates hidden fields from the trigger button's data-* attrs.
 * @param {string} id   - modal overlay element id
 * @param {DOMStringMap} data - dataset of the triggering button
 */
function openModal(id, data) {
  const overlay = document.getElementById(id);
  if (!overlay) return;

  // Populate any hidden inputs declared in the modal
  // Convention: button has data-field-<name>="<value>"
  Object.entries(data).forEach(([key, val]) => {
    if (key.startsWith('field')) {
      const fieldName = key.replace('field', '').toLowerCase();
      const input = overlay.querySelector(`[name="${fieldName}"]`);
      if (input) input.value = val;
    }
  });

  overlay.classList.add('open');
  document.body.style.overflow = 'hidden';
}

/**
 * Closes the modal with the given id.
 * @param {string} id
 */
function closeModal(id) {
  const overlay = document.getElementById(id);
  if (!overlay) return;
  overlay.classList.remove('open');
  document.body.style.overflow = '';
}


/* ══════════════════════════════════════════════════════════════
   CONFIRM DIALOGS (DELETE / CANCEL)
   ════════════════════════════════════════════════════════════ */

/**
 * Intercepts forms that require confirmation before submit.
 * Usage: add data-confirm="Are you sure?" to the submit button.
 */
document.addEventListener('click', e => {
  const btn = e.target.closest('[data-confirm]');
  if (!btn) return;
  const msg = btn.dataset.confirm || 'Are you sure?';
  if (!window.confirm(msg)) e.preventDefault();
});


/* ══════════════════════════════════════════════════════════════
   PRESCRIPTION PATIENT FILTER (AJAX)
   ════════════════════════════════════════════════════════════ */

/**
 * On the prescriptions page, filters the displayed prescriptions
 * by patient when the user selects one from the dropdown.
 */
const rxPatientFilter = document.getElementById('rx-patient-filter');
if (rxPatientFilter) {
  rxPatientFilter.addEventListener('change', async function () {
    const pid = this.value;
    const rows = document.querySelectorAll('.rx-row');

    if (!pid) {
      rows.forEach(r => r.style.display = '');
      return;
    }

    // Fetch patient prescriptions via AJAX
    try {
      const res = await fetch(`/prescriptions/patient/${pid}`);
      const data = await res.json();
      const apptIds = data.map(r => String(r.appointment_id));

      rows.forEach(row => {
        const apptId = row.dataset.apptId;
        row.style.display = apptIds.includes(apptId) ? '' : 'none';
      });
    } catch (_) {
      rows.forEach(r => r.style.display = '');
    }
  });
}


/* ══════════════════════════════════════════════════════════════
   BILL APPOINTMENT AUTOFILL
   ════════════════════════════════════════════════════════════ */

/**
 * When user selects an appointment to bill, auto-fills the
 * consultation fee field from the data attribute on the option.
 */
const billApptSelect = document.getElementById('bill_appointment_id');
const billConsFee    = document.getElementById('bill_consultation_fee');

if (billApptSelect && billConsFee) {
  billApptSelect.addEventListener('change', function () {
    const selected = this.options[this.selectedIndex];
    const fee = selected.dataset.fee || '0';
    billConsFee.value = parseFloat(fee).toFixed(2);
    updateBillTotal();
  });
}

/**
 * Recalculates the bill total whenever any charge field changes.
 */
['bill_consultation_fee', 'bill_medicine_charges', 'bill_other_charges'].forEach(id => {
  const el = document.getElementById(id);
  if (el) el.addEventListener('input', updateBillTotal);
});

/**
 * Updates the read-only total amount display.
 */
function updateBillTotal() {
  const cons = parseFloat(document.getElementById('bill_consultation_fee')?.value) || 0;
  const med  = parseFloat(document.getElementById('bill_medicine_charges')?.value) || 0;
  const oth  = parseFloat(document.getElementById('bill_other_charges')?.value)    || 0;
  const total = document.getElementById('bill_total_display');
  if (total) total.textContent = `₹${(cons + med + oth).toFixed(2)}`;
}
