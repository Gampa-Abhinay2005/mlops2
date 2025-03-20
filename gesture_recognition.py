"""Gesture Recognition Module.

This module detects hand gestures using MediaPipe Hands and sends recognized gestures
to an API for further processing.
"""

from __future__ import annotations

import threading
import time
from typing import Literal

import cv2
import httpx
import mediapipe as mp
from loguru import logger

# Constants for gesture detection thresholds
THUMB_TIP = 4
INDEX_TIP = 8
MIDDLE_TIP = 12
RING_TIP = 16
PINKY_TIP = 20
THRESHOLD_NEAR = 0.03
THRESHOLD_POINT = 0.05

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils


class GestureRecognition:
    """Gesture Recognition class to detect hand gestures and send them to an API."""

    def __init__(self, api_source: Literal["FastAPI", "Other"] = "FastAPI") -> None:
        """Initialize GestureRecognition with an API source."""
        self.API_SOURCE = api_source
        self.API_URL = (
            "http://localhost:8000/predict"
            if self.API_SOURCE == "FastAPI"
            else "http://other-api.com"
        )

        self.prev_gesture = None
        self.last_action_time = time.time()
        self.action_delay = 1.0  # Minimum delay between actions in seconds

        logger.info(f"Using {self.API_SOURCE} for gesture recognition.")

        self.hands = mp_hands.Hands(
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7,
        )
        self.cap = cv2.VideoCapture(0)

    def send_gesture_to_api(self, gesture: str) -> None:
        """Send recognized gesture to the API."""
        try:
            with httpx.Client() as client:
                response = client.post(self.API_URL, json={"gesture": gesture})
                logger.info(f"API Response: {response.json()}")
        except httpx.RequestError as e:
            logger.exception(f"Failed to send data to API: {e}")

    def detect_gesture(self, landmarks: list[tuple[float, float]]) -> str:
        """Determine the gesture based on hand landmarks."""
        if landmarks[THUMB_TIP][1] < landmarks[THUMB_TIP - 2][1]:
            return "Thumbs Up"
        if all(landmarks[i][1] < landmarks[i - 2][1] for i in
                [INDEX_TIP, MIDDLE_TIP,RING_TIP, PINKY_TIP]):
            return "Open Palm"
        if (
            abs(landmarks[THUMB_TIP][0] - landmarks[INDEX_TIP][0]) < THRESHOLD_NEAR
            and abs(landmarks[THUMB_TIP][1] - landmarks[INDEX_TIP][1]) < THRESHOLD_NEAR
        ):
            return "Ok"
        if landmarks[INDEX_TIP][0] < landmarks[INDEX_TIP - 2][0] and abs(
            landmarks[INDEX_TIP][1] - landmarks[INDEX_TIP - 2][1]) < THRESHOLD_POINT:
            return "Point Left"
        if landmarks[INDEX_TIP][0] > landmarks[INDEX_TIP - 2][0] and abs(
            landmarks[INDEX_TIP][1] - landmarks[INDEX_TIP - 2][1]) < THRESHOLD_POINT:
            return "Point Right"
        return "Unknown"

    def recognize_gesture(self) -> tuple[cv2.Mat | None, str]:
        """Detect hand gestures and return the processed frame and detected gesture."""
        ret, frame = self.cap.read()
        if not ret:
            return None, "No Frame Captured"

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(frame_rgb)
        gesture = "Unknown"

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks,
                                        mp_hands.HAND_CONNECTIONS)
                landmarks = [(lm.x, lm.y) for lm in hand_landmarks.landmark]
                gesture = self.detect_gesture(landmarks)

        # Send API request only when the gesture changes
        if gesture != self.prev_gesture:
            threading.Thread(target=self.send_gesture_to_api, args=(gesture,),
                            daemon=True).start()
            self.prev_gesture = gesture

        # Trigger actions in real-time without lag
        if time.time() - self.last_action_time > self.action_delay:
            self.last_action_time = time.time()

        cv2.putText(
            frame,
            f"Gesture: {gesture}",
            (50, 100),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2,
        )

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
