# Real-time Sign Language Detection

This document explains how to use the new real-time sign language detection feature that integrates the Python backend with model.p and data.pickle files.

## Overview

The real-time detection system consists of:
- **Frontend**: HTML/JavaScript interface (`src/pages/realtime.html`)
- **Backend**: Flask API server (`backend/app.py`) 
- **Model**: Uses `model.p` and `data.pickle` files for character recognition
- **Detection**: Supports A, B, L sign language characters

## Setup Instructions

### 1. Install Backend Dependencies

Navigate to the backend directory and install required packages:

```bash
cd backend
pip install -r requirements.txt
```

Required packages:
- Flask==2.3.3
- Flask-CORS==4.0.0
- opencv-python==4.8.1.78
- mediapipe==0.10.7
- numpy==1.24.3
- Pillow==10.0.1
- scikit-learn==1.3.2

### 2. Start the Backend Server

#### Option A: Using the startup script
```bash
cd backend
python start_server.py
```

#### Option B: Direct Flask execution
```bash
cd backend
python app.py
```

The server will start on `http://localhost:5000`

### 3. Access the Real-time Detection Page

1. Open your web browser
2. Navigate to `src/pages/realtime.html` or use the navigation menu
3. Click "Start Backend Server" if the backend is not running
4. Allow camera access when prompted

## How It Works

### Backend Process
1. **Model Loading**: Loads `model.p` and `data.pickle` files
2. **MediaPipe Integration**: Uses MediaPipe Hands for landmark detection
3. **Feature Extraction**: Extracts hand landmarks and normalizes coordinates
4. **Prediction**: Uses the loaded model to predict sign language characters
5. **API Response**: Returns prediction results via REST API

### Frontend Process
1. **Camera Access**: Captures video stream from user's camera
2. **MediaPipe Processing**: Processes video frames for hand detection
3. **API Communication**: Sends image data to backend for prediction
4. **Result Display**: Shows detected characters and confidence levels
5. **History Tracking**: Maintains detection history and statistics

## API Endpoints

### Status Check
```
GET /status
```
Returns backend status and model loading information.

### Prediction
```
POST /predict
Content-Type: application/json

{
    "image": "base64_encoded_image_data"
}
```
Returns prediction results with character and confidence.

### Health Check
```
GET /health
```
Simple health check endpoint.

## Supported Characters

The system currently supports detection of:
- **A**: Closed fist, thumb alongside index
- **B**: Open hand, fingers extended  
- **L**: Index up + thumb horizontal

## Troubleshooting

### Backend Issues
- **Model not loading**: Check if `src/models/model.p` exists
- **Dependencies missing**: Run `pip install -r requirements.txt`
- **Port conflicts**: Ensure port 5000 is available

### Frontend Issues
- **Camera not working**: Check browser permissions
- **Backend connection failed**: Verify server is running on localhost:5000
- **CORS errors**: Ensure Flask-CORS is properly installed

### Performance Issues
- **Slow detection**: Reduce camera resolution or frame rate
- **High CPU usage**: Close other applications
- **Memory issues**: Restart the backend server

## File Structure

```
├── backend/
│   ├── app.py                 # Flask API server
│   ├── requirements.txt       # Python dependencies
│   └── start_server.py       # Server startup script
├── src/
│   ├── pages/
│   │   └── realtime.html     # Real-time detection page
│   ├── js/
│   │   └── realtime.js       # Frontend JavaScript
│   └── models/
│       ├── model.p           # Trained model file
│       └── data.pickle       # Model data file
└── notebooks/
    └── inference_classifier.py # Original Python script
```

## Development Notes

- The backend runs on Flask with CORS enabled for cross-origin requests
- Image data is transmitted as base64-encoded strings
- MediaPipe Hands is used for both frontend and backend hand detection
- The system uses a prediction queue to avoid overwhelming the backend
- Error handling includes graceful degradation when backend is unavailable

## Future Enhancements

- Support for more sign language characters
- Batch prediction for multiple images
- Real-time video streaming optimization
- Model retraining capabilities
- User feedback integration for model improvement
