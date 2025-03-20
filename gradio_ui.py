"""Gradio UI for Gesture Recognition with API Selection.

This script provides a Gradio-based UI for selecting and starting different API sources
(FastAPI or BentoML) and launching gesture recognition.
"""

import shutil
import subprocess
import threading
import time

import cv2
import gradio as gr

from gesture_recognition import GestureRecognition


class APIManager:
    """Manages API processes and gesture recognition."""

    def __init__(self) -> None:
        """Initialize APIManager with default values."""
        self.api_process = None
        self.gesture_recognizer = None

    def get_uv_path(self) -> str:
        """Get the absolute path of 'uv' command."""
        uv_path = shutil.which("uv")
        if not uv_path:
            error_msg = "uv executable not found in PATH."
            raise FileNotFoundError(error_msg)
        return uv_path

    def start_api(self, api_source: str) -> str:
        """Start the selected API service.

        Terminates any existing API process before starting a new one.

        Args:
            api_source (str): The API to start, either "FastAPI" or "BentoML".

        Returns:
            str: Confirmation message indicating which API has started.

        """
        if self.api_process:
            self.api_process.terminate()
            time.sleep(2)  # Allow process to terminate properly

        uv_path = self.get_uv_path()
        api_script = "fast_api.py" if api_source == "FastAPI" else "bentoml_service.py"

        # Securely start the subprocess
        self.api_process = subprocess.Popen([uv_path, "run", api_script], shell=False)

        time.sleep(3)  # Allow some time for the API to start
        return f"Started {api_source} API!"

    def start_gesture_recognition(self, api_source: str) -> str:
        """Start gesture recognition using the selected API source.

        Args:
            api_source (str): The API to use for gesture recognition.

        Returns:
            str: Confirmation message indicating gesture recognition has started.

        """
        self.gesture_recognizer = GestureRecognition(api_source)

        def run_recognition() -> None:
            """Continuously capture and display gestures until stopped."""
            while True:
                frame, gesture_info = self.gesture_recognizer.recognize_gesture()
                if frame is None:
                    break
                cv2.imshow("Gesture Recognition", cv2.cvtColor(frame,
                                                               cv2.COLOR_RGB2BGR))
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
            self.gesture_recognizer.release_resources()

        threading.Thread(target=run_recognition, daemon=True).start()
        return "Gesture Recognition Started!"


def gradio_interface(api_manager: APIManager) -> gr.Blocks:
    """Create the Gradio UI for selecting APIs and starting gesture recognition.

    Args:
        api_manager (APIManager): The API manager instance handling API and
        gesture recognition.

    Returns:
        gr.Blocks: The Gradio UI instance.

    """
    with gr.Blocks() as demo:
        gr.Markdown("# Gesture Recognition with API Selection")

        api_selector = gr.Radio(["FastAPI", "BentoML"], label="Select API Source",
                                value="FastAPI")
        start_api_btn = gr.Button("Start API")
        start_gesture_btn = gr.Button("Start Gesture Recognition")

        api_output = gr.Textbox(label="API Status", interactive=False)
        gesture_output = gr.Textbox(label="Gesture Recognition Status",
                                    interactive=False)

        start_api_btn.click(api_manager.start_api, inputs=[api_selector],
                            outputs=[api_output])
        start_gesture_btn.click(api_manager.start_gesture_recognition,
                                inputs=[api_selector],outputs=[gesture_output])

    return demo


if __name__ == "__main__":
    api_manager = APIManager()
    demo = gradio_interface(api_manager)
    demo.launch()
