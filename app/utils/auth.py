from functools import wraps
from flask import jsonify, request, current_app
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt
from app.models import User, UserRole, db
import jwt

def token_required(f):
    """Decorador que requiere un token JWT válido"""
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            verify_jwt_in_request()
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({'message': 'Token inválido o expirado', 'error': str(e)}), 401
    return decorated

def admin_required(f):
    """Decorador que requiere rol de administrador"""
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            verify_jwt_in_request()
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)
            
            if not user:
                return jsonify({'message': 'Usuario no encontrado'}), 404
            
            if not user.is_admin():
                return jsonify({'message': 'Acceso denegado. Se requieren permisos de administrador'}), 403
            
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({'message': 'Error de autenticación', 'error': str(e)}), 401
    return decorated

def role_required(required_role):
    """Decorador que requiere un rol específico"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            try:
                verify_jwt_in_request()
                current_user_id = get_jwt_identity()
                user = User.query.get(current_user_id)
                
                if not user:
                    return jsonify({'message': 'Usuario no encontrado'}), 404
                
                if user.role != required_role:
                    return jsonify({'message': f'Acceso denegado. Se requiere rol: {required_role.value}'}), 403
                
                return f(*args, **kwargs)
            except Exception as e:
                return jsonify({'message': 'Error de autenticación', 'error': str(e)}), 401
        return decorated
    return decorator

def get_current_user():
    """Obtiene el usuario actual basado en el token JWT"""
    try:
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()
        return User.query.get(current_user_id)
    except Exception:
        return None

def check_user_permissions(user_id=None, admin_only=False):
    """Verifica los permisos del usuario actual"""
    current_user = get_current_user()
    
    if not current_user:
        return False, "Usuario no autenticado"
    
    if not current_user.is_active:
        return False, "Usuario inactivo"
    
    if admin_only and not current_user.is_admin():
        return False, "Se requieren permisos de administrador"
    
    # Si se especifica un user_id, verificar que sea el mismo usuario o un admin
    if user_id and user_id != current_user.id and not current_user.is_admin():
        return False, "No tiene permisos para acceder a este recurso"
    
    return True, "Permisos válidos"

class AuthUtils:
    """Utilidades para autenticación y autorización"""
    
    @staticmethod
    def validate_password(password):
        """Valida que la contraseña cumpla con los requisitos mínimos"""
        if len(password) < 8:
            return False, "La contraseña debe tener al menos 8 caracteres"
        
        if not any(c.isupper() for c in password):
            return False, "La contraseña debe contener al menos una letra mayúscula"
        
        if not any(c.islower() for c in password):
            return False, "La contraseña debe contener al menos una letra minúscula"
        
        if not any(c.isdigit() for c in password):
            return False, "La contraseña debe contener al menos un número"
        
        return True, "Contraseña válida"
    
    @staticmethod
    def create_user(email, password, role=UserRole.USER):
        """Crea un nuevo usuario con validaciones"""
        # Verificar si el email ya existe
        if User.query.filter_by(email=email).first():
            return None, "El email ya está registrado"
        
        # Validar contraseña
        is_valid, message = AuthUtils.validate_password(password)
        if not is_valid:
            return None, message
        
        try:
            user = User(email=email, role=role)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            return user, "Usuario creado exitosamente"
        except Exception as e:
            db.session.rollback()
            return None, f"Error al crear usuario: {str(e)}"
    
    @staticmethod
    def authenticate_user(email, password):
        """Autentica un usuario y devuelve el objeto usuario si es válido"""
        user = User.query.filter_by(email=email).first()
        
        if not user:
            return None, "Usuario no encontrado"
        
        if not user.is_active:
            return None, "Usuario inactivo"
        
        if not user.check_password(password):
            return None, "Contraseña incorrecta"
        
        return user, "Autenticación exitosa"