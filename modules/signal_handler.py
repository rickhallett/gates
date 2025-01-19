import signal
import sys
import os

class SignalHandler:
    def __init__(self, thread_manager, client):
        self.thread_manager = thread_manager
        self.client = client
        
    def setup(self):
        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)
        
    def _handle_signal(self, signum, frame):
        print(f"Gates was thrown overboard. Signum: {signum}, Frame: {frame}")
        self.client.send_message({
            "type": "stream",
            "to": "gates",
            "topic": "status",
            "content": f"Gates was thrown overboard. Signum: {signum}, Frame: {frame}"
        })
        self.thread_manager.stop_all()
        os._exit(0)
