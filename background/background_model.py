import cv2
import numpy as np


class BackgroundModel:
    def __init__(self, blur_ksize=(5, 5), alpha=0.05):
        self.blur_ksize = blur_ksize
        self.alpha = alpha
        self.background = None
        self.is_initialized = False

        self.frame_area = None
        self.frozen = False

    def capture(self, frame):

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, self.blur_ksize, 0)

        self.background = gray.astype(np.float32)
        self.is_initialized = True

        h, w = gray.shape
        self.frame_area = h * w

    def update(self, frame):
        if not self.is_initialized:
            raise RuntimeError("Background not initialized")

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, self.blur_ksize, 0)

        cv2.accumulateWeighted(
            gray.astype(np.float32),
            self.background,
            self.alpha
        )

    def get(self):
        if not self.is_initialized:
            raise RuntimeError("Background not initialized")

        return self.background.astype(np.uint8)

    def update_if_stable(self, frame, motion_area, max_motion_area_ratio=0.02):
        if not self.is_initialized or self.frozen:
            return

        if motion_area > max_motion_area_ratio * self.frame_area:
            return

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, self.blur_ksize, 0)

        cv2.accumulateWeighted(
            gray.astype(np.float32),
            self.background,
            self.alpha
        )


    def freeze(self):
        self.frozen = True

    def unfreeze(self):
        self.frozen = False