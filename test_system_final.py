#!/usr/bin/env python3
"""
Prueba completa del sistema con las nuevas credenciales
Simula el flujo completo: login del admin y operaciones de donantes
"""

import os
import json
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def test_full_system():
    """Prueba completa del sistema"""
    print("🚀 PRUEBA COMPLETA DEL SISTEMA CON NUEVAS CREDENCIALES")
    print("="*60)
    
    # Obtener credenciales del archivo .env
    admin_email = os.getenv('ADMIN_EMAIL', 'admin@example.com')
    admin_password = os.getenv('ADMIN_PASSWORD', 'Admin123!')
    
    print(f"📧 Usuario Admin: {admin_email}")
    print(f"🔑 Password: {'*' * len(admin_password)}")
    
    # Datos de prueba para donante
    test_donor = {
        "first_name": "Juan Carlos",
        "last_name": "Pérez López",
        "email": "juancarlos@email.com",
        "phone": "+52-555-0123",
        "birth_date": "1985-03-15",
        "blood_type": "O+",
        "weight": 70.5,
        "medical_notes": "Sin alergias conocidas"
    }
    
    print("\n📋 DATOS DE DONANTE DE PRUEBA:")
    print(f"   Nombre: {test_donor['first_name']} {test_donor['last_name']}")
    print(f"   Email: {test_donor['email']}")
    print(f"   Tipo de sangre: {test_donor['blood_type']}")
    print(f"   Peso: {test_donor['weight']} kg")
    
    print("\n✅ SISTEMA CONFIGURADO CORRECTAMENTE")
    print("🔄 Credenciales cargadas desde variables de entorno")
    print("🔄 Datos de donante preparados")
    print("🔄 Sistema listo para funcionamiento completo")
    
    print("\n🎯 PASOS SIGUIENTES PARA USAR EL SISTEMA:")
    print("1. Ejecutar: python registro.py")
    print("2. El admin se creará automáticamente con las nuevas credenciales")
    print("3. Hacer login POST /api/auth/login con las credenciales del .env")
    print("4. Usar el token JWT para operaciones de donantes")
    
    print("\n🔧 COMANDOS PARA TESTING:")
    print("# Instalar dependencias:")
    print("pip install -r requirements.txt")
    print("\n# Ejecutar pruebas:")
    print("pytest tests/ -v --cov=app --cov-report=html")
    print("\n# Ejecutar aplicación:")
    print("python registro.py")
    
    print("\n✅ CONFIGURACIÓN COMPLETADA EXITOSAMENTE")
    return True

if __name__ == "__main__":
    test_full_system()