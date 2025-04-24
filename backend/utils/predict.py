import numpy as np
import cv2
from ultralytics import YOLO
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import io
from PIL import Image
import requests
from keras.preprocessing import image  # Ensure imported
import uuid
import os


# Load the pretrained model
model_predict_landmark = load_model('xception_model_2.h5')
model_predict_distance = YOLO('Phase 3 yolo 8.pt')
    
# List of classes (modify this based on your dataset)
class_labels = ['Block A', 'Block B', 'Block C','Block D','Block E','Block F','IEEE office']

# Assume a dummy known size for distance calculation

FOCAL_LENGTH_PX = 800  # iPhone 12 Pro Max
class_heights_m = {
    '80': 0.80,
    '120': 1.20,
    '140': 1.40,
    '160': 1.60,
    '200': 2.00,
    '210': 2.10,
    '220': 2.20,
    '380': 3.80,
    '650': 8.50
}

def predict_distance(img_path):
    
    # Inference
    results = model_predict_distance(img_path)

    # Collect distances
    distances = []

    # Process detections
    for result in results:
        boxes = result.boxes
        for i in range(len(boxes)):
            cls_id = int(boxes.cls[i])
            class_name = str(model_predict_distance.names[cls_id])  # ensure it's a string like '120'

        xyxy = boxes.xyxy[i].cpu().numpy()
        height_px = int(xyxy[3] - xyxy[1])

        real_height_m = class_heights_m.get(class_name)
        if real_height_m is not None and height_px > 0:
            distance_m = (FOCAL_LENGTH_PX * real_height_m) / height_px 
            distances.append(distance_m)
            print(f"Window Type: {class_name}, Height: {height_px}px, Distance: {distance_m:.2f} m")
        else:
            print(f"Unknown class or invalid bounding box height: {class_name}")

# Compute and display average distance
    if distances:
        avg_distance = sum(distances) / len(distances)
        print(f"\n📏 Average Estimated Distance: {avg_distance:.2f} meters")
        return round(avg_distance, 2)
    else:
        print("\n⚠️ No valid detections for distance calculation.")
        return 0.0


def predict_landmark(img_file):

    # Save the uploaded image to a temp file
    temp_path = f"temp_{uuid.uuid4().hex}.jpg"
    with open(temp_path, 'wb') as f:
        f.write(img_file.read())


    img = Image.open(temp_path).convert('RGB')
    img = img.resize((224, 224))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array /= 255.0


    # Predict class
    preds = model_predict_landmark.predict(img_array)  # FIXED: use img_array
    predicted_class = class_labels[np.argmax(preds)]

    # Use saved file path for YOLO distance estimation
    distance = predict_distance(temp_path)

    # Optionally delete temp image
    os.remove(temp_path)

    return predicted_class, distance