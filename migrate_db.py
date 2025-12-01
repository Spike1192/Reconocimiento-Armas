#!/usr/bin/env python3
"""
Script para migrar la base de datos y agregar columnas faltantes
"""

import sys
from app import app, db
from models import Usuario, Alerta
from sqlalchemy import text

def migrate_database():
    """Agregar columnas faltantes a las tablas existentes"""
    try:
        with app.app_context():
            print("Iniciando migración de base de datos...")
            
            # Verificar conexión
            db.engine.connect()
            print("✓ Conexión a PostgreSQL exitosa")
            
            # Agregar columnas faltantes a la tabla usuarios si no existen
            print("\nVerificando columnas de la tabla 'usuarios'...")
            
            with db.engine.connect() as conn:
                # Verificar qué columnas existen
                result = conn.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'usuarios'
                """))
                existing_columns = [row[0] for row in result]
                
                print(f"Columnas existentes: {existing_columns}")
                
                # Agregar columnas faltantes
                columns_to_add = {
                    'Email': 'VARCHAR(100)',
                    'Rol': 'VARCHAR(50)',
                    'UbicacionAsignada': 'VARCHAR(100)',
                    'TelefonoContacto': 'VARCHAR(20)',
                    'UltimoAcceso': 'TIMESTAMP'
                }
                
                for column_name, column_type in columns_to_add.items():
                    if column_name.lower() not in [col.lower() for col in existing_columns]:
                        try:
                            conn.execute(text(f"""
                                ALTER TABLE usuarios 
                                ADD COLUMN "{column_name}" {column_type}
                            """))
                            conn.commit()
                            print(f"✓ Columna '{column_name}' agregada")
                        except Exception as e:
                            print(f"⚠ Error agregando columna '{column_name}': {e}")
                            conn.rollback()
                    else:
                        print(f"  Columna '{column_name}' ya existe")
            
            # Crear tabla alertas si no existe
            print("\nVerificando tabla 'alertas'...")
            db.create_all()
            
            # Verificar si hay usuarios sin los nuevos campos y actualizarlos
            print("\nVerificando usuarios existentes...")
            usuarios = Usuario.query.all()
            
            if usuarios:
                print(f"Encontrados {len(usuarios)} usuarios")
                # Los usuarios existentes tendrán valores NULL en los nuevos campos
                # Esto está bien, se pueden actualizar manualmente o dejarlos como están
            else:
                print("No hay usuarios en la base de datos")
                # Crear usuarios predefinidos
                from init_db import crear_usuarios_predefinidos
                crear_usuarios_predefinidos()
            
            print("\n✓ Migración completada exitosamente")
            
    except Exception as e:
        print(f"\n✗ Error en la migración:")
        print(f"  {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    migrate_database()

