import cv2
import numpy as np
from collections import deque


class MotionDetector:
    def __init__(
        self,
        roi_polygon,
        alpha=0.05,
        threshold=25,
        min_area=1500,
        area_buffer_size=5
    ):
        self.roi_polygon = roi_polygon
        self.alpha = alpha
        self.threshold = threshold
        self.min_area = min_area

        self.background = None
        self.area_buffer = deque(maxlen=area_buffer_size)

        # ماسک ROI از پیش محاسبه می‌شود (بهینه + پایدار)
        self.roi_mask = None

    def initialize_background(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)
        self.background = gray.copy()

        h, w = gray.shape
        self.roi_mask = np.zeros((h, w), dtype=np.uint8)
        cv2.fillPoly(self.roi_mask, [self.roi_polygon], 255)

    def detect(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)

        if self.background is None:
            self.initialize_background(frame)

        # --- Foreground ---
        diff = cv2.absdiff(gray, self.background)
        _, motion_mask = cv2.threshold(
            diff, self.threshold, 255, cv2.THRESH_BINARY
        )

        # --- Morphology (حذف نویز) ---
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        motion_mask = cv2.morphologyEx(motion_mask, cv2.MORPH_OPEN, kernel)
        motion_mask = cv2.morphologyEx(motion_mask, cv2.MORPH_CLOSE, kernel)

        # --- ROI filtering ---
        motion_mask = cv2.bitwise_and(motion_mask, self.roi_mask)

        # --- Motion Area ---
        motion_area = cv2.countNonZero(motion_mask)

        if motion_area < self.min_area:
            motion_area = 0

        # --- Temporal smoothing ---
        self.area_buffer.append(motion_area)
        smoothed_area = int(np.mean(self.area_buffer))

        # --- Background update ---
        self.background = cv2.addWeighted(
            self.background.astype(np.float32),
            1 - self.alpha,
            gray.astype(np.float32),
            self.alpha,
            0
        ).astype(np.uint8)

        # --- Draw ROI ---
        cv2.polylines(
            frame,
            [self.roi_polygon],
            isClosed=True,
            color=(0, 255, 0),
            thickness=2
        )

        return frame, motion_mask, smoothed_area