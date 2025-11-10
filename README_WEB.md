# Sistema de Detección de Armas - Versión Web

Este proyecto es una aplicación web desarrollada con Flask y PostgreSQL para la detección de armas en tiempo real utilizando el modelo YOLOv8.

## 🚀 Características

- **Interfaz Web Moderna**: Interfaz responsive desarrollada con HTML5, CSS3 y JavaScript
- **Detección en Tiempo Real**: Streaming de video con detección de armas usando WebSockets
- **Base de Datos PostgreSQL**: Almacenamiento persistente de todas las detecciones
- **API RESTful**: Endpoints para consultar detecciones, estadísticas y configuraciones
- **Alertas en Tiempo Real**: Notificaciones instantáneas cuando se detectan armas
- **Exportación de Datos**: Descarga de historial de detecciones en formato JSON

## 📋 Requisitos Previos

- Python 3.7 o superior
- PostgreSQL instalado y configurado
- Cámara web (opcional, para detección en tiempo real)

## 🛠️ Instalación

### 1. Clonar el Repositorio

```bash
git clone https://github.com/Spike1192/Reconocimiento-Armas.git
cd Reconocimiento-Armas
```

### 2. Crear y Activar Entorno Virtual

```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar PostgreSQL

#### Crear Base de Datos

```sql
-- Conectarse a PostgreSQL
psql -U postgres

-- Crear base de datos
CREATE DATABASE weapon_detection;

-- Crear usuario (opcional)
CREATE USER weapon_user WITH PASSWORD 'tu_password';
GRANT ALL PRIVILEGES ON DATABASE weapon_detection TO weapon_user;
```

#### Configurar Variables de Entorno (Opcional)

Puedes crear un archivo `.env` o configurar variables de entorno:

```bash
# Windows
set POSTGRES_HOST=localhost
set POSTGRES_PORT=5432
set POSTGRES_USER=postgres
set POSTGRES_PASSWORD=tu_password
set POSTGRES_DB=weapon_detection

# Linux/Mac
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export POSTGRES_USER=postgres
export POSTGRES_PASSWORD=tu_password
export POSTGRES_DB=weapon_detection
```

O editar directamente `config.py` con tus credenciales.

### 5. Inicializar Base de Datos

```bash
python init_db.py
```

## ▶️ Ejecutar la Aplicación

```bash
python app.py
```

La aplicación estará disponible en: `http://localhost:5000`

## 📖 Uso de la Aplicación

1. **Acceder a la Interfaz**: Abre tu navegador y ve a `http://localhost:5000`
2. **Video en Tiempo Real**: El video de la cámara se mostrará automáticamente
3. **Controles**:
   - **Activar/Desactivar Detección**: Toggle para pausar la detección
   - **Umbral de Confianza**: Ajusta la sensibilidad del detector (10-100%)
   - **Capturar Frame**: Guarda una captura del frame actual
4. **Ver Detecciones**: El panel derecho muestra todas las detecciones con sus detalles
5. **Exportar Datos**: Botón para descargar el historial completo en JSON

## 🔌 API Endpoints

### Obtener Detecciones

```
GET /api/detections
```

### Obtener Estadísticas

```
GET /api/stats
```

### Obtener Detección Específica

```
GET /api/detection/<id>
```

### Activar/Desactivar Detección

```
POST /api/toggle_detection
Body: { "enabled": true/false }
```

### Actualizar Umbral de Confianza

```
POST /api/update_confidence
Body: { "confidence": 0.5 }
```

## 🗄️ Estructura de la Base de Datos

### Tabla: weapon_detections

| Campo           | Tipo         | Descripción                         |
| --------------- | ------------ | ----------------------------------- |
| id              | INTEGER      | ID único (Primary Key)              |
| timestamp       | DATETIME     | Fecha y hora de la detección        |
| weapon_count    | INTEGER      | Número de armas detectadas          |
| alert_level     | VARCHAR(20)  | Nivel de alerta (high, medium, low) |
| detection_types | TEXT         | Tipos de armas detectadas           |
| image_path      | VARCHAR(255) | Ruta a la imagen capturada          |
| metadata        | TEXT         | JSON con información adicional      |

## 🏗️ Estructura del Proyecto

```
Reconocimiento-Armas/
├── app.py                 # Aplicación Flask principal
├── config.py              # Configuración
├── models.py              # Modelos de base de datos
├── init_db.py             # Script de inicialización de BD
├── templates/             # Plantillas HTML
│   └── index.html
├── static/                 # Archivos estáticos
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js
├── process/                # Procesamiento de detección
│   └── weapon_detection.py
├── captures/               # Imágenes capturadas
└── requirements.txt        # Dependencias
```

## 🔧 Configuración Avanzada

### Cambiar Puerto

Edita `app.py`:

```python
socketio.run(app, host='0.0.0.0', port=5000, debug=True)
```

### Cambiar Cámara

Edita `app.py` en la función `generate_frames()`:

```python
camera = cv2.VideoCapture(0)  # 0 = primera cámara, 1 = segunda, etc.
```

## 🐛 Solución de Problemas

### Error de Conexión a PostgreSQL

- Verifica que PostgreSQL esté corriendo
- Confirma las credenciales en `config.py`
- Asegúrate de que la base de datos existe

### Error al Iniciar Cámara

- Verifica que la cámara esté conectada
- Cambia el índice de la cámara en `app.py` (0, 1, 2...)
- En algunos sistemas, puede requerir permisos de administrador

### Error de Módulos

```bash
pip install -r requirements.txt
```

## 📝 Notas

- La aplicación usa WebSockets para comunicación en tiempo real
- Las imágenes se guardan en el directorio `captures/`
- El modelo YOLOv8 se carga automáticamente desde `runs/detect/train9/weights/best.pt`

## 📄 Licencia

Este proyecto es parte de un proyecto académico.
