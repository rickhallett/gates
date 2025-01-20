import threading
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

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
            print("Starting message listener")
            while not self._stop_event.is_set():
                print("Calling on each message")
                self.client.call_on_each_message(handler)
                print("Checking threads status")
                self.check_threads_status()
        
        self.message_thread = threading.Thread(target=message_listener)
        self.message_thread.start()

    def check_threads_status(self):
        # Check the status of the event and message threads
        if self.event_thread:
            print(f"Event Thread Alive: {self.event_thread.is_alive()}")
        if self.message_thread:
            print(f"Message Thread Alive: {self.message_thread.is_alive()}")

    def stop_all(self):
        print("Stopping all threads")
        self._stop_event.set()
        if self.event_thread:
            print("Stopping event thread")
            self.event_thread.join(timeout=1)
        if self.message_thread:
            print("Stopping message thread")
            self.message_thread.join(timeout=1)  

        if os.getenv("ENVIRONMENT") == "production":
            self.client.send_message({
                "type": "stream",
                "to": "sandbox",
                "topic": "test",
                "content": "Gates is off deck."
            })

        print("All threads stopped")
