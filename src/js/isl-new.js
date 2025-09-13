// ISL New Model Integration JavaScript
// Advanced sign language detection using the ISL_NEW model

// --- Background Animation ---
(function createNodeBackground() {
    const canvas = document.createElement('canvas');
    canvas.id = 'node-bg-canvas';
    canvas.style.position = 'fixed';
    canvas.style.top = '0';
    canvas.style.left = '0';
    canvas.style.width = '100vw';
    canvas.style.height = '100vh';
    canvas.style.zIndex = '-1';
    canvas.style.pointerEvents = 'none';
    document.body.prepend(canvas);
    const ctx = canvas.getContext('2d');

    let width = window.innerWidth;
    let height = window.innerHeight;
    canvas.width = width;
    canvas.height = height;

    window.addEventListener('resize', () => {
        width = window.innerWidth;
        height = window.innerHeight;
        canvas.width = width;
        canvas.height = height;
    });

    const NODES = 60;
    const nodes = [];
    for (let i = 0; i < NODES; i++) {
        nodes.push({
            x: Math.random() * width,
            y: Math.random() * height,
            vx: (Math.random() - 0.5) * 0.7,
            vy: (Math.random() - 0.5) * 0.7
        });
    }

    function draw() {
        ctx.clearRect(0, 0, width, height);
        // Draw lines
        for (let i = 0; i < NODES; i++) {
            for (let j = i + 1; j < NODES; j++) {
                const dx = nodes[i].x - nodes[j].x;
                const dy = nodes[i].y - nodes[j].y;
                const dist = Math.sqrt(dx * dx + dy * dy);
                if (dist < 140) {
                    ctx.strokeStyle = 'rgba(102, 126, 234,' + (1 - dist / 140) + ')';
                    ctx.lineWidth = 1.2;
                    ctx.beginPath();
                    ctx.moveTo(nodes[i].x, nodes[i].y);
                    ctx.lineTo(nodes[j].x, nodes[j].y);
                    ctx.stroke();
                }
            }
        }
        // Draw nodes
        for (let i = 0; i < NODES; i++) {
            ctx.beginPath();
            ctx.arc(nodes[i].x, nodes[i].y, 3, 0, 2 * Math.PI);
            ctx.fillStyle = '#fff';
            ctx.shadowColor = '#667eea';
            ctx.shadowBlur = 8;
            ctx.fill();
            ctx.shadowBlur = 0;
        }
    }

    function update() {
        for (let i = 0; i < NODES; i++) {
            nodes[i].x += nodes[i].vx;
            nodes[i].y += nodes[i].vy;
            if (nodes[i].x < 0 || nodes[i].x > width) nodes[i].vx *= -1;
            if (nodes[i].y < 0 || nodes[i].y > height) nodes[i].vy *= -1;
        }
    }

    function animate() {
        update();
        draw();
        requestAnimationFrame(animate);
    }
    animate();
})();

// DOM Elements
const videoElement = document.getElementById('isl-video');
const canvasElement = document.getElementById('isl-canvas');
const canvasCtx = canvasElement.getContext('2d');
const predictedCharacter = document.getElementById('predicted-character');
const confidenceFill = document.getElementById('confidence-fill');
const confidenceText = document.getElementById('confidence-text');
const statusDot = document.getElementById('status-dot');
const statusText = document.getElementById('status-text');
const detectionStatus = document.getElementById('detection-status');
const loadingOverlay = document.getElementById('loading-overlay');

// Control elements
const startDetectionBtn = document.getElementById('start-detection');
const stopDetectionBtn = document.getElementById('stop-detection');
const captureFrameBtn = document.getElementById('capture-frame');
const clearHistoryBtn = document.getElementById('clear-history');
const detectionMode = document.getElementById('detection-mode');
const confidenceThreshold = document.getElementById('confidence-threshold');
const thresholdValue = document.getElementById('threshold-value');
const detectionSpeed = document.getElementById('detection-speed');

// History elements
const historyList = document.getElementById('history-list');
const backendStatusValue = document.getElementById('backend-status-value');
const lastDetected = document.getElementById('last-detected');

// Global variables
let hands = null;
let camera = null;
let isDetectionActive = false;
let detectionHistory = [];
let lastPrediction = null;
let predictionQueue = [];
let isProcessing = false;

// Backend API configuration
const BACKEND_URL = 'http://localhost:5000';
const API_ENDPOINTS = {
    status: `${BACKEND_URL}/status`,
    predict: `${BACKEND_URL}/predict`,
    health: `${BACKEND_URL}/health`,
    isl_new_predict: `${BACKEND_URL}/isl_new_predict`
};

// Hand connections for MediaPipe Hands
const HAND_CONNECTIONS = [
    [0, 1], [1, 2], [2, 3], [3, 4], // thumb
    [0, 5], [5, 6], [6, 7], [7, 8], // index finger
    [0, 9], [9, 10], [10, 11], [11, 12], // middle finger
    [0, 13], [13, 14], [14, 15], [15, 16], // ring finger
    [0, 17], [17, 18], [18, 19], [19, 20], // pinky
    [0, 5], [5, 9], [9, 13], [13, 17] // palm connections
];

// MediaPipe Hands configuration
const handsConfig = {
    locateFile: (file) => {
        return `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`;
    }
};

const modelConfig = {
    maxNumHands: 1,
    modelComplexity: 1,
    minDetectionConfidence: 0.5,
    minTrackingConfidence: 0.5
};

// Detection speed configurations
const SPEED_CONFIGS = {
    fast: { interval: 33, maxQueue: 2 },      // ~30 FPS
    balanced: { interval: 67, maxQueue: 3 },  // ~15 FPS
    accurate: { interval: 100, maxQueue: 5 }  // ~10 FPS
};

// Status update function
function updateStatus(message, type = 'info') {
    if (statusText) {
        statusText.textContent = message;
    }
    
    if (statusDot) {
        statusDot.className = 'status-dot ' + type;
    }
    
    console.log(`ISL New Status: ${message} (${type})`);
}

// Update model status
function updateModelStatus(status) {
    const modelStatusElement = document.getElementById('model-status');
    if (modelStatusElement) {
        modelStatusElement.textContent = status;
    }
}

// Backend status check
async function checkBackendStatus() {
    try {
        const response = await fetch(API_ENDPOINTS.status, {
            method: 'GET',
            timeout: 5000
        });
        
        if (response.ok) {
            const data = await response.json();
            const isConnected = data.model_loaded && data.mediapipe_loaded;
            
            if (isConnected) {
                updateStatus('Backend connected - Ready for detection', 'success');
                updateModelStatus('Online');
                if (backendStatusValue) {
                    backendStatusValue.textContent = 'Online';
                }
                return true;
            } else {
                updateStatus('Backend connected but model not loaded', 'warning');
                updateModelStatus('Partial');
                if (backendStatusValue) {
                    backendStatusValue.textContent = 'Partial';
                }
                return false;
            }
        } else {
            throw new Error('Backend not responding');
        }
    } catch (error) {
        updateStatus('Backend offline - Please start the server', 'error');
        updateModelStatus('Offline');
        if (backendStatusValue) {
            backendStatusValue.textContent = 'Offline';
        }
        console.error('Backend check failed:', error);
        return false;
    }
}

// Extract hand features from MediaPipe results
function extractHandFeatures(results) {
    if (!results.multiHandLandmarks || results.multiHandLandmarks.length === 0) {
        return null;
    }
    
    try {
        const landmarks = results.multiHandLandmarks[0];
        const data_aux = [];
        const x_ = [];
        const y_ = [];
        
        // Extract coordinates
        for (let i = 0; i < landmarks.length; i++) {
            x_.push(landmarks[i].x);
            y_.push(landmarks[i].y);
        }
        
        // Normalize coordinates (same as ISL_NEW inference_classifier.py)
        for (let i = 0; i < landmarks.length; i++) {
            data_aux.push(landmarks[i].x - Math.min(...x_));
            data_aux.push(landmarks[i].y - Math.min(...y_));
        }
        
        // Pad or truncate to expected length (84 features as per ISL_NEW)
        const expected_len = 84;
        if (data_aux.length < expected_len) {
            data_aux.push(...Array(expected_len - data_aux.length).fill(0));
        } else {
            data_aux.splice(expected_len);
        }
        
        return data_aux;
    } catch (error) {
        console.error('Error extracting hand features:', error);
        return null;
    }
}

// Send prediction request to backend
async function sendPredictionRequest(handFeatures) {
    if (!handFeatures || isProcessing) {
        return null;
    }
    
    try {
        isProcessing = true;
        
        const response = await fetch(API_ENDPOINTS.isl_new_predict, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                features: handFeatures
            })
        });
        
        if (response.ok) {
            const data = await response.json();
            return data;
        } else {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
    } catch (error) {
        console.error('Prediction request failed:', error);
        return null;
    } finally {
        isProcessing = false;
    }
}

// Update confidence display
function updateConfidenceDisplay(confidence) {
    if (confidenceFill) {
        confidenceFill.style.width = `${confidence * 100}%`;
    }
    
    if (confidenceText) {
        confidenceText.textContent = `Confidence: ${(confidence * 100).toFixed(1)}%`;
    }
}

// Add detection to history
function addToHistory(character, confidence) {
    const timestamp = new Date().toLocaleTimeString();
    const historyItem = {
        character,
        confidence,
        timestamp
    };
    
    detectionHistory.unshift(historyItem);
    
    // Keep only last 50 items
    if (detectionHistory.length > 50) {
        detectionHistory = detectionHistory.slice(0, 50);
    }
    
    updateHistoryDisplay();
}

// Update history display
function updateHistoryDisplay() {
    if (!historyList) return;
    
    if (detectionHistory.length === 0) {
        historyList.innerHTML = '<div class="history-placeholder" style="text-align: center; color: #666; padding: 20px;">No detections yet. Start detection to see results here.</div>';
        return;
    }
    
    const historyHTML = detectionHistory.map(item => `
        <div class="history-item">
            <div class="history-character">${item.character}</div>
            <div class="history-confidence">${(item.confidence * 100).toFixed(1)}%</div>
            <div class="history-time">${item.timestamp}</div>
        </div>
    `).join('');
    
    historyList.innerHTML = historyHTML;
}

// Update statistics
function updateStats() {
    if (lastDetected && detectionHistory.length > 0) {
        lastDetected.textContent = detectionHistory[0].character;
    }
}

// MediaPipe Hands results handler
function onResults(results) {
    canvasCtx.save();
    canvasCtx.clearRect(0, 0, canvasElement.width, canvasElement.height);
    
    // Draw the video frame
    if (results.image) {
        canvasCtx.drawImage(results.image, 0, 0, canvasElement.width, canvasElement.height);
    }
    
    // Draw hand landmarks
    if (results.multiHandLandmarks) {
        for (const landmarks of results.multiHandLandmarks) {
            drawConnectors(canvasCtx, landmarks, HAND_CONNECTIONS, { color: '#00FF00', lineWidth: 2 });
            drawLandmarks(canvasCtx, landmarks, { color: '#FF0000', lineWidth: 1, radius: 3 });
        }
        
        // Update detection status
        if (detectionStatus) {
            detectionStatus.textContent = 'Hand detected - Processing...';
        }
        
        // Send prediction request if hands are detected and detection is active
        if (results.multiHandLandmarks.length > 0 && isDetectionActive && !isProcessing) {
            const handFeatures = extractHandFeatures(results);
            
            if (handFeatures) {
                // Add to prediction queue based on speed setting
                const speedConfig = SPEED_CONFIGS[detectionSpeed.value];
                if (predictionQueue.length < speedConfig.maxQueue) {
                    predictionQueue.push(handFeatures);
                    
                    // Process queue if not already processing
                    if (predictionQueue.length === 1) {
                        processPredictionQueue();
                    }
                }
            }
        }
    } else {
        // No hand detected
        if (detectionStatus) {
            detectionStatus.textContent = 'No hand detected';
        }
        
        if (isDetectionActive) {
            predictedCharacter.textContent = '-';
            updateConfidenceDisplay(0);
        }
    }
    
    canvasCtx.restore();
}

// Process prediction queue
async function processPredictionQueue() {
    if (predictionQueue.length === 0) return;
    
    const handFeatures = predictionQueue.shift();
    const prediction = await sendPredictionRequest(handFeatures);
    
    if (prediction && prediction.success) {
        const threshold = parseFloat(confidenceThreshold.value);
        
        if (prediction.confidence >= threshold) {
            predictedCharacter.textContent = prediction.prediction;
            updateConfidenceDisplay(prediction.confidence);
            
            // Add to history if confidence is above threshold
            addToHistory(prediction.prediction, prediction.confidence);
            lastPrediction = prediction;
        } else {
            predictedCharacter.textContent = 'Low Confidence';
            updateConfidenceDisplay(prediction.confidence);
        }
    } else if (prediction && !prediction.success) {
        predictedCharacter.textContent = prediction.prediction || 'No hand detected';
        updateConfidenceDisplay(0);
    }
    
    // Process next item in queue with speed-based delay
    if (predictionQueue.length > 0) {
        const speedConfig = SPEED_CONFIGS[detectionSpeed.value];
        setTimeout(() => processPredictionQueue(), speedConfig.interval);
    }
}

// Start detection
async function startDetection() {
    try {
        updateStatus('Starting detection...', 'info');
        
        // Check backend status
        const backendReady = await checkBackendStatus();
        if (!backendReady) {
            updateStatus('Backend not ready - Please start the server', 'error');
            return;
        }
        
        // Initialize MediaPipe Hands if not already done
        if (!hands) {
            updateStatus('Initializing MediaPipe Hands...', 'info');
            hands = new Hands(handsConfig);
            hands.setOptions(modelConfig);
            hands.onResults(onResults);
        }
        
        // Setup camera if not already done
        if (!camera) {
            updateStatus('Setting up camera...', 'info');
            camera = new Camera(videoElement, {
                onFrame: async () => {
                    await hands.send({ image: videoElement });
                },
                width: 640,
                height: 480
            });
        }
        
        // Start camera
        camera.start();
        isDetectionActive = true;
        
        // Update UI
        startDetectionBtn.disabled = true;
        stopDetectionBtn.disabled = false;
        captureFrameBtn.disabled = false;
        
        updateStatus('Detection active - Show hand signs', 'success');
        updateModelStatus('Detecting');
        
    } catch (error) {
        console.error('Error starting detection:', error);
        updateStatus('Failed to start detection', 'error');
    }
}

// Stop detection
function stopDetection() {
    isDetectionActive = false;
    predictionQueue = [];
    
    if (camera) {
        camera.stop();
    }
    
    // Update UI
    startDetectionBtn.disabled = false;
    stopDetectionBtn.disabled = true;
    captureFrameBtn.disabled = true;
    
    predictedCharacter.textContent = '-';
    updateConfidenceDisplay(0);
    
    if (detectionStatus) {
        detectionStatus.textContent = 'Detection stopped';
    }
    
    updateStatus('Detection stopped', 'info');
    updateModelStatus('Online');
}

// Capture single frame
async function captureFrame() {
    if (!isDetectionActive) {
        alert('Please start detection first');
        return;
    }
    
    try {
        updateStatus('Capturing frame...', 'info');
        
        // Get current frame from canvas
        const imageData = canvasElement.toDataURL('image/jpeg', 0.8);
        
        // Send to backend for processing
        const response = await fetch(API_ENDPOINTS.predict, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                image: imageData
            })
        });
        
        if (response.ok) {
            const data = await response.json();
            if (data.success) {
                predictedCharacter.textContent = data.prediction;
                updateConfidenceDisplay(data.confidence);
                
                addToHistory(data.prediction, data.confidence);
                
                updateStatus('Frame captured and processed', 'success');
            } else {
                updateStatus('No hand detected in frame', 'warning');
            }
        } else {
            throw new Error('Failed to process frame');
        }
        
    } catch (error) {
        console.error('Error capturing frame:', error);
        updateStatus('Failed to capture frame', 'error');
    }
}

// Clear detection history
function clearHistory() {
    detectionHistory = [];
    updateHistoryDisplay();
    updateStatus('History cleared', 'info');
}

// Update threshold display
function updateThresholdDisplay() {
    if (thresholdValue) {
        thresholdValue.textContent = `${Math.round(confidenceThreshold.value * 100)}%`;
    }
}

// Loading overlay functions
function showLoadingOverlay() {
    if (loadingOverlay) {
        loadingOverlay.style.display = 'flex';
    }
}

function hideLoadingOverlay() {
    if (loadingOverlay) {
        loadingOverlay.style.display = 'none';
    }
}

// Initialize the ISL New detection system
async function initialize() {
    try {
        showLoadingOverlay();
        updateStatus('Initializing ISL New Model...', 'info');
        
        // Check backend status
        await checkBackendStatus();
        
        // Initialize MediaPipe Hands
        updateStatus('Initializing MediaPipe Hands...', 'info');
        hands = new Hands(handsConfig);
        hands.setOptions(modelConfig);
        hands.onResults(onResults);
        
        // Setup camera
        updateStatus('Setting up camera...', 'info');
        camera = new Camera(videoElement, {
            onFrame: async () => {
                await hands.send({ image: videoElement });
            },
            width: 640,
            height: 480
        });
        
        // Hide loading overlay
        setTimeout(() => {
            hideLoadingOverlay();
            updateStatus('Ready for detection - Click Start Detection', 'success');
        }, 1000);
        
    } catch (error) {
        console.error('Initialization error:', error);
        updateStatus('Failed to initialize detection system', 'error');
        hideLoadingOverlay();
    }
}

// Event listeners
if (startDetectionBtn) {
    startDetectionBtn.addEventListener('click', startDetection);
}

if (stopDetectionBtn) {
    stopDetectionBtn.addEventListener('click', stopDetection);
}

if (captureFrameBtn) {
    captureFrameBtn.addEventListener('click', captureFrame);
}

if (clearHistoryBtn) {
    clearHistoryBtn.addEventListener('click', clearHistory);
}

if (confidenceThreshold) {
    confidenceThreshold.addEventListener('input', updateThresholdDisplay);
}

// Periodic backend status check
setInterval(checkBackendStatus, 15000); // Check every 15 seconds

// Initialize the system when page loads
document.addEventListener('DOMContentLoaded', initialize);
