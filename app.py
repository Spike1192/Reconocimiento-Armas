#!/usr/bin/env python3
"""
Aplicación Flask principal para el Sistema de Detección de Armas
"""

from flask import Flask, render_template, Response, jsonify, request, send_from_directory
from flask_socketio import SocketIO, emit
import cv2
import os
import base64
import threading
from datetime import datetime
import json

from config import Config
from models import db, WeaponDetection
from process.weapon_detection import WeaponDetector

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Inicializar detector de armas
weapon_detector = WeaponDetector()
camera = None
camera_thread = None
camera_running = False
detection_enabled = True

def init_db():
    """Inicializar base de datos"""
    with app.app_context():
        db.create_all()
        print("Base de datos inicializada")

def generate_frames():
    """Generar frames de video con detección"""
    global camera, camera_running, detection_enabled, weapon_detector
    
    if camera is None:
        camera = cv2.VideoCapture(1)
        if not camera.isOpened():
            print("Error: No se pudo abrir la cámara")
            return
    
    camera_running = True
    
    while camera_running:
        ret, frame = camera.read()
        if not ret:
            break
        
        if detection_enabled:
            # Realizar detección
            results, detections = weapon_detector.detect_weapons(frame)
            
            # Dibujar detecciones
            annotated_frame = weapon_detector.draw_detections(frame, detections)
            
            # Enviar alerta si hay detecciones
            if detections:
                summary = weapon_detector.get_detection_summary(detections)
                socketio.emit('weapon_detected', {
                    'detections': detections,
                    'summary': summary,
                    'timestamp': datetime.now().isoformat()
                })
                
                # Guardar en base de datos
                save_detection_to_db(detections, summary, annotated_frame)
        else:
            annotated_frame = frame
        
        # Codificar frame como JPEG
        ret, buffer = cv2.imencode('.jpg', annotated_frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        if not ret:
            continue
        
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

def save_detection_to_db(detections, summary, frame):
    """Guardar detección en base de datos"""
    try:
        # Guardar imagen
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        os.makedirs("captures", exist_ok=True)
        image_path = f"captures/weapon_detection_{timestamp}.jpg"
        cv2.imwrite(image_path, frame)
        
        # Guardar metadatos
        metadata = {
            'detections': detections,
            'summary': summary
        }
        
        # Crear registro en base de datos
        detection = WeaponDetection(
            weapon_count=summary['weapons_detected'],
            alert_level=summary['alert_level'],
            detection_types=', '.join(summary['detection_types']),
            image_path=image_path,
            detection_metadata=json.dumps(metadata)
        )
        
        db.session.add(detection)
        db.session.commit()
        
    except Exception as e:
        print(f"Error guardando detección: {e}")

@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    """Stream de video"""
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/detections')
def get_detections():
    """Obtener historial de detecciones"""
    try:
        detections = WeaponDetection.query.order_by(
            WeaponDetection.timestamp.desc()
        ).limit(50).all()
        
        result = []
        for det in detections:
            result.append({
                'id': det.id,
                'timestamp': det.timestamp.isoformat(),
                'weapon_count': det.weapon_count,
                'alert_level': det.alert_level,
                'detection_types': det.detection_types,
                'image_path': det.image_path
            })
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats')
def get_stats():
    """Obtener estadísticas"""
    try:
        total = WeaponDetection.query.count()
        high_alerts = WeaponDetection.query.filter_by(
            alert_level='high'
        ).count()
        medium_alerts = WeaponDetection.query.filter_by(
            alert_level='medium'
        ).count()
        
        return jsonify({
            'total': total,
            'high_alerts': high_alerts,
            'medium_alerts': medium_alerts
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/detection/<int:detection_id>')
def get_detection(detection_id):
    """Obtener detalles de una detección"""
    try:
        detection = WeaponDetection.query.get_or_404(detection_id)
        return jsonify({
            'id': detection.id,
            'timestamp': detection.timestamp.isoformat(),
            'weapon_count': detection.weapon_count,
            'alert_level': detection.alert_level,
            'detection_types': detection.detection_types,
            'image_path': detection.image_path,
            'metadata': json.loads(detection.detection_metadata) if detection.detection_metadata else {}
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/toggle_detection', methods=['POST'])
def toggle_detection():
    """Activar/desactivar detección"""
    global detection_enabled
    data = request.get_json()
    detection_enabled = data.get('enabled', True)
    return jsonify({'enabled': detection_enabled})

@app.route('/api/update_confidence', methods=['POST'])
def update_confidence():
    """Actualizar umbral de confianza"""
    data = request.get_json()
    confidence = data.get('confidence', 0.5)
    weapon_detector.confidence_threshold = confidence
    return jsonify({'confidence': confidence})

@app.route('/captures/<path:filename>')
def serve_capture(filename):
    """Servir imágenes capturadas"""
    return send_from_directory('captures', filename)

@socketio.on('connect')
def handle_connect():
    """Manejar conexión de cliente"""
    emit('status', {'message': 'Conectado al sistema de detección'})

@socketio.on('disconnect')
def handle_disconnect():
    """Manejar desconexión de cliente"""
    print('Cliente desconectado')

# La cámara se inicializa cuando se necesita en generate_frames()

if __name__ == '__main__':
    # Inicializar base de datos
    init_db()
    
    # Iniciar aplicación
    print("Iniciando servidor Flask...")
    print("Accede a http://localhost:5000")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)

