# 🚀 Setup & Run Guide — MediCare Hospital PMS

Complete step-by-step instructions to get the Hospital Patient Management System running on your local machine.

---

## ✅ Prerequisites

| Requirement  | Version   | Check Command         |
|--------------|-----------|-----------------------|
| Python       | 3.8+      | `python --version`    |
| pip          | latest    | `pip --version`       |
| Flask        | 3.x       | `pip show flask`      |

> **Note**: SQLite comes built-in with Python — no separate installation needed.

---

## 📥 Step 1 — Navigate to the Project Directory

Open a terminal (PowerShell / CMD / Bash) and navigate to the project folder:

```powershell
cd path\to\mini_project\hospital_pms
```

Verify you can see these files:
```
app.py   database.py   schema.sql   seed.py   static/   templates/
```

---

## 📦 Step 2 — Install Flask

Install the only external dependency:

```bash
pip install flask
```

Verify installation:
```bash
python -c "import flask; print(flask.__version__)"
```

You should see something like `3.0.3`.

> **Tip (optional)**: Use a virtual environment to isolate dependencies:
> ```bash
> python -m venv venv
> venv\Scripts\activate          # Windows
> source venv/bin/activate       # macOS/Linux
> pip install flask
> ```

---

## 🗄️ Step 3 — Initialize the Database & Seed Sample Data

Run the seeder script to:
1. Create the SQLite database (`hospital.db`)
2. Create all 5 tables from `schema.sql`
3. Insert sample data (5 patients, 5 doctors, 10 appointments, 5 prescriptions, 5 bills)

```bash
python seed.py
```

Expected output:
```
=== Hospital PMS – Database Seeder ===

Schema initialised.
  ✓ Inserted 5 patients
  ✓ Inserted 5 doctors
  ✓ Inserted 10 appointments
  ✓ Inserted 5 prescriptions
  ✓ Inserted 5 bills

✅ All seed data inserted successfully!

Run:  python app.py   to start the server.
```

A new file `hospital.db` will appear in the project directory.

---

## ▶️ Step 4 — Start the Flask Server

```bash
python app.py
```

Expected output:
```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
 * Press CTRL+C to quit
```

---

## 🌐 Step 5 — Open in Browser

Open your web browser and go to:

```
http://127.0.0.1:5000
```

You will see the **Dashboard** with live stats populated from the seed data.

---

## 📖 How to Use Each Module

### 🧑‍🤝‍🧑 Patients
| Action          | How |
|-----------------|-----|
| Register        | Fill form on the right panel of Patients page → Submit |
| Edit            | Click ✏️ Edit button next to a patient |
| Delete          | Click 🗑️ Delete (requires confirmation) |
| Medical History | Click 📋 History to see all visits, prescriptions, bills |

### 👨‍⚕️ Doctors
| Action          | How |
|-----------------|-----|
| Add Doctor      | Fill form on Doctors page → Submit |
| Edit            | Click ✏️ Edit |
| View Schedule   | Click 📅 Schedule to see all their appointments |

### 📅 Appointments
| Action          | How |
|-----------------|-----|
| Book            | Select patient → specialization (loads doctors via AJAX) → doctor → date → time slot → reason → Book |
| Complete        | Click ✅ button (changes status to completed) |
| Cancel          | Click ❌ button |
| Reschedule      | Click 🔄 button → modal opens → pick new date/slot |

> **Double-booking prevention**: The system will show an error if the selected doctor already has that time slot booked.

### 💊 Prescriptions
| Action         | How |
|----------------|-----|
| Add            | Select a **completed** appointment → fill medicines, dosage → Save |
| Filter by patient | Use the dropdown at the top-right of the Prescriptions list |

### 💳 Billing
| Action         | How |
|----------------|-----|
| Generate Bill  | Select a **completed, unbilled** appointment → consultation fee auto-fills → add medicine/other charges → Generate |
| Mark as Paid   | Click ✅ Pay button |
| View/Print     | Click 🖨️ View → opens printable bill page → use browser print |

---

## 🔄 Resetting the Database

To reset everything and start fresh:

```bash
# Delete the database
del hospital.db           # Windows CMD
rm hospital.db            # macOS/Linux

# Re-seed the database
python seed.py
```

---

## 🐞 Troubleshooting

### "ModuleNotFoundError: No module named 'flask'"
```bash
pip install flask
```

### "Address already in use" (port 5000 busy)
```bash
# Run on a different port:
python app.py --port 5001
```
Or edit `app.py` and change `port=5000` to another port.

### Database errors / schema mismatch
```bash
del hospital.db    # or: rm hospital.db
python seed.py
```

### Browser shows "Connection Refused"
- Make sure `python app.py` is still running in your terminal
- Try `http://localhost:5000` instead of `127.0.0.1:5000`

---

## 🗂️ File Reference

| File              | Purpose                                      |
|-------------------|----------------------------------------------|
| `app.py`          | Flask routes and controllers                 |
| `database.py`     | All SQL queries (parameterized)              |
| `schema.sql`      | CREATE TABLE statements                      |
| `seed.py`         | Sample data insertion                        |
| `hospital.db`     | SQLite database (auto-generated)             |
| `static/style.css`| All UI styling                               |
| `static/script.js`| AJAX, validation, modals                    |
| `templates/*.html`| Jinja2 HTML templates                        |
| `README.md`       | Project overview and feature list            |
| `ER_DIAGRAM.md`   | Entity-relationship diagram                  |

---

## 🧪 Running Without Seed Data

If you want to start with an empty database (no sample data):

```bash
python -c "import database; database.init_db(); print('Database initialized!')"
python app.py
```

---

## 📊 Verifying Database Contents

You can inspect the SQLite database directly:

```bash
# Using Python REPL
python
>>> import sqlite3
>>> conn = sqlite3.connect('hospital.db')
>>> conn.row_factory = sqlite3.Row
>>> print([dict(r) for r in conn.execute('SELECT * FROM patients').fetchall()])
```

Or use a GUI tool like:
- [DB Browser for SQLite](https://sqlitebrowser.org/) (free, cross-platform)
- [SQLiteOnline.com](https://sqliteonline.com/) (web-based)

---

## 🎓 Academic Context

This project demonstrates the following **DBMS concepts**:

1. **DDL** — `CREATE TABLE`, `PRIMARY KEY`, `FOREIGN KEY`, `CHECK`, `UNIQUE`, `DEFAULT`
2. **DML** — `INSERT`, `SELECT`, `UPDATE`, `DELETE` with `WHERE` clauses
3. **Joins** — `INNER JOIN` across 4–5 tables for dashboard and history views
4. **Subqueries** — Finding unbilled/unprescribed appointments
5. **Aggregation** — `COUNT(*)` for dashboard stats
6. **Referential Integrity** — `ON DELETE CASCADE`
7. **Transaction Safety** — Parameterized queries
8. **Normalization** — 1NF, 2NF, 3NF achieved across all tables
