import pytest
import json
from datetime import date, timedelta
from app import create_app
from app.models import db, User, Donor, UserRole, BloodType

@pytest.fixture
def app():
    """Fixture de la aplicación Flask para pruebas"""
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    """Cliente de prueba"""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Runner de comandos"""
    return app.test_cli_runner()

@pytest.fixture
def admin_user(app):
    """Usuario administrador para pruebas"""
    with app.app_context():
        user = User(email='admin@test.com', role=UserRole.ADMIN)
        user.set_password('Admin123!')
        db.session.add(user)
        db.session.commit()
        return user

@pytest.fixture
def regular_user(app):
    """Usuario regular para pruebas"""
    with app.app_context():
        user = User(email='user@test.com', role=UserRole.USER)
        user.set_password('User123!')
        db.session.add(user)
        db.session.commit()
        return user

@pytest.fixture
def admin_token(client, admin_user):
    """Token JWT para usuario administrador"""
    response = client.post('/api/auth/login', json={
        'email': 'admin@test.com',
        'password': 'Admin123!'
    })
    return json.loads(response.data)['access_token']

@pytest.fixture
def user_token(client, regular_user):
    """Token JWT para usuario regular"""
    response = client.post('/api/auth/login', json={
        'email': 'user@test.com',
        'password': 'User123!'
    })
    return json.loads(response.data)['access_token']

@pytest.fixture
def sample_donor_data():
    """Datos de ejemplo para crear un donante"""
    return {
        'first_name': 'Juan',
        'last_name': 'Pérez',
        'email': 'juan.perez@test.com',
        'phone': '1234567890',
        'birth_date': '1990-01-01',
        'blood_type': 'O+',
        'weight': 70.5,
        'is_eligible': True,
        'medical_notes': 'Sin observaciones'
    }

class TestAuthRoutes:
    """Pruebas para las rutas de autenticación"""
    
    def test_register_user_success(self, client):
        """Prueba registro exitoso de usuario"""
        response = client.post('/api/auth/register', json={
            'email': 'nuevo@test.com',
            'password': 'Password123!',
            'role': 'usuario'
        })
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['message'] == 'Usuario registrado exitosamente'
        assert data['user']['email'] == 'nuevo@test.com'
        assert data['user']['role'] == 'usuario'
    
    def test_register_user_invalid_email(self, client):
        """Prueba registro con email inválido"""
        response = client.post('/api/auth/register', json={
            'email': 'email-invalido',
            'password': 'Password123!',
            'role': 'usuario'
        })
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'email inválido' in data['message'].lower()
    
    def test_register_user_weak_password(self, client):
        """Prueba registro con contraseña débil"""
        response = client.post('/api/auth/register', json={
            'email': 'test@test.com',
            'password': '123',
            'role': 'usuario'
        })
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'contraseña' in data['message'].lower()
    
    def test_register_duplicate_email(self, client, regular_user):
        """Prueba registro con email duplicado"""
        response = client.post('/api/auth/register', json={
            'email': 'user@test.com',
            'password': 'Password123!',
            'role': 'usuario'
        })
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'ya está registrado' in data['message']
    
    def test_login_success(self, client, regular_user):
        """Prueba login exitoso"""
        response = client.post('/api/auth/login', json={
            'email': 'user@test.com',
            'password': 'User123!'
        })
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'access_token' in data
        assert data['user']['email'] == 'user@test.com'
    
    def test_login_invalid_credentials(self, client, regular_user):
        """Prueba login con credenciales inválidas"""
        response = client.post('/api/auth/login', json={
            'email': 'user@test.com',
            'password': 'wrong-password'
        })
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'contraseña incorrecta' in data['message'].lower()
    
    def test_get_profile_success(self, client, user_token):
        """Prueba obtener perfil con token válido"""
        response = client.get('/api/auth/profile', headers={
            'Authorization': f'Bearer {user_token}'
        })
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['user']['email'] == 'user@test.com'
    
    def test_get_profile_no_token(self, client):
        """Prueba obtener perfil sin token"""
        response = client.get('/api/auth/profile')
        
        assert response.status_code == 401
    
    def test_admin_get_all_users(self, client, admin_token, regular_user):
        """Prueba admin obteniendo todos los usuarios"""
        response = client.get('/api/auth/users', headers={
            'Authorization': f'Bearer {admin_token}'
        })
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['users']) >= 2  # admin + regular user
    
    def test_user_get_all_users_forbidden(self, client, user_token):
        """Prueba usuario regular intentando obtener todos los usuarios"""
        response = client.get('/api/auth/users', headers={
            'Authorization': f'Bearer {user_token}'
        })
        
        assert response.status_code == 403

class TestDonorRoutes:
    """Pruebas para las rutas de donantes"""
    
    def test_create_donor_success(self, client, user_token, sample_donor_data):
        """Prueba creación exitosa de donante"""
        response = client.post('/api/donors', 
                             json=sample_donor_data,
                             headers={'Authorization': f'Bearer {user_token}'})
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['message'] == 'Donante registrado exitosamente'
        assert data['donor']['email'] == sample_donor_data['email']
        assert data['donor']['blood_type'] == sample_donor_data['blood_type']
    
    def test_create_donor_missing_fields(self, client, user_token):
        """Prueba creación de donante con campos faltantes"""
        response = client.post('/api/donors', 
                             json={'first_name': 'Juan'},
                             headers={'Authorization': f'Bearer {user_token}'})
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'errores de validación' in data['message'].lower()
        assert len(data['errors']) > 0
    
    def test_create_donor_invalid_email(self, client, user_token, sample_donor_data):
        """Prueba creación de donante con email inválido"""
        sample_donor_data['email'] = 'email-invalido'
        response = client.post('/api/donors', 
                             json=sample_donor_data,
                             headers={'Authorization': f'Bearer {user_token}'})
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert any('email' in error.lower() for error in data['errors'])
    
    def test_create_donor_invalid_age(self, client, user_token, sample_donor_data):
        """Prueba creación de donante con edad inválida"""
        sample_donor_data['birth_date'] = '2010-01-01'  # Muy joven
        response = client.post('/api/donors', 
                             json=sample_donor_data,
                             headers={'Authorization': f'Bearer {user_token}'})
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert any('edad' in error.lower() for error in data['errors'])
    
    def test_create_donor_invalid_weight(self, client, user_token, sample_donor_data):
        """Prueba creación de donante con peso inválido"""
        sample_donor_data['weight'] = 30  # Muy bajo
        response = client.post('/api/donors', 
                             json=sample_donor_data,
                             headers={'Authorization': f'Bearer {user_token}'})
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert any('peso' in error.lower() for error in data['errors'])
    
    def test_create_donor_duplicate_email(self, client, user_token, sample_donor_data, app):
        """Prueba creación de donante con email duplicado"""
        # Crear primer donante
        with app.app_context():
            donor = Donor(
                first_name='Test',
                last_name='User',
                email=sample_donor_data['email'],
                birth_date=date(1990, 1, 1),
                blood_type=BloodType.O_POSITIVE,
                weight=70,
                created_by=1
            )
            db.session.add(donor)
            db.session.commit()
        
        # Intentar crear segundo donante con mismo email
        response = client.post('/api/donors', 
                             json=sample_donor_data,
                             headers={'Authorization': f'Bearer {user_token}'})
        
        assert response.status_code == 409
        data = json.loads(response.data)
        assert 'ya existe' in data['message'].lower()
    
    def test_get_donors_success(self, client, user_token):
        """Prueba obtener lista de donantes"""
        response = client.get('/api/donors', headers={
            'Authorization': f'Bearer {user_token}'
        })
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'donors' in data
        assert 'pagination' in data
    
    def test_get_donors_no_token(self, client):
        """Prueba obtener donantes sin token"""
        response = client.get('/api/donors')
        assert response.status_code == 401
    
    def test_get_donor_by_id(self, client, user_token, app, regular_user):
        """Prueba obtener donante específico"""
        # Crear donante
        with app.app_context():
            donor = Donor(
                first_name='Test',
                last_name='Donor',
                email='test.donor@test.com',
                birth_date=date(1990, 1, 1),
                blood_type=BloodType.O_POSITIVE,
                weight=70,
                created_by=regular_user.id
            )
            db.session.add(donor)
            db.session.commit()
            donor_id = donor.id
        
        response = client.get(f'/api/donors/{donor_id}', headers={
            'Authorization': f'Bearer {user_token}'
        })
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['donor']['email'] == 'test.donor@test.com'
    
    def test_update_donor_success(self, client, user_token, app, regular_user):
        """Prueba actualización exitosa de donante"""
        # Crear donante
        with app.app_context():
            donor = Donor(
                first_name='Test',
                last_name='Donor',
                email='test.donor@test.com',
                birth_date=date(1990, 1, 1),
                blood_type=BloodType.O_POSITIVE,
                weight=70,
                created_by=regular_user.id
            )
            db.session.add(donor)
            db.session.commit()
            donor_id = donor.id
        
        update_data = {'first_name': 'Updated', 'weight': 75}
        response = client.put(f'/api/donors/{donor_id}', 
                            json=update_data,
                            headers={'Authorization': f'Bearer {user_token}'})
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['donor']['first_name'] == 'Updated'
        assert data['donor']['weight'] == 75
    
    def test_delete_donor_success(self, client, user_token, app, regular_user):
        """Prueba eliminación exitosa de donante"""
        # Crear donante
        with app.app_context():
            donor = Donor(
                first_name='Test',
                last_name='Donor',
                email='test.donor@test.com',
                birth_date=date(1990, 1, 1),
                blood_type=BloodType.O_POSITIVE,
                weight=70,
                created_by=regular_user.id
            )
            db.session.add(donor)
            db.session.commit()
            donor_id = donor.id
        
        response = client.delete(f'/api/donors/{donor_id}', headers={
            'Authorization': f'Bearer {user_token}'
        })
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'eliminado exitosamente' in data['message']
    
    def test_check_donor_eligibility(self, client, user_token, app, regular_user):
        """Prueba verificación de elegibilidad de donante"""
        # Crear donante elegible
        with app.app_context():
            donor = Donor(
                first_name='Eligible',
                last_name='Donor',
                email='eligible@test.com',
                birth_date=date(1990, 1, 1),
                blood_type=BloodType.O_POSITIVE,
                weight=70,
                is_eligible=True,
                created_by=regular_user.id
            )
            db.session.add(donor)
            db.session.commit()
            donor_id = donor.id
        
        response = client.get(f'/api/donors/eligibility-check/{donor_id}', headers={
            'Authorization': f'Bearer {user_token}'
        })
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'eligible' in data
        assert 'reason' in data
    
    def test_donor_statistics_admin_only(self, client, admin_token, user_token):
        """Prueba que las estadísticas solo son accesibles para admins"""
        # Admin puede acceder
        response = client.get('/api/donors/statistics', headers={
            'Authorization': f'Bearer {admin_token}'
        })
        assert response.status_code == 200
        
        # Usuario regular no puede acceder
        response = client.get('/api/donors/statistics', headers={
            'Authorization': f'Bearer {user_token}'
        })
        assert response.status_code == 403

class TestModels:
    """Pruebas para los modelos de datos"""
    
    def test_user_password_hashing(self, app):
        """Prueba el hash de contraseñas"""
        with app.app_context():
            user = User(email='test@test.com')
            user.set_password('password123')
            
            assert user.password_hash != 'password123'
            assert user.check_password('password123')
            assert not user.check_password('wrong-password')
    
    def test_user_role_admin_check(self, app):
        """Prueba verificación de rol de administrador"""
        with app.app_context():
            admin = User(email='admin@test.com', role=UserRole.ADMIN)
            user = User(email='user@test.com', role=UserRole.USER)
            
            assert admin.is_admin()
            assert not user.is_admin()
    
    def test_donor_age_calculation(self, app):
        """Prueba cálculo de edad del donante"""
        with app.app_context():
            birth_date = date(1990, 1, 1)
            donor = Donor(
                first_name='Test',
                last_name='Donor',
                email='test@test.com',
                birth_date=birth_date,
                blood_type=BloodType.O_POSITIVE,
                weight=70,
                created_by=1
            )
            
            age = donor.get_age()
            expected_age = date.today().year - 1990
            assert age == expected_age or age == expected_age - 1  # Dependiendo del día
    
    def test_donor_eligibility_age_limits(self, app):
        """Prueba límites de edad para elegibilidad"""
        with app.app_context():
            # Donante muy joven (17 años)
            young_donor = Donor(
                first_name='Young',
                last_name='Donor',
                email='young@test.com',
                birth_date=date.today() - timedelta(days=17*365),
                blood_type=BloodType.O_POSITIVE,
                weight=70,
                created_by=1
            )
            
            eligible, reason = young_donor.is_eligible_for_donation()
            assert not eligible
            assert 'edad' in reason.lower()
    
    def test_donor_eligibility_weight_limit(self, app):
        """Prueba límite de peso para elegibilidad"""
        with app.app_context():
            low_weight_donor = Donor(
                first_name='Light',
                last_name='Donor',
                email='light@test.com',
                birth_date=date(1990, 1, 1),
                blood_type=BloodType.O_POSITIVE,
                weight=45,  # Bajo el límite
                created_by=1
            )
            
            eligible, reason = low_weight_donor.is_eligible_for_donation()
            assert not eligible
            assert 'peso' in reason.lower()
    
    def test_donor_eligibility_recent_donation(self, app):
        """Prueba elegibilidad con donación reciente"""
        with app.app_context():
            recent_donor = Donor(
                first_name='Recent',
                last_name='Donor',
                email='recent@test.com',
                birth_date=date(1990, 1, 1),
                blood_type=BloodType.O_POSITIVE,
                weight=70,
                last_donation_date=date.today() - timedelta(days=30),  # Hace 30 días
                created_by=1
            )
            
            eligible, reason = recent_donor.is_eligible_for_donation()
            assert not eligible
            assert 'esperar' in reason.lower()

class TestUtilities:
    """Pruebas para utilidades y funciones auxiliares"""
    
    def test_password_validation(self):
        """Prueba validación de contraseñas"""
        from app.utils.auth import AuthUtils
        
        # Contraseña válida
        valid, msg = AuthUtils.validate_password('Password123!')
        assert valid
        
        # Contraseña muy corta
        valid, msg = AuthUtils.validate_password('P1!')
        assert not valid
        assert 'caracteres' in msg
        
        # Sin mayúscula
        valid, msg = AuthUtils.validate_password('password123!')
        assert not valid
        assert 'mayúscula' in msg
        
        # Sin minúscula
        valid, msg = AuthUtils.validate_password('PASSWORD123!')
        assert not valid
        assert 'minúscula' in msg
        
        # Sin número
        valid, msg = AuthUtils.validate_password('Password!')
        assert not valid
        assert 'número' in msg