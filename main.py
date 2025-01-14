import sys
import threading
import signal
import logging
import zulip
from data_types import Message

def start_event_listener():
    client.call_on_each_event(on_event)

def start_message_listener():
    client.call_on_each_message(on_message)

def on_event(event):
    pass

def on_message(message):
    new_message = Message(**message)
    sys.stdout.write(str(new_message) + "\n\n")
    logging.info(str(new_message))
    if new_message.audio_links:
        for link in new_message.audio_links:
            print(link)

def signal_handler(signal, frame):
    print("Gates is off deck.")
    
    if event_listener_thread:
        event_listener_thread.join()
    if message_listener_thread:
        message_listener_thread.join()

    sys.exit(0)

def setup_logging():
    logging.basicConfig(filename="logs/gates.message.log", level=logging.INFO)
    logging.basicConfig(filename="logs/gates.event.log", level=logging.INFO)

client = zulip.Client(config_file="zuliprc")
event_listener_thread = None
message_listener_thread = None

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def main():
    print("Gates is on deck.")
    print("Running script. Press Ctrl+C to terminate.")

    try:
        event_listener_thread = threading.Thread(target=start_event_listener)
        event_listener_thread.start()
        message_listener_thread = threading.Thread(target=start_message_listener)
        message_listener_thread.start()
    except KeyboardInterrupt:
        print("Keyboard interrupt detected. Exiting...")
        signal_handler(signal.SIGINT, signal_handler)
    except Exception as e:
        print(f"Error starting threads: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
