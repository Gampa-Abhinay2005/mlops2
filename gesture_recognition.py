# """gesture recognition processing."""

# from __future__ import annotations

# import threading
# import time
# from typing import Literal

# import cv2
# import httpx
# import mediapipe as mp
# import pyautogui

# from logger_setup import logger

# mp_hands = mp.solutions.hands
# mp_drawing = mp.solutions.drawing_utils


# class GestureRecognition:
#     """Class for real-time gesture recognition using MediaPipe Hands."""

#     def __init__(self, api_source: Literal["FastAPI", "Other"] = "FastAPI") -> None:
#         """Initialize gesture recognition system with API source."""
#         self.API_SOURCE = api_source
#         self.API_URL = (
#             "http://127.0.0.1:8000/process_gesture/"
#             if self.API_SOURCE == "FastAPI"
#             else "http://127.0.0.1:3000/process_gesture/"
#         )

#         logger.info(f"Using {self.API_SOURCE} for gesture recognition.")
#         self.hands = mp_hands.Hands(min_detection_confidence=0.7,
#                                     min_tracking_confidence=0.7)
#         self.cap = cv2.VideoCapture(0)

#         self.prev_gesture: str = ""
#         self.cooldown_time = 0.01  # Lower cooldown for real-time actions
#         self.last_action_time = time.time()
#         self.lock = threading.Lock()

#     def send_gesture_to_api(self, gesture: str) -> None:
#         """Send API request asynchronously in a separate thread to avoid lag."""
#         try:
#             with httpx.Client() as client:
#                 response = client.post(self.API_URL, json={"gesture": gesture})
#                 # logger.info("API Response: %s", response.json())
#         except httpx.RequestError as e:
#             logger.exception("Failed to send data to API: %s", e)

#     def recognize_gesture(self) -> tuple[cv2.Mat | None, str]:
#         """Detect hand gestures and return the processed frame and detected gesture."""
#         ret, frame = self.cap.read()
#         if not ret:
#             return None, "Error: Camera feed not available"

#         frame = cv2.flip(frame, 1)
#         rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#         results = self.hands.process(rgb_frame)

#         gesture = "Unknown"

#         if results.multi_hand_landmarks:
#             for hand_landmarks in results.multi_hand_landmarks:
#                 mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
#                 landmarks = [(lm.x, lm.y) for lm in hand_landmarks.landmark]

#                 index_finger_tip = landmarks[8]   # Index finger tip
#                 middle_finger_tip = landmarks[12] # Middle finger tip
#                 ring_finger_tip = landmarks[16]   # Ring finger tip
#                 pinky_finger_tip = landmarks[20]  # Pinky finger tip
#                 thumb_tip = landmarks[4]          # Thumb tip

#                 index_finger_dip = landmarks[6]  # Index DIP (near knuckle)
#                 middle_finger_dip = landmarks[10] # Middle DIP
#                 ring_finger_dip = landmarks[14]   # Ring DIP
#                 pinky_finger_dip = landmarks[18]  # Pinky DIP

#                 # 👊 **Fist Detection**: All fingertips below their DIPs
#                 if (
#                     index_finger_tip[1] > index_finger_dip[1] and
#                     middle_finger_tip[1] > middle_finger_dip[1] and
#                     ring_finger_tip[1] > ring_finger_dip[1] and
#                     pinky_finger_tip[1] > pinky_finger_dip[1]
#                 ):
#                     gesture = "Fist"

#                 # 👍 **Thumbs Up**: Thumb up, all other fingers down
#                 elif (
#                     thumb_tip[1] < index_finger_dip[1] and  # Thumb is raised above DIP
#                     index_finger_tip[1] > index_finger_dip[1] and  # Index down
#                     middle_finger_tip[1] > middle_finger_dip[1] and  # Middle down
#                     ring_finger_tip[1] > ring_finger_dip[1] and  # Ring down
#                     pinky_finger_tip[1] > pinky_finger_dip[1]  # Pinky down
#                 ):
#                     gesture = "Thumbs Up"

#                 # ✋ **Open Palm**: All fingertips above their DIPs
#                 elif (
#                     index_finger_tip[1] < index_finger_dip[1] and
#                     middle_finger_tip[1] < middle_finger_dip[1] and
#                     ring_finger_tip[1] < ring_finger_dip[1] and
#                     pinky_finger_tip[1] < pinky_finger_dip[1]
#                 ):
#                     gesture = "Open Palm"

#                 # 👈 **Point Left**: Index extended left, other fingers not extended
#                 elif (
#                     index_finger_tip[0] < index_finger_dip[0] and  # Index pointing left
#                     abs(index_finger_tip[1] - index_finger_dip[1]) < 0.05 and  # Not raised
#                     middle_finger_tip[1] > middle_finger_dip[1] and
#                     ring_finger_tip[1] > ring_finger_dip[1] and
#                     pinky_finger_tip[1] > pinky_finger_dip[1]
#                 ):
#                     gesture = "Point Left"

#                 # 👉 **Point Right**: Index extended right, other fingers not extended
#                 elif (
#                     index_finger_tip[0] > index_finger_dip[0] and  # Index pointing right
#                     abs(index_finger_tip[1] - index_finger_dip[1]) < 0.05 and  # Not raised
#                     middle_finger_tip[1] > middle_finger_dip[1] and
#                     ring_finger_tip[1] > ring_finger_dip[1] and
#                     pinky_finger_tip[1] > pinky_finger_dip[1]
#                 ):
#                     gesture = "Point Right"

#         # Send API request only when the gesture changes
#         if gesture != self.prev_gesture:
#             threading.Thread(target=self.send_gesture_to_api, args=(gesture,), daemon=True).start()

#         # Trigger actions in real-time without lag
#         if time.time() - self.last_action_time > self.cooldown_time:
#             if gesture == "Fist":
#                 pyautogui.press("space")
#                 logger.info("Action Triggered: Jump")
#             elif gesture == "Thumbs Up":
#                 pyautogui.press("up")
#                 logger.info("Action Triggered: Move Up")
#             elif gesture == "Open Palm":
#                 pyautogui.press("p")
#                 logger.info("Action Triggered: Pause Game")
#             elif gesture == "Point Left":
#                 pyautogui.press("left")
#                 logger.info("Action Triggered: Move Left")
#             elif gesture == "Point Right":
#                 pyautogui.press("right")
#                 logger.info("Action Triggered: Move Right")

#             self.prev_gesture = gesture
#             self.last_action_time = time.time()

#         cv2.putText(frame, f"Gesture: {gesture}", (50, 100),
#                     cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
#         return frame, f"Detected Gesture: {gesture}"

#     def run(self) -> None:
#         """Continuously process camera frames for gesture recognition."""
#         while True:
#             frame, message = self.recognize_gesture()
#             if frame is None:
#                 logger.info(message)
#                 break  # Stop if the camera is not available

#             cv2.imshow("Gesture Recognition", frame)

#             # Press 'q' to exit
#             if cv2.waitKey(1) & 0xFF == ord("q"):
#                 break

#         self.release_resources()

#     def release_resources(self) -> None:
#         """Release camera and close all OpenCV windows."""
#         self.cap.release()
#         cv2.destroyAllWindows()
#         logger.info("Resources released.")


# # Run the gesture recognition continuously
# if __name__ == "__main__":
#     recognizer = GestureRecognition()
#     recognizer.run()



"""Gesture recognition processing."""

from __future__ import annotations

import threading
import time
from typing import Literal

import cv2
import httpx
import mediapipe as mp
import pyautogui
import numpy as np

from logger_setup import logger

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils


class GestureRecognition:
    """Class for real-time gesture recognition using MediaPipe Hands."""

    def __init__(self, api_source: Literal["FastAPI", "Other"] = "FastAPI") -> None:
        """Initialize gesture recognition system with API source."""
        self.API_SOURCE = api_source
        self.API_URL = (
            "http://127.0.0.1:8000/process_gesture/"
            if self.API_SOURCE == "FastAPI"
            else "http://127.0.0.1:3000/process_gesture/"
        )

        logger.info(f"Using {self.API_SOURCE} for gesture recognition.")
        self.hands = mp_hands.Hands(min_detection_confidence=0.8,  
                                    min_tracking_confidence=0.8)  
        self.cap = cv2.VideoCapture(0)

        self.cooldown_time = 0.1  
        self.last_action_time = time.time()

    def send_gesture_to_api(self, gesture: str) -> None:
        """Send API request asynchronously in a separate thread to avoid lag."""
        try:
            with httpx.Client() as client:
                response = client.post(self.API_URL, json={"gesture": gesture})
        except httpx.RequestError as e:
            logger.exception("Failed to send data to API: %s", e)

    def recognize_gesture(self) -> tuple[cv2.Mat | None, str]:
        """Detect hand gestures and return the processed frame and detected gesture."""
        ret, frame = self.cap.read()
        if not ret:
            return None, "Error: Camera feed not available"

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)

        gesture = "Unknown"

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                landmarks = [(lm.x, lm.y) for lm in hand_landmarks.landmark]

                wrist = landmarks[0]
                index_tip = landmarks[8]
                middle_tip = landmarks[12]
                ring_tip = landmarks[16]
                pinky_tip = landmarks[20]

                index_pip = landmarks[6]
                middle_pip = landmarks[10]
                ring_pip = landmarks[14]
                pinky_pip = landmarks[18]

                # Gesture Detection
                if all(landmarks[i][1] > landmarks[i - 2][1] for i in [8, 12, 16, 20]):
                    gesture = "Fist"
                elif all(landmarks[i][1] < landmarks[i - 2][1] for i in [8, 12, 16, 20]):
                    gesture = "Open Palm"
                elif abs(landmarks[4][0] - landmarks[8][0]) < 0.03 and abs(landmarks[4][1] - landmarks[8][1]) < 0.03:
                    gesture = "Ok"
                elif landmarks[8][0] < landmarks[6][0] and abs(landmarks[8][1] - landmarks[6][1]) < 0.05:
                    gesture = "Point Left"
                elif landmarks[8][0] > landmarks[6][0] and abs(landmarks[8][1] - landmarks[6][1]) < 0.05:
                    gesture = "Point Right"
                elif wrist[1] > max(index_tip[1], middle_tip[1]) and all(landmarks[i][1] < wrist[1] for i in [8, 12, 16, 20]):
                    gesture = "Move Down"

        # **No action for "Open Palm" - just recognize it**
        if gesture == "Open Palm":
            cv2.putText(frame, f"Gesture: {gesture}", (50, 100),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            return frame, f"Detected Gesture: {gesture}"

        # **Trigger Actions Even If Gesture Repeats**
        if time.time() - self.last_action_time > self.cooldown_time:
            threading.Thread(target=self.send_gesture_to_api, args=(gesture,), daemon=True).start()

            actions = {
                "Fist": "space",
                "Point Left": "left",
                "Point Right": "right",
                "Move Down": "s"
            }
            if gesture in actions:
                pyautogui.press(actions[gesture])
                logger.info(f"Action Triggered: {gesture}")

            self.last_action_time = time.time()

        cv2.putText(frame, f"Gesture: {gesture}", (50, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        return frame, f"Detected Gesture: {gesture}"

    def run(self) -> None:
        """Continuously process camera frames for gesture recognition."""
        while True:
            frame, message = self.recognize_gesture()
            if frame is None:
                logger.info(message)
                break  # Stop if the camera is not available

            cv2.imshow("Gesture Recognition", frame)

            # Press 'q' to exit
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        self.release_resources()

    def release_resources(self) -> None:
        """Release camera and close all OpenCV windows."""
        self.cap.release()
        cv2.destroyAllWindows()
        logger.info("Resources released.")


# Run the gesture recognition continuously
if __name__ == "__main__":
    recognizer = GestureRecognition()
    recognizer.run()