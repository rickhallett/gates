import sys
import signal
import time
from modules.config import create_client
from modules.thread_manager import ThreadManager
from modules.signal_handler import SignalHandler
from modules.logging_config import setup_logging
from modules.handlers import MessageHandler

class App:
    def __init__(self):
        self.client = create_client()
        self.thread_manager = ThreadManager(self.client)
        self.signal_handler = SignalHandler(self.thread_manager, self.client)
        self.message_handler = MessageHandler(self.client)
        
    def start(self):
        print("Gates is on deck.")
        print("Running script. Press Ctrl+C to terminate.")

        self.client.send_message({
            "type": "stream",
            "to": "gates",
            "topic": "status",
            "content": "Gates is on deck."
        })
        
        try:
            setup_logging()
            self.signal_handler.setup()

            queue_id = None
            last_event_id = -1  # Track the last event ID
            while True:
                try:
                    if queue_id is None:
                        response = self.client.register()
                        queue_id = response['queue_id']
                        last_event_id = -1  # Reset event ID on new queue
                    
                    response = self.client.get_events(queue_id=queue_id, last_event_id=last_event_id)
                    if 'events' not in response:
                        print(f"Invalid response from server: {response}")
                        queue_id = None  # Force re-registration
                        time.sleep(5)
                        continue

                    for event in response['events']:
                        last_event_id = max(last_event_id, event['id'])
                        if event['type'] == 'message':
                            self.message_handler.on_message(event['message'])
                except Exception as e:
                    print(f"Error in event loop: {e}")
                    print(f"Full error response: {response}")  # Add more debug info
                    queue_id = None  # Force re-registration
                    time.sleep(5)  # Wait before retrying
        except KeyboardInterrupt:
            print("Keyboard interrupt detected. Exiting...")
            self.signal_handler._handle_signal(signal.SIGINT, None)
        except SystemExit:
            print("System exit detected. Exiting...")
            self.signal_handler._handle_signal(signal.SIGTERM, None)
        except Exception as e:
            print(f"Error starting application: {e}")
            sys.exit(1)

        

def main():
    app = App()
    app.start()

if __name__ == "__main__":
    main()
