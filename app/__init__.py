from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from app.models import db
from app.routes.auth import auth_bp
from app.routes.donors import donors_bp
from app.routes.web import web_bp
import os
from datetime import timedelta
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def create_app(config_name='development'):
    """Factory function para crear la aplicación Flask"""
    app = Flask(__name__)
    
    # Configuración
    if config_name == 'testing':
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['TESTING'] = True
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///donors.db')
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-change-in-production')
    
    # Inicializar extensiones
    db.init_app(app)
    jwt = JWTManager(app)
    
    # Registrar blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(donors_bp)
    app.register_blueprint(web_bp)
    
    # Rutas básicas de la API
    @app.route('/api')
    def api_index():
        return jsonify({
            'message': 'API de Registro de Donantes',
            'version': '1.0',
            'endpoints': {
                'auth': '/api/auth',
                'donors': '/api/donors'
            }
        })
    
    @app.route('/health')
    def health():
        return jsonify({'status': 'OK', 'message': 'Servicio funcionando correctamente'})
    
    # Manejo de errores JWT
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({'message': 'Token expirado'}), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({'message': 'Token inválido'}), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({'message': 'Token de autorización requerido'}), 401
    
    # Crear tablas
    with app.app_context():
        db.create_all()
        
        # Crear usuario administrador por defecto si no existe
        from app.models import User, UserRole
        
        # Obtener credenciales desde variables de entorno
        admin_email = os.getenv('ADMIN_EMAIL', 'admin@example.com')
        admin_password = os.getenv('ADMIN_PASSWORD', 'Admin123!')
        
        admin_user = User.query.filter_by(email=admin_email).first()
        if not admin_user:
            admin_user = User(
                email=admin_email,
                role=UserRole.ADMIN
            )
            admin_user.set_password(admin_password)
            db.session.add(admin_user)
            db.session.commit()
            print(f"Usuario administrador creado: {admin_email}")
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)