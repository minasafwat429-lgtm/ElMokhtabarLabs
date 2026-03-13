from flask import Blueprint, request, jsonify
from ..models.user import User
from ..utils.jwt_handler import generate_token
from .. import db

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Missing email or password'}), 400
        
    user = User.query.filter_by(email=data.get('email')).first()
    
    if not user or not user.check_password(data.get('password')):
        return jsonify({'message': 'Invalid credentials'}), 401
        
    token = generate_token(user.id, user.role)
    
    return jsonify({
        'token': token,
        'user': user.to_dict()
    })

@bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        if User.query.filter_by(email=data.get('email')).first():
            return jsonify({'message': 'البريد الإلكتروني مستخدم بالفعل'}), 400
            
        new_user = User(
            full_name=data.get('full_name'),
            email=data.get('email'),
            phone=data.get('phone'),
            role=data.get('role', 'patient')
        )
        new_user.set_password(data.get('password'))
        
        db.session.add(new_user)
        db.session.flush() # Generate User ID
        
        if new_user.role == 'patient':
            from ..models.lab_schema import Patient
            
            # Simple ID generation strategy for Patient table
            max_id = db.session.query(db.func.max(Patient.p_id)).scalar() or 0
            new_patient_id = max_id + 1
            
            new_patient = Patient(
                p_id=new_patient_id,
                p_email=new_user.email,
                p_name=new_user.full_name,
                p_phone_number=new_user.phone
            )
            
            db.session.add(new_patient)

        db.session.commit()
        
        # Auto-login: Generate token
        token = generate_token(new_user.id, new_user.role)
        
        return jsonify({
            'message': 'تم إنشاء الحساب بنجاح',
            'token': token,
            'user': new_user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Registration Error: {e}")
        return jsonify({'message': 'حدث خطأ أثناء إنشاء الحساب. الرجاء المحاولة مرة أخرى.'}), 500
