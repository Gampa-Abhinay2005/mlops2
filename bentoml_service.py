"""BentoML service for processing gesture data."""

import bentoml
from bentoml.io import JSON
from pydantic import BaseModel

from logger_setup import logger
from validate import load_and_validate_toml

# Define BentoML service (Move it to the top)
svc = bentoml.Service("gesture_service")

# Load and validate configuration
config = load_and_validate_toml("config.toml")
if not config:
    mess = "Invalid TOML Configuration!"
    raise ValueError(mess)

server_config = config.server_2

class GestureData(BaseModel):
    """Represents gesture data received from the client."""

    gesture: str

@svc.api(input=JSON(pydantic_model=GestureData), output=JSON())
def process_gesture(data: GestureData) -> dict:
    """Process gesture data and return a response."""
    logger.info(f"Processing gesture: {data.gesture}")
    return {"status": "success", "processed_data": data.dict()}

if __name__ == "__main__":
    logger.info("Starting BentoML service...")
    bentoml.serve(svc, host=server_config.host, port=server_config.port)
