from .. import db
from datetime import datetime

class PatientTest(db.Model):
    __tablename__ = 'patient_tests'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    guest_name = db.Column(db.String(100), nullable=True) # For offline/admin bookings
    test_name = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), default='Pending') # Pending, Completed
    price = db.Column(db.Float, default=0.0)
    report_pdf_path = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    patient = db.relationship('User', backref='tests')

    def to_dict(self):
        p_name = self.guest_name
        if self.patient:
            p_name = self.patient.full_name
            
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'patient_name': p_name or 'Unknown',
            'test_name': self.test_name,
            'status': self.status,
            'price': self.price,
            'report_available': bool(self.report_pdf_path),
            'created_at': self.created_at.isoformat()
        }
