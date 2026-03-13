from flask import Blueprint, request, jsonify
from ..models.test_catalog import TestCatalog
from ..utils.jwt_handler import admin_required
from .. import db

bp = Blueprint('tests', __name__)

@bp.route('/all', methods=['GET'])
def get_all_tests():
    tests = TestCatalog.query.all()
    return jsonify([test.to_dict() for test in tests])

@bp.route('/add', methods=['POST'])
@admin_required
def add_test(current_user):
    data = request.get_json()
    
    new_test = TestCatalog(
        name=data.get('name'),
        category=data.get('category'),
        description=data.get('description'),
        price=data.get('price')
    )
    
    db.session.add(new_test)
    db.session.commit()
    
    return jsonify(new_test.to_dict()), 201

@bp.route('/<int:id>', methods=['PUT'])
@admin_required
def update_test(current_user, id):
    test = TestCatalog.query.get(id)
    if not test:
        return jsonify({'message': 'Test not found'}), 404
        
    data = request.get_json()
    
    test.name = data.get('name', test.name)
    test.category = data.get('category', test.category)
    test.description = data.get('description', test.description)
    if data.get('price'):
        test.price = data.get('price')
        
    db.session.commit()
    return jsonify(test.to_dict())

@bp.route('/<int:id>', methods=['DELETE'])
@admin_required
def delete_test(current_user, id):
    test = TestCatalog.query.get(id)
    if not test:
        return jsonify({'message': 'Test not found'}), 404
        
    db.session.delete(test)
    db.session.commit()
    return jsonify({'message': 'Test deleted'})
