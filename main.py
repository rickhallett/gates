import sys
import signal
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

            self.client.call_on_each_message(self.message_handler.on_message)
            
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
