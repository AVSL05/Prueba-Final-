"""
Rutas para servir la interfaz web
"""

from flask import Blueprint, render_template

# Crear blueprint para las rutas web
web_bp = Blueprint('web', __name__)

@web_bp.route('/')
def index():
    """Página principal del sistema"""
    return render_template('index.html')

@web_bp.route('/app')
def app():
    """Alias para la página principal"""
    return render_template('index.html')