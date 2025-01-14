import sys
import logging
from data_types import Message

message_logger = logging.getLogger('message_logger')
event_logger = logging.getLogger('event_logger')

def on_event(event):
    event_logger.info(str(event))
    pass

def on_message(message):
    new_message = Message(**message)
    sys.stdout.write(str(new_message) + "\n\n")
    message_logger.info(str(new_message) + "\n\n")
