"""ZeroMQ log client for sending log messages.

This script sends log messages to a ZeroMQ server for centralized logging.
"""

import zmq
from loguru import logger

# ZeroMQ client setup
context = zmq.Context()
socket = context.socket(zmq.PUSH)
socket.connect("tcp://localhost:5555")


def log_to_server(message: str) -> None:
    """Send a log message to the ZeroMQ server."""
    socket.send_string(message)


logger.remove()  # Remove default Loguru handlers
logger.add(log_to_server, format="{time} {level} {message}", level="INFO")

logger.info("Client logging initialized")
