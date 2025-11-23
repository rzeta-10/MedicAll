from models.base import db, utc_now, Role, AppointmentStatus
from models.user import User
from models.department import Department
from models.doctor_profile import DoctorProfile
from models.patient_profile import PatientProfile
from models.doctor_availability import DoctorAvailability
from models.appointment import Appointment
from models.treatment import Treatment


def init_db():
    db.create_all()
    
    admin = User.query.filter_by(email='admin@hospital.com', role=Role.ADMIN).first()
    if not admin:
        admin = User(
            email='admin@hospital.com',
            name='System Admin',
            role=Role.ADMIN,
            is_active=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("✓ Predefined admin created (email: admin@hospital.com, password: admin123)")
    
    default_departments = [
        {'name': 'Cardiology', 'description': 'Heart and cardiovascular system'},
        {'name': 'Oncology', 'description': 'Cancer treatment and care'},
        {'name': 'General', 'description': 'General medicine and primary care'},
        {'name': 'Neurology', 'description': 'Brain and nervous system'},
        {'name': 'Orthopedics', 'description': 'Bones, joints, and muscles'}
    ]
    
    for dept_data in default_departments:
        dept = Department.query.filter_by(name=dept_data['name']).first()
        if not dept:
            dept = Department(**dept_data)
            db.session.add(dept)
    
    db.session.commit()
    print("✓ Database initialized successfully")


__all__ = [
    'db',
    'utc_now',
    'Role',
    'AppointmentStatus',
    'User',
    'Department',
    'DoctorProfile',
    'PatientProfile',
    'DoctorAvailability',
    'Appointment',
    'Treatment',
    'init_db'
]
