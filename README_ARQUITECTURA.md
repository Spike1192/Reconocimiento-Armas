# Arquitectura del Sistema de Detección de Armas

## 📋 Tabla de Contenidos

1. [Visión General](#visión-general)
2. [Arquitectura de la Base de Datos](#arquitectura-de-la-base-de-datos)
3. [Arquitectura de la API](#arquitectura-de-la-api)
4. [Modelos de Datos](#modelos-de-datos)
5. [Endpoints de la API](#endpoints-de-la-api)
6. [Comunicación en Tiempo Real](#comunicación-en-tiempo-real)
7. [Flujo de Datos](#flujo-de-datos)
8. [Configuración](#configuración)

---

## 🎯 Visión General

Este sistema es una aplicación web desarrollada con **Flask** que utiliza inteligencia artificial (YOLO) para detectar armas en tiempo real mediante cámaras de seguridad. El sistema está compuesto por:

- **Backend**: Flask con SQLAlchemy ORM
- **Base de Datos**: PostgreSQL
- **Comunicación en Tiempo Real**: Flask-SocketIO
- **Procesamiento de Video**: OpenCV
- **Detección de Armas**: YOLOv8 (Ultralytics)

---

## 🗄️ Arquitectura de la Base de Datos

### Sistema de Gestión de Base de Datos

El proyecto utiliza **PostgreSQL** como sistema de gestión de base de datos relacional. La configuración se realiza mediante variables de entorno o valores por defecto.

### Configuración de Conexión

```python
# Configuración por defecto (config.py)
POSTGRES_HOST = 'localhost'
POSTGRES_PORT = '5432'
POSTGRES_USER = 'postgres'
POSTGRES_PASSWORD = '123456'
POSTGRES_DB = 'weapon_detection'
```

### ORM: SQLAlchemy

El proyecto utiliza **SQLAlchemy** como Object-Relational Mapping (ORM), lo que permite:

- Definir modelos de datos como clases Python
- Realizar consultas usando sintaxis Python
- Gestionar transacciones de forma automática
- Migraciones de esquema simplificadas

---

## 📊 Modelos de Datos

### 1. **Usuario** (`usuarios`)

Modelo que representa a los usuarios del sistema con autenticación.

**Campos:**
- `idUsuario` (String, PK): Identificador único del usuario
- `Nombre` (String): Nombre completo del usuario
- `Clave` (String): Hash de la contraseña (usando Werkzeug)
- `Email` (String): Correo electrónico
- `Rol` (String): Rol del usuario (Administrador, Operador, Supervisor, etc.)
- `UbicacionAsignada` (String): Ubicación asignada al usuario
- `TelefonoContacto` (String): Teléfono de contacto
- `UltimoAcceso` (DateTime): Fecha y hora del último acceso

**Métodos:**
- `autenticar(clave_ingresada)`: Verifica si la contraseña es correcta
- `ingreso_sistema()`: Registra el último acceso al sistema
- `to_dict()`: Convierte el objeto a diccionario (sin incluir contraseña)

### 2. **Alerta** (`alertas`)

Modelo que almacena las alertas generadas por detección de armas.

**Campos:**
- `idAlerta` (Integer, PK): Identificador único de la alerta
- `tipoAlerta` (String): Tipo de alerta generada
- `fechaHora` (DateTime): Fecha y hora de la alerta
- `camara` (String): Cámara que generó la alerta (default: 'CAMERA 01')
- `weapon_count` (Integer): Cantidad de armas detectadas
- `alert_level` (String): Nivel de alerta (high, medium, low)
- `detection_types` (Text): Tipos de armas detectadas (separados por comas)
- `image_path` (String): Ruta a la imagen capturada
- `detection_metadata` (Text): JSON con información adicional de la detección
- `motivo` (Text): Motivo de la alarma
- `solucion` (Text): Solución aplicada a la alerta

**Métodos:**
- `generar_alerta()`: Genera una nueva alerta (según UML)
- `enviar_notificacion()`: Envía notificación de la alerta (según UML)
- `to_dict()`: Convierte el objeto a diccionario

### 3. **WeaponDetection** (`weapon_detections`)

Modelo que almacena el historial de detecciones de armas (compatibilidad).

**Campos:**
- `id` (Integer, PK): Identificador único
- `timestamp` (DateTime): Fecha y hora de la detección
- `weapon_count` (Integer): Cantidad de armas detectadas
- `alert_level` (String): Nivel de alerta (high, medium, low)
- `detection_types` (Text): Tipos de armas detectadas
- `image_path` (String): Ruta a la imagen capturada
- `detection_metadata` (Text): JSON con metadatos adicionales

**Métodos:**
- `to_dict()`: Convierte el objeto a diccionario

---

## 🔌 Arquitectura de la API

### Framework: Flask

La aplicación utiliza **Flask** como framework web, proporcionando:

- Servidor HTTP integrado
- Sistema de rutas y decoradores
- Manejo de sesiones
- Integración con templates HTML

### Estructura de la API

La API sigue un patrón **RESTful** con los siguientes componentes:

#### 1. **Autenticación y Sesiones**

- **Sesiones Flask**: Almacenamiento de sesiones del lado del servidor
- **Decorador `@login_required`**: Protección de rutas que requieren autenticación
- **Sesiones Permanentes**: Duración de 24 horas

#### 2. **Endpoints REST**

Todos los endpoints devuelven respuestas en formato **JSON**.

---

## 📡 Endpoints de la API

### Autenticación

#### `POST /api/login`
Autentica un usuario en el sistema.

**Request Body:**
```json
{
  "usuario": "admin",
  "clave": "password123"
}
```

**Response (200):**
```json
{
  "success": true,
  "usuario": {
    "idUsuario": "admin",
    "Nombre": "Administrador",
    "Email": "admin@example.com",
    "Rol": "Administrador",
    ...
  },
  "message": "Login exitoso"
}
```

#### `POST /api/logout`
Cierra la sesión del usuario actual.

**Response (200):**
```json
{
  "success": true,
  "message": "Sesión cerrada"
}
```

#### `GET /api/check_session`
Verifica si hay una sesión activa.

**Response (200):**
```json
{
  "authenticated": true,
  "usuario": { ... }
}
```

### Gestión de Usuarios

#### `GET /api/user/profile`
Obtiene el perfil del usuario autenticado.

**Requisitos:** Autenticación requerida

**Response (200):**
```json
{
  "idUsuario": "admin",
  "Nombre": "Administrador",
  ...
}
```

### Gestión de Alertas

#### `GET /api/alertas`
Obtiene todas las alertas (últimas 100).

**Requisitos:** Autenticación requerida

**Response (200):**
```json
[
  {
    "idAlerta": 1,
    "tipoAlerta": "ALERTA ALTA: 2 arma(s) detectada(s)",
    "fechaHora": "2024-01-15T10:30:00",
    "camara": "CAMERA 01",
    "weapon_count": 2,
    "alert_level": "high",
    ...
  },
  ...
]
```

#### `GET /api/alerta/<alerta_id>`
Obtiene los detalles de una alerta específica.

**Requisitos:** Autenticación requerida

**Response (200):**
```json
{
  "idAlerta": 1,
  "tipoAlerta": "...",
  ...
}
```

#### `PUT /api/alerta/<alerta_id>`
Actualiza el motivo y solución de una alerta.

**Requisitos:** Autenticación requerida

**Request Body:**
```json
{
  "motivo": "Detección confirmada",
  "solucion": "Se contactó a seguridad"
}
```

**Response (200):**
```json
{
  "idAlerta": 1,
  "motivo": "Detección confirmada",
  "solucion": "Se contactó a seguridad",
  ...
}
```

### Detecciones

#### `GET /api/detections`
Obtiene el historial de detecciones (últimas 50).

**Requisitos:** Autenticación requerida

**Response (200):**
```json
[
  {
    "id": 1,
    "timestamp": "2024-01-15T10:30:00",
    "weapon_count": 2,
    "alert_level": "high",
    ...
  },
  ...
]
```

#### `GET /api/detection/<detection_id>`
Obtiene los detalles de una detección específica.

**Requisitos:** Autenticación requerida

#### `GET /api/stats`
Obtiene estadísticas del sistema.

**Requisitos:** Autenticación requerida

**Response (200):**
```json
{
  "total": 150,
  "high_alerts": 25,
  "medium_alerts": 50
}
```

### Control del Sistema

#### `POST /api/toggle_detection`
Activa/desactiva la detección de armas.

**Requisitos:** Autenticación requerida

**Request Body:**
```json
{
  "enabled": true
}
```

#### `POST /api/update_confidence`
Actualiza el umbral de confianza para las detecciones.

**Requisitos:** Autenticación requerida

**Request Body:**
```json
{
  "confidence": 0.6
}
```

### Streaming de Video

#### `GET /video_feed`
Stream de video en tiempo real con detección de armas.

**Requisitos:** Autenticación requerida

**Response:** Stream MJPEG (multipart/x-mixed-replace)

**Características:**
- FPS objetivo: 30 FPS
- Procesamiento de detección cada 3 frames (para mantener rendimiento)
- Calidad JPEG: 80%
- Redimensionamiento automático si el ancho > 1280px

### Servicio de Archivos

#### `GET /captures/<filename>`
Sirve imágenes capturadas desde el directorio `captures/`.

#### `GET /script.js`
Sirve el archivo JavaScript principal.

#### `GET /style.css`
Sirve el archivo CSS principal.

#### `GET /svg/<filename>`
Sirve archivos SVG desde `templates/svg/`.

---

## 🔄 Comunicación en Tiempo Real

### WebSockets: Flask-SocketIO

El sistema utiliza **Flask-SocketIO** para comunicación bidireccional en tiempo real entre el servidor y los clientes.

#### Eventos del Servidor

##### `weapon_detected`
Emitido cuando se detecta un arma.

**Datos:**
```json
{
  "alerta_id": 123,
  "detections": [
    {
      "bbox": [100, 200, 300, 400],
      "confidence": 0.85,
      "class_name": "gun"
    }
  ],
  "summary": {
    "weapons_detected": 1,
    "alert_level": "high",
    "detection_types": ["gun"]
  },
  "tipo_alerta": "ALERTA ALTA: 1 arma(s) detectada(s)",
  "timestamp": "2024-01-15T10:30:00",
  "camara": "CAMERA 01"
}
```

##### `status`
Emitido cuando un cliente se conecta.

**Datos:**
```json
{
  "message": "Conectado al sistema de detección"
}
```

#### Eventos del Cliente

##### `connect`
Maneja la conexión de un cliente.

##### `disconnect`
Maneja la desconexión de un cliente.

---

## 🔀 Flujo de Datos

### 1. Flujo de Detección de Armas

```
Cámara → OpenCV → YOLO Detector → Procesamiento
                                          ↓
                                    ¿Armas detectadas?
                                          ↓
                                    Sí → Guardar en BD
                                          ↓
                                    Crear Alerta
                                          ↓
                                    Emitir WebSocket
                                          ↓
                                    Clientes notificados
```

### 2. Flujo de Autenticación

```
Cliente → POST /api/login
              ↓
         Validar credenciales
              ↓
         ¿Válidas?
              ↓
         Sí → Crear sesión
              ↓
         Actualizar UltimoAcceso
              ↓
         Retornar datos del usuario
```

### 3. Flujo de Almacenamiento de Alertas

```
Detección → save_detection_to_db()
                ↓
           Guardar imagen en /captures
                ↓
           Crear registro en tabla 'alertas'
                ↓
           Crear registro en tabla 'weapon_detections'
                ↓
           Commit transacción
                ↓
           Retornar ID de alerta
                ↓
           Emitir evento WebSocket
```

### 4. Optimizaciones de Rendimiento

- **Frame Skipping**: La detección se procesa cada 3 frames para mantener FPS fluido
- **Threading**: El guardado en BD y notificaciones se realizan en threads separados
- **Buffer de Cámara**: Configurado a 1 para reducir latencia
- **Redimensionamiento**: Frames > 1280px se redimensionan automáticamente
- **Calidad JPEG**: 80% para balance entre calidad y velocidad

---

## ⚙️ Configuración

### Variables de Entorno

El sistema puede configurarse mediante variables de entorno:

```bash
# Base de Datos
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=tu_contraseña
POSTGRES_DB=weapon_detection

# Seguridad
SECRET_KEY=tu_clave_secreta_aqui
```

### Inicialización de la Base de Datos

La base de datos se inicializa automáticamente al iniciar la aplicación mediante:

```python
def init_db():
    with app.app_context():
        db.create_all()  # Crea todas las tablas
        crear_usuarios_predefinidos()  # Crea usuarios iniciales
```

### Estructura de Directorios

```
proyecto/
├── app.py                 # Aplicación Flask principal
├── config.py              # Configuración
├── models.py              # Modelos de base de datos
├── process/
│   └── weapon_detection.py  # Lógica de detección YOLO
├── templates/             # Templates HTML
├── captures/              # Imágenes capturadas
└── runs/                  # Modelos YOLO entrenados
```

---

## 🔒 Seguridad

### Autenticación

- **Hashing de Contraseñas**: Utiliza `werkzeug.security.generate_password_hash`
- **Verificación**: Utiliza `werkzeug.security.check_password_hash`
- **Sesiones**: Almacenadas del lado del servidor con Flask sessions
- **Protección de Rutas**: Decorador `@login_required` para endpoints protegidos

### Validación

- Validación de datos de entrada en endpoints
- Sanitización de parámetros de consulta
- Manejo de errores con códigos HTTP apropiados

---

## 📈 Escalabilidad

### Consideraciones

1. **Base de Datos**: PostgreSQL soporta alta concurrencia
2. **Conexiones**: SQLAlchemy gestiona pool de conexiones
3. **WebSockets**: Flask-SocketIO soporta múltiples clientes simultáneos
4. **Procesamiento**: Threading para operaciones asíncronas

### Posibles Mejoras

- Implementar Redis para sesiones distribuidas
- Usar Celery para procesamiento de tareas pesadas
- Implementar caché para consultas frecuentes
- Balanceador de carga para múltiples instancias

---

## 🛠️ Tecnologías Utilizadas

| Tecnología | Versión/Descripción | Propósito |
|------------|---------------------|-----------|
| Flask | Framework web | Backend API |
| SQLAlchemy | ORM | Gestión de base de datos |
| PostgreSQL | SGBD | Base de datos relacional |
| Flask-SocketIO | WebSockets | Comunicación en tiempo real |
| OpenCV | Procesamiento de video | Captura y procesamiento de frames |
| YOLOv8 | Ultralytics | Detección de armas |
| Werkzeug | Seguridad | Hashing de contraseñas |

---

## 📝 Notas Adicionales

- El sistema está diseñado para funcionar con una cámara USB (índice 1)
- Las imágenes capturadas se almacenan en el directorio `captures/`
- El modelo YOLO se carga desde `runs/detect/train9/weights/best.pt` si existe
- El sistema soporta múltiples tipos de armas: gun, knife, sword
- Los niveles de alerta se determinan según cantidad y confianza de detecciones

---

**Última actualización:** Enero 2024

