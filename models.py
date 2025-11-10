"""
Modelos de base de datos usando SQLAlchemy
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

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

