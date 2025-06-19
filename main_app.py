#!/usr/bin/env python3
"""
Aplicación principal que permite elegir entre:
1. Sistema de Reconocimiento de Placas
2. Sistema de Detección de Armas
"""

import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QMessageBox,
                             QGroupBox, QGridLayout, QTextEdit)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap, QIcon

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Sistema de Seguridad - Menú Principal")
        self.setGeometry(200, 200, 800, 600)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        
        # Título principal
        title_label = QLabel("SISTEMA DE SEGURIDAD")
        title_label.setFont(QFont("Arial", 24, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #2c3e50; margin: 20px;")
        main_layout.addWidget(title_label)
        
        # Subtítulo
        subtitle_label = QLabel("Selecciona el módulo que deseas ejecutar")
        subtitle_label.setFont(QFont("Arial", 14))
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("color: #7f8c8d; margin-bottom: 30px;")
        main_layout.addWidget(subtitle_label)
        
        # Contenedor de botones
        buttons_container = QWidget()
        buttons_layout = QHBoxLayout(buttons_container)
        
        # Botón para Reconocimiento de Placas
        plates_btn = self.create_module_button(
            "Reconocimiento de Placas",
            "Sistema de detección y reconocimiento de placas vehiculares en tiempo real",
            "🚗",
            self.open_plates_system
        )
        buttons_layout.addWidget(plates_btn)
        
        # Botón para Detección de Armas
        weapons_btn = self.create_module_button(
            "Detección de Armas",
            "Sistema de detección de armas y objetos peligrosos en tiempo real",
            "🔫",
            self.open_weapons_system
        )
        buttons_layout.addWidget(weapons_btn)
        
        main_layout.addWidget(buttons_container)
        
        # Información del sistema
        info_group = QGroupBox("Información del Sistema")
        info_layout = QVBoxLayout(info_group)
        
        info_text = QTextEdit()
        info_text.setMaximumHeight(150)
        info_text.setReadOnly(True)
        info_text.setPlainText("""
SISTEMA DE SEGURIDAD INTEGRADO

Este sistema incluye dos módulos principales:

1. RECONOCIMIENTO DE PLACAS:
   • Detección automática de placas vehiculares
   • Reconocimiento de caracteres mediante OCR
   • Almacenamiento en base de datos MySQL
   • Interfaz gráfica intuitiva

2. DETECCIÓN DE ARMAS:
   • Detección de armas y objetos peligrosos
   • Análisis en tiempo real mediante YOLOv8
   • Sistema de alertas por niveles de riesgo
   • Registro de eventos y exportación de datos

TECNOLOGÍAS UTILIZADAS:
• Python 3.7+
• OpenCV para procesamiento de imágenes
• YOLOv8 para detección de objetos
• PyQt5 para interfaz gráfica
• MySQL para almacenamiento de datos
• EasyOCR para reconocimiento de texto
        """)
        info_layout.addWidget(info_text)
        
        main_layout.addWidget(info_group)
        
        # Botones de control
        control_layout = QHBoxLayout()
        
        exit_btn = QPushButton("Salir")
        exit_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        exit_btn.clicked.connect(self.close)
        control_layout.addWidget(exit_btn)
        
        main_layout.addLayout(control_layout)
        
        # Estilo general
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #ecf0f1, stop:1 #bdc3c7);
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 3px;
                font-size: 11px;
            }
        """)
    
    def create_module_button(self, title, description, icon, callback):
        """Crear botón de módulo con estilo"""
        button = QPushButton()
        button.setMinimumSize(300, 200)
        button.setCursor(Qt.PointingHandCursor)
        
        # Layout del botón
        layout = QVBoxLayout(button)
        
        # Icono
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Arial", 48))
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)
        
        # Título
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #2c3e50; margin: 5px;")
        layout.addWidget(title_label)
        
        # Descripción
        desc_label = QLabel(description)
        desc_label.setFont(QFont("Arial", 10))
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #7f8c8d; margin: 5px;")
        layout.addWidget(desc_label)
        
        # Conectar callback
        button.clicked.connect(callback)
        
        # Estilo del botón
        button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f8f9fa);
                border: 2px solid #dee2e6;
                border-radius: 10px;
                padding: 10px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #e9ecef, stop:1 #dee2e6);
                border: 2px solid #adb5bd;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #dee2e6, stop:1 #ced4da);
            }
        """)
        
        return button
    
    def open_plates_system(self):
        """Abrir sistema de reconocimiento de placas"""
        try:
            # Verificar si existe el archivo principal del sistema de placas
            plates_app_path = "Vista/app.py"
            if os.path.exists(plates_app_path):
                print("Iniciando sistema de reconocimiento de placas...")
                # Aquí podrías importar y ejecutar el sistema de placas
                QMessageBox.information(self, "Sistema de Placas", 
                                      "Iniciando sistema de reconocimiento de placas...")
                # Por ahora solo mostramos un mensaje
            else:
                QMessageBox.warning(self, "Error", 
                                  "No se encontró el sistema de reconocimiento de placas")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al iniciar sistema de placas: {e}")
    
    def open_weapons_system(self):
        """Abrir sistema de detección de armas"""
        try:
            # Verificar si existe el archivo de detección de armas
            weapons_app_path = "Vista/weapon_detection_app.py"
            if os.path.exists(weapons_app_path):
                print("Iniciando sistema de detección de armas...")
                
                # Importar y ejecutar el sistema de armas
                from Vista.weapon_detection_app import WeaponDetectionApp
                
                # Crear nueva ventana
                self.weapons_window = WeaponDetectionApp()
                self.weapons_window.show()
                
                # Ocultar ventana principal
                self.hide()
                
                # Conectar señal de cierre
                self.weapons_window.destroyed.connect(self.show)
                
            else:
                QMessageBox.warning(self, "Error", 
                                  "No se encontró el sistema de detección de armas")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al iniciar sistema de armas: {e}")
    
    def closeEvent(self, event):
        """Manejar cierre de la aplicación"""
        reply = QMessageBox.question(self, 'Salir', 
                                   '¿Estás seguro de que quieres salir?',
                                   QMessageBox.Yes | QMessageBox.No,
                                   QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

def main():
    app = QApplication(sys.argv)
    
    # Configurar información de la aplicación
    app.setApplicationName("Sistema de Seguridad")
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
            # Si no existe el archivo de armas, mostrar menú principal
            print("No se encontró el sistema de detección de armas, mostrando menú principal...")
            window = MainApp()
            window.show()
            
    except Exception as e:
        print(f"Error al iniciar sistema de armas: {e}")
        # En caso de error, mostrar menú principal
        window = MainApp()
        window.show()
    
    # Ejecutar aplicación
    sys.exit(app.exec_())

if __name__ == '__main__':
    main() 