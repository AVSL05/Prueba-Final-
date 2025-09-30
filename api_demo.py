

import json
import time

def print_header(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def print_step(step, description):
    print(f"\n{step}. {description}")
    print("-" * 50)

def print_curl_command(method, url, headers=None, data=None):
    cmd = f"curl -X {method} {url}"
    
    if headers:
        for key, value in headers.items():
            cmd += f' \\\n  -H "{key}: {value}"'
    
    if data:
        cmd += f' \\\n  -d \'{json.dumps(data, indent=2)}\''
    
    print(f"\nComando curl equivalente:")
    print(cmd)

def demo_api_usage():
    
    print_header("DEMOSTRACIÓN DE LA API DE REGISTRO DE DONANTES")
    
    base_url = "http://localhost:5000"
    admin_token = None
    user_token = None
    donor_id = None
    
    print_step(1, "REGISTRO DE USUARIO REGULAR")
    
    register_data = {
        "email": "doctor@hospital.com",
        "password": "SecurePass123!",
        "role": "usuario"
    }
    
    print(f"Datos a enviar:")
    print(json.dumps(register_data, indent=2))
    
    print_curl_command("POST", f"{base_url}/api/auth/register", 
                      headers={"Content-Type": "application/json"}, 
                      data=register_data)
    
    print("\nRespuesta esperada:")
    print(json.dumps({
        "message": "Usuario registrado exitosamente",
        "user": {
            "id": 1,
            "email": "doctor@hospital.com",
            "role": "usuario",
            "is_active": True
        }
    }, indent=2))
    
    print_step(2, "LOGIN DE USUARIO REGULAR")
    
    login_data = {
        "email": "doctor@hospital.com",
        "password": "SecurePass123!"
    }
    
    print(f"Datos a enviar:")
    print(json.dumps(login_data, indent=2))
    
    print_curl_command("POST", f"{base_url}/api/auth/login",
                      headers={"Content-Type": "application/json"},
                      data=login_data)
    
    user_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.USER_TOKEN"
    
    print("\nRespuesta esperada:")
    print(json.dumps({
        "message": "Login exitoso",
        "access_token": user_token,
        "user": {
            "id": 1,
            "email": "doctor@hospital.com",
            "role": "usuario"
        }
    }, indent=2))
    
    print_step(3, "CREAR DONANTE")
    
    donor_data = {
        "first_name": "Ana",
        "last_name": "García",
        "email": "ana.garcia@email.com",
        "phone": "1234567890",
        "birth_date": "1985-03-15",
        "blood_type": "A+",
        "weight": 65,
        "medical_notes": "Sin observaciones especiales"
    }
    
    print(f"Datos del donante:")
    print(json.dumps(donor_data, indent=2))
    
    print_curl_command("POST", f"{base_url}/api/donors",
                      headers={
                          "Content-Type": "application/json",
                          "Authorization": f"Bearer {user_token}"
                      },
                      data=donor_data)
    
    donor_id = 1
    print("\nRespuesta esperada:")
    print(json.dumps({
        "message": "Donante registrado exitosamente",
        "donor": {
            "id": donor_id,
            "first_name": "Ana",
            "last_name": "García",
            "email": "ana.garcia@email.com",
            "age": 39,
            "blood_type": "A+",
            "weight": 65,
            "eligibility_status": {
                "eligible": True,
                "reason": "Elegible para donación"
            }
        }
    }, indent=2))
    
    print_step(4, "VERIFICAR ELEGIBILIDAD DE DONANTE")
    
    print_curl_command("GET", f"{base_url}/api/donors/eligibility-check/{donor_id}",
                      headers={"Authorization": f"Bearer {user_token}"})
    
    print("\nRespuesta esperada:")
    print(json.dumps({
        "message": "Verificación de elegibilidad completada",
        "donor_id": donor_id,
        "donor_name": "Ana García",
        "eligible": True,
        "reason": "Elegible para donación",
        "details": {
            "age": 39,
            "weight": 65,
            "blood_type": "A+",
            "last_donation_date": None,
            "is_marked_eligible": True
        }
    }, indent=2))
    
    print_step(5, "OBTENER LISTA DE DONANTES")
    
    print_curl_command("GET", f"{base_url}/api/donors?blood_type=A%2B&page=1&per_page=10",
                      headers={"Authorization": f"Bearer {user_token}"})
    
    print("\nRespuesta esperada:")
    print(json.dumps({
        "message": "Donantes obtenidos exitosamente",
        "donors": [
            {
                "id": 1,
                "first_name": "Ana",
                "last_name": "García",
                "blood_type": "A+",
                "eligible": True
            }
        ],
        "pagination": {
            "page": 1,
            "pages": 1,
            "per_page": 10,
            "total": 1
        }
    }, indent=2))
    
    print_step(6, "ACTUALIZAR DONANTE")
    
    update_data = {
        "weight": 67,
        "medical_notes": "Actualizado: donante en excelente estado de salud"
    }
    
    print(f"Datos de actualización:")
    print(json.dumps(update_data, indent=2))
    
    print_curl_command("PUT", f"{base_url}/api/donors/{donor_id}",
                      headers={
                          "Content-Type": "application/json",
                          "Authorization": f"Bearer {user_token}"
                      },
                      data=update_data)
    
    print_step(7, "LOGIN COMO ADMINISTRADOR")
    
    admin_login_data = {
        "email": "admin@example.com",
        "password": "Admin123!"
    }
    
    print(f"Credenciales de administrador:")
    print(json.dumps(admin_login_data, indent=2))
    
    print_curl_command("POST", f"{base_url}/api/auth/login",
                      headers={"Content-Type": "application/json"},
                      data=admin_login_data)
    
    admin_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.ADMIN_TOKEN"
    
    print("\nRespuesta esperada:")
    print(json.dumps({
        "message": "Login exitoso",
        "access_token": admin_token,
        "user": {
            "id": 1,
            "email": "admin@example.com",
            "role": "administrador"
        }
    }, indent=2))
    
    print_step(8, "OBTENER ESTADÍSTICAS (Solo Administradores)")
    
    print_curl_command("GET", f"{base_url}/api/donors/statistics",
                      headers={"Authorization": f"Bearer {admin_token}"})
    
    print("\nRespuesta esperada:")
    print(json.dumps({
        "message": "Estadísticas obtenidas exitosamente",
        "statistics": {
            "total_donors": 5,
            "eligible_donors": 4,
            "ineligible_donors": 1,
            "eligibility_rate": 80.0,
            "blood_type_distribution": {
                "A+": 2,
                "A-": 1,
                "B+": 1,
                "O+": 1,
                "O-": 0,
                "AB+": 0,
                "AB-": 0,
                "B-": 0
            },
            "age_distribution": {
                "16-25": 1,
                "26-35": 2,
                "36-45": 1,
                "46-55": 1,
                "56-65": 0,
                "66+": 0
            }
        }
    }, indent=2))
    
    print_step(9, "OBTENER TODOS LOS USUARIOS (Solo Administradores)")
    
    print_curl_command("GET", f"{base_url}/api/auth/users",
                      headers={"Authorization": f"Bearer {admin_token}"})
    
    print("\nRespuesta esperada:")
    print(json.dumps({
        "message": "Usuarios obtenidos exitosamente",
        "users": [
            {
                "id": 1,
                "email": "admin@example.com",
                "role": "administrador",
                "is_active": True
            },
            {
                "id": 2,
                "email": "doctor@hospital.com",
                "role": "usuario",
                "is_active": True
            }
        ],
        "total": 2
    }, indent=2))
    
    print_step(10, "EJEMPLOS DE VALIDACIONES Y ERRORES")
    
    print("\n10.1 Intento de crear donante con datos inválidos:")
    invalid_donor = {
        "first_name": "A",  # Muy corto
        "email": "email-invalido",
        "birth_date": "2010-01-01",  # Muy joven
        "weight": 30  # Muy bajo
    }
    
    print(json.dumps(invalid_donor, indent=2))
    
    print("\nRespuesta esperada:")
    print(json.dumps({
        "message": "Errores de validación",
        "errors": [
            "first_name debe tener al menos 2 caracteres",
            "Formato de email inválido",
            "El donante debe tener al menos 16 años",
            "El peso mínimo es 45 kg",
            "El campo last_name es requerido",
            "El campo blood_type es requerido"
        ]
    }, indent=2))
    
    print("\n10.2 Intento de acceso sin autorización:")
    print("GET /api/donors/statistics (sin token)")
    
    print("\nRespuesta esperada:")
    print(json.dumps({
        "message": "Token de autorización requerido"
    }, indent=2))
    
    print("\n10.3 Intento de acceso con rol insuficiente:")
    print("GET /api/donors/statistics (token de usuario regular)")
    
    print("\nRespuesta esperada:")
    print(json.dumps({
        "message": "Acceso denegado. Se requieren permisos de administrador"
    }, indent=2))
    
    print_header("INSTRUCCIONES PARA EJECUTAR LA API")
    
    print("""
Para probar la API completa:

1. Iniciar el servidor:
   python registro.py

2. La API estará disponible en: http://localhost:5000

3. Endpoints disponibles:
   - POST /api/auth/register - Registrar usuario
   - POST /api/auth/login - Iniciar sesión
   - GET /api/auth/profile - Obtener perfil
   - GET /api/auth/users - Listar usuarios (admin)
   
   - POST /api/donors - Crear donante
   - GET /api/donors - Listar donantes
   - GET /api/donors/{id} - Obtener donante
   - PUT /api/donors/{id} - Actualizar donante
   - DELETE /api/donors/{id} - Eliminar donante
   - GET /api/donors/eligibility-check/{id} - Verificar elegibilidad
   - GET /api/donors/statistics - Estadísticas (admin)

4. Usuario administrador por defecto:
   Email: admin@example.com
   Contraseña: Admin123!

5. Todos los endpoints requieren autenticación JWT excepto register y login

6. Los headers deben incluir:
   Content-Type: application/json
   Authorization: Bearer <token>
""")
    
    print_header("VALIDACIONES IMPLEMENTADAS")
    
    validations = [
        "Autenticación JWT con expiración de 24 horas",
        "Contraseñas hasheadas con Werkzeug",
        "Validación de formato de email",
        "Control de roles (administrador/usuario)",
        "Validación de datos de donante (nombres, edad, peso, tipo sangre)",
        "Verificación de elegibilidad para donación",
        "Control de intervalos entre donaciones (8 semanas mínimo)",
        "Límites de edad (18-65 años para donar, 16-70 para registrar)",
        "Peso mínimo para donación (50kg)",
        "Unicidad de emails para usuarios y donantes",
        "Paginación en listados",
        "Filtros por tipo de sangre y elegibilidad",
        "Sanitización de datos de entrada",
        "Manejo de errores con códigos HTTP apropiados"
    ]
    
    for i, validation in enumerate(validations, 1):
        print(f"{i:2d}. ✓ {validation}")

if __name__ == "__main__":
    demo_api_usage()