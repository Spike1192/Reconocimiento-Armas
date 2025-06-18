#!/usr/bin/env python3
"""
Script para crear una imagen de prueba con formas que simulen armas
"""

import cv2
import numpy as np
import os

def create_test_image():
    """Crear imagen de prueba con formas que simulen armas"""
    
    # Crear imagen en blanco
    img = np.ones((600, 800, 3), dtype=np.uint8) * 255
    
    # Dibujar "pistola" (rectángulo largo con mango)
    # Cuerpo de la pistola
    cv2.rectangle(img, (200, 250), (400, 280), (50, 50, 50), -1)
    # Mango de la pistola
    cv2.rectangle(img, (200, 280), (220, 320), (30, 30, 30), -1)
    # Cañón
    cv2.rectangle(img, (400, 260), (450, 270), (20, 20, 20), -1)
    # Gatillo
    cv2.circle(img, (210, 300), 5, (0, 0, 0), -1)
    
    # Dibujar "cuchillo" (triángulo con mango)
    # Hoja del cuchillo
    pts = np.array([[500, 200], [550, 250], [500, 300]], np.int32)
    cv2.fillPoly(img, [pts], (100, 100, 100))
    # Mango del cuchillo
    cv2.rectangle(img, (480, 240), (500, 260), (139, 69, 19), -1)
    
    # Dibujar "rifle" (rectángulo largo)
    # Cuerpo del rifle
    cv2.rectangle(img, (100, 400), (500, 420), (40, 40, 40), -1)
    # Culata
    cv2.rectangle(img, (100, 400), (120, 450), (30, 30, 30), -1)
    # Mira
    cv2.rectangle(img, (450, 390), (470, 430), (20, 20, 20), -1)
    
    # Agregar texto descriptivo
    cv2.putText(img, "Test Image - Weapon Detection", (50, 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    cv2.putText(img, "Pistol", (200, 240), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
    cv2.putText(img, "Knife", (480, 190), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
    cv2.putText(img, "Rifle", (100, 390), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
    
    # Crear directorio si no existe
    os.makedirs("examples", exist_ok=True)
    
    # Guardar imagen
    output_path = "examples/test_weapon.jpg"
    cv2.imwrite(output_path, img)
    
    print(f"✓ Imagen de prueba creada: {output_path}")
    print(f"  - Tamaño: {img.shape[1]}x{img.shape[0]}")
    print(f"  - Contiene: Pistola, Cuchillo, Rifle")
    
    return output_path

def create_safe_test_image():
    """Crear imagen de prueba segura (sin armas)"""
    
    # Crear imagen en blanco
    img = np.ones((600, 800, 3), dtype=np.uint8) * 240
    
    # Dibujar objetos seguros
    # Teléfono
    cv2.rectangle(img, (150, 200), (250, 300), (0, 100, 200), -1)
    cv2.rectangle(img, (160, 210), (240, 290), (255, 255, 255), -1)
    cv2.circle(img, (200, 250), 15, (0, 0, 0), -1)
    
    # Libro
    cv2.rectangle(img, (400, 250), (500, 350), (139, 69, 19), -1)
    cv2.rectangle(img, (410, 260), (490, 340), (255, 255, 255), -1)
    cv2.line(img, (450, 260), (450, 340), (0, 0, 0), 2)
    
    # Lápiz
    cv2.rectangle(img, (300, 150), (350, 200), (255, 255, 0), -1)
    cv2.rectangle(img, (350, 150), (360, 200), (139, 69, 19), -1)
    
    # Agregar texto
    cv2.putText(img, "Safe Test Image - No Weapons", (50, 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    cv2.putText(img, "Phone", (150, 190), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
    cv2.putText(img, "Book", (400, 240), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
    cv2.putText(img, "Pencil", (300, 140), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
    
    # Crear directorio si no existe
    os.makedirs("examples", exist_ok=True)
    
    # Guardar imagen
    output_path = "examples/test_safe.jpg"
    cv2.imwrite(output_path, img)
    
    print(f"✓ Imagen segura creada: {output_path}")
    print(f"  - Tamaño: {img.shape[1]}x{img.shape[0]}")
    print(f"  - Contiene: Telefono, Libro, Lapiz (objetos seguros)")
    
    return output_path

def main():
    """Función principal"""
    print("=" * 50)
    print("    CREANDO IMÁGENES DE PRUEBA")
    print("=" * 50)
    print()
    
    # Crear imagen con armas simuladas
    weapon_image = create_test_image()
    
    # Crear imagen segura
    safe_image = create_safe_test_image()
    
    print("\n" + "=" * 50)
    print("    IMÁGENES CREADAS EXITOSAMENTE")
    print("=" * 50)
    print()
    print("Ahora puedes probar el sistema con:")
    print(f"  python test_single_image.py {weapon_image}")
    print(f"  python test_single_image.py {safe_image}")
    print()
    print("O ejecutar el script interactivo:")
    print("  python test_single_image.py")

if __name__ == "__main__":
    main() 