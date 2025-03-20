"""Gradio-based UI for gesture recognition with API selection.

This module provides an interactive UI for running gesture recognition
while allowing users to choose between FastAPI and BentoML as the API source.
"""

from __future__ import annotations

import subprocess
import threading
import time

import cv2
import gradio as gr

from gesture_recognition import GestureRecognition

api_process: subprocess.Popen | None = None
gesture_recognizer: GestureRecognition | None = None

def start_api(api_source: str) -> str:
    """Start the selected API (FastAPI or BentoML)."""
    global api_process
    if api_process:
        api_process.terminate()
        time.sleep(2)

    if api_source == "FastAPI":
        api_process = subprocess.Popen(["uv", "run", "fast_api.py"], text=True)
    else:
        api_process = subprocess.Popen(
            ["bentoml", "serve", "bentoml_service:svc", "--host", "127.0.0.1",
            "--port", "3000"],
            text=True,
        )

    time.sleep(3)
    return f"Started {api_source} API!"

def start_gesture_recognition(api_source: str) -> str:
    """Start gesture recognition using the selected API."""
    global gesture_recognizer
    gesture_recognizer = GestureRecognition(api_source)

    def run_recognition() -> None:
        """Run the gesture recognition loop."""
        while True:
            frame, gesture_info = gesture_recognizer.recognize_gesture()
            if frame is None:
                break
            cv2.imshow("Gesture Recognition", cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
        gesture_recognizer.release_resources()

    thread = threading.Thread(target=run_recognition, daemon=True)
    thread.start()
    return "Gesture Recognition Started!"

def gradio_interface() -> gr.Blocks:
    """Create the Gradio interface."""
    with gr.Blocks() as demo:
        gr.Markdown("# Gesture Recognition with API Selection")

        api_selector = gr.Radio(
            ["FastAPI", "BentoML"], label="Select API Source", value="FastAPI")
        start_api_btn = gr.Button("Start API")
        start_gesture_btn = gr.Button("Start Gesture Recognition")

        api_output = gr.Textbox(label="API Status", interactive=False)
        gesture_output = gr.Textbox(
            label="Gesture Recognition Status", interactive=False)

        start_api_btn.click(start_api, inputs=[api_selector], outputs=[api_output])
        start_gesture_btn.click(
            start_gesture_recognition, inputs=[api_selector], outputs=[gesture_output])

    return demo

if __name__ == "__main__":
    demo = gradio_interface()
    demo.launch()
