"""BentoML service for processing gesture data."""

import bentoml
from bentoml.io import JSON
from pydantic import BaseModel

from logger_setup import logger
from validate import load_and_validate_toml

# Load and validate configuration
config = load_and_validate_toml("config.toml")
if not config:
    error_msg = "Invalid TOML Configuration!"
    raise ValueError(error_msg)

server_config = config.server_2

svc = bentoml.Service("gesture_service")

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
    bentoml.serve(
        "bentoml_service:svc",
        host=server_config["host"],
        port=server_config["port"],
    )
