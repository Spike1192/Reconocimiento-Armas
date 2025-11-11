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
    """Generar frames de video con detección optimizado para 20 FPS"""
    import time
    
    global camera, camera_running, detection_enabled, weapon_detector
    
    if camera is None:
        camera = cv2.VideoCapture(1)
        if not camera.isOpened():
            print("Error: No se pudo abrir la cámara")
            return
        
        # Configurar buffer de cámara para reducir latencia
        camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    
    camera_running = True
    
    # Control de FPS (20 FPS = 0.05 segundos por frame)
    target_fps = 30
    frame_time = 1.0 / target_fps
    last_frame_time = time.time()
    
    # Variables para procesamiento optimizado de detección
    frame_count = 0
    detection_frame_skip = 3  # Procesar detección cada 3 frames para mantener FPS
    last_detections = []
    last_annotated_frame = None
    
    while camera_running:
        current_time = time.time()
        elapsed = current_time - last_frame_time
        
        # Control de FPS: esperar si es necesario
        if elapsed < frame_time:
            time.sleep(frame_time - elapsed)
        
        ret, frame = camera.read()
        if not ret:
            # Si falla la lectura, intentar reconectar
            time.sleep(0.1)
            continue
        
        frame_count += 1
        
        # Procesar detección solo en ciertos frames para mantener FPS fluido
        if detection_enabled and frame_count % detection_frame_skip == 0:
            # Realizar detección (esto puede ser lento, pero solo cada 3 frames)
            try:
                results, detections = weapon_detector.detect_weapons(frame)
                last_detections = detections
                
                # Dibujar detecciones
                annotated_frame = weapon_detector.draw_detections(frame.copy(), detections)
                last_annotated_frame = annotated_frame
                
                # Enviar alerta si hay detecciones (en thread separado)
                if detections:
                    summary = weapon_detector.get_detection_summary(detections)
                    socketio.emit('weapon_detected', {
                        'detections': detections,
                        'summary': summary,
                        'timestamp': datetime.now().isoformat()
                    })
                    
                    # Guardar en base de datos en thread separado para no bloquear
                    threading.Thread(
                        target=save_detection_to_db,
                        args=(detections, summary, annotated_frame),
                        daemon=True
                    ).start()
            except Exception as e:
                print(f"Error en detección: {e}")
                annotated_frame = frame
        elif detection_enabled and last_annotated_frame is not None and last_detections:
            # Usar último frame con detecciones mientras se procesa el nuevo
            # Aplicar detecciones del frame anterior al frame actual
            annotated_frame = weapon_detector.draw_detections(frame.copy(), last_detections)
        else:
            annotated_frame = frame
        
        # Redimensionar frame para mejor rendimiento de streaming (si es muy grande)
        height, width = annotated_frame.shape[:2]
        if width > 1280:
            scale = 1280 / width
            new_width = 1280
            new_height = int(height * scale)
            annotated_frame = cv2.resize(annotated_frame, (new_width, new_height), interpolation=cv2.INTER_LINEAR)
        
        # Codificar frame como JPEG con calidad optimizada para streaming
        ret, buffer = cv2.imencode('.jpg', annotated_frame, [
            cv2.IMWRITE_JPEG_QUALITY, 80  # Calidad balanceada para buen FPS
        ])
        if not ret:
            continue
        
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        
        last_frame_time = time.time()

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

