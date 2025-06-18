import sys
import os
import cv2
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QLabel, QWidget, QScrollArea, QHBoxLayout, QFrame, QPushButton
from PyQt5.QtGui import QPixmap, QImage, QFont
from PyQt5.QtCore import Qt, QTimer
import pymysql

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from process.main import PlateRecognition
from db.main import connection  # Importar la conexión a la base de datos

# Crear una carpeta para guardar las capturas si no existe
os.makedirs('captures', exist_ok=True)

class VideoWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PlaCam")
        self.setGeometry(100, 100, 1200, 800)  # Tamaño de la ventana

        # Aplicar estilo minimalista
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2C2F33;
                color: #FFFFFF;
            }
            QLabel {
                color: #FFFFFF;
                font-size: 14px;
            }
            QPushButton {
                background-color: #7289DA;
                color: #FFFFFF;
                font-size: 12px;
                padding: 8px 15px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #5B6EAE;
            }
        """)

        # Layout principal
        main_layout = QHBoxLayout()

        # Crear la sección izquierda para mostrar las capturas
        self.capture_list = QVBoxLayout()
        self.capture_list.setAlignment(Qt.AlignTop)

        # Scroll area para las capturas
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_widget.setLayout(self.capture_list)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setFixedWidth(300)  # Ancho fijo para la columna izquierda
        scroll_area.setStyleSheet("background-color: #23272A; border: none;")

        # Crear la sección derecha para el video en tiempo real
        self.video_frame = QLabel()
        self.video_frame.setFrameShape(QFrame.Box)
        self.video_frame.setAlignment(Qt.AlignCenter)
        self.video_frame.setStyleSheet("background-color: #23272A; border: 2px solid #7289DA;")

        # Añadir secciones al layout principal
        main_layout.addWidget(scroll_area)
        main_layout.addWidget(self.video_frame)

        # Crear widget central y establecer layout
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Configuración de la cámara y procesamiento
        self.processor = PlateRecognition()
        self.cap = cv2.VideoCapture('examples/image_example.jpeg')  
        # Temporizador para actualizar el video en tiempo real
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # Actualización cada 30 ms

        # Inicializar un conjunto para almacenar placas guardadas
        self.saved_plates = set()

        # Cargar capturas existentes de la base de datos al iniciar
        self.load_saved_captures()

    def load_saved_captures(self):
        try:
            # Conexión a la base de datos
            cursor = connection.cursor()

            # Consulta para obtener todas las placas y las rutas de las imágenes guardadas
            cursor.execute("SELECT num_placa, imagen FROM Informacion")
            rows = cursor.fetchall()

            # Iterar sobre los resultados y agregar a la interfaz
            for row in rows:
                license_plate, image_path = row
                if os.path.exists(image_path):
                    self.add_capture_card(license_plate, image_path)

        except pymysql.MySQLError as e:
            print(f"Error al cargar datos desde la base de datos: {e}")
        finally:
            cursor.close()

    def update_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return

        # Procesar el frame para detectar la placa
        vehicle_image, license_plate, info = self.processor.process_vehicular_plate(frame, True, True)

        # Mostrar el frame en la ventana derecha
        self.display_video(vehicle_image)

        # Si la placa fue identificada y no está repetida, guardar una captura
        if license_plate and license_plate not in self.saved_plates:
            self.saved_plates.add(license_plate)
            capture_filename = f'captures/{license_plate}.png'
            cv2.imwrite(capture_filename, vehicle_image)
            self.save_to_database(license_plate, capture_filename)
            self.add_capture_card(license_plate, capture_filename)

    def display_video(self, frame):
        # Convertir la imagen de OpenCV a formato compatible con PyQt5
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        q_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)

        # Mostrar la imagen en la etiqueta de video
        self.video_frame.setPixmap(pixmap)

    def add_capture_card(self, license_plate, image_path):
        # Crear una carta para mostrar la captura del vehículo
        card_layout = QVBoxLayout()
        card_layout.setAlignment(Qt.AlignCenter)

        # Título con la placa del vehículo
        title = QLabel(f"Placa: {license_plate}")
        title.setAlignment(Qt.AlignCenter)

        # Mostrar la imagen en la carta
        image_label = QLabel()
        pixmap = QPixmap(image_path)
        pixmap = pixmap.scaled(250, 150, Qt.KeepAspectRatio)
        image_label.setPixmap(pixmap)

        # Añadir título e imagen al layout de la carta
        card_layout.addWidget(title)
        card_layout.addWidget(image_label)

        # Crear un widget para la carta y añadirlo a la lista de capturas
        card_widget = QWidget()
        card_widget.setLayout(card_layout)
        card_widget.setStyleSheet("background-color: #2C2F33; margin: 10px; border-radius: 8px;")
        card_widget.mousePressEvent = lambda event, p=license_plate, img=image_path: self.show_large_image(p, img)

        self.capture_list.addWidget(card_widget)

    def show_large_image(self, license_plate, image_path):
        # Crear una ventana secundaria para mostrar la imagen en grande
        large_image_window = QMainWindow(self)
        large_image_window.setWindowTitle(f"Detalle de la Placa - {license_plate}")
        large_image_window.setGeometry(300, 200, 800, 600)

        # Layout de la ventana secundaria
        layout = QVBoxLayout()

        # Mostrar la imagen en grande
        image_label = QLabel()
        pixmap = QPixmap(image_path)
        pixmap = pixmap.scaled(600, 400, Qt.KeepAspectRatio)
        image_label.setPixmap(pixmap)
        image_label.setAlignment(Qt.AlignCenter)

        # Mostrar la placa del vehículo
        title = QLabel(f"Placa: {license_plate}")
        title.setFont(QFont("Arial", 16))
        title.setAlignment(Qt.AlignCenter)

        # Botón para cerrar la ventana secundaria
        close_button = QPushButton("Volver")
        close_button.clicked.connect(large_image_window.close)
        close_button.setStyleSheet("margin-top: 20px;")

        # Añadir elementos al layout
        layout.addWidget(title)
        layout.addWidget(image_label)
        layout.addWidget(close_button)

        # Configurar layout de la ventana secundaria
        widget = QWidget()
        widget.setLayout(layout)
        large_image_window.setCentralWidget(widget)
        large_image_window.show()

    def save_to_database(self, license_plate, image_path):
        try:
            # Conexión a la base de datos
            cursor = connection.cursor()

            # Insertar información en la base de datos
            query = "INSERT INTO Informacion (num_placa, imagen) VALUES (%s, %s)"
            cursor.execute(query, (license_plate, image_path))
            connection.commit()

        except pymysql.MySQLError as e:
            print(f"Error al guardar en la base de datos: {e}")
        finally:
            cursor.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VideoWindow()
    window.show()
    sys.exit(app.exec_())
