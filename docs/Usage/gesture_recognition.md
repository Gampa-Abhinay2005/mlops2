# Gesture Recognition

The **Gesture Recognition** component handles the detection of gestures in real-time using the **MediaPipe** library.

### Key Features:
- Uses **MediaPipe** for hand landmark detection.
- Detects common gestures such as:
  - **Fist**
  - **Open Palm**
  - **Point Left**
  - **Point Right**
- Triggers **pyautogui** actions (e.g., pressing keys) based on detected gestures.

### Usage
The gesture recognition runs in a loop, capturing frames from the webcam, processing them, and triggering actions based on the detected gestures.
