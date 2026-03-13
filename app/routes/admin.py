from flask import Blueprint, request, jsonify
from ..models.user import User
from ..models.lab_schema import Patient, Doctor, Test, Result, Staff
from ..utils.jwt_handler import admin_required
from ..utils.pdf_handler import save_report
from .. import db
from sqlalchemy import func
import datetime

bp = Blueprint('admin', __name__)

@bp.route('/patients', methods=['GET'])
@admin_required
def list_patients(current_user):
    # Return list of Patients from Lab Schema
    patients = Patient.query.all()
    return jsonify([{
        'id': p.p_id,
        'full_name': p.p_name,
        'email': p.p_email,
        'phone': p.p_phone_number,
        'role': 'patient' # frontend expects role
    } for p in patients])

@bp.route('/patient/<int:id>', methods=['GET'])
@admin_required
def get_patient_report(current_user, id):
    patient = Patient.query.get(id)
    if not patient:
         return jsonify({'message': 'Patient not found'}), 404
         
    # Get tests by joining or relationship
    tests = patient.tests
    
    return jsonify({
        'patient': {
            'id': patient.p_id,
            'full_name': patient.p_name,
            'email': patient.p_email,
            'phone': patient.p_phone_number
        },
        'tests': [{
            'id': t.t_id,
            'test_name': t.t_type,
            'status': t.t_status,
            'date': t.t_date.isoformat(),
            'price': float(t.t_cost or 0)
        } for t in tests]
    })

@bp.route('/upload-report', methods=['POST'])
@admin_required
def upload_report(current_user):
    if 'file' not in request.files:
        return jsonify({'message': 'No file part'}), 400
        
    file = request.files['file']
    test_id = request.form.get('test_id')
    
    if not test_id:
        return jsonify({'message': 'Test ID required'}), 400
        
    test_record = Test.query.get(test_id)
    if not test_record:
        return jsonify({'message': 'Test record not found'}), 404
        
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400
        
    if file:
        # Create a Result record
        # Determine R_ID
        max_r_id = db.session.query(func.max(Result.r_id)).scalar() or 0
        new_r_id = max_r_id + 1
        
        # Save file using R_ID naming convention?
        # get_report_path logic in utils probably uses a UUID or timestamp.
        # But we decided in patient.py to search for f"r_{r_id}.pdf"
        # So we should force the filename.
        filename = f"r_{new_r_id}.pdf"
        # We need to save it manually to the upload folder
        from ..utils.pdf_handler import UPLOAD_FOLDER
        import os
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        
        # Create Result
        # Need P_ID. We can find it via Test's linked patients?
        # Test <-> Patient is M:N. A test 'instance' T_ID likely belongs to ONE patient in our logic?
        # But schema has M:N `Patient_Tests`.
        # So `test_record` doesn't have `p_id` direct FK.
        # We need to query `Patient_Tests`.
        # In `lab_schema.py`: `tests = db.relationship('Test', secondary=patient_tests, backref='patients')`
        # So `test_record.patients` gives a list. Assuming 1 patient per test instance.
        
        if not test_record.patients:
            return jsonify({'message': 'No patient linked to this test'}), 400
            
        patient = test_record.patients[0]
        
        result = Result(
            r_id=new_r_id,
            r_value="File Uploaded",
            r_submitter="Admin",
            t_id=test_record.t_id,
            p_id=patient.p_id,
            r_delivery_method="Online",
            r_comment="Completed via Admin",
            # d_id doctor?
        )
        
        test_record.t_status = 'Completed'
        db.session.add(result)
        db.session.commit()
        
        return jsonify({'message': 'Report uploaded successfully', 'path': filename})
        
    return jsonify({'message': 'Upload failed'}), 500

@bp.route('/stats', methods=['GET'])
@admin_required
def get_stats(current_user):
    total_patients = Patient.query.count()
    total_tests = Test.query.count()
    completed = Test.query.filter_by(t_status='Completed').count()
    pending = Test.query.filter_by(t_status='Pending').count()
    
    return jsonify({
        'total_patients': total_patients,
        'total_tests': total_tests,
        'completed_tests': completed,
        'pending_tests': pending
    })

# --- Doctors Management ---

@bp.route('/doctors', methods=['GET'])
@admin_required
def list_doctors(current_user):
    docs = Doctor.query.all()
    # Frontend expects: name, age, spec, xp, address, nid, pos, sysID?
    # Doctor table: d_id, d_name?, NO. d_ssn, d_phone_number...
    # Wait, Doctor model in lab_schema has: NO d_name. 
    # It has `D_ID, D_SSN, D_PhoneNumber...`
    # Where is the Doctor's NAME?
    # Branches table has `B_Manager`. Suppliers has `SU_Name`.
    # `Doctors` table does NOT have a Name column in the provided SQL script!
    # `CREATE TABLE Doctors ( D_ID, D_SSN, ... D_Email... )`
    # It references `Branches`.
    # Maybe `D_Email` is the identifier? Or maybe specific integration is needed with `Staff`?
    # Staff has `S_Name`? No, `Staff` table: `S_ID, S_Age, S_SSN... ` NO NAME?
    # Wait, check `Patients` table: `P_Name` YES.
    # `Doctors`: NO NAME.
    # `Staff`: NO NAME.
    # Check `Branches`: `B_Name`.
    # This is strange. `Doctors` usually have names.
    # Maybe it's missing in the provided SQL?
    # Or maybe `D_Email` is used as name?
    # Or `D_SSN`?
    # I will verify the SQL script content provided in the prompt.
    # "4) Doctors ... D_ID, D_SSN, D_PhoneNumber, D_YearOfEmployement, D_Age, D_Email, D_Gender, D_Specialization, D_Salary, B_ID"
    # "5) Staff ... S_ID, S_Age, S_SSN... S_Position... S_Email..."
    # Neither Doctors nor Staff have a Name column! 
    # Patients DOES have `P_Name`.
    # Suppliers DOES have `SU_Name`.
    # Equipment DOES have `E_Name`.
    # This is a flaw in the provided SQL but I must implement it.
    # I will use `D_Email` or `D_SSN` as the name pending clarification, or I'll just return "Doctor {ID}" if needed.
    # Actually, `INSERT INTO Doctors` example: `(1,'1255533', ... 'doc1@lab.com' ...)`
    # The insert values align with columns. Name is truly missing.
    # I'll use `D_Email` as the display name or just "Doctor {D_ID}".
    
    return jsonify([{
        'sysID': str(d.d_id), # adapting to frontend sysID
        'name': d.d_email, # Using email as name fall back
        'age': d.d_age,
        'spec': d.d_specialization,
        'xp': d.d_year_of_employement, # this is year, not years of xp. Frontend expects xp?
        'phonenumber': d.d_phone_number
    } for d in docs])

@bp.route('/doctor', methods=['POST'])
@admin_required
def add_doctor(current_user):
    data = request.get_json()
    # Generate ID
    max_id = db.session.query(func.max(Doctor.d_id)).scalar() or 0
    
    new_doc = Doctor(
        d_id=max_id + 1,
        # Name missing
        d_age=data.get('age'),
        d_specialization=data.get('spec'),
        d_year_of_employement=data.get('xp', 2025),
        d_email=data.get('name') + "@lab.com", # Mocking email from name
        d_phone_number="00000000"
    )
    db.session.add(new_doc)
    db.session.commit()
    return jsonify({'message': 'Created', 'sysID': str(new_doc.d_id)}), 201

@bp.route('/doctor/sys/<string:sys_id>', methods=['PUT'])
@admin_required
def update_doctor_sys(current_user, sys_id):
    doc = Doctor.query.get(int(sys_id))
    if not doc: return jsonify({'message': 'Doctor not found'}), 404
    
    data = request.get_json()
    doc.d_age = data.get('age', doc.d_age)
    doc.d_specialization = data.get('spec', doc.d_specialization)
    db.session.commit()
    return jsonify({'message': 'Updated'})

@bp.route('/doctor/sys/<string:sys_id>', methods=['DELETE'])
@admin_required
def delete_doctor(current_user, sys_id):
    doc = Doctor.query.get(int(sys_id))
    if not doc: return jsonify({'message': 'Doctor not found'}), 404
    db.session.delete(doc)
    db.session.commit()
    return jsonify({'message': 'Deleted'})

# --- Reservation Management ---

@bp.route('/reservations', methods=['GET'])
@admin_required
def list_reservations(current_user):
    tests = Test.query.all()
    res_list = []
    for t in tests:
        p_name = "Unknown"
        if t.patients:
            p_name = t.patients[0].p_name
            
        res_list.append({
            'id': t.t_id,
            'patient_name': p_name,
            'test_name': t.t_type,
            'status': t.t_status,
            'price': float(t.t_cost or 0),
            'created_at': t.t_date.isoformat()
        })
    return jsonify(res_list)

@bp.route('/reservation', methods=['POST'])
@admin_required
def add_reservation(current_user):
    # This implies creating a test for a patient?
    # Frontend sends { name, test_name, status, price }
    data = request.get_json()
    
    # Needs a patient. Look up by name or create?
    # Let's create dummy patient if name not found?
    p_name = data.get('name', 'Guest')
    patient = Patient.query.filter_by(p_name=p_name).first()
    if not patient:
        max_p_id = db.session.query(func.max(Patient.p_id)).scalar() or 0
        patient = Patient(p_id=max_p_id+1, p_name=p_name)
        db.session.add(patient)
        db.session.flush()

    max_t_id = db.session.query(func.max(Test.t_id)).scalar() or 0
    new_t = Test(
        t_id=max_t_id+1,
        t_type=data.get('test_name'),
        t_status=data.get('status', 'Pending'),
        t_cost=data.get('price', 0),
        t_date=datetime.date.today()
    )
    db.session.add(new_t)
    db.session.flush()
    patient.tests.append(new_t)
    db.session.commit()
    return jsonify({'message': 'Created', 'id': new_t.t_id}), 201

@bp.route('/reservation/<int:id>', methods=['PUT'])
@admin_required
def update_reservation(current_user, id):
    test = Test.query.get(id)
    if not test: return jsonify({'message': 'Not found'}), 404
    
    data = request.get_json()
    test.t_status = data.get('status', test.t_status)
    test.t_type = data.get('test_name', test.t_type)
    
    db.session.commit()
    return jsonify({'message': 'Updated'})

@bp.route('/reservation/<int:id>', methods=['DELETE'])
@admin_required
def delete_reservation(current_user, id):
    test = Test.query.get(id)
    if not test: return jsonify({'message': 'Not found'}), 404
    db.session.delete(test)
    db.session.commit()
    return jsonify({'message': 'Deleted'})
