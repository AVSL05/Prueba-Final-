from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.models import Donor, BloodType, db
from app.utils.auth import get_current_user, admin_required, check_user_permissions
from email_validator import validate_email, EmailNotValidError
from datetime import datetime, date
import re

donors_bp = Blueprint('donors', __name__, url_prefix='/api/donors')

def validate_donor_data(data, is_update=False):
    """Valida los datos del donante"""
    errors = []
    
    # Validar campos requeridos (solo para creación)
    if not is_update:
        required_fields = ['first_name', 'last_name', 'email', 'birth_date', 'blood_type', 'weight']
        for field in required_fields:
            if not data.get(field):
                errors.append(f'El campo {field} es requerido')
    
    # Validar email si está presente
    if 'email' in data and data['email']:
        try:
            validate_email(data['email'])
        except EmailNotValidError:
            errors.append('Formato de email inválido')
    
    # Validar nombres
    for field in ['first_name', 'last_name']:
        if field in data and data[field]:
            if len(data[field].strip()) < 2:
                errors.append(f'{field} debe tener al menos 2 caracteres')
            if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', data[field].strip()):
                errors.append(f'{field} solo puede contener letras y espacios')
    
    # Validar teléfono
    if 'phone' in data and data['phone']:
        phone = re.sub(r'[^\d]', '', data['phone'])
        if len(phone) < 10:
            errors.append('El teléfono debe tener al menos 10 dígitos')
    
    # Validar fecha de nacimiento
    if 'birth_date' in data and data['birth_date']:
        try:
            birth_date = datetime.strptime(data['birth_date'], '%Y-%m-%d').date()
            age = (date.today() - birth_date).days // 365
            if age < 16:
                errors.append('El donante debe tener al menos 16 años')
            if age > 70:
                errors.append('El donante no puede tener más de 70 años')
        except ValueError:
            errors.append('Formato de fecha inválido. Use YYYY-MM-DD')
    
    # Validar tipo de sangre
    if 'blood_type' in data and data['blood_type']:
        valid_blood_types = [bt.value for bt in BloodType]
        if data['blood_type'] not in valid_blood_types:
            errors.append(f'Tipo de sangre inválido. Valores válidos: {", ".join(valid_blood_types)}')
    
    # Validar peso
    if 'weight' in data and data['weight'] is not None:
        try:
            weight = float(data['weight'])
            if weight < 45:
                errors.append('El peso mínimo es 45 kg')
            if weight > 200:
                errors.append('El peso máximo es 200 kg')
        except (ValueError, TypeError):
            errors.append('El peso debe ser un número válido')
    
    # Validar fecha de última donación
    if 'last_donation_date' in data and data['last_donation_date']:
        try:
            last_donation = datetime.strptime(data['last_donation_date'], '%Y-%m-%d').date()
            if last_donation > date.today():
                errors.append('La fecha de última donación no puede ser futura')
        except ValueError:
            errors.append('Formato de fecha de última donación inválido. Use YYYY-MM-DD')
    
    return errors

@donors_bp.route('', methods=['POST'])
@jwt_required()
def create_donor():
    """Crea un nuevo donante"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'message': 'Usuario no autenticado'}), 401
        
        data = request.get_json()
        if not data:
            return jsonify({'message': 'No se proporcionaron datos'}), 400
        
        # Validar datos
        errors = validate_donor_data(data)
        if errors:
            return jsonify({'message': 'Errores de validación', 'errors': errors}), 400
        
        # Verificar si el email ya existe
        existing_donor = Donor.query.filter_by(email=data['email']).first()
        if existing_donor:
            return jsonify({'message': 'Ya existe un donante con este email'}), 409
        
        # Crear donante
        donor = Donor(
            first_name=data['first_name'].strip(),
            last_name=data['last_name'].strip(),
            email=data['email'].strip().lower(),
            phone=data.get('phone', '').strip() if data.get('phone') else None,
            birth_date=datetime.strptime(data['birth_date'], '%Y-%m-%d').date(),
            blood_type=BloodType(data['blood_type']),
            weight=float(data['weight']),
            last_donation_date=datetime.strptime(data['last_donation_date'], '%Y-%m-%d').date() if data.get('last_donation_date') else None,
            is_eligible=data.get('is_eligible', True),
            medical_notes=data.get('medical_notes', '').strip() if data.get('medical_notes') else None,
            created_by=current_user.id
        )
        
        db.session.add(donor)
        db.session.commit()
        
        return jsonify({
            'message': 'Donante registrado exitosamente',
            'donor': donor.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error interno del servidor', 'error': str(e)}), 500

@donors_bp.route('', methods=['GET'])
@jwt_required()
def get_donors():
    """Obtiene la lista de donantes con filtros opcionales"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'message': 'Usuario no autenticado'}), 401
        
        # Construir query base
        query = Donor.query
        
        # Los usuarios normales solo ven sus propios donantes
        if not current_user.is_admin():
            query = query.filter_by(created_by=current_user.id)
        
        # Aplicar filtros
        blood_type = request.args.get('blood_type')
        if blood_type:
            try:
                query = query.filter_by(blood_type=BloodType(blood_type))
            except ValueError:
                return jsonify({'message': 'Tipo de sangre inválido'}), 400
        
        is_eligible = request.args.get('is_eligible')
        if is_eligible is not None:
            query = query.filter_by(is_eligible=is_eligible.lower() == 'true')
        
        # Paginación
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)
        
        donors = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        return jsonify({
            'message': 'Donantes obtenidos exitosamente',
            'donors': [donor.to_dict() for donor in donors.items],
            'pagination': {
                'page': donors.page,
                'pages': donors.pages,
                'per_page': donors.per_page,
                'total': donors.total
            }
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Error interno del servidor', 'error': str(e)}), 500

@donors_bp.route('/<int:donor_id>', methods=['GET'])
@jwt_required()
def get_donor(donor_id):
    """Obtiene un donante específico"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'message': 'Usuario no autenticado'}), 401
        
        donor = Donor.query.get_or_404(donor_id)
        
        # Verificar permisos
        if not current_user.is_admin() and donor.created_by != current_user.id:
            return jsonify({'message': 'No tiene permisos para ver este donante'}), 403
        
        return jsonify({
            'message': 'Donante obtenido exitosamente',
            'donor': donor.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Error interno del servidor', 'error': str(e)}), 500

@donors_bp.route('/<int:donor_id>', methods=['PUT'])
@jwt_required()
def update_donor(donor_id):
    """Actualiza un donante"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'message': 'Usuario no autenticado'}), 401
        
        donor = Donor.query.get_or_404(donor_id)
        
        # Verificar permisos
        if not current_user.is_admin() and donor.created_by != current_user.id:
            return jsonify({'message': 'No tiene permisos para modificar este donante'}), 403
        
        data = request.get_json()
        if not data:
            return jsonify({'message': 'No se proporcionaron datos'}), 400
        
        # Validar datos
        errors = validate_donor_data(data, is_update=True)
        if errors:
            return jsonify({'message': 'Errores de validación', 'errors': errors}), 400
        
        # Verificar email único
        if 'email' in data:
            existing_donor = Donor.query.filter_by(email=data['email']).filter(Donor.id != donor_id).first()
            if existing_donor:
                return jsonify({'message': 'Ya existe un donante con este email'}), 409
        
        # Actualizar campos
        update_fields = [
            'first_name', 'last_name', 'email', 'phone', 'birth_date',
            'blood_type', 'weight', 'last_donation_date', 'is_eligible', 'medical_notes'
        ]
        
        for field in update_fields:
            if field in data:
                if field == 'birth_date' and data[field]:
                    setattr(donor, field, datetime.strptime(data[field], '%Y-%m-%d').date())
                elif field == 'last_donation_date' and data[field]:
                    setattr(donor, field, datetime.strptime(data[field], '%Y-%m-%d').date())
                elif field == 'blood_type' and data[field]:
                    setattr(donor, field, BloodType(data[field]))
                elif field in ['first_name', 'last_name', 'email']:
                    setattr(donor, field, data[field].strip())
                else:
                    setattr(donor, field, data[field])
        
        db.session.commit()
        
        return jsonify({
            'message': 'Donante actualizado exitosamente',
            'donor': donor.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error interno del servidor', 'error': str(e)}), 500

@donors_bp.route('/<int:donor_id>', methods=['DELETE'])
@jwt_required()
def delete_donor(donor_id):
    """Elimina un donante"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'message': 'Usuario no autenticado'}), 401
        
        donor = Donor.query.get_or_404(donor_id)
        
        # Verificar permisos (solo admin o el creador puede eliminar)
        if not current_user.is_admin() and donor.created_by != current_user.id:
            return jsonify({'message': 'No tiene permisos para eliminar este donante'}), 403
        
        db.session.delete(donor)
        db.session.commit()
        
        return jsonify({'message': 'Donante eliminado exitosamente'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error interno del servidor', 'error': str(e)}), 500

@donors_bp.route('/eligibility-check/<int:donor_id>', methods=['GET'])
@jwt_required()
def check_donor_eligibility(donor_id):
    """Verifica la elegibilidad de un donante para donar"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'message': 'Usuario no autenticado'}), 401
        
        donor = Donor.query.get_or_404(donor_id)
        
        # Verificar permisos
        if not current_user.is_admin() and donor.created_by != current_user.id:
            return jsonify({'message': 'No tiene permisos para ver este donante'}), 403
        
        eligible, reason = donor.is_eligible_for_donation()
        
        return jsonify({
            'message': 'Verificación de elegibilidad completada',
            'donor_id': donor_id,
            'donor_name': f"{donor.first_name} {donor.last_name}",
            'eligible': eligible,
            'reason': reason,
            'details': {
                'age': donor.get_age(),
                'weight': donor.weight,
                'blood_type': donor.blood_type.value,
                'last_donation_date': donor.last_donation_date.isoformat() if donor.last_donation_date else None,
                'is_marked_eligible': donor.is_eligible
            }
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Error interno del servidor', 'error': str(e)}), 500

@donors_bp.route('/statistics', methods=['GET'])
@admin_required
def get_donor_statistics():
    """Obtiene estadísticas de donantes (solo administradores)"""
    try:
        total_donors = Donor.query.count()
        eligible_donors = Donor.query.filter_by(is_eligible=True).count()
        
        # Estadísticas por tipo de sangre
        blood_type_stats = {}
        for blood_type in BloodType:
            count = Donor.query.filter_by(blood_type=blood_type).count()
            blood_type_stats[blood_type.value] = count
        
        # Donantes por rango de edad
        age_ranges = {
            '16-25': 0,
            '26-35': 0,
            '36-45': 0,
            '46-55': 0,
            '56-65': 0,
            '66+': 0
        }
        
        all_donors = Donor.query.all()
        for donor in all_donors:
            age = donor.get_age()
            if 16 <= age <= 25:
                age_ranges['16-25'] += 1
            elif 26 <= age <= 35:
                age_ranges['26-35'] += 1
            elif 36 <= age <= 45:
                age_ranges['36-45'] += 1
            elif 46 <= age <= 55:
                age_ranges['46-55'] += 1
            elif 56 <= age <= 65:
                age_ranges['56-65'] += 1
            else:
                age_ranges['66+'] += 1
        
        return jsonify({
            'message': 'Estadísticas obtenidas exitosamente',
            'statistics': {
                'total_donors': total_donors,
                'eligible_donors': eligible_donors,
                'ineligible_donors': total_donors - eligible_donors,
                'eligibility_rate': round((eligible_donors / total_donors * 100) if total_donors > 0 else 0, 2),
                'blood_type_distribution': blood_type_stats,
                'age_distribution': age_ranges
            }
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Error interno del servidor', 'error': str(e)}), 500