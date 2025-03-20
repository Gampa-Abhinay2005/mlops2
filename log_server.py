"""Log server for receiving and storing log messages.

This script listens for log messages from the ZeroMQ server and logs them to a file.
"""

import zmq
from loguru import logger

# ZeroMQ server setup
context = zmq.Context()
socket = context.socket(zmq.PULL)
socket.bind("tcp://*:5555")  # Listen for log messages

# Setup Loguru logging to file
logger.add("logs/unified_log.log", rotation="00:00", compression="zip", level="INFO")

logger.info("Logging server started...")

while True:
    message = socket.recv_string()
    logger.info(message)
