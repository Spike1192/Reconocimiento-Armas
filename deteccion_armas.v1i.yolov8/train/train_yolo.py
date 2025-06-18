from ultralytics import YOLO

# Entrena el modelo con tu dataset
model = YOLO('yolov8n.pt')
model.train(data='deteccion_armas.v1i.yolov8/data.yaml', epochs=50, imgsz=640)