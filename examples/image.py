import os
import sys
import cv2
from datetime import datetime
import pymysql

# Ajusta la ruta para importar PlateRecognition
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from process.main import PlateRecognition
from db.main import connection  # Importar la conexión a la base de datos

# Crear una carpeta para guardar las capturas si no existe
os.makedirs('captures', exist_ok=True)

# Inicializar un conjunto para almacenar placas guardadas
saved_plates = set()

# Función para insertar datos en la base de datos
def save_to_database(license_plate, image_path):
    try:
        with connection.cursor() as cursor:
            # Insertar la información en la base de datos
            sql = "INSERT INTO Informacion (num_placa, imagen) VALUES (%s, %s)"
            cursor.execute(sql, (license_plate, image_path))
            connection.commit()  # Confirmar la inserción
            print(f'Información guardada en la base de datos: {license_plate}')
    except pymysql.MySQLError as e:
        print(f'Error al guardar en la base de datos: {e}')

if __name__ == "__main__":
    processor = PlateRecognition()
    image_path = 'examples/image_example.jpeg'
    vehicle_image, license_plate, info = processor.process_static_image(image_path, draw=True)

    # Verificar si la placa no está repetida
    if license_plate and license_plate not in saved_plates:
        # Agregar la placa al conjunto de placas guardadas
        saved_plates.add(license_plate)
        
        # Generar el nombre de archivo basado en la placa
        capture_filename = f'captures/{license_plate}.png'
        
        # Guardar la imagen capturada
        cv2.imwrite(capture_filename, vehicle_image)
        print(f'Captura guardada: {capture_filename}')
        
        # Guardar la información en la base de datos
        save_to_database(license_plate, capture_filename)
    else:
        if license_plate in saved_plates:
            print('La placa ya ha sido registrada previamente.')

    print(f'License plate: {license_plate} \nInfo: {info}')
    cv2.imshow('plate recognition', vehicle_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# Cerrar la conexión a la base de datos al final
connection.close()
