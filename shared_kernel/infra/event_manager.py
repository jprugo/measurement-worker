import threading
import queue
import time

class EventManager:
    def __init__(self):
        self.event_queue = queue.Queue()
        self.subscribers = []
        self.running = False
        self.lock = threading.Lock()

    def start(self):
        self.running = True
        threading.Thread(target=self.process_events, daemon=True).start()

    def stop(self):
        self.running = False
        self.clear_events()

    def publish(self, message, **kwargs):
        with self.lock:
            if self.running:
                self.event_queue.put((message, kwargs))
                self.notify_subscribers(message, **kwargs)

    def subscribe(self, callback):
        with self.lock:
            self.subscribers.append(callback)

    def notify_subscribers(self, message, **kwargs):
        for callback in self.subscribers:
            callback(message, **kwargs)

    def process_events(self):
        while self.running:
            try:
                message, kwargs = self.event_queue.get(timeout=0.1)  # Use timeout to avoid blocking
                self.handle_event(message, **kwargs)
            except queue.Empty:
                continue

    def handle_event(self, message, **kwargs):
        print(f"Processed event: {message} with args: {kwargs}")

    def clear_events(self):
        while not self.event_queue.empty():
            self.event_queue.get()
        print("Cleared all events.")
