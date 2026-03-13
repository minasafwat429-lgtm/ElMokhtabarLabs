
from flask import Blueprint, request, jsonify, send_file
from ..models.user import User
from ..models.lab_schema import Patient, Test, Result, Patient_Tests, patient_tests
from ..utils.jwt_handler import token_required
from ..utils.pdf_handler import get_report_path
from .. import db
import datetime
from sqlalchemy import func

bp = Blueprint('patient', __name__)

@bp.route('/book', methods=['POST'])
@token_required
def book_test(current_user):
    data = request.get_json()
    
    if not data.get('test_name'):
        return jsonify({'message': 'Test name is required'}), 400
        
    # Find linked Patient record
    # We assume syncing happened at register, but we fallback to email lookup
    patient = Patient.query.filter_by(p_email=current_user.email).first()
    
    if not patient:
        # Should not happen if registered correctly, but handle legacy
        return jsonify({'message': 'Patient record not found. Please contact support.'}), 404

    # Generate T_ID (assuming manual for now as per schema script potentially not being auto-inc)
    max_id = db.session.query(func.max(Test.t_id)).scalar() or 0
    new_t_id = max_id + 1
    
    # Create Test
    new_test = Test(
        t_id=new_t_id,
        t_type=data.get('test_name'),
        t_date=datetime.date.today(),
        t_cost=data.get('price', 0), # Frontend should send price or we lookup
        t_status='Pending',
        t_pre_test=data.get('pre_test', 'No special instructions')
    )
    
    db.session.add(new_test)
    db.session.flush() # Ensure t_id is available
    
    # Link Patient to Test (Many-to-Many)
    # Using the ORM relationship 'tests' on Patient model
    patient.tests.append(new_test)
    
    db.session.commit()
    
    return jsonify({
        'message': 'Booking successful', 
        'booking': {
            'id': new_test.t_id,
            'test_name': new_test.t_type,
            'date': new_test.t_date.isoformat(),
            'status': new_test.t_status
        }
    }), 201

@bp.route('/results/<int:id>', methods=['GET'])
@token_required
def get_results(current_user, id):
    # 'id' here is likely User ID or Patient ID? 
    # Frontend sends User ID usually.
    if current_user.id != id:
        return jsonify({'message': 'Unauthorized'}), 401
    
    patient = Patient.query.filter_by(p_email=current_user.email).first()
    if not patient:
         return jsonify([])

    # Fetch Results
    # We can use the relationship patient.results
    results = patient.results
    
    return jsonify([{
        'id': r.r_id,
        'test_name': r.test.t_type if r.test else 'Unknown',
        'value': r.r_value,
        'comment': r.r_comment,
        'status': 'Completed', # if result exists
        'date': r.test.t_date.isoformat() if r.test else None,
        'report_available': True # verify file exists?
    } for r in results])

@bp.route('/download/<int:result_id>', methods=['GET'])
@token_required
def download_report(current_user, result_id):
    # result_id matches R_ID
    result = Result.query.get(result_id)
    
    if not result:
        return jsonify({'message': 'Report not found'}), 404
        
    # Check ownership
    patient = Patient.query.filter_by(p_email=current_user.email).first()
    if not patient or result.p_id != patient.p_id:
         return jsonify({'message': 'Unauthorized'}), 401
         
    # File naming convention: r_{R_ID}.pdf or t_{T_ID}.pdf?
    # Let's say we save as r_{R_ID}.pdf
    filename = f"r_{result.r_id}.pdf"
    
    try:
        path = get_report_path(filename)
        return send_file(path, as_attachment=True)
    except Exception as e:
        return jsonify({'message': 'File not generated or found'}), 404

@bp.route('/results/search', methods=['POST'])
def search_results():
    data = request.get_json()
    p_id = data.get('id') # Patient ID (P_ID)
    phone = data.get('phone')
    
    if not p_id: 
        return jsonify({'message': 'ID required'}), 400
        
    # Search Patient table directly
    patient = Patient.query.filter_by(p_id=p_id).first()
    
    if patient and patient.p_phone_number == phone:
         results = patient.results
         return jsonify([{
            'id': r.r_id,
            'test_name': r.test.t_type if r.test else 'Unknown',
            'value': r.r_value,
            'status': 'Completed',
            'date': r.test.t_date.isoformat() if r.test else None
         } for r in results])
    
    return jsonify({'message': 'No records found matching details'}), 404

@bp.route('/book-guest', methods=['POST'])
def book_guest():
    data = request.get_json()
    if not data.get('test_name') or not data.get('name'):
         return jsonify({'message': 'Missing data'}), 400

    # For guest, we create a Patient record? Or just a Test?
    # Schema requires P_ID in Patient_Tests? Yes, Patient_Tests(P_ID, T_ID).
    # So we MUST have a Patient record.
    # We can check if a patient with this name/phone exists or create a temp one?
    # Or search by phone?
    # Let's search by Phone.
    
    patient = None
    phone = data.get('phone')
    if phone:
        patient = Patient.query.filter_by(p_phone_number=phone).first()
        
    if not patient:
        # Create new Patient
        max_p_id = db.session.query(func.max(Patient.p_id)).scalar() or 0
        patient = Patient(
            p_id=max_p_id + 1,
            p_name=data.get('name'),
            p_phone_number=phone,
            p_email=data.get('email', 'guest@local') # Dummy email if missing
        )
        db.session.add(patient)
        db.session.flush()

    # Create Test
    max_t_id = db.session.query(func.max(Test.t_id)).scalar() or 0
    new_test = Test(
        t_id=max_t_id + 1,
        t_type=data.get('test_name'),
        t_date=datetime.date.today(),
        t_cost=data.get('price', 0),
        t_status='Pending'
    )
    db.session.add(new_test)
    db.session.flush()
    
    # Link
    patient.tests.append(new_test)
    db.session.commit()
    
    return jsonify({
        'message': 'Booking successful', 
        'booking': {
            'id': new_test.t_id,
            'test_name': new_test.t_type,
            'patient_id': patient.p_id
        }
    }), 201

@bp.route('/public-download/<int:result_id>', methods=['GET'])
def public_download(result_id):
    # Allow public if they have the ID (insecure but matching request level)
    result = Result.query.get(result_id)
    if not result:
        return jsonify({'message': 'File not found'}), 404
        
    filename = f"r_{result.r_id}.pdf"
    try:
        path = get_report_path(filename)
        return send_file(path, as_attachment=True)
    except:
        return jsonify({'message': 'File not found'}), 404

