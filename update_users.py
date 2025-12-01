#!/usr/bin/env python3
"""
Script para actualizar usuarios existentes con los nuevos campos
"""

from app import app, db
from models import Usuario

def update_existing_users():
    """Actualizar usuarios existentes con datos completos"""
    try:
        with app.app_context():
            print("Actualizando usuarios existentes...")
            
            # Datos para actualizar usuarios existentes
            usuarios_data = {
                'admin': {
                    'Email': 'admin@sistema.com',
                    'Rol': 'Administrador',
                    'UbicacionAsignada': 'Centro de Control Principal',
                    'TelefonoContacto': '+1234567890'
                },
                'operador1': {
                    'Email': 'operador1@sistema.com',
                    'Rol': 'Operador',
                    'UbicacionAsignada': 'Zona Norte',
                    'TelefonoContacto': '+1234567891'
                },
                'supervisor': {
                    'Email': 'supervisor@sistema.com',
                    'Rol': 'Supervisor',
                    'UbicacionAsignada': 'Centro de Monitoreo',
                    'TelefonoContacto': '+1234567892'
                }
            }
            
            usuarios_actualizados = 0
            
            for id_usuario, datos in usuarios_data.items():
                usuario = Usuario.query.filter_by(idUsuario=id_usuario).first()
                if usuario:
                    # Actualizar solo si los campos están vacíos
                    if not usuario.Email:
                        usuario.Email = datos['Email']
                    if not usuario.Rol:
                        usuario.Rol = datos['Rol']
                    if not usuario.UbicacionAsignada:
                        usuario.UbicacionAsignada = datos['UbicacionAsignada']
                    if not usuario.TelefonoContacto:
                        usuario.TelefonoContacto = datos['TelefonoContacto']
                    
                    usuarios_actualizados += 1
                    print(f"✓ Usuario '{id_usuario}' actualizado")
            
            if usuarios_actualizados > 0:
                db.session.commit()
                print(f"\n✓ {usuarios_actualizados} usuario(s) actualizado(s) correctamente")
            else:
                print("\n✓ No hay usuarios para actualizar")
                
    except Exception as e:
        print(f"\n✗ Error actualizando usuarios:")
        print(f"  {str(e)}")
        import traceback
        traceback.print_exc()
        db.session.rollback()

if __name__ == '__main__':
    update_existing_users()

