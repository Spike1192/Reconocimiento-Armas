#!/usr/bin/env python3
"""
Script de instalación automática para el Sistema de Detección de Armas
"""

import os
import sys
import subprocess
import platform
import sqlite3
import pymysql
from pathlib import Path

class WeaponDetectionInstaller:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.venv_path = self.project_root / "venv"
        self.requirements_file = self.project_root / "requirements.txt"
        
    def print_header(self):
        """Imprimir encabezado del instalador"""
        print("=" * 60)
        print("    INSTALADOR DEL SISTEMA DE DETECCIÓN DE ARMAS")
        print("=" * 60)
        print()
    
    def check_python_version(self):
        """Verificar versión de Python"""
        print("1. Verificando versión de Python...")
        
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 7):
            print(f"✗ Python {version.major}.{version.minor} detectado")
            print("  Se requiere Python 3.7 o superior")
            return False
        
        print(f"✓ Python {version.major}.{version.minor}.{version.micro} detectado")
        return True
    
    def create_virtual_environment(self):
        """Crear entorno virtual"""
        print("\n2. Creando entorno virtual...")
        
        if self.venv_path.exists():
            print("✓ Entorno virtual ya existe")
            return True
        
        try:
            subprocess.run([sys.executable, "-m", "venv", str(self.venv_path)], 
                         check=True, capture_output=True)
            print("✓ Entorno virtual creado exitosamente")
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ Error al crear entorno virtual: {e}")
            return False
    
    def get_pip_command(self):
        """Obtener comando pip para el entorno virtual"""
        if platform.system() == "Windows":
            return str(self.venv_path / "Scripts" / "pip.exe")
        else:
            return str(self.venv_path / "bin" / "pip")
    
    def get_python_command(self):
        """Obtener comando python para el entorno virtual"""
        if platform.system() == "Windows":
            return str(self.venv_path / "Scripts" / "python.exe")
        else:
            return str(self.venv_path / "bin" / "python")
    
    def install_dependencies(self):
        """Instalar dependencias"""
        print("\n3. Instalando dependencias...")
        
        pip_cmd = self.get_pip_command()
        
        # Actualizar pip
        try:
            subprocess.run([pip_cmd, "install", "--upgrade", "pip"], 
                         check=True, capture_output=True)
            print("✓ Pip actualizado")
        except subprocess.CalledProcessError as e:
            print(f"⚠ Advertencia: No se pudo actualizar pip: {e}")
        
        # Instalar dependencias
        if self.requirements_file.exists():
            try:
                subprocess.run([pip_cmd, "install", "-r", str(self.requirements_file)], 
                             check=True, capture_output=True)
                print("✓ Dependencias instaladas exitosamente")
                return True
            except subprocess.CalledProcessError as e:
                print(f"✗ Error al instalar dependencias: {e}")
                return False
        else:
            print("✗ Archivo requirements.txt no encontrado")
            return False
    
    def test_yolo_model(self):
        """Probar descarga del modelo YOLO"""
        print("\n4. Probando modelo YOLO...")
        
        python_cmd = self.get_python_command()
        
        try:
            # Script para probar YOLO
            test_script = """
import sys
try:
    from ultralytics import YOLO
    model = YOLO('yolov8n.pt')
    print("SUCCESS")
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)
"""
            
            result = subprocess.run([python_cmd, "-c", test_script], 
                                  capture_output=True, text=True)
            
            if "SUCCESS" in result.stdout:
                print("✓ Modelo YOLO descargado y probado exitosamente")
                return True
            else:
                print(f"✗ Error con modelo YOLO: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"✗ Error al probar YOLO: {e}")
            return False
    
    def setup_database(self):
        """Configurar base de datos"""
        print("\n5. Configurando base de datos...")
        
        # Probar conexión MySQL
        try:
            connection = pymysql.connect(
                host="localhost",
                user="root",
                password="",
                charset='utf8mb4'
            )
            
            with connection.cursor() as cursor:
                # Crear base de datos si no existe
                cursor.execute("CREATE DATABASE IF NOT EXISTS placas")
                cursor.execute("USE placas")
                
                # Crear tabla de detecciones de armas
                create_table_sql = """
                CREATE TABLE IF NOT EXISTS weapon_detections (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    weapon_count INT NOT NULL,
                    alert_level VARCHAR(20) NOT NULL,
                    detection_types TEXT,
                    image_path VARCHAR(255),
                    metadata TEXT
                )
                """
                cursor.execute(create_table_sql)
                connection.commit()
            
            connection.close()
            print("✓ Base de datos MySQL configurada exitosamente")
            return True
            
        except Exception as e:
            print(f"⚠ Advertencia: No se pudo configurar MySQL: {e}")
            print("  Puedes configurar la base de datos manualmente más tarde")
            return False
    
    def create_directories(self):
        """Crear directorios necesarios"""
        print("\n6. Creando directorios...")
        
        directories = [
            "captures",
            "exports", 
            "examples",
            "models"
        ]
        
        for directory in directories:
            dir_path = self.project_root / directory
            dir_path.mkdir(exist_ok=True)
            print(f"✓ Directorio {directory} creado/verificado")
    
    def create_config_file(self):
        """Crear archivo de configuración"""
        print("\n7. Creando archivo de configuración...")
        
        config_content = """# Configuración del Sistema de Detección de Armas

[DATABASE]
host = localhost
user = root
password = 
database = placas

[DETECTION]
confidence_threshold = 0.5
weapon_classes = pistol,rifle,knife,sword,gun,weapon

[ALERTS]
high_threshold = 3
high_confidence = 0.8
medium_confidence = 0.6

[STORAGE]
captures_dir = captures
exports_dir = exports
auto_save = true
"""
        
        config_file = self.project_root / "weapon_config.ini"
        with open(config_file, 'w') as f:
            f.write(config_content)
        
        print("✓ Archivo de configuración creado")
    
    def run_tests(self):
        """Ejecutar pruebas básicas"""
        print("\n8. Ejecutando pruebas básicas...")
        
        python_cmd = self.get_python_command()
        test_file = self.project_root / "test_weapon_detection.py"
        
        if test_file.exists():
            try:
                result = subprocess.run([python_cmd, str(test_file)], 
                                      capture_output=True, text=True, timeout=60)
                if result.returncode == 0:
                    print("✓ Pruebas ejecutadas exitosamente")
                    return True
                else:
                    print(f"⚠ Advertencia: Algunas pruebas fallaron")
                    print(f"  {result.stderr}")
                    return False
            except subprocess.TimeoutExpired:
                print("⚠ Advertencia: Las pruebas tardaron demasiado")
                return False
            except Exception as e:
                print(f"⚠ Advertencia: Error al ejecutar pruebas: {e}")
                return False
        else:
            print("⚠ Archivo de pruebas no encontrado")
            return False
    
    def print_activation_instructions(self):
        """Imprimir instrucciones de activación"""
        print("\n" + "=" * 60)
        print("    INSTALACIÓN COMPLETADA")
        print("=" * 60)
        print()
        print("Para activar el entorno virtual:")
        
        if platform.system() == "Windows":
            print(f"  {self.venv_path}\\Scripts\\activate")
        else:
            print(f"  source {self.venv_path}/bin/activate")
        
        print()
        print("Para ejecutar el sistema:")
        print("  python main_app.py")
        print()
        print("Para ejecutar solo detección de armas:")
        print("  python Vista/weapon_detection_app.py")
        print()
        print("Para ejecutar pruebas:")
        print("  python test_weapon_detection.py")
        print()
        print("¡El sistema está listo para usar!")
    
    def install(self):
        """Ejecutar instalación completa"""
        self.print_header()
        
        steps = [
            ("Verificar Python", self.check_python_version),
            ("Crear entorno virtual", self.create_virtual_environment),
            ("Instalar dependencias", self.install_dependencies),
            ("Probar modelo YOLO", self.test_yolo_model),
            ("Configurar base de datos", self.setup_database),
            ("Crear directorios", self.create_directories),
            ("Crear configuración", self.create_config_file),
            ("Ejecutar pruebas", self.run_tests)
        ]
        
        failed_steps = []
        
        for step_name, step_func in steps:
            try:
                if not step_func():
                    failed_steps.append(step_name)
            except Exception as e:
                print(f"✗ Error en {step_name}: {e}")
                failed_steps.append(step_name)
        
        if failed_steps:
            print(f"\n⚠ Advertencia: Los siguientes pasos fallaron:")
            for step in failed_steps:
                print(f"  - {step}")
            print("\nPuedes intentar completar estos pasos manualmente.")
        
        self.print_activation_instructions()

def main():
    """Función principal"""
    installer = WeaponDetectionInstaller()
    installer.install()

if __name__ == "__main__":
    main() 