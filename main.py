import toml
from fastapi import FastAPI
from logger_setup import logger

# Load configuration
config = toml.load("config.toml")
server_config = config["server"]

app = FastAPI()

@app.get("/")
async def root():
    logger.info("Root API called")
    return {"message": "API is running!"}

@app.post("/process_gesture/")
async def process_gesture(data: dict):
    """Example API for processing gestures."""
    logger.info(f"Processing gesture data: {data}")
    return {"status": "success", "processed_data": data}

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting API server...")
    uvicorn.run("main:app", host=server_config["host"], port=server_config["port"], workers=server_config["workers"])
