from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, User, DoctorProfile, PatientProfile, Appointment, Department, Role
from werkzeug.security import generate_password_hash

admin = Blueprint('admin', __name__, url_prefix='/admin')

@admin.before_request
@login_required
def require_admin():
    if current_user.role != Role.ADMIN:
        return "Access Denied", 403

@admin.route('/dashboard')
def dashboard():
    doctor_count = User.query.filter_by(role=Role.DOCTOR).count()
    patient_count = User.query.filter_by(role=Role.PATIENT).count()
    appointment_count = Appointment.query.count()
    return render_template('dashboards/admin.html', 
                         doctor_count=doctor_count,
                         patient_count=patient_count,
                         appointment_count=appointment_count)

@admin.route('/doctors')
def doctors():
    search = request.args.get('search', '')
    query = User.query.filter_by(role=Role.DOCTOR)
    if search:
        query = query.filter(User.name.ilike(f'%{search}%'))
    doctors = query.all()
    return render_template('admin/doctors.html', doctors=doctors, search=search)

@admin.route('/doctors/add', methods=['GET', 'POST'])
def add_doctor():
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')
        dept_id = request.form.get('department_id')
        qualification = request.form.get('qualification')
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists')
            return redirect(url_for('admin.add_doctor'))
            
        user = User(email=email, name=name, role=Role.DOCTOR)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        profile = DoctorProfile(user_id=user.id, department_id=dept_id, qualification=qualification)
        db.session.add(profile)
        db.session.commit()
        
        flash('Doctor added successfully')
        return redirect(url_for('admin.doctors'))
        
    departments = Department.query.all()
    return render_template('admin/doctor_form.html', departments=departments)

@admin.route('/doctors/<int:id>/edit', methods=['GET', 'POST'])
def edit_doctor(id):
    doctor = db.session.get(User, id)
    if not doctor or doctor.role != Role.DOCTOR:
        return "Not Found", 404
        
    if request.method == 'POST':
        doctor.name = request.form.get('name')
        doctor.email = request.form.get('email')
        doctor.doctor_profile.department_id = request.form.get('department_id')
        doctor.doctor_profile.qualification = request.form.get('qualification')
        
        if request.form.get('password'):
            doctor.set_password(request.form.get('password'))
            
        db.session.commit()
        flash('Doctor updated successfully')
        return redirect(url_for('admin.doctors'))
        
    departments = Department.query.all()
    return render_template('admin/doctor_form.html', doctor=doctor, departments=departments)

@admin.route('/doctors/<int:id>/delete', methods=['POST'])
def delete_doctor(id):
    doctor = db.session.get(User, id)
    if doctor and doctor.role == Role.DOCTOR:
        db.session.delete(doctor)
        db.session.commit()
        flash('Doctor deleted successfully')
    return redirect(url_for('admin.doctors'))

@admin.route('/patients')
def patients():
    search = request.args.get('search', '')
    query = User.query.filter_by(role=Role.PATIENT)
    if search:
        query = query.filter(User.name.ilike(f'%{search}%'))
    patients = query.all()
    return render_template('admin/patients.html', patients=patients, search=search)

@admin.route('/patients/<int:id>/toggle_status', methods=['POST'])
def toggle_patient_status(id):
    patient = db.session.get(User, id)
    if patient and patient.role == Role.PATIENT:
        patient.patient_profile.is_blacklisted = not patient.patient_profile.is_blacklisted
        db.session.commit()
        status = "blacklisted" if patient.patient_profile.is_blacklisted else "activated"
        flash(f'Patient {status} successfully')
    return redirect(url_for('admin.patients'))

@admin.route('/appointments')
def appointments():
    appointments = Appointment.query.order_by(Appointment.appointment_start.desc()).all()
    return render_template('admin/appointments.html', appointments=appointments)
