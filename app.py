from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3

app=Flask(__name__)
app.secret_key = "abds09"

database = "./database/hospital.sqlite3"

def get_db():
    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    return redirect(url_for('role_selection'))

@app.route('/login/role')
def role_selection():
    return render_template('Login/role.html')

@app.route('/login/login_patient.html', methods=['GET', 'POST'])
def login_patient():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        conn = get_db()
        user = conn.execute('SELECT * FROM Patient WHERE email = ?', (email,)).fetchone()
        conn.close()
        if user and user['password'] == password:
            if user['is_blacklisted'] == 1:
                flash('Access denied. You are blacklisted.')
                
            else:
                flash('Login successful')
                session['patient_email'] = user['email']
                session['patient_name'] = user['username']
                session['patient_id'] = user['pat_id'] 

                return redirect('/Patient_Dashboard/dashboard.html')
        else:
            return render_template('Login/login_patient.html',
                                   popup="Invalid email or password")
    return render_template('Login/login_patient.html')


@app.route('/login/patient_registration.html', methods=['GET', 'POST'])
def pat_register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        username = request.form.get('username')
        dob = request.form.get('dob')
        gender = request.form.get('gender')
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO Patient ( username, email, password, dob, gender) VALUES (?, ?, ?, ?, ?)',(username, email, password, dob, gender.lower()))
        id = cursor.lastrowid
        pat_id_val = f"pat_{id}"
        cursor.execute('UPDATE Patient SET pat_id = ? WHERE id = ?', (pat_id_val, id))     
        conn.commit()
        conn.close()
        return render_template('/login/login_patient.html',popup="Registration Successful!")
    return render_template("Login/patient_registration.html")


@app.route('/login/login_doctor.html', methods=['GET', 'POST'])
def login_doctor():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        conn = get_db()
        user = conn.execute('SELECT * FROM Doctor WHERE email = ?', (email,)).fetchone()
        conn.close()
        if user and user['password'] == password:
            if user['is_blacklisted'] == 1:
                return render_template('Login/login_doctor.html',
                                       popup="Access denied. You are blacklisted.")

            else:
                session['doctor_name'] = user['username']
                session['doctor_email']= user['email']
                return redirect("/Doctor_Dashboard/dashboard.html")
        else:
            return render_template('Login/login_doctor.html',
                                   popup="Invalid email or password")
    return render_template('Login/login_doctor.html')

@app.route('/login/login_admin.html', methods=['GET', 'POST'])
def login_admin():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        conn = get_db()
        user = conn.execute('SELECT * FROM Admin WHERE email = ?', (email,)).fetchone()
        conn.close()
        print(email,password)
        if user and (user['password'] == password):
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('/login/login_admin.html',popup_message="Invalid email or password")
    return render_template('Login/login_Admin.html')

@app.route('/Admin_Dashboard/dashboard.html', methods=['GET','POST'])
def admin_dashboard():
    conn = get_db()
    doctors = conn.execute("SELECT id, username, is_blacklisted FROM Doctor").fetchall()
    patients = conn.execute("SELECT id, username, is_blacklisted FROM Patient").fetchall()

    appointments = conn.execute("""
    SELECT a.id AS sr_no,
           p.username AS patient_name,
           p.id AS patient_row_id,
           d.username AS doctor_name,
           a.dept AS department
    FROM Appointments a
    LEFT JOIN Patient p ON a.patient_id = p.pat_id
    LEFT JOIN Doctor d ON a.doctor_id = d.doc_id
    WHERE a.status='Upcoming'
    ORDER BY a.id
""").fetchall()

    conn.close()
    print(doctors)
    return render_template('Admin_Dashboard/dashboard.html',doctors=doctors,patients=patients,appointments=appointments)

@app.route('/Admin_Dashboard/doc_registration.html', methods=['GET', 'POST'])
def doc_register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        username = request.form.get('username')
        specialization = request.form.get('specialization')
        department = request.form.get('department')
        about = request.form.get('about')
        print(about)
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO Doctor ( username, email, password, specialization, department_id, about) VALUES (?, ?, ?, ?, ?, ?)',(username, email, password, specialization, department, about))
        id = cursor.lastrowid
        doc_id_val = f"doc_{id}"
        cursor.execute('UPDATE Doctor SET doc_id = ? WHERE id = ?', (doc_id_val, id))     
        conn.commit()
        conn.close()
        flash("Registration Successful")
        return redirect("/Admin_Dashboard/dashboard.html")
    return render_template('/Admin_Dashboard/doc_registration.html')


@app.route('/Admin_Dashboard/edit_doc.html', methods=['GET', 'POST'])
def edit_doc():
    conn = get_db()
    cursor = conn.cursor()
    if request.method == 'POST':
        doc_id = request.form.get('id')
        username = request.form.get('username')
        email = request.form.get('email')
        specialization = request.form.get('specialization')
        department = request.form.get('department')
        about = request.form.get('about')
        password = request.form.get('password')
        if password:
            cursor.execute("""
                UPDATE Doctor
                SET username=?, email=?, password=?, specialization=?, department_id=?, about=?
                WHERE id=?
            """, (username, email, password, specialization, department, about, doc_id))
        else:
            cursor.execute("""
                UPDATE Doctor
                SET username=?, email=?, specialization=?, department_id=?, about=?
                WHERE id=?
            """, (username, email, specialization, department, about, doc_id))
        conn.commit()
        conn.close()
        flash("Doctor details updated successfully")
        return redirect('/Admin_Dashboard/dashboard.html')
    doc_id = request.args.get('id')
    doctor = cursor.execute("SELECT * FROM Doctor WHERE id=?", (doc_id,)).fetchone()
    print(doctor)
    conn.close()
    return render_template('Admin_Dashboard/edit_doc.html', doctor=doctor)

@app.route('/Admin_Dashboard/delete', methods=['GET', 'POST'])
def delete():
    conn = get_db()
    cursor = conn.cursor()
    doc_id = request.args.get('id')
    cursor.execute("DELETE FROM Doctor WHERE id=?", (doc_id,))
    conn.commit()
    conn.close()
    flash("Doctor deleted successfully")
    return redirect('/Admin_Dashboard/dashboard.html')

@app.route('/Admin_Dashboard/toggle_blacklist')
def toggle_blacklist():
    doc_id = request.args.get('id')
    conn = get_db()
    cursor = conn.cursor()

    doctor = cursor.execute(
        "SELECT is_blacklisted FROM Doctor WHERE id=?", (doc_id,)
    ).fetchone()

    if not doctor:
        flash("Doctor not found")
        return redirect('/Admin_Dashboard/dashboard.html')

    new_status = 0 if doctor['is_blacklisted'] == 1 else 1

    cursor.execute(
        "UPDATE Doctor SET is_blacklisted=? WHERE id=?",
        (new_status, doc_id)
    )

    conn.commit()
    conn.close()

    flash("Updated successfully")
    return redirect('/Admin_Dashboard/dashboard.html')

@app.route('/Admin_Dashboard/delete_patient', methods=['GET'])
def delete_patient():
    pat_id = request.args.get('id')
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM Patient WHERE id=?", (pat_id,))
    conn.commit()
    conn.close()

    flash("Patient deleted successfully")
    return redirect('/Admin_Dashboard/dashboard.html')

@app.route('/Admin_Dashboard/toggle_blacklist_patient')
def toggle_blacklist_patient():
    pat_id = request.args.get('id')
    conn = get_db()
    cursor = conn.cursor()

    patient = cursor.execute(
        "SELECT is_blacklisted FROM Patient WHERE id=?", 
        (pat_id,)
    ).fetchone()

    if not patient:
        flash("Patient not found")
        return redirect('/Admin_Dashboard/dashboard.html')

    new_status = 0 if patient['is_blacklisted'] == 1 else 1

    cursor.execute(
        "UPDATE Patient SET is_blacklisted=? WHERE id=?", 
        (new_status, pat_id)
    )

    conn.commit()
    conn.close()

    flash("Updated successfully")
    return redirect('/Admin_Dashboard/dashboard.html')

@app.route('/Admin_Dashboard/edit_pat.html', methods=['GET', 'POST'])
def edit_pat():
    conn = get_db()
    cursor = conn.cursor()

    if request.method == 'POST':
        pat_id = request.form.get('id')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        dob = request.form.get('dob')
        gender = request.form.get('gender')

        if password:
            cursor.execute("""
                UPDATE Patient
                SET username=?, email=?, password=?, dob=?, gender=?
                WHERE id=?
            """, (username, email, password, dob, gender, pat_id))
        else:
            cursor.execute("""
                UPDATE Patient
                SET username=?, email=?, dob=?, gender=?
                WHERE id=?
            """, (username, email, dob, gender, pat_id))

        conn.commit()
        conn.close()
        flash("Patient details updated successfully")
        return redirect('/Admin_Dashboard/dashboard.html')

    pat_id = request.args.get('id')
    patient = cursor.execute(
        "SELECT * FROM Patient WHERE id=?", (pat_id,)
    ).fetchone()

    conn.close()
    return render_template("Admin_Dashboard/edit_pat.html", patient=patient)

@app.route('/Admin_Dashboard/view_pat.html')
def view_pat():
    pat_row_id = request.args.get('id')
    print(pat_row_id)
    conn = get_db()

    patient = conn.execute(
        "SELECT username, pat_id FROM Patient WHERE id = ?",
        (pat_row_id,)
    ).fetchone()
    print(patient)

    visits = conn.execute("""
        SELECT 
            d.username AS doctor_name,
            d.department_id AS department,
            t.visit_type,
            t.test_done,
            t.diagnosis,
            t.prescription,
            t.medicine
        FROM Treatment t
        JOIN Appointments a ON t.appointment_id = a.id
        JOIN Doctor d ON a.doctor_id = d.doc_id
        WHERE a.patient_id = ?
    """, (patient['pat_id'],)).fetchall()

    conn.close()

    return render_template(
        "Admin_Dashboard/view_pat.html",
        patient_name=patient['username'],
        visits=visits
    )



@app.route('/Doctor_Dashboard/dashboard.html')
def doctor_dashboard():
    doc_email = session.get('doctor_email')
    conn = get_db()


    doctor = conn.execute(
        "SELECT id, doc_id, username FROM Doctor WHERE email=?",
        (doc_email,)
    ).fetchone()

    appointments = conn.execute("""
        SELECT a.id AS sr_no, 
               p.username AS patient_name,
               d.username AS doctor_name,
               a.dept AS department
        FROM Appointments a
        JOIN Patient p ON a.patient_id = p.pat_id
        JOIN Doctor d ON a.doctor_id = d.doc_id
        WHERE a.doctor_id = ? AND a.status = 'Upcoming'
    """, (doctor['doc_id'],)).fetchall()


    assigned_patients = conn.execute("""
    SELECT DISTINCT Patient.* 
    FROM Patient 
    JOIN Appointments ON Patient.pat_id = Appointments.patient_id
    WHERE Appointments.doctor_id = ? 
      AND Appointments.status = 'Upcoming'
    """, (doctor['doc_id'],)).fetchall()

    conn.close()

    return render_template(
        "Doctor_Dashboard/dashboard.html",
        Doc_name=doctor['username'],
        appointments=appointments,
        assigned_patients=assigned_patients
    )


@app.route('/Doctor_Dashboard/update_pat.html', methods=['GET', 'POST'])
def update_treatment():
    conn = get_db()
    cursor = conn.cursor()

    if request.method == 'POST':
        appointment_id = request.form.get('appointment_id')
        diagnosis = request.form.get('diagnosis')
        prescription = request.form.get('prescription')
        medicine = request.form.get('medicine')
        test_done = request.form.get('test_done')
        visit_type = request.form.get('visit_type')
        existing = cursor.execute(
            "SELECT id FROM Treatment WHERE appointment_id = ?", (appointment_id,)
        ).fetchone()

        if existing:
            cursor.execute("""
                UPDATE Treatment
                SET diagnosis=?, prescription=?, medicine=?, test_done=?, visit_type=?
                WHERE appointment_id=?
            """, (diagnosis, prescription, medicine, test_done, visit_type, appointment_id))
            flash("Treatment details updated successfully.")
        else:
            cursor.execute("""
                INSERT INTO Treatment (appointment_id, diagnosis, prescription, medicine, test_done, visit_type)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (appointment_id, diagnosis, prescription, medicine, test_done, visit_type))
            flash("New treatment record added.")

        conn.commit()
        conn.close()
        return redirect('/Doctor_Dashboard/dashboard.html')
    appointment_id = request.args.get('appointment_id')
    treatment = None
    if appointment_id:
        treatment = cursor.execute(
            "SELECT * FROM Treatment WHERE appointment_id = ?", (appointment_id,)
        ).fetchone()
    conn.close()
    return render_template('/Doctor_Dashboard/update_pat.html', treatment=treatment)


@app.route('/Doctor_Dashboard/cancel_appointment', methods=['GET'])
def cancel_appointment():
    appt_id = request.args.get('id')
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE Appointments
    SET status = 'Cancelled'
    WHERE id = ?
    """, (appt_id,))
    cursor.execute("DELETE FROM Treatment WHERE appointment_id = ?", (appt_id,))

    
    conn.commit()
    conn.close()

    flash("Appointment cancelled successfully.")
    return redirect('/Doctor_Dashboard/dashboard.html')

@app.route('/Doctor_Dashboard/mark_completed', methods=['GET'])
def mark_completed():
    appt_id = request.args.get('id')
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE Appointments
        SET status = 'Completed'
        WHERE id = ?
    """, (appt_id,))

    conn.commit()
    conn.close()

    flash("Appointment marked as completed.")
    return redirect('/Doctor_Dashboard/dashboard.html')

@app.route('/Doctor_Dashboard/view_patient.html')
def view_patient():
    pat_row_id = request.args.get('id')
    print(pat_row_id)
    conn = get_db()

    patient = conn.execute(
        "SELECT username, pat_id FROM Patient WHERE id = ?",
        (pat_row_id,)
    ).fetchone()
    print(patient)

    visits = conn.execute("""
        SELECT 
            d.username AS doctor_name,
            d.department_id AS department,
            t.visit_type,
            t.test_done,
            t.diagnosis,
            t.prescription,
            t.medicine
        FROM Treatment t
        JOIN Appointments a ON t.appointment_id = a.id
        JOIN Doctor d ON a.doctor_id = d.doc_id
        WHERE a.patient_id = ?
    """, (patient['pat_id'],)).fetchall()

    conn.close()

    return render_template(
        "Doctor_Dashboard/view_patient.html",
        patient_name=patient['username'],
        visits=visits
    )


@app.route('/Patient_Dashboard/dashboard.html')
def patient_dashboard():
    pat_email = session.get('patient_email')
    if not pat_email:
        flash("Please log in first.")
        return redirect('/login/login_patient.html')

    conn = get_db()
    patient = conn.execute(
        "SELECT id, pat_id, username FROM Patient WHERE email = ?",
        (pat_email,)
    ).fetchone()

    departments = conn.execute("SELECT * FROM Department").fetchall()

    appointments = conn.execute("""
        SELECT a.id, 
               d.username AS doctor_name, 
               a.dept, 
               a.date, 
               a.time
        FROM Appointments a
        JOIN Doctor d ON a.doctor_id = d.doc_id
        WHERE a.patient_id = ? AND a.status = 'Upcoming'
        ORDER BY a.date, a.time
    """, (patient['pat_id'],)).fetchall()

    print("Appointments fetched:", appointments)

    conn.close()
    return render_template(
        '/Patient_Dashboard/dashboard.html',
        patient_name=patient['username'],
        patient_id=patient['pat_id'],
        p_id=patient['id'],
        departments=departments,
        appointments=appointments
    )

@app.route('/Patient_Dashboard/view_patient.html')
def patient_view_patient():
    pat_row_id = request.args.get('id')
    conn = get_db()

    patient = conn.execute(
        "SELECT username, pat_id FROM Patient WHERE id = ?",
        (pat_row_id,)
    ).fetchone()

    visits = conn.execute("""
        SELECT 
            d.username AS doctor_name,
            d.department_id AS department,
            t.visit_type,
            t.test_done,
            t.diagnosis,
            t.prescription,
            t.medicine
        FROM Treatment t
        JOIN Appointments a ON t.appointment_id = a.id
        JOIN Doctor d ON a.doctor_id = d.doc_id
        WHERE a.patient_id = ?
    """, (patient['pat_id'],)).fetchall()

    conn.close()

    return render_template(
        "Patient_Dashboard/view_patient.html",
        patient_name=patient['username'],
        visits=visits
    )

@app.route('/Patient/edit_profile.html', methods=['GET', 'POST'])
def edit_patient_profile():
    # Make sure the patient is logged in
    patient_id = session.get('patient_id')
    if not patient_id:
        flash("Please log in first.")
        return redirect('/login/login_patient.html')

    conn = get_db()
    cursor = conn.cursor()

    if request.method == 'POST':
        # Get updated form data
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        dob = request.form.get('dob')
        gender = request.form.get('gender')

        # Update patient info
        if password:
            cursor.execute("""
                UPDATE Patient
                SET username=?, email=?, password=?, dob=?, gender=?
                WHERE pat_id=?
            """, (username, email, password, dob, gender, patient_id))
        else:
            cursor.execute("""
                UPDATE Patient
                SET username=?, email=?, dob=?, gender=?
                WHERE pat_id=?
            """, (username, email, dob, gender, patient_id))

        conn.commit()
        conn.close()
        flash("Profile updated successfully")
        return redirect('/Patient_Dashboard/dashboard.html')

    # GET request: fetch patient info
    patient = cursor.execute(
        "SELECT * FROM Patient WHERE pat_id=?", (patient_id,)
    ).fetchone()
    conn.close()
    return render_template("Patient_Dashboard/edit_profile.html", patient=patient)


@app.route('/Patient_Dashboard/department_details.html')
def department_details():
    dept_id = request.args.get('id')
    conn = get_db()
    department = conn.execute(
        "SELECT * FROM Department WHERE dept_id = ?", (dept_id,)
    ).fetchone()

    doctors = conn.execute("""
        SELECT doc_id, username, specialization 
        FROM Doctor
        WHERE department_id = ?
    """, (dept_id,)).fetchall()

    conn.close()
    return render_template(
        'Patient_Dashboard/department_details.html',
        department=department,
        doctors=doctors
    )

@app.route("/doctor/<doctor_id>/availability", methods=["GET", "POST"])
def doctor_availability(doctor_id):
    conn = get_db()
    doctor = conn.execute("SELECT * FROM Doctor WHERE doc_id=?", (doctor_id,)).fetchone()

    # Date range for date picker
    from datetime import datetime, timedelta
    today = datetime.today().date()
    max_date = today + timedelta(days=30)
    
    selected_date = request.form.get("date")
    slots = []

    if selected_date:
        # Fetch all booked slots for this doctor on the selected date
        booked_slots = conn.execute(
            "SELECT time FROM Appointments WHERE doctor_id=? AND date=? AND status='Upcoming'",
            (doctor_id, selected_date)
        ).fetchall()
        booked_times = [b['time'] for b in booked_slots]

        # Define all possible slots (9AM-12PM, 2PM-5PM)
        possible_slots = ["09:00", "10:00", "11:00", "12:00", "14:00", "15:00", "16:00", "17:00"]
        slots = [{"time": t, "booked": t in booked_times} for t in possible_slots]

    conn.close()
    return render_template(
        "Patient_Dashboard/doctor_availability.html",
        doctor=doctor,
        selected_date=selected_date,
        slots=slots,
        today=today.strftime("%Y-%m-%d"),
        max_date=max_date.strftime("%Y-%m-%d")
    )

@app.route("/book_appointment", methods=["POST"])
def book_appointment():
    doctor_id = request.form.get("doctor_id")
    patient_id = session.get("patient_id")
    date = request.form.get("date")
    time = request.form.get("time")
    dept = request.form.get("dept")

    if not patient_id:
        return redirect("/login/login_patient.html?popup=Please+login+first")

    conn = get_db()
    cursor = conn.cursor()

    # Check if slot is already booked
    existing = cursor.execute(
        "SELECT * FROM Appointments WHERE doctor_id=? AND date=? AND time=? AND status='Upcoming'",
        (doctor_id, date, time)
    ).fetchone()

    if existing:
        conn.close()
        return redirect(f"/doctor_availability/{doctor_id}?date={date}&popup=Slot+already+booked")

    # Insert appointment
    cursor.execute(
        "INSERT INTO Appointments (patient_id, doctor_id, dept, date, time) VALUES (?, ?, ?, ?, ?)",
        (patient_id, doctor_id, dept, date, time)
    )
    conn.commit()
    conn.close()

    return redirect(f"/Patient_Dashboard/dashboard.html?popup=Appointment+Booked+Successfully")


@app.route('/Patient_Dashboard/cancel_appointment')
def patient_cancel_appointment():
    appt_id = request.args.get('id')
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE Appointments
        SET status = 'Cancelled'
        WHERE id = ? AND status = 'Upcoming'
    """, (appt_id,))

    conn.commit()
    conn.close()

    flash("Appointment cancelled successfully.")
    return redirect('/Patient_Dashboard/dashboard.html')

@app.route('/doctor/<doctor_id>')
def doctor_details(doctor_id):
    conn = get_db()
    doctor = conn.execute("SELECT * FROM Doctor WHERE doc_id = ?", (doctor_id,)).fetchone()
    dept = conn.execute("SELECT name FROM Department WHERE dept_id = ?", (doctor['department_id'],)).fetchone()
    conn.close()

    return render_template("Patient_Dashboard/doctor_details.html", doctor=doctor, department=dept['name'])


@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out successfully.")
    return redirect('/login/role')


if __name__ == '__main__':
    app.run(debug=True)
