# core/hand_tracker.py
"""
Hand tracking functionality using Ultra Leap
Extracted from the original tic_tac_toe.py for reusability
"""

import leap
import time
import threading
from dataclasses import dataclass
from .constants import WINDOW_WIDTH, WINDOW_HEIGHT, HAND_PINCH_THRESHOLD, HAND_TRACKING_UPDATE_RATE


@dataclass
class HandData:
    x: int = 400
    y: int = 400
    pinching: bool = False
    active: bool = False
    hands_count: int = 0


class HandTracker:
    def __init__(self):
        self.hand_data = HandData()
        self.connection = None
        self.running = False
        self.thread = None
        
    def start(self):
        """Start hand tracking in a separate thread"""
        self.running = True
        self.thread = threading.Thread(target=self._tracking_loop, daemon=True)
        self.thread.start()
        
    def stop(self):
        """Stop hand tracking thread"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
            
    def _tracking_loop(self):
        """Separate thread for hand tracking"""
        print("Starting hand tracking thread...")
        
        listener = TrackingListener(self.hand_data)
        connection = leap.Connection()
        connection.add_listener(listener)
        
        try:
            with connection.open():
                connection.set_tracking_mode(leap.TrackingMode.Desktop)
                print("Hand tracking thread connected")
                
                while self.running:
                    time.sleep(HAND_TRACKING_UPDATE_RATE)
                    
        except Exception as e:
            print(f"Hand tracking error: {e}")
        
        print("Hand tracking thread stopped")


class TrackingListener(leap.Listener):
    def __init__(self, hand_data):
        self.hand_data = hand_data
        self.last_update = 0
        
    def on_connection_event(self, event):
        print("Connected to Ultra Leap (threaded)")
        
    def on_device_event(self, event):
        try:
            with event.device.open():
                info = event.device.get_info()
        except leap.LeapCannotOpenDeviceError:
            info = event.device.get_info()
        print(f"Found device {info.serial} (threaded)")
        
    def on_tracking_event(self, event):
        current_time = time.time()
        
        self.hand_data.hands_count = len(event.hands)
        self.hand_data.active = True
        
        if event.hands:
            hand = event.hands[0]
            palm = hand.palm
            
            # Convert coordinates
            self.hand_data.x = int((palm.position.x + 200) * (WINDOW_WIDTH / 400))
            self.hand_data.y = int((400 - palm.position.y) * (WINDOW_HEIGHT / 400))
            
            # Keep within bounds
            self.hand_data.x = max(0, min(WINDOW_WIDTH, self.hand_data.x))
            self.hand_data.y = max(0, min(WINDOW_HEIGHT, self.hand_data.y))
            
            # Detect pinch
            if len(hand.digits) >= 2:
                thumb_tip = hand.digits[0].distal.next_joint
                index_tip = hand.digits[1].distal.next_joint
                distance = ((thumb_tip.x - index_tip.x) ** 2 + 
                           (thumb_tip.y - index_tip.y) ** 2 + 
                           (thumb_tip.z - index_tip.z) ** 2) ** 0.5
                self.hand_data.pinching = distance < HAND_PINCH_THRESHOLD
            else:
                self.hand_data.pinching = False
        else:
            self.hand_data.pinching = False
            
        self.last_update = current_time