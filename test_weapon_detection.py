#!/usr/bin/env python3
"""
Script de prueba para el sistema de detección de armas
"""

import cv2
import numpy as np
import os
from process.weapon_detection import WeaponDetector

def test_weapon_detection():
    """Prueba básica del detector de armas"""
    print("Iniciando prueba del detector de armas...")
    
    # Inicializar detector
    detector = WeaponDetector()
    print("✓ Detector inicializado correctamente")
    
    # Probar con imagen de ejemplo (si existe)
    test_image_path = "examples/test_weapon.jpg"
    
    if os.path.exists(test_image_path):
        print(f"Probando con imagen: {test_image_path}")
        frame = cv2.imread(test_image_path)
        
        if frame is not None:
            # Realizar detección
            results, detections = detector.detect_weapons(frame)
            
            print(f"✓ Detección completada")
            print(f"  - Armas detectadas: {len(detections)}")
            
            if detections:
                for i, detection in enumerate(detections):
                    print(f"  - Detección {i+1}: {detection['class_name']} (confianza: {detection['confidence']:.2f})")
                
                # Generar resumen
                summary = detector.get_detection_summary(detections)
                print(f"  - Resumen: {summary['message']}")
                
                # Dibujar detecciones
                annotated_frame = detector.draw_detections(frame, detections)
                
                # Guardar resultado
                output_path = "captures/test_result.jpg"
                os.makedirs("captures", exist_ok=True)
                cv2.imwrite(output_path, annotated_frame)
                print(f"✓ Resultado guardado en: {output_path}")
            else:
                print("  - No se detectaron armas en la imagen")
        else:
            print("✗ Error al cargar la imagen de prueba")
    else:
        print("No se encontró imagen de prueba, probando con cámara web...")
        test_camera_detection(detector)

def test_camera_detection(detector):
    """Prueba con cámara web"""
    print("Iniciando cámara web...")
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("✗ No se pudo abrir la cámara web")
        return
    
    print("✓ Cámara web iniciada")
    print("Presiona 'q' para salir, 's' para guardar captura")
    
    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            print("✗ Error al leer frame de la cámara")
            break
        
        # Realizar detección cada 10 frames para optimizar rendimiento
        if frame_count % 10 == 0:
            results, detections = detector.detect_weapons(frame)
            
            if detections:
                print(f"¡Armas detectadas! {len(detections)} arma(s) encontrada(s)")
                summary = detector.get_detection_summary(detections)
                print(f"  - {summary['message']}")
            
            # Dibujar detecciones
            annotated_frame = detector.draw_detections(frame, detections)
        else:
            annotated_frame = frame
        
        # Mostrar frame
        cv2.imshow('Detección de Armas - Prueba', annotated_frame)
        
        # Manejar teclas
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s'):
            # Guardar captura
            timestamp = f"capture_{frame_count}"
            save_path = f"captures/{timestamp}.jpg"
            os.makedirs("captures", exist_ok=True)
            
            if detections:
                detector.save_detection(frame, detections, save_path)
                print(f"✓ Captura guardada con detecciones: {save_path}")
            else:
                cv2.imwrite(save_path, frame)
                print(f"✓ Captura guardada: {save_path}")
        
        frame_count += 1
    
    cap.release()
    cv2.destroyAllWindows()
    print("✓ Prueba de cámara completada")

def test_model_download():
    """Prueba la descarga del modelo YOLO"""
    print("Verificando modelo YOLO...")
    
    try:
        from ultralytics import YOLO
        model = YOLO('yolov8n.pt')
        print("✓ Modelo YOLO cargado correctamente")
        return True
    except Exception as e:
        print(f"✗ Error al cargar modelo YOLO: {e}")
        print("Intentando descargar modelo...")
        
        try:
            from ultralytics import YOLO
            model = YOLO('yolov8n.pt')
            print("✓ Modelo YOLO descargado y cargado correctamente")
            return True
        except Exception as e2:
            print(f"✗ Error al descargar modelo: {e2}")
            return False

def main():
    """Función principal de prueba"""
    print("=" * 50)
    print("PRUEBA DEL SISTEMA DE DETECCIÓN DE ARMAS")
    print("=" * 50)
    
    # Verificar dependencias
    print("\n1. Verificando dependencias...")
    try:
        import cv2
        import numpy as np
        from ultralytics import YOLO
        print("✓ Todas las dependencias están disponibles")
    except ImportError as e:
        print(f"✗ Dependencia faltante: {e}")
        print("Instala las dependencias con: pip install -r requirements.txt")
        return
    
    # Verificar modelo
    print("\n2. Verificando modelo YOLO...")
    if not test_model_download():
        print("No se pudo cargar el modelo YOLO")
        return
    
    # Probar detector
    print("\n3. Probando detector de armas...")
    test_weapon_detection()
    
    print("\n" + "=" * 50)
    print("PRUEBA COMPLETADA")
    print("=" * 50)

if __name__ == "__main__":
    main() 