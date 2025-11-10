#!/usr/bin/env python3
"""
Aplicación principal del Sistema de Detección de Armas
"""

import sys
import os
from PyQt5.QtWidgets import QApplication, QMessageBox

def main():
    app = QApplication(sys.argv)
    
    # Configurar información de la aplicación
    app.setApplicationName("Sistema de Detección de Armas")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("Proyecto Integrador")
    
    # Abrir directamente el sistema de detección de armas
    try:
        weapons_app_path = "Vista/weapon_detection_app.py"
        if os.path.exists(weapons_app_path):
            print("Iniciando sistema de detección de armas...")
            
            # Importar y ejecutar el sistema de armas
            from Vista.weapon_detection_app import WeaponDetectionApp
            
            # Crear y mostrar ventana de detección de armas
            window = WeaponDetectionApp()
            window.show()
            
        else:
            # Si no existe el archivo de armas, mostrar error
            QMessageBox.critical(None, "Error", 
                               "No se encontró el sistema de detección de armas.\n"
                               f"Ruta esperada: {os.path.abspath(weapons_app_path)}")
            sys.exit(1)
            
    except Exception as e:
        QMessageBox.critical(None, "Error", 
                           f"Error al iniciar sistema de armas:\n{str(e)}")
        sys.exit(1)
    
    # Ejecutar aplicación
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
