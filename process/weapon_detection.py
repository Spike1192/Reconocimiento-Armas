import cv2
import numpy as np
from ultralytics import YOLO
import os
from datetime import datetime
import json

class WeaponDetector:
    def __init__(self, model_path=None):
        """
        Inicializa el detector de armas
        Args:
            model_path: Ruta al modelo YOLO personalizado (opcional)
        """
        self.model = None
        self.confidence_threshold = 0.5
        self.weapon_classes = ['gun', 'knife', 'sword']
        
        # Obtener ruta absoluta al modelo entrenado
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        default_model_path = os.path.join(BASE_DIR, "computer_vision_models", "models", "best.pt")
        
        # Cargar modelo con mensajes de depuración
        if model_path and os.path.exists(model_path):
            print(f"[INFO] Usando modelo personalizado: {model_path}")
            self.model = YOLO(model_path)
        elif os.path.exists(default_model_path):
            print(f"[INFO] Usando modelo entrenado: {default_model_path}")
            self.model = YOLO(default_model_path)
        else:
            print("[INFO] Usando modelo por defecto: yolov8n.pt")
            self.model = YOLO('yolov8n.pt')
    
    def detect_weapons(self, frame):
        """
        Detecta armas en un frame
        Args:
            frame: Frame de imagen (numpy array)
        Returns:
            results: Resultados de la detección
            detections: Lista de detecciones con información
        """
        if self.model is None:
            return None, []
        
        # Realizar detección
        results = self.model(frame, conf=self.confidence_threshold)
        
        detections = []
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    # Obtener coordenadas del bounding box
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    confidence = box.conf[0].cpu().numpy()
                    class_id = int(box.cls[0].cpu().numpy())
                    class_name = result.names[class_id]
                    
                    # Verificar si es una clase de arma
                    if any(weapon in class_name.lower() for weapon in self.weapon_classes):
                        detection = {
                            'bbox': [int(x1), int(y1), int(x2), int(y2)],
                            'confidence': float(confidence),
                            'class_id': class_id,
                            'class_name': class_name
                        }
                        detections.append(detection)
        
        return results, detections
    
    def draw_detections(self, frame, detections):
        """
        Dibuja las detecciones en el frame
        Args:
            frame: Frame de imagen
            detections: Lista de detecciones
        Returns:
            frame: Frame con detecciones dibujadas
        """
        for detection in detections:
            x1, y1, x2, y2 = detection['bbox']
            confidence = detection['confidence']
            class_name = detection['class_name']
            
            # Dibujar bounding box
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
            
            # Dibujar etiqueta
            label = f"{class_name}: {confidence:.2f}"
            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
            cv2.rectangle(frame, (x1, y1 - label_size[1] - 10), 
                         (x1 + label_size[0], y1), (0, 0, 255), -1)
            cv2.putText(frame, label, (x1, y1 - 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        
        return frame
    
    def save_detection(self, frame, detections, save_path):
        """
        Guarda una captura con detección de armas
        Args:
            frame: Frame de imagen
            detections: Lista de detecciones
            save_path: Ruta donde guardar la imagen
        Returns:
            bool: True si se guardó exitosamente
        """
        try:
            # Dibujar detecciones en el frame
            annotated_frame = self.draw_detections(frame.copy(), detections)
            
            # Guardar imagen
            cv2.imwrite(save_path, annotated_frame)
            
            # Guardar metadatos
            metadata = {
                'timestamp': datetime.now().isoformat(),
                'detections': detections,
                'total_weapons': len(detections)
            }
            
            metadata_path = save_path.replace('.jpg', '_metadata.json')
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error al guardar detección: {e}")
            return False
    
    def get_detection_summary(self, detections):
        """
        Genera un resumen de las detecciones
        Args:
            detections: Lista de detecciones
        Returns:
            dict: Resumen de detecciones
        """
        if not detections:
            return {
                'weapons_detected': 0,
                'alert_level': 'safe',
                'message': 'No se detectaron armas'
            }
        
        weapon_count = len(detections)
        max_confidence = max([d['confidence'] for d in detections])
        
        # Determinar nivel de alerta
        if weapon_count >= 3 or max_confidence > 0.8:
            alert_level = 'high'
            message = f'ALERTA ALTA: {weapon_count} armas detectadas'
        elif weapon_count >= 1 or max_confidence > 0.6:
            alert_level = 'medium'
            message = f'ALERTA MEDIA: {weapon_count} arma(s) detectada(s)'
        else:
            alert_level = 'low'
            message = f'ALERTA BAJA: {weapon_count} arma(s) detectada(s)'
        
        return {
            'weapons_detected': weapon_count,
            'alert_level': alert_level,
            'message': message,
            'max_confidence': max_confidence,
            'detection_types': list(set([d['class_name'] for d in detections]))
        } 