import threading
from typing import Optional

class ThreadManager:
    def __init__(self, client):
        self.client = client
        self.event_thread: Optional[threading.Thread] = None
        self.message_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
    
    def start_event_listener(self, handler):
        def event_listener():
            while not self._stop_event.is_set():
                self.client.call_on_each_event(handler)
        
        self.event_thread = threading.Thread(target=event_listener)
        self.event_thread.start()
    
    def start_message_listener(self, handler):
        def message_listener():
            while not self._stop_event.is_set():
                self.client.call_on_each_message(handler)
        
        self.message_thread = threading.Thread(target=message_listener)
        self.message_thread.start()
        
    def stop_all(self):
        print("Stopping all threads")
        self._stop_event.set()  # Signal threads to stop
        if self.event_thread:
            print("Stopping event thread")
            self.event_thread.join(timeout=5)  # Use a timeout
        if self.message_thread:
            print("Stopping message thread")
            self.message_thread.join(timeout=5)  # Use a timeout

        self.client.send_message({
            "type": "stream",
            "to": "sandbox",
            "topic": "test",
            "content": "Gates is off deck."
        })

        print("All threads stopped")
