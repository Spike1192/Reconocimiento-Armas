Manual de Usuario
Descripción General
Esta aplicación es un sistema de Reconocimiento de Placas Vehiculares que permite la detección en tiempo real de placas de automóviles mediante video en vivo. Las imágenes capturadas se almacenan en una base de datos junto con la información de la placa, y son mostradas en una interfaz gráfica minimalista e intuitiva.

Características Principales
Detección en Tiempo Real de placas vehiculares mediante video.
Almacenamiento de Capturas en una base de datos MySQL.
Visualización de las capturas en una lista de tarjetas.
Interfaz Minimalista: Visualización clara y sencilla de las imágenes detectadas.
Detalle de Captura: Posibilidad de visualizar una imagen en tamaño grande con más detalles.
Requisitos Previos:
-Python instalado (versión 3.7 o superior).
-MySQL instalado y configurado.
Dependencias necesarias instaladas:
bash
Copiar código
pip install PyQt5 pymysql opencv-python
Base de Datos creada en MySQL con la tabla Informacion:
sql
Copiar código
CREATE DATABASE placas;
USE placas;

CREATE TABLE Informacion (
    id INT AUTO_INCREMENT PRIMARY KEY,
    num_placa VARCHAR(20) NOT NULL UNIQUE,
    imagen VARCHAR(255) NOT NULL,
    hora DATETIME DEFAULT CURRENT_TIMESTAMP
);
Instalación
Clona el repositorio en tu máquina local:
bash
Copiar código
git clone https://github.com/tu-usuario/tu-repositorio.git
Navega al directorio del proyecto:
bash
Copiar código
cd tu-repositorio
Instala las dependencias requeridas:
bash
Copiar código
pip install -r requirements.txt
Configura la conexión a la base de datos en db/main.py:
python
Copiar código
connection = pymysql.connect(
    host= "localhost",
    user= "root",
    password= "",
    db="placas"
)
Uso de la Aplicación
1. Inicio del Programa
Para iniciar la aplicación, abre la terminal en la carpeta del proyecto y ejecuta el siguiente comando:

bash
Copiar código
python interfaz_grafica.py
Esto abrirá la interfaz gráfica con las siguientes secciones:

2. Interfaz Gráfica
La interfaz está dividida en dos partes principales:

Izquierda - Lista de Capturas
Aquí se mostrarán todas las capturas guardadas de los vehículos.
Cada captura se muestra en una carta, con el título de la placa detectada.
Las capturas nuevas se añaden automáticamente cuando se detecta una placa en tiempo real.
Derecha - Video en Tiempo Real
Aquí se muestra la detección en tiempo real del video.
Cada vez que se detecta una placa, se guarda una captura si aún no ha sido registrada.
3. Visualizar Detalles de una Captura
Haz clic en cualquiera de las tarjetas en la lista de la izquierda para abrir una ventana secundaria.
La ventana mostrará la imagen capturada en tamaño grande, junto con el nombre de la placa.
En la parte inferior, hay un botón de "Volver" que te permitirá regresar a la vista principal.
Funcionalidades del Programa
Detección en Tiempo Real
El sistema detecta las placas en tiempo real a través de la cámara o un archivo de video.
Las placas detectadas son almacenadas junto con una captura del vehículo en la base de datos MySQL.
Almacenamiento en Base de Datos
Cada captura contiene la información de la placa y se guarda en la base de datos con los siguientes campos:
num_placa: Número de la placa detectada.
imagen: Ruta a la imagen capturada.
hora: Fecha y hora de la detección.
Visualización de Capturas
Las capturas almacenadas se visualizan en tarjetas en la parte izquierda de la interfaz.
Cada tarjeta contiene:
Una imagen en miniatura del vehículo capturado.
El número de la placa del vehículo.
Controles de la Aplicación
Atajos de Teclado
Esc: Cierra la ventana del programa.
Clic en Tarjeta: Abre la imagen en tamaño grande.
Botón Volver: Cierra la vista detallada de la captur
