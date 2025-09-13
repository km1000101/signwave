from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import pickle
import cv2
import mediapipe as mp
import numpy as np
import base64
import io
from PIL import Image
import logging
import threading
import time
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Global variables for model and MediaPipe
model = None
isl_new_model = None
mp_hands = None
hands = None
labels_dict = {'0': 'A', '1': 'B', '2': 'L'}
isl_new_labels_dict = {0: 'A', 1: 'B', 2: 'L'}

def initialize_model():
    """Initialize the model and MediaPipe components"""
    global model, isl_new_model, mp_hands, hands
    
    try:
        logger.info("Loading model...")
        
        # Try different possible paths for the model
        model_paths = [
            'src/models/model.p',
            '../src/models/model.p',
            '../../src/models/model.p',
            './src/models/model.p'
        ]
        
        model_loaded = False
        for model_path in model_paths:
            try:
                logger.info(f"Trying to load model from: {model_path}")
                model_dict = pickle.load(open(model_path, 'rb'))
                model = model_dict['model']
                logger.info(f"Model loaded successfully from: {model_path}")
                model_loaded = True
                break
            except FileNotFoundError:
                logger.warning(f"Model file not found at: {model_path}")
                continue
            except Exception as e:
                logger.error(f"Error loading model from {model_path}: {e}")
                continue
        
        if not model_loaded:
            logger.error("Could not load model from any path")
            return False
        
        # Load ISL_NEW model
        logger.info("Loading ISL_NEW model...")
        isl_new_model_paths = [
            'ISL_NEW/model.p',
            '../ISL_NEW/model.p',
            '../../ISL_NEW/model.p',
            './ISL_NEW/model.p'
        ]
        
        isl_new_loaded = False
        for model_path in isl_new_model_paths:
            try:
                logger.info(f"Trying to load ISL_NEW model from: {model_path}")
                model_dict = pickle.load(open(model_path, 'rb'))
                isl_new_model = model_dict['model']
                logger.info(f"ISL_NEW model loaded successfully from: {model_path}")
                isl_new_loaded = True
                break
            except FileNotFoundError:
                logger.warning(f"ISL_NEW model file not found at: {model_path}")
                continue
            except Exception as e:
                logger.error(f"Error loading ISL_NEW model from {model_path}: {e}")
                continue
        
        if not isl_new_loaded:
            logger.warning("Could not load ISL_NEW model - continuing with original model only")
        
        # Initialize MediaPipe
        logger.info("Initializing MediaPipe...")
        mp_hands = mp.solutions.hands
        hands = mp_hands.Hands(static_image_mode=True, min_detection_confidence=0.3)
        logger.info("MediaPipe initialized successfully!")
        
        return True
    except Exception as e:
        logger.error(f"Error initializing model: {e}")
        return False

def preprocess_image(image_data):
    """Convert base64 image data to OpenCV format"""
    try:
        # Remove data URL prefix if present
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        # Decode base64 image
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert to OpenCV format (BGR)
        image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        return image_cv
    except Exception as e:
        logger.error(f"Error preprocessing image: {e}")
        return None

def extract_hand_features(image_cv):
    """Extract hand landmarks and features from image"""
    try:
        H, W, _ = image_cv.shape
        frame_rgb = cv2.cvtColor(image_cv, cv2.COLOR_BGR2RGB)
        
        results = hands.process(frame_rgb)
        
        if results.multi_hand_landmarks:
            data_aux = []
            x_ = []
            y_ = []
            
            for hand_landmarks in results.multi_hand_landmarks:
                for i in range(len(hand_landmarks.landmark)):
                    x = hand_landmarks.landmark[i].x
                    y = hand_landmarks.landmark[i].y
                    x_.append(x)
                    y_.append(y)
                
                for i in range(len(hand_landmarks.landmark)):
                    x = hand_landmarks.landmark[i].x
                    y = hand_landmarks.landmark[i].y
                    data_aux.append(x - min(x_))
                    data_aux.append(y - min(y_))
            
            return np.asarray(data_aux), True
        else:
            return None, False
            
    except Exception as e:
        logger.error(f"Error extracting hand features: {e}")
        return None, False

@app.route('/')
def index():
    """Serve the main page"""
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Sign Language Detection API</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .status { padding: 10px; margin: 10px 0; border-radius: 5px; }
            .success { background-color: #d4edda; color: #155724; }
            .error { background-color: #f8d7da; color: #721c24; }
        </style>
    </head>
    <body>
        <h1>Sign Language Detection API</h1>
        <div class="status {{ 'success' if model_loaded else 'error' }}">
            Model Status: {{ 'Loaded' if model_loaded else 'Not Loaded' }}
        </div>
        <p>API Endpoints:</p>
        <ul>
            <li>POST /predict - Send image data for sign detection</li>
            <li>GET /status - Check API status</li>
            <li>GET /health - Health check</li>
        </ul>
    </body>
    </html>
    """, model_loaded=model is not None)

@app.route('/status')
def status():
    """Check API status"""
    # Check if model files exist
    model_paths = [
        'src/models/model.p',
        '../src/models/model.p',
        '../../src/models/model.p',
        './src/models/model.p'
    ]
    
    model_file_exists = False
    for model_path in model_paths:
        try:
            if Path(model_path).exists():
                model_file_exists = True
                break
        except:
            continue
    
    return jsonify({
        'status': 'running',
        'model_loaded': model is not None,
        'isl_new_model_loaded': isl_new_model is not None,
        'mediapipe_loaded': hands is not None,
        'model_file_exists': model_file_exists,
        'supported_labels': list(labels_dict.values()),
        'isl_new_supported_labels': list(isl_new_labels_dict.values()),
        'debug_info': {
            'model_type': str(type(model)) if model else 'None',
            'isl_new_model_type': str(type(isl_new_model)) if isl_new_model else 'None',
            'hands_type': str(type(hands)) if hands else 'None',
            'current_working_dir': str(Path.cwd())
        }
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'})

@app.route('/predict', methods=['POST'])
def predict():
    """Predict sign language from image data or hand features"""
    try:
        if model is None:
            return jsonify({'error': 'Model not loaded'}), 500
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Check if we have image data or hand features
        if 'image' in data:
            # Handle image data (base64 encoded)
            image_cv = preprocess_image(data['image'])
            if image_cv is None:
                return jsonify({'error': 'Invalid image data'}), 400
            
            # Extract hand features from image
            features, has_hand = extract_hand_features(image_cv)
            if not has_hand:
                return jsonify({
                    'prediction': 'No hand detected',
                    'confidence': 0.0,
                    'success': False
                })
        
        elif 'features' in data:
            # Handle pre-extracted hand features
            features = np.array(data['features'])
            if len(features) == 0:
                return jsonify({
                    'prediction': 'No hand features provided',
                    'confidence': 0.0,
                    'success': False
                })
        else:
            return jsonify({'error': 'No image or features data provided'}), 400
        
        # Make prediction
        prediction = model.predict([features])
        predicted_class = str(prediction[0])  # Convert to string
        predicted_character = labels_dict.get(predicted_class, 'Unknown')
        
        # Calculate confidence (simplified)
        confidence = 0.85  # Placeholder confidence
        
        return jsonify({
            'prediction': predicted_character,
            'confidence': confidence,
            'success': True,
            'features_count': len(features)
        })
        
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/predict_batch', methods=['POST'])
def predict_batch():
    """Predict multiple images at once"""
    try:
        if model is None:
            return jsonify({'error': 'Model not loaded'}), 500
        
        data = request.get_json()
        if not data or 'images' not in data:
            return jsonify({'error': 'No images data provided'}), 400
        
        results = []
        for i, image_data in enumerate(data['images']):
            try:
                # Preprocess image
                image_cv = preprocess_image(image_data)
                if image_cv is None:
                    results.append({'index': i, 'error': 'Invalid image data'})
                    continue
                
                # Extract hand features
                features, has_hand = extract_hand_features(image_cv)
                if not has_hand:
                    results.append({
                        'index': i,
                        'prediction': 'No hand detected',
                        'confidence': 0.0,
                        'success': False
                    })
                    continue
                
                # Make prediction
                prediction = model.predict([features])
                predicted_class = str(prediction[0])  # Convert to string
                predicted_character = labels_dict.get(predicted_class, 'Unknown')
                
                results.append({
                    'index': i,
                    'prediction': predicted_character,
                    'confidence': 0.85,
                    'success': True
                })
                
            except Exception as e:
                results.append({'index': i, 'error': str(e)})
        
        return jsonify({'results': results})
        
    except Exception as e:
        logger.error(f"Batch prediction error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/isl_new_predict', methods=['POST'])
def isl_new_predict():
    """Predict sign language using ISL_NEW model from hand features"""
    try:
        if isl_new_model is None:
            return jsonify({'error': 'ISL_NEW model not loaded'}), 500
        
        data = request.get_json()
        if not data or 'features' not in data:
            return jsonify({'error': 'No features data provided'}), 400
        
        features = np.array(data['features'])
        if len(features) == 0:
            return jsonify({
                'prediction': 'No hand features provided',
                'confidence': 0.0,
                'success': False
            })
        
        # Ensure features are the right length (84 for ISL_NEW model)
        expected_len = 84
        if len(features) < expected_len:
            features = np.pad(features, (0, expected_len - len(features)), 'constant')
        elif len(features) > expected_len:
            features = features[:expected_len]
        
        # Make prediction using ISL_NEW model
        prediction = isl_new_model.predict([features])
        predicted_label = prediction[0]
        
        # Convert prediction to character
        if isinstance(predicted_label, str):
            predicted_character = predicted_label
        else:
            predicted_character = isl_new_labels_dict.get(int(predicted_label), str(predicted_label))
        
        # Calculate confidence (simplified - in real implementation, use predict_proba)
        confidence = 0.85  # Placeholder confidence
        
        return jsonify({
            'prediction': predicted_character,
            'confidence': confidence,
            'success': True,
            'model': 'ISL_NEW',
            'features_count': len(features)
        })
        
    except Exception as e:
        logger.error(f"ISL_NEW prediction error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Initialize model in a separate thread to avoid blocking
    def init_model_thread():
        time.sleep(1)  # Give Flask time to start
        initialize_model()
    
    threading.Thread(target=init_model_thread, daemon=True).start()
    
    # Start Flask app
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
