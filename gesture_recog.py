import cv2
import mediapipe as mp
import pyautogui
import time
from logger_setup import logger  # Import the configured logger

logger.info("Starting Gesture-Controlled Game")

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)

cap = cv2.VideoCapture(0)

prev_gesture = None
cooldown_time = 0.5  # Delay between actions
log_cooldown_time = 0.5  # Delay between logs
last_action_time = time.time()
last_log_time = time.time()

try:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)
        gesture = "Unknown"

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                landmarks = [(lm.x, lm.y) for lm in hand_landmarks.landmark]

                if all(landmarks[i][1] > landmarks[i - 2][1] for i in [8, 12, 16, 20]):
                    gesture = "Fist"
                elif (landmarks[4][1] < landmarks[2][1]) and all(landmarks[i][1] > landmarks[5][1] for i in [8, 12, 16, 20]):  
                    gesture = "Thumbs Up"
                elif all(landmarks[i][1] < landmarks[i - 2][1] for i in [8, 12, 16, 20]):
                    gesture = "Open Palm"
                elif abs(landmarks[4][0] - landmarks[8][0]) < 0.03 and abs(landmarks[4][1] - landmarks[8][1]) < 0.03:
                    gesture = "Ok"
                elif landmarks[8][0] < landmarks[6][0] and abs(landmarks[8][1] - landmarks[6][1]) < 0.05:
                    gesture = "Point Left"
                elif landmarks[8][0] > landmarks[6][0] and abs(landmarks[8][1] - landmarks[6][1]) < 0.05:
                    gesture = "Point Right"

        if time.time() - last_log_time > log_cooldown_time:
            logger.info(f"Detected Gesture: {gesture}")
            last_log_time = time.time()

        if gesture != prev_gesture and time.time() - last_action_time > cooldown_time:
            if gesture == "Fist":
                pyautogui.press("space")  
                logger.info("Action Triggered: Jump")

            elif gesture == "Thumbs Up":
                pyautogui.press("up")  
                logger.info("Action Triggered: Move Up")

            elif gesture == "Open Palm":
                pyautogui.press("p")  
                logger.info("Action Triggered: Pause Game")

            elif gesture == "Point Left":
                pyautogui.press("left")  
                logger.info("Action Triggered: Move Left")

            elif gesture == "Point Right":
                pyautogui.press("right")  
                logger.info("Action Triggered: Move Right")

            prev_gesture = gesture
            last_action_time = time.time()

        # Display the detected gesture
        cv2.putText(frame, f"Gesture: {gesture}", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.imshow("Gesture Control", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
except Exception:
    logger.exception("An error occurred in the main loop")
finally:
    cap.release()
    cv2.destroyAllWindows()
    logger.info("Camera feed closed")
