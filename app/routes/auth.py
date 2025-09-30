from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.models import User, UserRole, db
from app.utils.auth import AuthUtils, get_current_user, admin_required
from email_validator import validate_email, EmailNotValidError
from datetime import timedelta

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    """Registro de nuevos usuarios"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'No se proporcionaron datos'}), 400
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        role = data.get('role', 'usuario')
        
        # Validaciones básicas
        if not email or not password:
            return jsonify({'message': 'Email y contraseña son requeridos'}), 400
        
        # Validar formato de email
        try:
            validate_email(email)
        except EmailNotValidError:
            return jsonify({'message': 'Formato de email inválido'}), 400
        
        # Validar rol
        user_role = UserRole.USER
        if role == 'administrador':
            user_role = UserRole.ADMIN
        elif role not in ['usuario', 'administrador']:
            return jsonify({'message': 'Rol inválido. Use "usuario" o "administrador"'}), 400
        
        # Crear usuario
        user, message = AuthUtils.create_user(email, password, user_role)
        
        if not user:
            return jsonify({'message': message}), 400
        
        return jsonify({
            'message': 'Usuario registrado exitosamente',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'message': 'Error interno del servidor', 'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Autenticación de usuarios"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'No se proporcionaron datos'}), 400
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({'message': 'Email y contraseña son requeridos'}), 400
        
        # Autenticar usuario
        user, message = AuthUtils.authenticate_user(email, password)
        
        if not user:
            return jsonify({'message': message}), 401
        
        # Crear token JWT
        access_token = create_access_token(
            identity=user.id,
            expires_delta=timedelta(hours=24)
        )
        
        return jsonify({
            'message': 'Login exitoso',
            'access_token': access_token,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Error interno del servidor', 'error': str(e)}), 500

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Obtiene el perfil del usuario actual"""
    try:
        current_user = get_current_user()
        
        if not current_user:
            return jsonify({'message': 'Usuario no encontrado'}), 404
        
        return jsonify({
            'message': 'Perfil obtenido exitosamente',
            'user': current_user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Error interno del servidor', 'error': str(e)}), 500

@auth_bp.route('/users', methods=['GET'])
@admin_required
def get_all_users():
    """Obtiene todos los usuarios (solo administradores)"""
    try:
        users = User.query.all()
        return jsonify({
            'message': 'Usuarios obtenidos exitosamente',
            'users': [user.to_dict() for user in users],
            'total': len(users)
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Error interno del servidor', 'error': str(e)}), 500

@auth_bp.route('/users/<int:user_id>', methods=['PUT'])
@admin_required
def update_user(user_id):
    """Actualiza un usuario (solo administradores)"""
    try:
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'No se proporcionaron datos'}), 400
        
        # Actualizar campos permitidos
        if 'email' in data:
            email = data['email'].strip().lower()
            try:
                validate_email(email)
                # Verificar que el email no esté en uso por otro usuario
                existing_user = User.query.filter_by(email=email).filter(User.id != user_id).first()
                if existing_user:
                    return jsonify({'message': 'El email ya está en uso'}), 400
                user.email = email
            except EmailNotValidError:
                return jsonify({'message': 'Formato de email inválido'}), 400
        
        if 'role' in data:
            role = data['role']
            if role == 'administrador':
                user.role = UserRole.ADMIN
            elif role == 'usuario':
                user.role = UserRole.USER
            else:
                return jsonify({'message': 'Rol inválido'}), 400
        
        if 'is_active' in data:
            user.is_active = bool(data['is_active'])
        
        db.session.commit()
        
        return jsonify({
            'message': 'Usuario actualizado exitosamente',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error interno del servidor', 'error': str(e)}), 500

@auth_bp.route('/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    """Elimina un usuario (solo administradores)"""
    try:
        current_user = get_current_user()
        
        # No permitir que el admin se elimine a sí mismo
        if current_user.id == user_id:
            return jsonify({'message': 'No puede eliminar su propia cuenta'}), 400
        
        user = User.query.get_or_404(user_id)
        
        # Verificar si el usuario tiene donantes asociados
        if user.donors:
            return jsonify({
                'message': 'No se puede eliminar el usuario porque tiene donantes asociados',
                'donors_count': len(user.donors)
            }), 400
        
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({'message': 'Usuario eliminado exitosamente'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error interno del servidor', 'error': str(e)}), 500