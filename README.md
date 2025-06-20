# Sistema de Detección de Armas con YOLOv8

Este proyecto es una aplicación de escritorio desarrollada en Python con PyQt5 para la detección de armas en tiempo real utilizando el modelo YOLOv8. El sistema analiza un flujo de video (cámara en vivo o archivo de video) y resalta las armas detectadas, guardando capturas y registrando la información en una base de datos.

## 🚀 Características Principales

- **Detección en Tiempo Real**: Utiliza YOLOv8 para analizar flujos de video y detectar armas con alta precisión.
- **Interfaz Gráfica Intuitiva**: Desarrollada con PyQt5, permite una fácil interacción y visualización de los resultados.
- **Selección de Fuente de Video**: Permite al usuario elegir entre una cámara en vivo, un archivo de video o una imagen estática.
- **Registro de Eventos**: Guarda un registro de cada detección, incluyendo una captura de pantalla y metadatos (fecha, hora, tipo de arma).
- **Exportación de Datos**: Permite exportar los registros de detección a archivos CSV o PDF.
- **Visualización de Capturas**: Muestra una galería de las capturas de armas detectadas.
- **Alertas Configurables**: Sistema de alertas visuales en la interfaz cuando se detecta un arma.

## 🛠️ Tecnologías Utilizadas

- **Python 3.7+**
- **PyQt5**: Para la interfaz gráfica de usuario.
- **OpenCV**: Para el procesamiento de imágenes y video.
- **Ultralytics (YOLOv8)**: Para el modelo de detección de objetos.
- **PyMySQL**: Para la conexión con la base de datos MySQL (si se utiliza).
- **Pandas**: Para la manipulación y exportación de datos.

## 📦 Instalación y Configuración

Sigue estos pasos para poner en marcha el proyecto en tu máquina local.

### 1. Clonar el Repositorio

```bash
git clone https://github.com/Spike1192/Reconocimiento-Armas.git
cd Reconocimiento-Armas
```

### 2. Crear y Activar un Entorno Virtual

Es altamente recomendable crear un entorno virtual para aislar las dependencias del proyecto.

```bash
# Crear el entorno virtual
python -m venv venv

# Activar en Windows
.\venv\Scripts\activate

# Activar en macOS/Linux
source venv/bin/activate
```

### 3. Instalar Dependencias

Instala todas las librerías necesarias utilizando el archivo `requirements.txt`.

```bash
pip install -r requirements.txt
```

## ▶️ Cómo Ejecutar la Aplicación

Una vez que hayas completado la instalación, puedes iniciar la aplicación con el siguiente comando:

```bash
python main_app.py
```

Esto abrirá directamente la interfaz del sistema de detección de armas.

## 📖 Uso de la Aplicación

1.  **Seleccionar Fuente**: Al iniciar la aplicación, utiliza los botones para seleccionar si deseas analizar una imagen, un video desde un archivo o la cámara en vivo.
2.  **Iniciar Detección**: Una vez seleccionada la fuente, el sistema comenzará a analizar el contenido en busca de armas.
3.  **Visualizar Resultados**: Las detecciones se mostrarán en tiempo real en el visor de video. Las capturas de las detecciones se añadirán a la galería.
4.  **Exportar Datos**: Utiliza los botones correspondientes para exportar el historial de detecciones a un archivo CSV o PDF.
