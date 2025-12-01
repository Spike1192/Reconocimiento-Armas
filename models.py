"""
Modelos de base de datos usando SQLAlchemy
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import json

db = SQLAlchemy()

class WeaponDetection(db.Model):
    """Modelo para almacenar detecciones de armas"""
    
    __tablename__ = 'weapon_detections'
    
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    weapon_count = db.Column(db.Integer, nullable=False)
    alert_level = db.Column(db.String(20), nullable=False)  # high, medium, low
    detection_types = db.Column(db.Text)  # Tipos de armas detectadas
    image_path = db.Column(db.String(255))  # Ruta a la imagen capturada
    detection_metadata = db.Column(db.Text)  # JSON con información adicional (renombrado de 'metadata' porque es palabra reservada)
    
    def __repr__(self):
        return f'<WeaponDetection {self.id}: {self.weapon_count} armas - {self.alert_level}>'
    
    def to_dict(self):
        """Convertir a diccionario"""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'weapon_count': self.weapon_count,
            'alert_level': self.alert_level,
            'detection_types': self.detection_types,
            'image_path': self.image_path,
            'metadata': self.detection_metadata
        }


class Usuario(db.Model):
    """Modelo de Usuario según el UML - Sistema de autenticación sin registro"""
    
    __tablename__ = 'usuarios'
    
    idUsuario = db.Column(db.String(50), primary_key=True)
    Nombre = db.Column(db.String(100), nullable=False)
    Clave = db.Column(db.String(255), nullable=False)  # Hash de la contraseña
    Email = db.Column(db.String(100))
    Rol = db.Column(db.String(50))  # Administrador, Operador, Supervisor, etc.
    UbicacionAsignada = db.Column(db.String(100))
    TelefonoContacto = db.Column(db.String(20))
    UltimoAcceso = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<Usuario {self.idUsuario}: {self.Nombre}>'
    
    def autenticar(self, clave_ingresada):
        """
        Método autenticar() según el UML
        Verifica si la contraseña ingresada es correcta
        Returns: boolean
        """
        return check_password_hash(self.Clave, clave_ingresada)
    
    def ingreso_sistema(self):
        """
        Método ingreso_sistema() según el UML
        Registra el ingreso del usuario al sistema
        """
        self.UltimoAcceso = datetime.utcnow()
        db.session.commit()
    
    def to_dict(self):
        """Convertir a diccionario (sin incluir la contraseña)"""
        return {
            'idUsuario': self.idUsuario,
            'Nombre': self.Nombre,
            'Email': self.Email or '',
            'Rol': self.Rol or '',
            'UbicacionAsignada': self.UbicacionAsignada or '',
            'TelefonoContacto': self.TelefonoContacto or '',
            'UltimoAcceso': self.UltimoAcceso.isoformat() if self.UltimoAcceso else None
        }
    
    @staticmethod
    def set_password(clave):
        """Generar hash de la contraseña"""
        return generate_password_hash(clave)


class Alerta(db.Model):
    """Modelo de Alerta según el UML - Alertas generadas por detección de armas"""
    
    __tablename__ = 'alertas'
    
    idAlerta = db.Column(db.Integer, primary_key=True)
    tipoAlerta = db.Column(db.String(50), nullable=False)  # Tipo de alerta
    fechaHora = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    camara = db.Column(db.String(50), default='CAMERA 01')  # Cámara que generó la alerta
    weapon_count = db.Column(db.Integer, nullable=False)
    alert_level = db.Column(db.String(20), nullable=False)  # high, medium, low
    detection_types = db.Column(db.Text)  # Tipos de armas detectadas
    image_path = db.Column(db.String(255))  # Ruta a la imagen capturada
    detection_metadata = db.Column(db.Text)  # JSON con información adicional
    motivo = db.Column(db.Text)  # Motivo de la alarma
    solucion = db.Column(db.Text)  # Solución aplicada
    
    def __repr__(self):
        return f'<Alerta {self.idAlerta}: {self.tipoAlerta} - {self.fechaHora}>'
    
    def generar_alerta(self):
        """
        Método generar_alerta() según el UML
        Genera una nueva alerta
        """
        pass
    
    def enviar_notificacion(self):
        """
        Método enviar_notificacion() según el UML
        Envía notificación de la alerta
        """
        pass
    
    def to_dict(self):
        """Convertir a diccionario"""
        return {
            'idAlerta': self.idAlerta,
            'tipoAlerta': self.tipoAlerta,
            'fechaHora': self.fechaHora.isoformat(),
            'camara': self.camara,
            'weapon_count': self.weapon_count,
            'alert_level': self.alert_level,
            'detection_types': self.detection_types,
            'image_path': self.image_path,
            'metadata': json.loads(self.detection_metadata) if self.detection_metadata else {},
            'motivo': self.motivo or '',
            'solucion': self.solucion or ''
        }

