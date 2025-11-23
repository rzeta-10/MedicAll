from models.base import db


class DoctorAvailability(db.Model):
    __tablename__ = "doctor_availabilities"
    
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctor_profiles.id", ondelete="CASCADE"), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    notes = db.Column(db.String(255))
    
    doctor = db.relationship("DoctorProfile", back_populates="availabilities")
    
    __table_args__ = (
        db.UniqueConstraint('doctor_id', 'date', 'start_time', 'end_time', name='u_doctor_date_window'),
    )
    
    def __repr__(self):
        return f'<DoctorAvailability Doctor:{self.doctor_id} Date:{self.date}>'
