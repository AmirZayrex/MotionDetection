import os
import time
import cv2

from utils.draw import draw_text

class EventLogger:
    def __init__(self, events_dir="logs"):
        self.events_dir = events_dir
        os.makedirs(self.events_dir, exist_ok=True)
        self.logged_events = []

    def log_event(self, event_type, frame, area):
        ts = int(time.time() * 1000)
        filename = f"{self.events_dir}/{event_type}_{ts}.jpg"

        frame_to_save = frame.copy()

        draw_text(
            frame_to_save,
            f"Area: {int(area)}",
            (40, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            thickness=2
        )

        cv2.imwrite(filename, frame)

        event_data = {
            "type": event_type,
            "time": ts,
            "area": area,
            "image": filename
        }

        self.logged_events.append(event_data)

        print(f"[EVENT] {event_type} | Area: {int(area)}\n")

        return event_data