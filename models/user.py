from werkzeug.security import generate_password_hash
from models.base import db, utc_now, Role


from flask_login import UserMixin

class User(UserMixin, db.Model):
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(180), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)
    
    doctor_profile = db.relationship("DoctorProfile", uselist=False, back_populates="user", cascade="all, delete-orphan")
    patient_profile = db.relationship("PatientProfile", uselist=False, back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<User {self.email} ({self.role})>'
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password_hash, password)
