"""FastAPI server for gesture processing."""

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

from logger_setup import logger
from validate import load_and_validate_toml

# Load and validate configuration
config = load_and_validate_toml("config.toml")
if not config:
    error_msg = "Invalid TOML Configuration!"
    raise ValueError(error_msg)

server_config = config.server_1

app = FastAPI()

class GestureData(BaseModel):
    """Represents gesture data received from the client."""

    gesture: str

@app.get("/")
async def root() -> dict:
    """Root endpoint that verifies API status."""
    logger.info("Root API called")
    return {"message": "API is running!"}

@app.post("/process_gesture/")
async def process_gesture(data: GestureData) -> dict:
    """Process gesture data and return a response."""
    logger.info(f"Processing gesture: {data.gesture}")
    if data.gesture == "Unknown":
        return {"status": "error", "message": "Unknown gesture"}
    return {"status": "success", "processed_data": data.dict()}

if __name__ == "__main__":
    logger.info("Starting FastAPI server...")
    uvicorn.run(
        app,
        host=server_config["host"],
        port=server_config["port"],
        workers=server_config["workers"],
    )
