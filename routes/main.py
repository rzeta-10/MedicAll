from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from models import Role

main = Blueprint('main', __name__)

@main.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == Role.ADMIN:
            return redirect(url_for('admin.dashboard'))
        elif current_user.role == Role.DOCTOR:
            return redirect(url_for('doctor.dashboard'))
        return redirect(url_for('patient.dashboard'))
    return redirect(url_for('auth.login'))
