import sys
import signal
from modules.config import create_client
from modules.thread_manager import ThreadManager
from modules.signal_handler import SignalHandler
from modules.logging_config import setup_logging
from modules.handlers import on_event, on_message

class App:
    def __init__(self):
        self.client = create_client()
        self.thread_manager = ThreadManager(self.client)
        self.signal_handler = SignalHandler(self.thread_manager)
        
    def start(self):
        print("Gates is on deck.")
        print("Running script. Press Ctrl+C to terminate.")
        
        try:
            setup_logging()
            self.signal_handler.setup()
            
            self.thread_manager.start_event_listener(on_event)
            self.thread_manager.start_message_listener(on_message)
            
        except KeyboardInterrupt:
            print("Keyboard interrupt detected. Exiting...")
            self.signal_handler._handle_signal(signal.SIGINT, None)
        except SystemExit:
            raise
        except Exception as e:
            print(f"Error starting application: {e}")
            sys.exit(1)

        msg = {
            "type": "stream",
            "to": "sandbox",
            "topic": "test",
            "content": "Gates is on deck."
        }

        self.client.send_message(msg)

def main():
    app = App()
    app.start()

if __name__ == "__main__":
    main()
