from flask import Blueprint, request, jsonify
from app.database import db
from app.models import User
from app import bcrypt
from flask_jwt_extended import create_access_token, get_jwt_identity
import validators

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')
users = {}  

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email', '').lower().strip()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400

    if not validators.email(email):
        return jsonify({'error': 'Invalid email'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 409

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email', '').lower().strip()
    password = data.get('password', '')

    user = User.query.filter_by(email=email).first()
    if not user or not bcrypt.check_password_hash(user.password, password):
        return jsonify({'error': 'Invalid email or password'}), 401
    
    identity_value = user.email  # kesin string olması için
    print("Using identity:", identity_value)
    
    access_token = create_access_token(identity=str(user.id))  # identity artık string

    return jsonify({'token': access_token}), 200

