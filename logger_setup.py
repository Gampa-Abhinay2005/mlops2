from loguru import logger

# Configure Loguru Logging
logger.add("gesture_logs.log", rotation="00:00", compression="zip", level="INFO")

logger.info("Logger initialized")

# Export logger for use in other scripts
__all__ = ["logger"]
