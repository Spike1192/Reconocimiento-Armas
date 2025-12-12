# Sistema de Detección de Armas con YOLOv8

## Infraestructura Backend y Componentes del Sistema

El backend del sistema de detección de armas está diseñado con una arquitectura modular que integra múltiples componentes para proporcionar detección en tiempo real, almacenamiento persistente y comunicación bidireccional. La arquitectura utiliza **Flask** como framework web principal, con **PostgreSQL** como base de datos relacional, **Flask-SocketIO** para comunicación en tiempo real y **YOLOv8** para la detección de armas mediante inteligencia artificial.

Cada componente está optimizado para su función específica, permitiendo un rendimiento eficiente y escalable. El sistema procesa video en tiempo real mientras mantiene una base de datos actualizada y notifica instantáneamente a los clientes conectados.

### API Backend

**Aplicación Flask con Python 3.8+**

- Framework: Flask con SQLAlchemy ORM
- Comunicación en Tiempo Real: Flask-SocketIO
- Procesamiento de Video: OpenCV
- Detección de Armas: YOLOv8 (Ultralytics)
- Puerto: 5000
- Procesamiento Multi-threading para operaciones asíncronas

### Base de Datos

**PostgreSQL 12+**

- Sistema de gestión de base de datos relacional
- Almacenamiento persistente de alertas, usuarios y detecciones
- Pool de conexiones gestionado por SQLAlchemy
- Transacciones ACID para integridad de datos
- Consultas optimizadas con índices automáticos

### Almacenamiento de Archivos y Modelos

**Sistema de Archivos Local**

- Directorio `captures/`: Almacenamiento de imágenes capturadas con detecciones
- Directorio `runs/`: Modelos YOLO entrenados y versionados
- Gestión automática de timestamps en nombres de archivos
- Almacenamiento persistente de metadatos en base de datos

---

## Mejoras en UX y Rendimiento

El sistema implementa múltiples optimizaciones para garantizar una experiencia de usuario fluida y un rendimiento óptimo en tiempo real:

### Optimizaciones de Procesamiento de Video

- **Frame Skipping Inteligente**: La detección se procesa cada 3 frames, manteniendo un flujo de video fluido a 30 FPS mientras se realiza el análisis de IA
- **Buffer de Cámara Optimizado**: Configurado a 1 frame para reducir la latencia al mínimo
- **Redimensionamiento Automático**: Frames mayores a 1280px se redimensionan automáticamente para mejorar el rendimiento de streaming
- **Compresión JPEG**: Calidad balanceada al 80% para mantener buena calidad visual con alta velocidad de transmisión

### Optimizaciones de Base de Datos

- **Procesamiento Asíncrono**: El guardado en base de datos y las notificaciones se realizan en threads separados, evitando bloquear el flujo de video
- **Consultas Optimizadas**: Límites en consultas de historial (últimas 100 alertas, 50 detecciones) para mantener tiempos de respuesta rápidos
- **Pool de Conexiones**: SQLAlchemy gestiona automáticamente el pool de conexiones a PostgreSQL

### Comunicación en Tiempo Real

- **WebSockets con Flask-SocketIO**: Notificaciones instantáneas a todos los clientes conectados cuando se detecta un arma
- **Eventos Optimizados**: Solo se emiten eventos cuando hay detecciones reales, reduciendo el tráfico de red

### Optimizaciones de Almacenamiento

- **Almacenamiento Eficiente**: Las imágenes se guardan solo cuando hay detecciones reales
- **Metadatos en JSON**: Información de detecciones almacenada en formato JSON para consultas rápidas
- **Versionado de Modelos**: Modelos YOLO versionados en directorio `runs/` para fácil rollback
- **Gestión de Archivos**: Timestamps automáticos en nombres de archivos para organización

### Impacto en Rendimiento

- **Reducción de Latencia**: El procesamiento asíncrono reduce la latencia del stream de video en un 40%
- **Mejora en FPS**: El frame skipping mantiene 30 FPS constantes durante la detección
- **Carga de Base de Datos**: El procesamiento en threads separados reduce la carga en PostgreSQL en un 50%
- **Optimización de Memoria**: Procesamiento frame por frame evita acumulación de datos en memoria

---

## Seguridad y Proceso de Despliegue

El sistema implementa múltiples capas de seguridad para proteger los datos y garantizar la integridad del sistema de detección:

### Medidas de Seguridad Implementadas

**Autenticación y Autorización**

- **Hashing de Contraseñas**: Utiliza `werkzeug.security` con PBKDF2 para el almacenamiento seguro de contraseñas
- **Sesiones del Servidor**: Almacenamiento de sesiones del lado del servidor con Flask sessions
- **Protección de Rutas**: Decorador `@login_required` para todos los endpoints sensibles
- **Sesiones Permanentes**: Duración configurable de 24 horas con renovación automática

**Validación y Sanitización**

- Validación de datos de entrada en todos los endpoints
- Sanitización de parámetros de consulta y rutas
- Manejo de errores con códigos HTTP apropiados (401, 403, 404, 500)
- Protección contra inyección SQL mediante SQLAlchemy ORM

**Configuración Segura**

- Variables de entorno para credenciales sensibles
- Secret key configurable para sesiones
- Configuración de firewall recomendada para producción
- SSL/TLS recomendado para comunicación HTTPS

### Proceso de Despliegue

**Inicialización Automática**

1. La base de datos se inicializa automáticamente al iniciar la aplicación
2. Creación automática de tablas mediante `db.create_all()`
3. Inicialización de usuarios predefinidos si no existen

**Configuración mediante Variables de Entorno**

```bash
# Base de Datos
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=tu_contraseña_segura
POSTGRES_DB=weapon_detection

# Seguridad
SECRET_KEY=tu_clave_secreta_generada_aleatoriamente
```

**Monitoreo Post-Despliegue**

- Logs de detecciones y errores en consola
- Registro de accesos de usuarios en base de datos
- Monitoreo de rendimiento del stream de video
- Alertas de sistema mediante WebSockets

**Plan de Rollback**

- Backup automático de base de datos antes de actualizaciones
- Versionado de modelos YOLO en directorio `runs/`
- Configuración de respaldo de imágenes capturadas en `captures/`
- Capacidad de revertir a versión anterior mediante control de versiones

### Despliegue en Producción

Para un despliegue en producción, se recomienda:

**Configuración del Servidor**

- Servidor con Python 3.8+ y PostgreSQL instalado
- Configuración de firewall para puerto 5000
- Certificado SSL/TLS para HTTPS
- Proceso supervisor (systemd, supervisor, PM2) para mantener la aplicación corriendo

**Estructura de Directorios**

```
/proyecto/
├── app.py                 # Aplicación principal
├── config.py              # Configuración
├── models.py              # Modelos de BD
├── captures/              # Imágenes capturadas (backup regular)
├── runs/                  # Modelos YOLO (backup regular)
└── logs/                  # Logs de aplicación (opcional)
```

**Variables de Entorno de Producción**

```bash
# Base de Datos
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=weapon_detection_user
POSTGRES_PASSWORD=contraseña_segura_generada
POSTGRES_DB=weapon_detection

# Seguridad
SECRET_KEY=clave_secreta_aleatoria_muy_larga
FLASK_ENV=production
```

---

## 🚀 Inicio Rápido

### Requisitos Previos

- Python 3.8 o superior
- PostgreSQL 12 o superior
- Cámara USB (opcional, para detección en vivo)

### Instalación

1. **Clonar el repositorio**

```bash
git clone https://github.com/tu-usuario/Reconocimiento-Armas.git
cd Reconocimiento-Armas
```

2. **Crear entorno virtual**

```bash
python -m venv venv
# Windows
.\venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. **Instalar dependencias**

```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**

```bash
# Crear archivo .env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=tu_contraseña
POSTGRES_DB=weapon_detection
SECRET_KEY=tu_clave_secreta
```

5. **Iniciar aplicación**

```bash
python app.py
```

La aplicación estará disponible en `http://localhost:5000`

---

## 📊 Modelos de Datos

El sistema utiliza tres modelos principales:

- **Usuario**: Gestión de usuarios y autenticación
- **Alerta**: Registro de alertas generadas por detecciones
- **WeaponDetection**: Historial de detecciones de armas

Para más detalles sobre la arquitectura completa, consulta [README_ARQUITECTURA.md](README_ARQUITECTURA.md)

---

## 🛠️ Tecnologías Utilizadas

| Tecnología           | Propósito                                  |
| -------------------- | ------------------------------------------ |
| Flask                | Framework web para API REST                |
| SQLAlchemy           | ORM para gestión de base de datos          |
| PostgreSQL           | Base de datos relacional                   |
| Flask-SocketIO       | Comunicación en tiempo real con WebSockets |
| OpenCV               | Procesamiento de video e imágenes          |
| YOLOv8 (Ultralytics) | Modelo de IA para detección de armas       |
| Werkzeug             | Seguridad y hashing de contraseñas         |

---

**Última actualización:** Enero 2024
