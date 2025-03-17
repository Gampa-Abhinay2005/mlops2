import sys
import zmq
from loguru import logger

# ZeroMQ server setup
context = zmq.Context()
socket = context.socket(zmq.PULL)
socket.bind("tcp://*:5555")

# Loguru setup
logger.add("logs/gesture_logs.log", rotation="00:00", compression="zip")

logger.info("Logging server started, waiting for messages...")

while True:
    try:
        log_message = socket.recv_string()
        logger.info(log_message)
    except Exception as e:
        logger.exception("Error receiving log message")
