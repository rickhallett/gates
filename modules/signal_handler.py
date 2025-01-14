import signal
import sys
import os

class SignalHandler:
    def __init__(self, thread_manager):
        self.thread_manager = thread_manager
        
    def setup(self):
        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)
        
    def _handle_signal(self, signum, frame):
        self.thread_manager.stop_all()
        print("Gates is off deck.")
        os._exit(0)
        print("Shouldn't see this")
