from models.base import db, utc_now


class Department(db.Model):
    __tablename__ = "departments"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=utc_now)
    
    doctor_profiles = db.relationship("DoctorProfile", backref="department", lazy=True)
    
    def __repr__(self):
        return f'<Department {self.name}>'
