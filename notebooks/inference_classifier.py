import pickle
import cv2
import mediapipe as mp
import numpy as np
import sys

print("Starting sign language detector...")

# Load the model
try:
    print("Loading model...")
    model_dict = pickle.load(open('./model.p', 'rb'))
    model = model_dict['model']
    print("Model loaded successfully!")
except Exception as e:
    print(f"Error loading model: {e}")
    sys.exit(1)

# Initialize camera
print("Initializing camera...")
cap = cv2.VideoCapture(0)

# Check if camera is opened successfully
if not cap.isOpened():
    print("Error: Could not open camera. Please check if your camera is connected and not being used by another application.")
    sys.exit(1)

print("Camera initialized successfully!")

# Initialize MediaPipe
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

hands = mp_hands.Hands(static_image_mode=True, min_detection_confidence=0.3)

labels_dict = {0: 'A', 1: 'B', 2: 'L'}

print("Starting detection loop. Press 'q' to quit...")

try:
    while True:

        data_aux = []
        x_ = []
        y_ = []

        ret, frame = cap.read()
        
        if not ret:
            print("Error: Could not read frame from camera")
            break

        H, W, _ = frame.shape

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        results = hands.process(frame_rgb)
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    frame,  # image to draw
                    hand_landmarks,  # model output
                    mp_hands.HAND_CONNECTIONS,  # hand connections
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style())

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

            x1 = int(min(x_) * W) - 10
            y1 = int(min(y_) * H) - 10

            x2 = int(max(x_) * W) - 10
            y2 = int(max(y_) * H) - 10

            prediction = model.predict([np.asarray(data_aux)])

            predicted_character = labels_dict[int(prediction[0])]

            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 0), 4)
            cv2.putText(frame, predicted_character, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 0, 0), 3,
                        cv2.LINE_AA)

        cv2.imshow('Sign Language Detector', frame)
        
        # Check for 'q' key press to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Quitting...")
            break

except KeyboardInterrupt:
    print("\nInterrupted by user")
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    print("Cleaning up...")
    cap.release()
    cv2.destroyAllWindows()
    print("Done!")
