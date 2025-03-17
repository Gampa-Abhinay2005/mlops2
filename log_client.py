import zmq
from loguru import logger

# ZeroMQ client setup
context = zmq.Context()
socket = context.socket(zmq.PUSH)
socket.connect("tcp://localhost:5555")

def log_to_server(message):
    socket.send_string(message)

logger.add(log_to_server, level="INFO")

logger.info("Client logging initialized")
