from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from models import Role

main = Blueprint('main', __name__)

@main.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == Role.ADMIN:
            return redirect(url_for('main.admin_dashboard'))
        elif current_user.role == Role.DOCTOR:
            return redirect(url_for('main.doctor_dashboard'))
        return redirect(url_for('main.patient_dashboard'))
    return redirect(url_for('auth.login'))

@main.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.role != Role.ADMIN:
        return "Access Denied", 403
    return render_template('dashboards/admin.html')

@main.route('/doctor/dashboard')
@login_required
def doctor_dashboard():
    if current_user.role != Role.DOCTOR:
        return "Access Denied", 403
    return render_template('dashboards/doctor.html')

@main.route('/patient/dashboard')
@login_required
def patient_dashboard():
    if current_user.role != Role.PATIENT:
        return "Access Denied", 403
    return render_template('dashboards/patient.html')
