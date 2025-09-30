# API de Registro de Donantes

## Descripción

Sistema básico de registro de personas donantes con autenticación JWT y control de acceso basado en roles. Desarrollado con Flask, SQLAlchemy y JWT.

## Características Principales

- **Autenticación JWT**: Sistema de tokens seguros para autenticación
- **Control de Roles**: Administrador y Usuario con permisos diferenciados
- **Registro de Donantes**: CRUD completo con validaciones
- **Validación de Elegibilidad**: Verificación automática para donación
- **Pruebas Unitarias**: Cobertura superior al 80%
- **API RESTful**: Endpoints bien documentados

## Arquitectura del Proyecto

```
actfinalIDS/
├── app/
│   ├── __init__.py          # Factory de la aplicación Flask
│   ├── models/
│   │   └── __init__.py      # Modelos User y Donor
│   ├── routes/
│   │   ├── auth.py          # Rutas de autenticación
│   │   └── donors.py        # Rutas de donantes
│   └── utils/
│       └── auth.py          # Utilidades de autenticación
├── tests/
│   ├── __init__.py
│   ├── test_app.py          # Pruebas principales
│   └── test_basic.py        # Pruebas básicas
├── .env                     # Variables de entorno (no subir al repo)
├── requirements.txt
├── pytest.ini
└── registro.py              # Punto de entrada
```

## ⚙️ Configuración

### Variables de Entorno

El sistema utiliza variables de entorno para configuración segura. Crea un archivo `.env` en la raíz del proyecto:

```bash
# Variables de entorno para producción
ADMIN_EMAIL=admin@papusaurio.com
ADMIN_PASSWORD=Papusaurio.123
DATABASE_URL=postgresql://user:pass@localhost/db_name
JWT_SECRET_KEY=JTWPapusaurio2024SecretKey
SECRET_KEY=Secretkeypapu
```

**Importante:** 
- Nunca subas el archivo `.env` al repositorio
- Cambia las credenciales por defecto en producción
- El archivo `.env` está incluido en `.gitignore`

## Modelos de Datos

### Usuario (User)

- **id**: Identificador único
- **email**: Email único del usuario
- **password_hash**: Contraseña hasheada
- **role**: Rol (administrador/usuario)
- **is_active**: Estado activo/inactivo
- **created_at/updated_at**: Timestamps

### Donante (Donor)

- **id**: Identificador único
- **first_name/last_name**: Nombres del donante
- **email**: Email único del donante
- **phone**: Teléfono (opcional)
- **birth_date**: Fecha de nacimiento
- **blood_type**: Tipo de sangre (A+, A-, B+, B-, AB+, AB-, O+, O-)
- **weight**: Peso en kg
- **last_donation_date**: Última fecha de donación
- **is_eligible**: Elegibilidad marcada manualmente
- **medical_notes**: Notas médicas
- **created_by**: Usuario que creó el registro

## Endpoints de la API

### Autenticación (`/api/auth`)

#### POST `/api/auth/register`

Registra un nuevo usuario.

**Body:**

```json
{
  "email": "usuario@example.com",
  "password": "Password123!",
  "role": "usuario" // o "administrador"
}
```

#### POST `/api/auth/login`

Autentica un usuario y devuelve un token JWT.

**Body:**

```json
{
  "email": "usuario@example.com",
  "password": "Password123!"
}
```

**Response:**

```json
{
  "message": "Login exitoso",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "email": "usuario@example.com",
    "role": "usuario"
  }
}
```

#### GET `/api/auth/profile`

Obtiene el perfil del usuario autenticado.

**Headers:** `Authorization: Bearer <token>`

#### GET `/api/auth/users` (Solo Administradores)

Obtiene todos los usuarios registrados.

### Donantes (`/api/donors`)

#### POST `/api/donors`

Crea un nuevo donante.

**Headers:** `Authorization: Bearer <token>`

**Body:**

```json
{
  "first_name": "Juan",
  "last_name": "Pérez",
  "email": "juan.perez@example.com",
  "phone": "1234567890",
  "birth_date": "1990-01-01",
  "blood_type": "O+",
  "weight": 70.5,
  "medical_notes": "Sin observaciones"
}
```

#### GET `/api/donors`

Obtiene la lista de donantes con filtros opcionales.

**Query Parameters:**

- `blood_type`: Filtrar por tipo de sangre
- `is_eligible`: Filtrar por elegibilidad (true/false)
- `page`: Número de página (paginación)
- `per_page`: Elementos por página

#### GET `/api/donors/{id}`

Obtiene un donante específico.

#### PUT `/api/donors/{id}`

Actualiza un donante existente.

#### DELETE `/api/donors/{id}`

Elimina un donante.

#### GET `/api/donors/eligibility-check/{id}`

Verifica la elegibilidad de un donante para donar.

#### GET `/api/donors/statistics` (Solo Administradores)

Obtiene estadísticas de donantes.

## Validaciones Implementadas

### Usuario

- **Email**: Formato válido y único
- **Contraseña**: Mínimo 8 caracteres, incluye mayúscula, minúscula y número
- **Rol**: Solo valores válidos (administrador/usuario)

### Donante

- **Nombres**: Mínimo 2 caracteres, solo letras y espacios
- **Email**: Formato válido y único
- **Teléfono**: Mínimo 10 dígitos
- **Edad**: Entre 16 y 70 años
- **Peso**: Entre 45 y 200 kg
- **Tipo de sangre**: Solo valores válidos del enum
- **Fechas**: Formatos válidos y lógicos

### Elegibilidad para Donación

- **Edad**: 18-65 años
- **Peso**: Mínimo 50 kg
- **Última donación**: Mínimo 8 semanas (56 días) de intervalo
- **Estado**: Marcado como elegible

## Control de Acceso

### Roles y Permisos

#### Usuario Regular

- Crear, ver, editar y eliminar sus propios donantes
- Ver su propio perfil
- No puede acceder a otros usuarios o estadísticas

#### Administrador

- Todas las funciones de usuario regular
- Ver, editar y eliminar cualquier donante
- Gestionar usuarios (crear, ver, editar, eliminar)
- Acceder a estadísticas del sistema
- Cambiar roles de usuarios

### Middleware de Autenticación

- `@token_required`: Requiere token JWT válido
- `@admin_required`: Requiere rol de administrador
- `@role_required(role)`: Requiere rol específico

## Instalación y Uso

### Requisitos

- Python 3.8+
- pip
- virtualenv (recomendado)

### Instalación

1. **Clonar el repositorio:**

```bash
git clone <repository-url>
cd actfinalIDS
```

2. **Crear entorno virtual:**

```bash
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
```

3. **Instalar dependencias:**

```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno (opcional):**

```bash
export JWT_SECRET_KEY="your-secret-key"
export SECRET_KEY="your-app-secret"
export DATABASE_URL="sqlite:///donors.db"
```

5. **Ejecutar la aplicación:**

```bash
python registro.py
```

La aplicación estará disponible en `http://localhost:5000`

### Usuario Administrador por Defecto

Al iniciar la aplicación por primera vez, se crea automáticamente un usuario administrador:

- **Email**: `admin@example.com`
- **Contraseña**: `Admin123!`

## Pruebas

### Ejecutar Pruebas

```bash
# Ejecutar todas las pruebas con cobertura
pytest tests/ --cov=app --cov-report=html --cov-report=term-missing

# Ejecutar pruebas específicas
pytest tests/test_app.py::TestAuthRoutes::test_login_success -v

# Generar reporte de cobertura
pytest tests/ --cov=app --cov-report=html
```

### Cobertura de Pruebas

El proyecto incluye pruebas unitarias con cobertura superior al 80%, cubriendo:

- **Autenticación**: Login, registro, validación de tokens
- **Gestión de Usuarios**: CRUD y permisos
- **Gestión de Donantes**: CRUD, validaciones, elegibilidad
- **Modelos**: Validaciones y métodos de negocio
- **Utilidades**: Funciones auxiliares y validadores

### Tipos de Pruebas Incluidas

#### Pruebas de Autenticación

- Registro de usuarios con datos válidos e inválidos
- Login con credenciales correctas e incorrectas
- Validación de tokens JWT
- Control de acceso por roles

#### Pruebas de Donantes

- Creación con validaciones de datos
- Actualización y eliminación
- Verificación de elegibilidad
- Filtros y paginación

#### Pruebas de Modelos

- Validación de contraseñas
- Cálculo de edad y elegibilidad
- Serialización a diccionarios

## Ejemplos de Uso

### 1. Registrar Usuario y Crear Donante

```bash
# 1. Registrar usuario
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "doctor@hospital.com",
    "password": "SecurePass123!",
    "role": "usuario"
  }'

# 2. Hacer login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "doctor@hospital.com",
    "password": "SecurePass123!"
  }'

# 3. Crear donante (usar token del paso 2)
curl -X POST http://localhost:5000/api/donors \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{
    "first_name": "Ana",
    "last_name": "García",
    "email": "ana.garcia@email.com",
    "birth_date": "1985-03-15",
    "blood_type": "A+",
    "weight": 65
  }'
```

### 2. Verificar Elegibilidad

```bash
# Verificar elegibilidad de donante
curl -X GET http://localhost:5000/api/donors/eligibility-check/1 \
  -H "Authorization: Bearer <TOKEN>"
```

### 3. Obtener Estadísticas (Admin)

```bash
# Login como admin
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "Admin123!"
  }'

# Obtener estadísticas
curl -X GET http://localhost:5000/api/donors/statistics \
  -H "Authorization: Bearer <ADMIN_TOKEN>"
```

## Estructura de Respuestas

### Respuesta Exitosa

```json
{
  "message": "Operación exitosa",
  "data": { ... },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### Respuesta de Error

```json
{
  "message": "Descripción del error",
  "errors": ["Lista de errores específicos"],
  "code": 400
}
```

## Consideraciones de Seguridad

1. **Contraseñas**: Hasheadas con Werkzeug
2. **Tokens JWT**: Expiración de 24 horas
3. **Validación de Entrada**: Sanitización de todos los datos
4. **Control de Acceso**: Verificación de permisos en cada endpoint
5. **HTTPS**: Recomendado para producción

## Mejoras Futuras

- [ ] Autenticación de dos factores (2FA)
- [ ] Logging y monitoreo avanzado
- [ ] Cache con Redis
- [ ] Documentación con Swagger/OpenAPI
- [ ] Notificaciones por email
- [ ] Dashboard web administrativo
- [ ] API de citas para donaciones
- [ ] Integración con sistemas hospitalarios

## Contribución

1. Fork el proyecto
2. Crear rama para nueva característica (`git checkout -b feature/nueva-caracteristica`)
3. Commit cambios (`git commit -am 'Agregar nueva característica'`)
4. Push a la rama (`git push origin feature/nueva-caracteristica`)
5. Crear Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo `LICENSE` para más detalles.
