import cv2
import numpy as np
from collections import deque


class MotionSignal:
    """
    FSM فقط از return value های این کلاس استفاده میکند و دیگر رابطه مستقیمی بین FSM و MotionDetector وجود ندارد
    درواقع این کلاس برای فیلتر کردن دیتای input FSM طراحی شده
    """
    def __init__(
            self,
            buffer_size=5,
            ema_alpha=0.3,
            dead_zone=200,
            enter_threshold=2000,
            exit_threshold=800
    ):
        self.buffer = deque(maxlen=buffer_size)
        self.ema_alpha = ema_alpha
        self.dead_zone = dead_zone

        self.enter_threshold = enter_threshold
        self.exit_threshold = exit_threshold

        self.ema_value = None
        self.prev_area = None
        self.motion_active = False

        self.stable_area = 0
        self.trend = 0
        self.motion_level = "LOW"

    def update(self, raw_area:float):
        # median filter
        self.buffer.append(raw_area)
        median_area = np.median(self.buffer)

        # Dead Zone
        if self.prev_area is not None:
            if np.abs(median_area - self.prev_area) < self.dead_zone:
                median_area = self.prev_area

        # EMA
        if self.ema_value is None:
            self.ema_value = median_area
        else:
            self.ema_value = (
                self.ema_alpha * median_area
                + (1 - self.ema_alpha) * self.ema_value
            )

        # Trend
        if self.prev_area is None:
            self.trend = 0
        else:
            self.trend = self.ema_value - self.prev_area
        self.prev_area = self.ema_value
        self.stable_area = int(self.ema_value)

        # Motion Area with Hysteresis
        if not self.motion_active and self.stable_area > self.enter_threshold:
            self.motion_active = True

        elif self.motion_active and self.stable_area < self.exit_threshold:
            self.motion_active = False

        # Motion Level
        if self.stable_area < self.exit_threshold:
            self.motion_level = "LOW"
        elif self.stable_area < self.enter_threshold:
            self.motion_level = "MID"
        else:
            self.motion_level = "HIGH"

    def is_motion_started(self):
        return self.motion_active and self.trend > 0

    def is_motion_ended(self):
        return not self.motion_active and self.trend < 0



