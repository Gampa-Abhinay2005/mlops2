import toml
from loguru import logger

# Load configuration
config = toml.load("config.toml")

# Extract logging settings
log_config = config["logging"]
log_file = log_config["log_file"]
rotation = log_config["rotation"]
compression = log_config["compression"]
level = log_config["level"]

# Set up logging
logger.add(log_file, rotation=rotation, compression=compression, level=level)

logger.info("Logger initialized.")

# Export logger
__all__ = ["logger"]
