import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QListWidget, 
                             QListWidgetItem, QFrame, QMessageBox, QSlider,
                             QGroupBox, QGridLayout, QTextEdit, QSplitter)
from PyQt5.QtCore import QTimer, QThread, pyqtSignal, Qt
from PyQt5.QtGui import QPixmap, QImage, QFont, QPalette, QColor
import os
from datetime import datetime
import json
import pymysql
from process.weapon_detection import WeaponDetector

class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)
    weapon_detected_signal = pyqtSignal(list, dict)
    
    def __init__(self, weapon_detector):
        super().__init__()
        self.weapon_detector = weapon_detector
        self.running = False
        self.cap = None
        self.detection_enabled = True
        
    def run(self):
        self.cap = cv2.VideoCapture(0)  # Cámara web
        self.running = True
        
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                if self.detection_enabled:
                    # Realizar detección de armas
                    results, detections = self.weapon_detector.detect_weapons(frame)
                    
                    # Dibujar detecciones
                    annotated_frame = self.weapon_detector.draw_detections(frame, detections)
                    
                    # Emitir señal si se detectaron armas
                    if detections:
                        summary = self.weapon_detector.get_detection_summary(detections)
                        self.weapon_detected_signal.emit(detections, summary)
                    
                    self.change_pixmap_signal.emit(annotated_frame)
                else:
                    self.change_pixmap_signal.emit(frame)
        
        if self.cap:
            self.cap.release()
    
    def stop(self):
        self.running = False
        self.wait()

class WeaponDetectionApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.weapon_detector = WeaponDetector()
        self.video_thread = VideoThread(self.weapon_detector)
        self.detections_history = []
        self.init_ui()
        self.setup_database()
        
    def setup_database(self):
        """Configurar conexión a la base de datos"""
        try:
            self.connection = pymysql.connect(
                host="localhost",
                user="root",
                password="",
                db="placas"
            )
            self.create_weapons_table()
        except Exception as e:
            print(f"Error de conexión a BD: {e}")
            self.connection = None
    
    def create_weapons_table(self):
        """Crear tabla para almacenar detecciones de armas"""
        try:
            with self.connection.cursor() as cursor:
                sql = """
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
                cursor.execute(sql)
                self.connection.commit()
        except Exception as e:
            print(f"Error creando tabla: {e}")
    
    def init_ui(self):
        self.setWindowTitle("Sistema de Detección de Armas")
        self.setGeometry(100, 100, 1400, 800)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QHBoxLayout(central_widget)
        
        # Splitter para dividir la interfaz
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # Panel izquierdo - Lista de detecciones
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)
        
        # Panel derecho - Video y controles
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)
        
        # Configurar proporciones del splitter
        splitter.setSizes([400, 1000])
        
        # Configurar video thread
        self.video_thread.change_pixmap_signal.connect(self.update_image)
        self.video_thread.weapon_detected_signal.connect(self.on_weapon_detected)
        
        # Iniciar video
        self.video_thread.start()
        
        # Estilo
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
                color: white;
            }
            QLabel {
                color: white;
                font-size: 12px;
            }
            QPushButton {
                background-color: #4a4a4a;
                border: 1px solid #555;
                color: white;
                padding: 8px;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
            }
            QPushButton:pressed {
                background-color: #3a3a3a;
            }
            QListWidget {
                background-color: #3a3a3a;
                border: 1px solid #555;
                color: white;
                font-size: 11px;
            }
            QGroupBox {
                color: white;
                font-weight: bold;
                border: 1px solid #555;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
    
    def create_left_panel(self):
        """Crear panel izquierdo con lista de detecciones"""
        left_widget = QWidget()
        layout = QVBoxLayout(left_widget)
        
        # Título
        title_label = QLabel("Detecciones de Armas")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Lista de detecciones
        self.detections_list = QListWidget()
        self.detections_list.itemClicked.connect(self.show_detection_details)
        layout.addWidget(self.detections_list)
        
        # Botones de control
        button_layout = QHBoxLayout()
        
        self.clear_btn = QPushButton("Limpiar Lista")
        self.clear_btn.clicked.connect(self.clear_detections)
        button_layout.addWidget(self.clear_btn)
        
        self.export_btn = QPushButton("Exportar")
        self.export_btn.clicked.connect(self.export_detections)
        button_layout.addWidget(self.export_btn)
        
        layout.addLayout(button_layout)
        
        # Estadísticas
        stats_group = QGroupBox("Estadísticas")
        stats_layout = QGridLayout(stats_group)
        
        self.total_detections_label = QLabel("Total: 0")
        self.high_alerts_label = QLabel("Alertas Altas: 0")
        self.medium_alerts_label = QLabel("Alertas Medias: 0")
        
        stats_layout.addWidget(self.total_detections_label, 0, 0)
        stats_layout.addWidget(self.high_alerts_label, 0, 1)
        stats_layout.addWidget(self.medium_alerts_label, 1, 0)
        
        layout.addWidget(stats_group)
        
        return left_widget
    
    def create_right_panel(self):
        """Crear panel derecho con video y controles"""
        right_widget = QWidget()
        layout = QVBoxLayout(right_widget)
        
        # Título del video
        video_title = QLabel("Video en Tiempo Real")
        video_title.setFont(QFont("Arial", 12, QFont.Bold))
        video_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(video_title)
        
        # Label para el video
        self.video_label = QLabel()
        self.video_label.setMinimumSize(640, 480)
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setStyleSheet("border: 2px solid #555;")
        layout.addWidget(self.video_label)
        
        # Controles
        controls_group = QGroupBox("Controles")
        controls_layout = QGridLayout(controls_group)
        
        # Botón de detección
        self.detection_btn = QPushButton("Desactivar Detección")
        self.detection_btn.setCheckable(True)
        self.detection_btn.clicked.connect(self.toggle_detection)
        controls_layout.addWidget(self.detection_btn, 0, 0)
        
        # Botón de captura
        self.capture_btn = QPushButton("Capturar Frame")
        self.capture_btn.clicked.connect(self.capture_frame)
        controls_layout.addWidget(self.capture_btn, 0, 1)
        
        # Slider de confianza
        confidence_label = QLabel("Umbral de Confianza:")
        self.confidence_slider = QSlider(Qt.Horizontal)
        self.confidence_slider.setRange(10, 100)
        self.confidence_slider.setValue(50)
        self.confidence_slider.valueChanged.connect(self.update_confidence)
        
        controls_layout.addWidget(confidence_label, 1, 0)
        controls_layout.addWidget(self.confidence_slider, 1, 1)
        
        layout.addWidget(controls_group)
        
        # Panel de alertas
        alerts_group = QGroupBox("Alertas")
        alerts_layout = QVBoxLayout(alerts_group)
        
        self.alerts_text = QTextEdit()
        self.alerts_text.setMaximumHeight(100)
        self.alerts_text.setReadOnly(True)
        alerts_layout.addWidget(self.alerts_text)
        
        layout.addWidget(alerts_group)
        
        return right_widget
    
    def update_image(self, cv_img):
        """Actualizar imagen del video"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(self.video_label.width(), self.video_label.height(), 
                                       Qt.KeepAspectRatio)
        self.video_label.setPixmap(QPixmap.fromImage(p))
    
    def on_weapon_detected(self, detections, summary):
        """Manejar detección de armas"""
        # Agregar a historial
        detection_info = {
            'timestamp': datetime.now(),
            'detections': detections,
            'summary': summary
        }
        self.detections_history.append(detection_info)
        
        # Actualizar lista
        self.update_detections_list()
        
        # Mostrar alerta
        self.show_alert(summary)
        
        # Guardar en base de datos
        self.save_to_database(detection_info)
        
        # Guardar imagen si es alerta alta
        if summary['alert_level'] == 'high':
            self.save_detection_image(detections)
    
    def update_detections_list(self):
        """Actualizar lista de detecciones"""
        self.detections_list.clear()
        
        for i, detection in enumerate(reversed(self.detections_history)):
            timestamp = detection['timestamp'].strftime("%H:%M:%S")
            summary = detection['summary']
            
            item_text = f"{timestamp} - {summary['message']}"
            item = QListWidgetItem(item_text)
            
            # Color según nivel de alerta
            if summary['alert_level'] == 'high':
                item.setBackground(QColor(255, 100, 100))
            elif summary['alert_level'] == 'medium':
                item.setBackground(QColor(255, 200, 100))
            else:
                item.setBackground(QColor(100, 255, 100))
            
            self.detections_list.addItem(item)
        
        # Actualizar estadísticas
        self.update_statistics()
    
    def update_statistics(self):
        """Actualizar estadísticas"""
        total = len(self.detections_history)
        high_alerts = sum(1 for d in self.detections_history if d['summary']['alert_level'] == 'high')
        medium_alerts = sum(1 for d in self.detections_history if d['summary']['alert_level'] == 'medium')
        
        self.total_detections_label.setText(f"Total: {total}")
        self.high_alerts_label.setText(f"Alertas Altas: {high_alerts}")
        self.medium_alerts_label.setText(f"Alertas Medias: {medium_alerts}")
    
    def show_alert(self, summary):
        """Mostrar alerta en el panel de alertas"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        alert_text = f"[{timestamp}] {summary['message']}\n"
        
        current_text = self.alerts_text.toPlainText()
        self.alerts_text.setText(alert_text + current_text)
        
        # Limitar a 10 líneas
        lines = self.alerts_text.toPlainText().split('\n')
        if len(lines) > 10:
            self.alerts_text.setText('\n'.join(lines[:10]))
    
    def toggle_detection(self):
        """Activar/desactivar detección"""
        if self.detection_btn.isChecked():
            self.video_thread.detection_enabled = False
            self.detection_btn.setText("Activar Detección")
        else:
            self.video_thread.detection_enabled = True
            self.detection_btn.setText("Desactivar Detección")
    
    def update_confidence(self):
        """Actualizar umbral de confianza"""
        confidence = self.confidence_slider.value() / 100.0
        self.weapon_detector.confidence_threshold = confidence
    
    def capture_frame(self):
        """Capturar frame actual"""
        if hasattr(self.video_thread, 'cap') and self.video_thread.cap:
            ret, frame = self.video_thread.cap.read()
            if ret:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"captures/weapon_capture_{timestamp}.jpg"
                
                # Crear directorio si no existe
                os.makedirs("captures", exist_ok=True)
                
                cv2.imwrite(filename, frame)
                QMessageBox.information(self, "Captura", f"Frame guardado como {filename}")
    
    def save_detection_image(self, detections):
        """Guardar imagen con detección"""
        if hasattr(self.video_thread, 'cap') and self.video_thread.cap:
            ret, frame = self.video_thread.cap.read()
            if ret:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"captures/weapon_detection_{timestamp}.jpg"
                
                os.makedirs("captures", exist_ok=True)
                self.weapon_detector.save_detection(frame, detections, filename)
    
    def save_to_database(self, detection_info):
        """Guardar detección en base de datos"""
        if self.connection:
            try:
                with self.connection.cursor() as cursor:
                    sql = """
                    INSERT INTO weapon_detections 
                    (weapon_count, alert_level, detection_types, metadata)
                    VALUES (%s, %s, %s, %s)
                    """
                    detection_types = ', '.join(detection_info['summary']['detection_types'])
                    metadata = json.dumps(detection_info['detections'])
                    
                    cursor.execute(sql, (
                        detection_info['summary']['weapons_detected'],
                        detection_info['summary']['alert_level'],
                        detection_types,
                        metadata
                    ))
                    self.connection.commit()
            except Exception as e:
                print(f"Error guardando en BD: {e}")
    
    def show_detection_details(self, item):
        """Mostrar detalles de una detección"""
        index = self.detections_list.row(item)
        detection = self.detections_history[-(index + 1)]
        
        details = f"""
        Timestamp: {detection['timestamp']}
        Armas detectadas: {detection['summary']['weapons_detected']}
        Nivel de alerta: {detection['summary']['alert_level']}
        Tipos: {', '.join(detection['summary']['detection_types'])}
        Confianza máxima: {detection['summary']['max_confidence']:.2f}
        """
        
        QMessageBox.information(self, "Detalles de Detección", details)
    
    def clear_detections(self):
        """Limpiar lista de detecciones"""
        self.detections_history.clear()
        self.detections_list.clear()
        self.alerts_text.clear()
        self.update_statistics()
    
    def export_detections(self):
        """Exportar detecciones a archivo"""
        if not self.detections_history:
            QMessageBox.warning(self, "Exportar", "No hay detecciones para exportar")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"exports/weapon_detections_{timestamp}.json"
        
        os.makedirs("exports", exist_ok=True)
        
        export_data = []
        for detection in self.detections_history:
            export_data.append({
                'timestamp': detection['timestamp'].isoformat(),
                'summary': detection['summary'],
                'detections': detection['detections']
            })
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        QMessageBox.information(self, "Exportar", f"Detecciones exportadas a {filename}")
    
    def closeEvent(self, event):
        """Manejar cierre de la aplicación"""
        self.video_thread.stop()
        if self.connection:
            self.connection.close()
        event.accept()

def main():
    app = QApplication(sys.argv)
    window = WeaponDetectionApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main() 