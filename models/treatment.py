from models.base import db, utc_now


class Treatment(db.Model):
    __tablename__ = "treatments"
    
    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey("appointments.id", ondelete="CASCADE"), unique=True, nullable=False)
    diagnosis = db.Column(db.Text)
    prescription = db.Column(db.Text)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=utc_now)
    doctor_notes = db.Column(db.Text)
    
    appointment = db.relationship("Appointment", back_populates="treatment")
    
    def __repr__(self):
        return f'<Treatment {self.id} - Appointment:{self.appointment_id}>'
