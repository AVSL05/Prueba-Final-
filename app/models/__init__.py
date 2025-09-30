from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from enum import Enum

db = SQLAlchemy()

class UserRole(Enum):
    ADMIN = "administrador"
    USER = "usuario"

class User(db.Model):
    """Modelo de usuario con autenticación y roles"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum(UserRole), nullable=False, default=UserRole.USER)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relación con donantes
    donors = db.relationship('Donor', backref='created_by_user', lazy=True)
    
    def set_password(self, password):
        """Establece la contraseña hasheada"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verifica la contraseña"""
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        """Verifica si el usuario es administrador"""
        return self.role == UserRole.ADMIN
    
    def to_dict(self):
        """Convierte el modelo a diccionario"""
        return {
            'id': self.id,
            'email': self.email,
            'role': self.role.value,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<User {self.email}>'

class BloodType(Enum):
    A_POSITIVE = "A+"
    A_NEGATIVE = "A-"
    B_POSITIVE = "B+"
    B_NEGATIVE = "B-"
    AB_POSITIVE = "AB+"
    AB_NEGATIVE = "AB-"
    O_POSITIVE = "O+"
    O_NEGATIVE = "O-"

class Donor(db.Model):
    """Modelo de donante de sangre"""
    __tablename__ = 'donors'
    
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20), nullable=True)
    birth_date = db.Column(db.Date, nullable=False)
    blood_type = db.Column(db.Enum(BloodType), nullable=False)
    weight = db.Column(db.Float, nullable=False)  # en kg
    last_donation_date = db.Column(db.Date, nullable=True)
    is_eligible = db.Column(db.Boolean, default=True, nullable=False)
    medical_notes = db.Column(db.Text, nullable=True)
    
    # Campos de auditoría
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    def get_age(self):
        """Calcula la edad del donante"""
        today = datetime.now().date()
        return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
    
    def is_eligible_for_donation(self):
        """Verifica si el donante es elegible para donar"""
        age = self.get_age()
        
        # Criterios básicos de elegibilidad
        if not self.is_eligible:
            return False, "Donante marcado como no elegible"
        
        if age < 18 or age > 65:
            return False, "Edad fuera del rango permitido (18-65 años)"
        
        if self.weight < 50:
            return False, "Peso insuficiente (mínimo 50kg)"
        
        # Verificar última donación (mínimo 8 semanas entre donaciones)
        if self.last_donation_date:
            days_since_last = (datetime.now().date() - self.last_donation_date).days
            if days_since_last < 56:  # 8 semanas = 56 días
                return False, f"Debe esperar {56 - days_since_last} días más para donar"
        
        return True, "Elegible para donación"
    
    def to_dict(self):
        """Convierte el modelo a diccionario"""
        eligible, reason = self.is_eligible_for_donation()
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'phone': self.phone,
            'birth_date': self.birth_date.isoformat() if self.birth_date else None,
            'age': self.get_age(),
            'blood_type': self.blood_type.value,
            'weight': self.weight,
            'last_donation_date': self.last_donation_date.isoformat() if self.last_donation_date else None,
            'is_eligible': self.is_eligible,
            'medical_notes': self.medical_notes,
            'eligibility_status': {
                'eligible': eligible,
                'reason': reason
            },
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': self.created_by
        }
    
    def __repr__(self):
        return f'<Donor {self.first_name} {self.last_name}>'