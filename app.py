#!/usr/bin/env python3
"""
Aplicación Flask principal para el Sistema de Detección de Armas
"""

from flask import Flask, render_template, Response, jsonify, request, send_from_directory, session
from flask_socketio import SocketIO, emit
import cv2
import os
import base64
import threading
from datetime import datetime
import json
from functools import wraps

from config import Config
from models import db, WeaponDetection, Usuario, Alerta
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
        
        # Crear usuarios predefinidos si no existen
        if not Usuario.query.first():
            from init_db import crear_usuarios_predefinidos
            crear_usuarios_predefinidos()

def login_required(f):
    """Decorador para proteger rutas que requieren autenticación"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'No autenticado'}), 401
        return f(*args, **kwargs)
    return decorated_function

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
                    
                    # Guardar en base de datos en thread separado para no bloquear
                    # Y luego emitir notificación con el ID de la alerta
                    def save_and_notify():
                        alerta_id = save_detection_to_db(detections, summary, annotated_frame)
                        if alerta_id:
                            # Emitir notificación a todos los clientes conectados
                            socketio.emit('weapon_detected', {
                                'alerta_id': alerta_id,
                                'detections': detections,
                                'summary': summary,
                                'tipo_alerta': f"Detección de {summary['weapons_detected']} arma(s)",
                                'timestamp': datetime.now().isoformat(),
                                'camara': 'CAMERA 01'
                            })
                    
                    threading.Thread(
                        target=save_and_notify,
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
    """Guardar detección como alerta en base de datos y retornar el ID de la alerta"""
    try:
        with app.app_context():
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
            
            # Determinar tipo de alerta según el nivel
            tipo_alerta = f"Detección de {summary['weapons_detected']} arma(s)"
            if summary['alert_level'] == 'high':
                tipo_alerta = f"ALERTA ALTA: {summary['weapons_detected']} arma(s) detectada(s)"
            elif summary['alert_level'] == 'medium':
                tipo_alerta = f"ALERTA MEDIA: {summary['weapons_detected']} arma(s) detectada(s)"
            
            # Crear alerta en base de datos
            alerta = Alerta(
                tipoAlerta=tipo_alerta,
                fechaHora=datetime.utcnow(),
                camara='CAMERA 01',
                weapon_count=summary['weapons_detected'],
                alert_level=summary['alert_level'],
                detection_types=', '.join(summary['detection_types']),
                image_path=image_path,
                detection_metadata=json.dumps(metadata),
                motivo=f"Detección de {', '.join(summary['detection_types'])} en {summary['weapons_detected']} ubicación(es)",
                solucion='Pendiente de revisión'
            )
            
            db.session.add(alerta)
            db.session.commit()
            
            # Obtener el ID de la alerta recién creada
            alerta_id = alerta.idAlerta
            
            # También guardar en WeaponDetection para compatibilidad
            detection = WeaponDetection(
                weapon_count=summary['weapons_detected'],
                alert_level=summary['alert_level'],
                detection_types=', '.join(summary['detection_types']),
                image_path=image_path,
                detection_metadata=json.dumps(metadata)
            )
            db.session.add(detection)
            db.session.commit()
            
            print(f"Alerta guardada: {tipo_alerta} - ID: {alerta_id} - {image_path}")
            return alerta_id
        
    except Exception as e:
        print(f"Error guardando detección: {e}")
        import traceback
        traceback.print_exc()
        return None

@app.route('/')
def index():
    """Página principal"""
    return render_template('camaras_seguridad.html')

@app.route('/api/login', methods=['POST'])
def login():
    """Autenticar usuario según el modelo UML"""
    try:
        data = request.get_json()
        usuario = data.get('usuario', '').strip()
        clave = data.get('clave', '').strip()
        
        if not usuario or not clave:
            return jsonify({'error': 'Usuario y contraseña son requeridos'}), 400
        
        # Buscar usuario en la base de datos
        user = Usuario.query.filter_by(idUsuario=usuario).first()
        
        if not user:
            return jsonify({'error': 'Usuario o contraseña incorrectos'}), 401
        
        # Autenticar usando el método del modelo UML
        if not user.autenticar(clave):
            return jsonify({'error': 'Usuario o contraseña incorrectos'}), 401
        
        # Registrar ingreso al sistema (método del UML)
        user.ingreso_sistema()
        db.session.commit()
        
        # Crear sesión
        session['user_id'] = user.idUsuario
        session['user_name'] = user.Nombre
        session.permanent = True
        
        return jsonify({
            'success': True,
            'usuario': user.to_dict(),
            'message': 'Login exitoso'
        })
        
    except Exception as e:
        return jsonify({'error': f'Error en el servidor: {str(e)}'}), 500

@app.route('/api/logout', methods=['POST'])
def logout():
    """Cerrar sesión"""
    session.clear()
    return jsonify({'success': True, 'message': 'Sesión cerrada'})

@app.route('/api/check_session', methods=['GET'])
def check_session():
    """Verificar si hay una sesión activa"""
    if 'user_id' in session:
        user = Usuario.query.filter_by(idUsuario=session['user_id']).first()
        if user:
            return jsonify({
                'authenticated': True,
                'usuario': user.to_dict()
            })
    
    return jsonify({'authenticated': False}), 401

@app.route('/api/user/profile', methods=['GET'])
@login_required
def get_user_profile():
    """Obtener perfil del usuario autenticado"""
    user = Usuario.query.filter_by(idUsuario=session['user_id']).first()
    if user:
        return jsonify(user.to_dict())
    return jsonify({'error': 'Usuario no encontrado'}), 404

@app.route('/api/alertas', methods=['GET'])
@login_required
def get_alertas():
    """Obtener todas las alertas"""
    try:
        alertas = Alerta.query.order_by(
            Alerta.fechaHora.desc()
        ).limit(100).all()
        
        result = [alerta.to_dict() for alerta in alertas]
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/alerta/<int:alerta_id>', methods=['GET'])
@login_required
def get_alerta(alerta_id):
    """Obtener detalles de una alerta específica"""
    try:
        alerta = Alerta.query.get_or_404(alerta_id)
        return jsonify(alerta.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/alerta/<int:alerta_id>', methods=['PUT'])
@login_required
def update_alerta(alerta_id):
    """Actualizar motivo y solución de una alerta"""
    try:
        alerta = Alerta.query.get_or_404(alerta_id)
        data = request.get_json()
        
        if 'motivo' in data:
            alerta.motivo = data['motivo']
        if 'solucion' in data:
            alerta.solucion = data['solucion']
        
        db.session.commit()
        return jsonify(alerta.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/video_feed')
@login_required
def video_feed():
    """Stream de video"""
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/detections')
@login_required
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
@login_required
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
@login_required
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
@login_required
def toggle_detection():
    """Activar/desactivar detección"""
    global detection_enabled
    data = request.get_json()
    detection_enabled = data.get('enabled', True)
    return jsonify({'enabled': detection_enabled})

@app.route('/api/update_confidence', methods=['POST'])
@login_required
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

@app.route('/script.js')
def serve_script():
    """Servir script.js desde templates"""
    return send_from_directory('templates', 'script.js', mimetype='application/javascript')

@app.route('/style.css')
def serve_style():
    """Servir style.css desde templates"""
    return send_from_directory('templates', 'style.css', mimetype='text/css')

@app.route('/svg/<path:filename>')
def serve_svg(filename):
    """Servir archivos SVG desde templates/svg"""
    return send_from_directory('templates/svg', filename, mimetype='image/svg+xml')

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

