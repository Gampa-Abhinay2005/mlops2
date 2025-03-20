"""Load Testing API Endpoints with Locust."""

import logging
from locust import HttpUser, task, between

# Configure logging
logging.basicConfig(filename="locust_requests.log", level=logging.INFO, format="%(asctime)s - %(message)s")

class GestureAPIUser(HttpUser):
    """Simulate a user sending requests to the Gesture APIs."""
    
    wait_time = between(1, 3)  # Simulate real user delay

    @task
    def test_fastapi_process_gesture(self) -> None:
        """Test FastAPI process_gesture endpoint."""
        response = self.client.post("http://localhost:8000/process_gesture/", json={"gesture": "Thumbs Up"})
        logging.info("FastAPI Response: %s", response.text)

    @task
    def test_bentoml_process_gesture(self) -> None:
        """Test BentoML process_gesture endpoint."""
        response = self.client.post("http://localhost:3000/process_gesture", json={"gesture": "Thumbs Up"})
        logging.info("BentoML Response: %s", response.text)
