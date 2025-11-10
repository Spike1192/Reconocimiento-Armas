#!/usr/bin/env python3
"""
Script para inicializar la base de datos PostgreSQL
"""

import sys
from app import app, db
from models import WeaponDetection

def init_database():
    """Crear todas las tablas en la base de datos"""
    try:
        with app.app_context():
            print("Conectando a la base de datos...")
            print(f"Base de datos: {app.config['SQLALCHEMY_DATABASE_URI'].split('@')[-1] if '@' in app.config['SQLALCHEMY_DATABASE_URI'] else 'N/A'}")
            
            # Verificar conexión primero
            db.engine.connect()
            print("✓ Conexión a PostgreSQL exitosa")
            
            print("Creando tablas en la base de datos...")
            db.create_all()
            print("✓ Base de datos inicializada correctamente")
            print(f"✓ Tabla '{WeaponDetection.__tablename__}' creada")
            
    except Exception as e:
        print(f"\n✗ Error al inicializar la base de datos:")
        print(f"  {str(e)}")
        print("\nVerifica:")
        print("  1. Que PostgreSQL esté corriendo")
        print("  2. Que la base de datos exista")
        print("  3. Que las credenciales en config.py sean correctas")
        print("  4. Que no haya caracteres especiales problemáticos en la contraseña")
        sys.exit(1)

if __name__ == '__main__':
    init_database()

