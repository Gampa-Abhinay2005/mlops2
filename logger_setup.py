import os
from loguru import logger

os.makedirs("logs", exist_ok=True)

logger.add("logs/gesture_logs.log", rotation="00:00", compression="zip", level="INFO")

logger.info("Logging initialized in logs/ folder")
