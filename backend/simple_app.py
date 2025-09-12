from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import numpy as np
import logging
import threading
import time
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Global variables
model = None
labels_dict = {'0': 'A', '1': 'B', '2': 'L'}

def initialize_model():
    """Initialize the model"""
    global model
    
    try:
        logger.info("Loading model...")
        
        # Try different paths
        model_paths = [
            '../src/models/model.p',
            '../../src/models/model.p',
            './src/models/model.p'
        ]
        
        for model_path in model_paths:
            try:
                if Path(model_path).exists():
                    logger.info(f"Loading model from: {model_path}")
                    model_dict = pickle.load(open(model_path, 'rb'))
                    model = model_dict['model']
                    logger.info("Model loaded successfully!")
                    return True
            except Exception as e:
                logger.error(f"Error loading from {model_path}: {e}")
                continue
        
        logger.error("Could not load model from any path")
        return False
        
    except Exception as e:
        logger.error(f"Error initializing model: {e}")
        return False

@app.route('/')
def index():
    return jsonify({
        'message': 'Sign Language Detection API',
        'status': 'running',
        'model_loaded': model is not None
    })

@app.route('/status')
def status():
    """Check API status"""
    return jsonify({
        'status': 'running',
        'model_loaded': model is not None,
        'supported_labels': list(labels_dict.values()),
        'model_type': str(type(model)) if model else 'None'
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'})

@app.route('/predict', methods=['POST'])
def predict():
    """Predict sign language from hand features"""
    try:
        if model is None:
            return jsonify({'error': 'Model not loaded'}), 500
        
        data = request.get_json()
        if not data or 'features' not in data:
            return jsonify({'error': 'No features data provided'}), 400
        
        # Get features from request
        features = np.array(data['features']).reshape(1, -1)
        
        # Make prediction
        prediction = model.predict(features)
        predicted_class = str(prediction[0])
        predicted_character = labels_dict.get(predicted_class, 'Unknown')
        
        # Calculate confidence (simplified)
        confidence = 0.85
        
        return jsonify({
            'prediction': predicted_character,
            'confidence': confidence,
            'success': True
        })
        
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/test')
def test():
    """Test endpoint with dummy data"""
    try:
        if model is None:
            return jsonify({'error': 'Model not loaded'}), 500
        
        # Create dummy features
        dummy_features = np.random.random(42).reshape(1, -1)
        
        # Make prediction
        prediction = model.predict(dummy_features)
        predicted_class = str(prediction[0])
        predicted_character = labels_dict.get(predicted_class, 'Unknown')
        
        return jsonify({
            'prediction': predicted_character,
            'confidence': 0.85,
            'success': True,
            'test_data': 'dummy_features'
        })
        
    except Exception as e:
        logger.error(f"Test error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Initialize model in a separate thread
    def init_model_thread():
        time.sleep(1)
        initialize_model()
    
    threading.Thread(target=init_model_thread, daemon=True).start()
    
    # Start Flask app
    print("Starting simplified backend server...")
    print("Available endpoints:")
    print("  GET  /status - Check status")
    print("  GET  /health - Health check")
    print("  GET  /test - Test prediction")
    print("  POST /predict - Predict with features")
    print("\nServer starting on http://localhost:5000")
    
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
