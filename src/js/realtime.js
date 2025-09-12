// --- Integrated Node Animation Background ---
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
                    ctx.strokeStyle = 'rgba(123,47,242,' + (1 - dist / 140) + ')';
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
            ctx.shadowColor = '#7b2ff2';
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
const videoElement = document.getElementById('realtime-video');
const canvasElement = document.getElementById('realtime-canvas');
const canvasCtx = canvasElement.getContext('2d');
const outputElement = document.getElementById('realtime-output');
const loadingOverlay = document.getElementById('loading-overlay');
const statusText = document.querySelector('.status-text');
const statusDot = document.querySelector('.status-dot');
const cameraOverlay = document.querySelector('.camera-overlay');
const confidenceFill = document.getElementById('realtime-confidence-fill');
const confidenceText = document.getElementById('realtime-confidence-text');
const backendStatus = document.getElementById('backend-status');
const startBackendBtn = document.getElementById('start-backend');
const backendStatusValue = document.getElementById('backend-status-value');

// Stats elements
const totalDetections = document.getElementById('total-detections');
const lastDetected = document.getElementById('last-detected');
const historyList = document.getElementById('history-list');
const clearHistoryBtn = document.getElementById('clear-history');

// Global variables
let hands = null;
let camera = null;
let detectionHistory = [];
let totalDetectionsCount = 0;
let backendConnected = false;
let predictionQueue = [];
let isProcessing = false;

// Backend API configuration
const BACKEND_URL = 'http://localhost:5000';
const API_ENDPOINTS = {
    status: `${BACKEND_URL}/status`,
    predict: `${BACKEND_URL}/predict`,
    health: `${BACKEND_URL}/health`
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

// Status update function
function updateStatus(message, type = 'info') {
    if (statusText) {
        statusText.textContent = message;
    }
    
    if (statusDot) {
        statusDot.className = 'status-dot ' + type;
    }
    
    console.log(`Status: ${message} (${type})`);
}

// Backend status functions
async function checkBackendStatus() {
    try {
        const response = await fetch(API_ENDPOINTS.status, {
            method: 'GET',
            timeout: 5000
        });
        
        if (response.ok) {
            const data = await response.json();
            backendConnected = data.model_loaded && data.mediapipe_loaded;
            
            if (backendConnected) {
                backendStatus.textContent = 'Backend connected and ready';
                backendStatusValue.textContent = 'Online';
                startBackendBtn.style.display = 'none';
                updateStatus('Backend connected - Ready for detection', 'success');
            } else {
                backendStatus.textContent = 'Backend connected but model not loaded';
                backendStatusValue.textContent = 'Partial';
                startBackendBtn.style.display = 'block';
                updateStatus('Backend connected but model not ready', 'warning');
            }
        } else {
            throw new Error('Backend not responding');
        }
    } catch (error) {
        backendConnected = false;
        backendStatus.textContent = 'Backend offline - Click to start server';
        backendStatusValue.textContent = 'Offline';
        startBackendBtn.style.display = 'block';
        updateStatus('Backend offline - Please start the server', 'error');
        console.error('Backend check failed:', error);
    }
}

// Start backend server (placeholder - would need actual server management)
function startBackendServer() {
    updateStatus('Starting backend server...', 'info');
    backendStatus.textContent = 'Starting server...';
    
    // In a real implementation, you would start the Python server here
    // For now, we'll just check the status again
    setTimeout(() => {
        checkBackendStatus();
    }, 2000);
}

// Convert canvas to base64 image
function canvasToBase64(canvas) {
    return canvas.toDataURL('image/jpeg', 0.8);
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
        
        // Normalize coordinates
        for (let i = 0; i < landmarks.length; i++) {
            data_aux.push(landmarks[i].x - Math.min(...x_));
            data_aux.push(landmarks[i].y - Math.min(...y_));
        }
        
        return data_aux;
    } catch (error) {
        console.error('Error extracting hand features:', error);
        return null;
    }
}

// Send prediction request to backend
async function sendPredictionRequest(handFeatures) {
    if (!backendConnected || isProcessing || !handFeatures) {
        return null;
    }
    
    try {
        isProcessing = true;
        
        const response = await fetch(API_ENDPOINTS.predict, {
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

function showCameraOverlay() {
    if (cameraOverlay) {
        cameraOverlay.style.display = 'flex';
    }
}

// Update confidence bar
function updateConfidenceBar(confidence) {
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
    
    // Keep only last 20 items
    if (detectionHistory.length > 20) {
        detectionHistory = detectionHistory.slice(0, 20);
    }
    
    updateHistoryDisplay();
    updateStats();
}

// Update history display
function updateHistoryDisplay() {
    if (!historyList) return;
    
    if (detectionHistory.length === 0) {
        historyList.innerHTML = '<div class="history-placeholder">No signs detected yet</div>';
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
    if (totalDetections) {
        totalDetections.textContent = totalDetectionsCount;
    }
    
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
        
        // Send prediction request if hands are detected and backend is connected
        if (results.multiHandLandmarks.length > 0 && backendConnected && !isProcessing) {
            const handFeatures = extractHandFeatures(results);
            
            if (handFeatures) {
                // Add to prediction queue to avoid overwhelming the backend
                predictionQueue.push(handFeatures);
                
                // Process queue if not already processing
                if (predictionQueue.length === 1) {
                    processPredictionQueue();
                }
            }
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
        outputElement.textContent = prediction.prediction;
        updateConfidenceBar(prediction.confidence);
        
        // Add to history if confidence is high enough
        if (prediction.confidence > 0.7) {
            totalDetectionsCount++;
            addToHistory(prediction.prediction, prediction.confidence);
        }
    } else if (prediction && !prediction.success) {
        outputElement.textContent = prediction.prediction || 'No hand detected';
        updateConfidenceBar(0);
    }
    
    // Process next item in queue
    if (predictionQueue.length > 0) {
        setTimeout(() => processPredictionQueue(), 100);
    }
}

// Initialize the real-time detection system
async function main() {
    try {
        showLoadingOverlay();
        updateStatus('Initializing Real-time Detection System...', 'info');
        
        // Check backend status first
        await checkBackendStatus();
        
        // Initialize MediaPipe Hands
        updateStatus('Initializing MediaPipe Hands...', 'info');
        hands = new Hands(handsConfig);
        hands.setOptions(modelConfig);
        hands.onResults(onResults);
        
        updateStatus('Setting up camera...', 'info');
        
        // Setup camera
        camera = new Camera(videoElement, {
            onFrame: async () => {
                await hands.send({ image: videoElement });
            },
            width: 640,
            height: 480
        });
        
        camera.start();
        
        // Hide loading overlay and show camera overlay
        setTimeout(() => {
            hideLoadingOverlay();
            if (backendConnected) {
                updateStatus('Camera active - Ready for real-time detection', 'success');
            } else {
                updateStatus('Camera active - Backend not connected', 'warning');
            }
            showCameraOverlay();
        }, 1000);
        
    } catch (error) {
        console.error('Initialization error:', error);
        updateStatus('Failed to initialize real-time detection system', 'error');
        
        if (outputElement) {
            outputElement.innerHTML = '<span style="color: #ff4444;">Error: Failed to initialize detection system</span>';
        }
        
        setTimeout(() => {
            hideLoadingOverlay();
        }, 2000);
    }
}

// Event listeners
if (startBackendBtn) {
    startBackendBtn.addEventListener('click', startBackendServer);
}

if (clearHistoryBtn) {
    clearHistoryBtn.addEventListener('click', () => {
        detectionHistory = [];
        totalDetectionsCount = 0;
        updateHistoryDisplay();
        updateStats();
    });
}

// Periodic backend status check
setInterval(checkBackendStatus, 10000); // Check every 10 seconds

// Initialize the system
main();
