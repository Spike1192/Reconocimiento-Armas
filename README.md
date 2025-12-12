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

Autores: Edgar Lopez, Jaider Lopez, Jorge Soto y Ricardo Arias
