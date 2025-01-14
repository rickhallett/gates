import logging

def setup_logging():
    # Configure message logging
    message_logger = logging.getLogger('message_logger')
    message_logger.setLevel(logging.INFO)
    message_handler = logging.FileHandler("logs/gates.message.log")
    message_logger.addHandler(message_handler)
    
    # Configure event logging
    event_logger = logging.getLogger('event_logger')
    event_logger.setLevel(logging.INFO)
    event_handler = logging.FileHandler("logs/gates.event.log")
    event_logger.addHandler(event_handler)
