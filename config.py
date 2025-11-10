"""
Configuración de la aplicación Flask
"""

import os
from datetime import timedelta

class Config:
    """Configuración base"""
    
    # Configuración de Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Configuración de PostgreSQL
    POSTGRES_HOST = os.environ.get('POSTGRES_HOST') or 'localhost'
    POSTGRES_PORT = os.environ.get('POSTGRES_PORT') or '5432'
    POSTGRES_USER = os.environ.get('POSTGRES_USER') or 'postgres'
    POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD') or '123456'
    POSTGRES_DB = os.environ.get('POSTGRES_DB') or 'weapon_detection'
    
    # URL de conexión a PostgreSQL (con codificación UTF-8 explícita)
    # Escapar caracteres especiales en la contraseña si es necesario
    from urllib.parse import quote_plus
    encoded_password = quote_plus(POSTGRES_PASSWORD) if POSTGRES_PASSWORD else ''
    encoded_user = quote_plus(POSTGRES_USER) if POSTGRES_USER else ''
    
    SQLALCHEMY_DATABASE_URI = (
        f'postgresql://{encoded_user}:{encoded_password}'
        f'@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}'
    )
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    
    # Configuración de sesión
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # Directorios
    UPLOAD_FOLDER = 'captures'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

