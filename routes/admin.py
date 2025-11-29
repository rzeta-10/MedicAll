from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, User, DoctorProfile, PatientProfile, Appointment, Department, Role, AppointmentStatus, DoctorAvailability
from werkzeug.security import generate_password_hash
from utils import validate_email, validate_password, validate_required_fields, ValidationError, sanitize_input, validate_date, validate_time_range
from datetime import datetime

admin = Blueprint('admin', __name__, url_prefix='/admin')

@admin.before_request
@login_required
def require_admin():
    if current_user.role != Role.ADMIN:
        return "Access Denied", 403

@admin.route('/dashboard')
def dashboard():
    # stats
    doctors_count = User.query.filter_by(role=Role.DOCTOR).count()
    patients_count = User.query.filter_by(role=Role.PATIENT).count()
    total_appts = Appointment.query.count()
    
    # blacklisted counts
    blocked_docs = DoctorProfile.query.filter_by(is_blacklisted=True).count()
    blocked_patients = PatientProfile.query.filter_by(is_blacklisted=True).count()
    total_blocked = blocked_docs + blocked_patients
    active_users = (doctors_count + patients_count) - total_blocked
    
    # chart data 1: doctors per dept
    dept_stats = db.session.query(Department.name, db.func.count(DoctorProfile.id))\
        .join(DoctorProfile, DoctorProfile.department_id == Department.id)\
        .group_by(Department.name).all()
        
    dept_labels = [s[0] for s in dept_stats]
    dept_data = [s[1] for s in dept_stats]
    
    # chart data 2: patient status
    active_patients = patients_count - blocked_patients
    pat_labels = ['Active Patients', 'Blacklisted Patients']
    pat_data = [active_patients, blocked_patients]
    
    # chart data 3: appt status
    status_counts = db.session.query(Appointment.status, db.func.count(Appointment.id))\
        .group_by(Appointment.status).all()
        
    status_map = {s[0]: s[1] for s in status_counts}
    appt_labels = ['Booked', 'Completed', 'Cancelled']
    appt_data = [
        status_map.get(AppointmentStatus.BOOKED, 0),
        status_map.get(AppointmentStatus.COMPLETED, 0),
        status_map.get(AppointmentStatus.CANCELLED, 0)
    ]
    
    return render_template('dashboards/admin.html', 
                         total_doctors=doctors_count,
                         total_patients=patients_count,
                         total_appointments=total_appts,
                         dept_labels=dept_labels,
                         dept_data=dept_data,
                         patient_status_labels=pat_labels,
                         patient_status_data=pat_data,
                         appt_status_labels=appt_labels,
                         appt_status_data=appt_data)

@admin.route('/doctors')
def doctors():
    search = request.args.get('search', '')
    query = User.query.filter_by(role=Role.DOCTOR, is_active=True)
    if search:
        search_term = f'%{search}%'
        query = query.outerjoin(DoctorProfile).outerjoin(Department).filter(
            db.or_(
                User.name.ilike(search_term),
                DoctorProfile.qualification.ilike(search_term),
                Department.name.ilike(search_term)
            )
        )
    doctors = query.all()
    return render_template('admin/doctors.html', doctors=doctors, search=search)

@admin.route('/doctors/add', methods=['GET', 'POST'])
def add_doctor():
    if request.method == 'POST':
        email = sanitize_input(request.form.get('email'))
        name = sanitize_input(request.form.get('name'))
        pwd = request.form.get('password')
        dept_id = request.form.get('department_id')
        qual = sanitize_input(request.form.get('qualification', ''))
        
        # validations
        try:
            validate_required_fields(request.form, ['email', 'name', 'password', 'department_id'])
            validate_email(email)
            validate_password(pwd)
            
            # check department
            dept = db.session.get(Department, dept_id)
            if not dept:
                raise ValidationError("Invalid department selected")
                
        except ValidationError as e:
            flash(str(e), 'danger')
            departments = Department.query.all()
            return render_template('admin/doctor_form.html', departments=departments)
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists', 'danger')
            departments = Department.query.all()
            return render_template('admin/doctor_form.html', departments=departments)
            
        user = User(email=email, name=name, role=Role.DOCTOR)
        user.set_password(pwd)
        db.session.add(user)
        db.session.commit()
        
        profile = DoctorProfile(user_id=user.id, department_id=dept_id, qualification=qual)
        db.session.add(profile)
        db.session.commit()
        
        flash('Doctor added successfully', 'success')
        return redirect(url_for('admin.doctors'))
        
    departments = Department.query.all()
    return render_template('admin/doctor_form.html', departments=departments)

@admin.route('/doctors/<int:id>/edit', methods=['GET', 'POST'])
def edit_doctor(id):
    doctor = db.session.get(User, id)
    if not doctor or doctor.role != Role.DOCTOR:
        return "Not Found", 404
        
    if request.method == 'POST':
        name = sanitize_input(request.form.get('name'))
        email = sanitize_input(request.form.get('email'))
        dept_id = request.form.get('department_id')
        qual = sanitize_input(request.form.get('qualification', ''))
        pwd = request.form.get('password')
        
        # validate inputs
        try:
            validate_required_fields(request.form, ['name', 'email', 'department_id'])
            validate_email(email)
            
            # verify department
            dept = db.session.get(Department, dept_id)
            if not dept:
                raise ValidationError("Invalid department selected")
            
            # check password only if provided
            if pwd:
                validate_password(pwd)
                
        except ValidationError as e:
            flash(str(e), 'danger')
            departments = Department.query.all()
            return render_template('admin/doctor_form.html', doctor=doctor, departments=departments)
        
        # email uniqueness check
        existing = User.query.filter_by(email=email).first()
        if existing and existing.id != doctor.id:
            flash('Email already exists', 'danger')
            departments = Department.query.all()
            return render_template('admin/doctor_form.html', doctor=doctor, departments=departments)
        
        doctor.name = name
        doctor.email = email
        doctor.doctor_profile.department_id = dept_id
        doctor.doctor_profile.qualification = qual
        
        if pwd:
            doctor.set_password(pwd)
            
        db.session.commit()
        flash('Doctor updated successfully', 'success')
        return redirect(url_for('admin.doctors'))
        
    departments = Department.query.all()
    return render_template('admin/doctor_form.html', doctor=doctor, departments=departments)

@admin.route('/doctors/<int:id>/delete', methods=['POST'])
def delete_doctor(id):
    doctor = db.session.get(User, id)
    if doctor and doctor.role == Role.DOCTOR:
        # cancel booked appointments before deleting
        if doctor.doctor_profile and doctor.doctor_profile.appointments:
            for appt in doctor.doctor_profile.appointments:
                if appt.status == AppointmentStatus.BOOKED:
                    appt.status = AppointmentStatus.CANCELLED
                    appt.canceled_by = 'ADMIN'
        
        doctor.is_active = False
        db.session.commit()
        flash('Doctor deleted successfully', 'success')
            
    return redirect(url_for('admin.doctors'))

@admin.route('/patients')
def patients():
    search = request.args.get('search', '')
    query = User.query.filter_by(role=Role.PATIENT)
    
    if search:
        search_term = f'%{search}%'
        conditions = [
            User.name.ilike(search_term),
            User.email.ilike(search_term),
            PatientProfile.phone.ilike(search_term)
        ]
        
        # Add ID search if input is numeric
        if search.isdigit():
            conditions.append(User.id == int(search))
            
        query = query.join(PatientProfile).filter(db.or_(*conditions))
        
    patients = query.all()
    return render_template('admin/patients.html', patients=patients, search=search)

@admin.route('/patients/<int:id>/edit', methods=['GET', 'POST'])
def edit_patient(id):
    patient = db.session.get(User, id)
    if not patient or patient.role != Role.PATIENT:
        return "Not Found", 404
        
    if request.method == 'POST':
        name = sanitize_input(request.form.get('name'))
        email = sanitize_input(request.form.get('email'))
        phone = sanitize_input(request.form.get('phone'))
        addr = sanitize_input(request.form.get('address'))
        gender = request.form.get('gender')
        dob_str = request.form.get('dob')
        
        try:
            validate_required_fields(request.form, ['name', 'email', 'phone'])
            validate_email(email)
            
            # check email unique
            existing = User.query.filter_by(email=email).first()
            if existing and existing.id != patient.id:
                raise ValidationError('Email already exists')
                
            if dob_str:
                dob = validate_date(dob_str, allow_future=False)
                patient.patient_profile.dob = dob
                
        except ValidationError as e:
            flash(str(e), 'danger')
            return render_template('admin/patient_form.html', patient=patient)
            
        patient.name = name
        patient.email = email
        patient.patient_profile.phone = phone
        patient.patient_profile.address = addr
        patient.patient_profile.gender = gender
        
        db.session.commit()
        flash('Patient details updated successfully', 'success')
        return redirect(url_for('admin.patients'))
        
    return render_template('admin/patient_form.html', patient=patient)

@admin.route('/patients/<int:id>/toggle_status', methods=['POST'])
def toggle_patient_status(id):
    patient = db.session.get(User, id)
    if patient and patient.role == Role.PATIENT:
        patient.patient_profile.is_blacklisted = not patient.patient_profile.is_blacklisted
        db.session.commit()
        status = "blacklisted" if patient.patient_profile.is_blacklisted else "activated"
        flash(f'Patient {status} successfully', 'success')
    return redirect(url_for('admin.patients'))

@admin.route('/appointments')
def appointments():
    appointments = Appointment.query.order_by(Appointment.appointment_start.desc()).all()
    return render_template('admin/appointments.html', appointments=appointments)

@admin.route('/appointments/<int:id>/cancel', methods=['POST'])
def cancel_appointment(id):
    appointment = db.session.get(Appointment, id)
    if appointment and appointment.status == AppointmentStatus.BOOKED:
        appointment.status = AppointmentStatus.CANCELLED
        appointment.canceled_by = 'ADMIN'
        db.session.commit()
        flash('Appointment cancelled successfully', 'success')
    return redirect(url_for('admin.appointments'))

@admin.route('/appointments/<int:id>/delete', methods=['POST'])
def delete_appointment(id):
    appointment = db.session.get(Appointment, id)
    if appointment:
        db.session.delete(appointment)
        db.session.commit()
        flash('Appointment deleted successfully', 'success')
    return redirect(url_for('admin.appointments'))

@admin.route('/doctors/<int:id>/availability', methods=['GET', 'POST'])
def doctor_availability(id):
    doctor = db.session.get(User, id)
    if not doctor or doctor.role != Role.DOCTOR:
        return "Not Found", 404
        
    if request.method == 'POST':
        date_str = request.form.get('date')
        start_time_str = request.form.get('start_time')
        end_time_str = request.form.get('end_time')
        
        try:
            validate_required_fields(request.form, ['date', 'start_time', 'end_time'])
            avail_date = validate_date(date_str, allow_future=True, allow_past=False)
            start_time = datetime.strptime(start_time_str, '%H:%M').time()
            end_time = datetime.strptime(end_time_str, '%H:%M').time()
            validate_time_range(start_time, end_time)
            
            existing = DoctorAvailability.query.filter_by(
                doctor_id=doctor.doctor_profile.id,
                date=avail_date
            ).filter(
                db.and_(
                    DoctorAvailability.start_time < end_time,
                    DoctorAvailability.end_time > start_time
                )
            ).first()
            
            if existing:
                raise ValidationError("This time slot overlaps with an existing availability")
            
            avail = DoctorAvailability(
                doctor_id=doctor.doctor_profile.id,
                date=avail_date,
                start_time=start_time,
                end_time=end_time
            )
            db.session.add(avail)
            db.session.commit()
            flash('Availability slot added', 'success')
            
        except (ValueError, ValidationError) as e:
            flash(str(e), 'danger')
            
        return redirect(url_for('admin.doctor_availability', id=id))
        
    today = datetime.now().date()
    availabilities = DoctorAvailability.query.filter_by(doctor_id=doctor.doctor_profile.id)\
        .filter(DoctorAvailability.date >= today)\
        .order_by(DoctorAvailability.date, DoctorAvailability.start_time).all()
        
    return render_template('admin/doctor_availability.html', doctor=doctor, availabilities=availabilities, today=today)

@admin.route('/doctors/<int:doctor_id>/availability/<int:avail_id>/delete', methods=['POST'])
def delete_doctor_availability(doctor_id, avail_id):
    avail = db.session.get(DoctorAvailability, avail_id)
    if avail and avail.doctor.user.id == doctor_id:
        db.session.delete(avail)
        db.session.commit()
        flash('Availability slot removed', 'success')
    return redirect(url_for('admin.doctor_availability', id=doctor_id))
