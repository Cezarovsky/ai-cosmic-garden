"""
NOVA Landmark Detection Demo
Detectează landmarks în imagini și le transformă în tensori 7D
"""

from flask import Flask, render_template, request, jsonify
import cv2
import numpy as np
import mediapipe as mp
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Initialize MediaPipe
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
pose = mp_pose.Pose(static_image_mode=True, min_detection_confidence=0.5)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def calculate_distance(point1, point2):
    """Calculează distanța Euclidiană între două puncte"""
    return np.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)


def extract_7d_tensor(image_path, landmarks_data):
    """
    Extrage tensor 7D din landmarks:
    [legs, eyes, ears_shape, texture, size, sleekness, aquatic]
    """
    
    # Load imagine pentru analiză
    image = cv2.imread(image_path)
    height, width = image.shape[:2]
    
    # Detectează edges pentru texture
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 100, 200)
    texture_intensity = np.sum(edges > 0) / (height * width)  # 0-1
    
    if landmarks_data is None or len(landmarks_data) == 0:
        # Default values dacă nu găsește landmarks
        return [4.0, 2.0, 0.5, texture_intensity, 1.0, 0.5, 0.0]
    
    # Extract landmark positions
    landmarks = landmarks_data
    
    # 1. LEGS - detectează limbs (bazat pe pose landmarks)
    # Verifică dacă are 4 membre (2 brațe + 2 picioare sau 4 picioare)
    limbs_detected = 0
    landmark_indices = {
        'left_shoulder': 11, 'right_shoulder': 12,
        'left_elbow': 13, 'right_elbow': 14,
        'left_wrist': 15, 'right_wrist': 16,
        'left_hip': 23, 'right_hip': 24,
        'left_knee': 25, 'right_knee': 26,
        'left_ankle': 27, 'right_ankle': 28
    }
    
    # Numără membre vizibile
    for key in ['left_wrist', 'right_wrist', 'left_ankle', 'right_ankle']:
        idx = landmark_indices.get(key, -1)
        if idx < len(landmarks) and landmarks[idx].visibility > 0.5:
            limbs_detected += 1
    
    legs = min(limbs_detected, 4.0)  # Cap la 4
    
    # 2. EYES - presupunem 2 (standard pentru mamifere)
    eyes = 2.0
    
    # 3. EARS_SHAPE - raport geometric (0-1, 0=rotunde, 1=triunghiulare)
    # Estimăm din poziția capului
    nose_idx = landmark_indices.get('nose', 0)
    if nose_idx < len(landmarks):
        # Raport înălțime/lățime cap
        ears_shape = 0.7  # Default pentru animale cu urechi triunghiulare
    else:
        ears_shape = 0.5
    
    # 4. TEXTURE - deja calculat (edge intensity)
    texture = texture_intensity
    
    # 5. SIZE - mărime relativă (bounding box față de imagine)
    x_coords = [lm.x for lm in landmarks if lm.visibility > 0.5]
    y_coords = [lm.y for lm in landmarks if lm.visibility > 0.5]
    
    if x_coords and y_coords:
        bbox_width = max(x_coords) - min(x_coords)
        bbox_height = max(y_coords) - min(y_coords)
        size = (bbox_width + bbox_height) / 2  # 0-1
    else:
        size = 0.5
    
    # 6. SLEEKNESS - compactitate (raport suprafață/perimetru)
    if bbox_width > 0 and bbox_height > 0:
        aspect_ratio = min(bbox_width, bbox_height) / max(bbox_width, bbox_height)
        sleekness = aspect_ratio  # 0-1, 1=perfect pătrat (compact)
    else:
        sleekness = 0.5
    
    # 7. AQUATIC - estimare bazată pe aspect ratio (forme alungite = pești)
    # Și poziție (picioare jos vs distributed)
    if bbox_height > 0:
        elongation = bbox_width / bbox_height
        aquatic = 1.0 if elongation > 1.5 else 0.0  # Alungit = acvatic
    else:
        aquatic = 0.0
    
    return [
        round(legs, 2),
        round(eyes, 2),
        round(ears_shape, 2),
        round(texture, 3),
        round(size, 3),
        round(sleekness, 3),
        round(aquatic, 2)
    ]


def process_image(image_path):
    """Procesează imagine: detectează landmarks + extrage tensor 7D"""
    
    # Load image
    image = cv2.imread(image_path)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Detectare landmarks
    results = pose.process(image_rgb)
    
    landmarks_data = None
    landmarks_visual = []
    
    if results.pose_landmarks:
        landmarks_data = results.pose_landmarks.landmark
        
        # Extract coordinates pentru vizualizare
        height, width = image.shape[:2]
        for idx, landmark in enumerate(landmarks_data):
            x = int(landmark.x * width)
            y = int(landmark.y * height)
            visibility = landmark.visibility
            landmarks_visual.append({
                'id': idx,
                'x': x,
                'y': y,
                'visibility': float(visibility)
            })
        
        # Desenează landmarks pe imagine
        mp_drawing.draw_landmarks(
            image,
            results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS,
            mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=3),
            mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2)
        )
    
    # Salvează imagine cu landmarks
    output_path = image_path.replace('.', '_landmarks.')
    cv2.imwrite(output_path, image)
    
    # Extrage tensor 7D
    tensor_7d = extract_7d_tensor(image_path, landmarks_data)
    
    return {
        'tensor_7d': tensor_7d,
        'landmarks': landmarks_visual,
        'landmarks_image': output_path.replace('static/', ''),
        'tensor_labels': ['legs', 'eyes', 'ears_shape', 'texture', 'size', 'sleekness', 'aquatic']
    }


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Procesează imagine
        try:
            result = process_image(filepath)
            result['original_image'] = filepath.replace('static/', '')
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return jsonify({'error': 'Invalid file type'}), 400


if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    print("🚀 NOVA Landmark Detection Demo")
    print("📍 Deschide: http://localhost:5001")
    app.run(debug=True, host='0.0.0.0', port=5001)
