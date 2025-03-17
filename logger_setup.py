from loguru import logger
import os

# Ensure the logs directory exists
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)  # This will create 'logs' if it doesn't exist

# Correct log file path
log_file_path = os.path.join(log_dir, "gesture_logs.log")

# Setup Loguru logging
logger.add(log_file_path, rotation="00:00", compression="zip", level="INFO")

logger.info("Logger initialized and logging to logs/gesture_logs.log")

# Export logger for use in other scripts
__all__ = ["logger"]
