from .. import db

class Doctor(db.Model):
    __tablename__ = 'doctors'
    
    id = db.Column(db.Integer, primary_key=True)
    sys_id = db.Column(db.String(50), unique=True, nullable=False) # The 'manual' ID they enter
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer)
    specialty = db.Column(db.String(100))
    years_experience = db.Column(db.Integer)
    address = db.Column(db.String(255))
    nid = db.Column(db.String(20)) # National ID
    position = db.Column(db.String(100))
    
    def to_dict(self):
        return {
            'id': self.id,
            'sysID': self.sys_id,
            'name': self.name,
            'age': self.age,
            'spec': self.specialty,
            'xp': self.years_experience,
            'address': self.address,
            'nid': self.nid,
            'pos': self.position
        }
