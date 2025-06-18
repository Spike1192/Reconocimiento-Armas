#!/usr/bin/env python3
"""
Script para probar detección de armas con una sola imagen
"""

import cv2
import numpy as np
import os
import sys
from pathlib import Path
from process.weapon_detection import WeaponDetector

def test_single_image(image_path):
    """Probar detección en una sola imagen"""
    print("=" * 60)
    print("    PRUEBA DE DETECCIÓN EN IMAGEN ÚNICA")
    print("=" * 60)
    print()
    
    # Verificar que la imagen existe
    if not os.path.exists(image_path):
        print(f"✗ Error: No se encontró la imagen '{image_path}'")
        print("Asegúrate de que la imagen esté en el directorio correcto")
        return False
    
    # Inicializar detector
    print("1. Inicializando detector de armas...")
    detector = WeaponDetector()
    print("✓ Detector listo")
    
    # Cargar imagen
    print(f"\n2. Cargando imagen: {image_path}")
    frame = cv2.imread(image_path)
    
    if frame is None:
        print("✗ Error: No se pudo cargar la imagen")
        return False
    
    print(f"✓ Imagen cargada - Tamaño: {frame.shape[1]}x{frame.shape[0]}")
    
    # Realizar detección
    print("\n3. Realizando detección de armas...")
    results, detections = detector.detect_weapons(frame)
    
    print(f"✓ Análisis completado")
    print(f"  - Armas detectadas: {len(detections)}")
    
    # Mostrar resultados
    if detections:
        print("\n4. Resultados de la detección:")
        print("-" * 40)
        
        for i, detection in enumerate(detections, 1):
            class_name = detection['class_name']
            confidence = detection['confidence']
            bbox = detection['bbox']
            
            print(f"  Arma {i}:")
            print(f"    - Tipo: {class_name}")
            print(f"    - Confianza: {confidence:.2f} ({confidence*100:.1f}%)")
            print(f"    - Posición: {bbox}")
            print()
        
        # Generar resumen
        summary = detector.get_detection_summary(detections)
        print("5. Resumen del análisis:")
        print("-" * 40)
        print(f"  - Nivel de alerta: {summary['alert_level'].upper()}")
        print(f"  - Mensaje: {summary['message']}")
        print(f"  - Confianza máxima: {summary['max_confidence']:.2f}")
        print(f"  - Tipos detectados: {', '.join(summary['detection_types'])}")
        
        # Dibujar detecciones en la imagen
        print("\n6. Procesando imagen con detecciones...")
        annotated_frame = detector.draw_detections(frame, detections)
        
        # Guardar resultado
        output_dir = Path("captures")
        output_dir.mkdir(exist_ok=True)
        
        # Generar nombre de archivo
        original_name = Path(image_path).stem
        output_path = output_dir / f"{original_name}_detected.jpg"
        
        cv2.imwrite(str(output_path), annotated_frame)
        print(f"✓ Imagen procesada guardada en: {output_path}")
        
        # Guardar metadatos
        metadata_path = output_dir / f"{original_name}_metadata.json"
        import json
        metadata = {
            'original_image': image_path,
            'detections': detections,
            'summary': summary,
            'timestamp': str(Path(image_path).stat().st_mtime)
        }
        
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Metadatos guardados en: {metadata_path}")
        
        # Mostrar imagen (opcional)
        show_image = input("\n¿Deseas ver la imagen procesada? (s/n): ").lower().strip()
        if show_image in ['s', 'si', 'sí', 'y', 'yes']:
            cv2.imshow('Detección de Armas', annotated_frame)
            print("Presiona cualquier tecla para cerrar la imagen...")
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        
    else:
        print("\n4. Resultados:")
        print("-" * 40)
        print("  ✓ No se detectaron armas en la imagen")
        print("  - La imagen parece ser segura")
        
        # Guardar imagen original como referencia
        output_dir = Path("captures")
        output_dir.mkdir(exist_ok=True)
        
        original_name = Path(image_path).stem
        output_path = output_dir / f"{original_name}_safe.jpg"
        
        cv2.imwrite(str(output_path), frame)
        print(f"✓ Imagen guardada como referencia: {output_path}")
    
    print("\n" + "=" * 60)
    print("    PRUEBA COMPLETADA")
    print("=" * 60)
    return True

def main():
    """Función principal"""
    print("SISTEMA DE DETECCIÓN DE ARMAS - PRUEBA CON IMAGEN")
    print()
    
    # Verificar argumentos
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        # Solicitar ruta de imagen
        print("Opciones de imagen:")
        print("1. Usar imagen de ejemplo (si existe)")
        print("2. Especificar ruta manual")
        print("3. Buscar imágenes en el directorio actual")
        
        choice = input("\nSelecciona una opción (1-3): ").strip()
        
        if choice == "1":
            # Buscar imagen de ejemplo
            example_paths = [
                "examples/test_weapon.jpg",
                "examples/weapon_sample.jpg", 
                "examples/sample.jpg",
                "test_image.jpg",
                "sample.jpg"
            ]
            
            for path in example_paths:
                if os.path.exists(path):
                    image_path = path
                    print(f"✓ Usando imagen de ejemplo: {path}")
                    break
            else:
                print("✗ No se encontraron imágenes de ejemplo")
                return
        
        elif choice == "2":
            image_path = input("Ingresa la ruta de la imagen: ").strip()
            if not image_path:
                print("✗ No se especificó una ruta")
                return
        
        elif choice == "3":
            # Buscar imágenes en el directorio actual
            image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
            image_files = []
            
            for ext in image_extensions:
                image_files.extend(Path('.').glob(f'*{ext}'))
                image_files.extend(Path('.').glob(f'*{ext.upper()}'))
            
            if image_files:
                print("\nImágenes encontradas:")
                for i, img_file in enumerate(image_files, 1):
                    print(f"  {i}. {img_file}")
                
                try:
                    selection = int(input("\nSelecciona una imagen (número): ")) - 1
                    if 0 <= selection < len(image_files):
                        image_path = str(image_files[selection])
                    else:
                        print("✗ Selección inválida")
                        return
                except ValueError:
                    print("✗ Entrada inválida")
                    return
            else:
                print("✗ No se encontraron imágenes en el directorio actual")
                return
        
        else:
            print("✗ Opción inválida")
            return
    
    # Ejecutar prueba
    success = test_single_image(image_path)
    
    if success:
        print("\n✅ Prueba completada exitosamente")
    else:
        print("\n❌ La prueba falló")

if __name__ == "__main__":
    main() 