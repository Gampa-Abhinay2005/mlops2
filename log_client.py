import zmq
from loguru import logger

# ZeroMQ client setup
context = zmq.Context()
socket = context.socket(zmq.PUSH)
socket.connect("tcp://localhost:5555")

def log_to_server(message):
    """Function to send log messages to the ZeroMQ server."""
    socket.send_string(message)


logger.remove()  # Remove default Loguru handlers
logger.add(log_to_server, format="{time} {level} {message}", level="INFO")

logger.info("Client logging initialized")
