#!/usr/bin/env python3
"""
Script para inicializar la base de datos PostgreSQL
"""

import sys
from app import app, db
from models import WeaponDetection, Usuario, Alerta

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
            print(f"✓ Tabla '{Usuario.__tablename__}' creada")
            print(f"✓ Tabla '{Alerta.__tablename__}' creada")
            
            # Crear usuarios predefinidos si no existen
            crear_usuarios_predefinidos()
            
    except Exception as e:
        print(f"\n✗ Error al inicializar la base de datos:")
        print(f"  {str(e)}")
        print("\nVerifica:")
        print("  1. Que PostgreSQL esté corriendo")
        print("  2. Que la base de datos exista")
        print("  3. Que las credenciales en config.py sean correctas")
        print("  4. Que no haya caracteres especiales problemáticos en la contraseña")
        sys.exit(1)

def crear_usuarios_predefinidos():
    """Crear usuarios predefinidos en la base de datos"""
    try:
        # Verificar si ya existen usuarios
        if Usuario.query.first():
            print("✓ Usuarios ya existen en la base de datos")
            return
        
        # Crear usuarios predefinidos
        usuarios_predefinidos = [
            {
                'idUsuario': 'admin',
                'Nombre': 'Administrador',
                'Clave': 'admin123',
                'Email': 'admin@sistema.com',
                'Rol': 'Administrador',
                'UbicacionAsignada': 'Centro de Control Principal',
                'TelefonoContacto': '+1234567890'
            },
            {
                'idUsuario': 'operador1',
                'Nombre': 'Operador de Seguridad',
                'Clave': 'operador123',
                'Email': 'operador1@sistema.com',
                'Rol': 'Operador',
                'UbicacionAsignada': 'Zona Norte',
                'TelefonoContacto': '+1234567891'
            },
            {
                'idUsuario': 'supervisor',
                'Nombre': 'Supervisor del Sistema',
                'Clave': 'supervisor123',
                'Email': 'supervisor@sistema.com',
                'Rol': 'Supervisor',
                'UbicacionAsignada': 'Centro de Monitoreo',
                'TelefonoContacto': '+1234567892'
            }
        ]
        
        for usuario_data in usuarios_predefinidos:
            usuario = Usuario(
                idUsuario=usuario_data['idUsuario'],
                Nombre=usuario_data['Nombre'],
                Clave=Usuario.set_password(usuario_data['Clave']),
                Email=usuario_data.get('Email'),
                Rol=usuario_data.get('Rol'),
                UbicacionAsignada=usuario_data.get('UbicacionAsignada'),
                TelefonoContacto=usuario_data.get('TelefonoContacto')
            )
            db.session.add(usuario)
        
        db.session.commit()
        print("Usuarios predefinidos creados:")
        for u in usuarios_predefinidos:
            print(f"  - {u['idUsuario']} ({u['Nombre']})")
            
    except Exception as e:
        print(f"Error al crear usuarios predefinidos: {e}")
        db.session.rollback()

if __name__ == '__main__':
    init_database()

