from .. import db
from datetime import datetime

# Junction link tables
branch_equipment = db.Table('branch_equipment',
    db.Column('b_id', db.Integer, db.ForeignKey('branches.b_id'), primary_key=True),
    db.Column('e_id', db.Integer, db.ForeignKey('equipment.e_id'), primary_key=True)
)

equipment_tests = db.Table('equipment_tests',
    db.Column('e_id', db.Integer, db.ForeignKey('equipment.e_id'), primary_key=True),
    db.Column('t_id', db.Integer, db.ForeignKey('tests.t_id'), primary_key=True)
)

# patient_tests = db.Table('patient_tests',
#     db.Column('p_id', db.Integer, db.ForeignKey('patients.p_id'), primary_key=True),
#     db.Column('t_id', db.Integer, db.ForeignKey('tests.t_id'), primary_key=True)
# )

test_samples = db.Table('test_samples',
    db.Column('t_id', db.Integer, db.ForeignKey('tests.t_id'), primary_key=True),
    db.Column('sa_id', db.Integer, db.ForeignKey('samples.sa_id'), primary_key=True)
)


class Branch(db.Model):
    __tablename__ = 'branches'
    b_id = db.Column(db.Integer, primary_key=True)
    b_phone = db.Column(db.String(20))
    b_name = db.Column(db.String(150))
    b_fax_number = db.Column(db.String(50))
    b_email = db.Column(db.String(150))
    b_manager = db.Column(db.String(150))
    b_location = db.Column(db.String(255))
    b_number_of_rooms = db.Column(db.Integer)

    doctors = db.relationship('Doctor', backref='branch')
    staff = db.relationship('Staff', backref='branch')
    equipment = db.relationship('Equipment', secondary=branch_equipment, backref='branches')

class Supplier(db.Model):
    __tablename__ = 'suppliers'
    su_id = db.Column(db.Integer, primary_key=True)
    su_name = db.Column(db.String(150))
    su_email = db.Column(db.String(150))
    su_phone_number = db.Column(db.String(20))
    su_address = db.Column(db.String(255))

    equipment = db.relationship('Equipment', backref='supplier')

class Patient(db.Model):
    __tablename__ = 'patients'
    p_id = db.Column(db.Integer, primary_key=True)
    p_email = db.Column(db.String(150))
    p_age = db.Column(db.Integer)
    p_ssn = db.Column(db.String(50))
    p_name = db.Column(db.String(150))
    p_insurance_provider = db.Column(db.String(100))
    p_insurance_number = db.Column(db.String(100))
    p_medical_history = db.Column(db.Text)
    p_gender = db.Column(db.String(20))
    p_address = db.Column(db.String(255))
    p_birth_date = db.Column(db.Date)
    p_account = db.Column(db.String(150))
    p_phone_number = db.Column(db.String(20))

    results = db.relationship('Result', backref='patient')
    payments = db.relationship('Payment', backref='patient')
    tests = db.relationship('Test', secondary=patient_tests, backref='patients')

class Doctor(db.Model):
    __tablename__ = 'doctors'
    d_id = db.Column(db.Integer, primary_key=True)
    d_ssn = db.Column(db.String(50))
    d_phone_number = db.Column(db.String(20))
    d_year_of_employement = db.Column(db.Integer)
    d_age = db.Column(db.Integer)
    d_email = db.Column(db.String(150))
    d_gender = db.Column(db.String(20))
    d_specialization = db.Column(db.String(100))
    d_salary = db.Column(db.Numeric(12, 2))
    b_id = db.Column(db.Integer, db.ForeignKey('branches.b_id'))

    supervised_tests = db.relationship('Test', backref='doctor')
    results = db.relationship('Result', backref='doctor')

class Staff(db.Model):
    __tablename__ = 'staff'
    s_id = db.Column(db.Integer, primary_key=True)
    s_age = db.Column(db.Integer)
    s_ssn = db.Column(db.String(50))
    s_phone_number = db.Column(db.String(20))
    s_salary = db.Column(db.Numeric(12, 2))
    s_gender = db.Column(db.String(20))
    s_position = db.Column(db.String(100))
    s_shift = db.Column(db.String(50))
    s_email = db.Column(db.String(150))
    s_address = db.Column(db.String(255))
    supervisor_id = db.Column(db.Integer, db.ForeignKey('staff.s_id'), nullable=True)
    b_id = db.Column(db.Integer, db.ForeignKey('branches.b_id'))

    subordinates = db.relationship('Staff', backref=db.backref('supervisor', remote_side=[s_id]))

class Equipment(db.Model):
    __tablename__ = 'equipment'
    e_id = db.Column(db.Integer, primary_key=True)
    e_name = db.Column(db.String(150))
    e_location = db.Column(db.String(150))
    e_maintenance_records = db.Column(db.Text)
    e_type = db.Column(db.String(150))
    su_id = db.Column(db.Integer, db.ForeignKey('suppliers.su_id'))

    tests = db.relationship('Test', secondary=equipment_tests, backref='equipment_used')

class Sample(db.Model):
    __tablename__ = 'samples'
    sa_id = db.Column(db.Integer, primary_key=True)
    sa_type = db.Column(db.String(100))
    sa_storing_condition = db.Column(db.String(255))
    sa_collection_date = db.Column(db.Date)
    sa_expiration_date = db.Column(db.Date)

class Test(db.Model):
    __tablename__ = 'tests'
    t_id = db.Column(db.Integer, primary_key=True)
    t_type = db.Column(db.String(150))
    t_date = db.Column(db.Date)
    t_cost = db.Column(db.Numeric(10, 2))
    t_pre_test = db.Column(db.Text)
    t_status = db.Column(db.String(50))
    d_id = db.Column(db.Integer, db.ForeignKey('doctors.d_id'))

    samples = db.relationship('Sample', secondary=test_samples, backref='tests')
    results = db.relationship('Result', backref='test')

class Result(db.Model):
    __tablename__ = 'results'
    r_id = db.Column(db.Integer, primary_key=True)
    r_value = db.Column(db.String(255))
    r_submitter = db.Column(db.String(150))
    r_delivery_method = db.Column(db.String(50))
    r_comment = db.Column(db.Text)
    r_reference_range = db.Column(db.String(150))
    p_id = db.Column(db.Integer, db.ForeignKey('patients.p_id'))
    d_id = db.Column(db.Integer, db.ForeignKey('doctors.d_id'))
    t_id = db.Column(db.Integer, db.ForeignKey('tests.t_id'))

class Payment(db.Model):
    __tablename__ = 'payments'
    pm_id = db.Column(db.Integer, primary_key=True)
    pm_date = db.Column(db.Date)
    pm_method = db.Column(db.String(50))
    pm_discount = db.Column(db.Numeric(10, 2))
    pm_amount = db.Column(db.Numeric(10, 2))
    p_id = db.Column(db.Integer, db.ForeignKey('patients.p_id'))
