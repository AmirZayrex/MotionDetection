import cv2
import numpy as np


class BackgroundModel:
    def __init__(self, blur_ksize=(5, 5), alpha=0.05):
        self.blur_ksize = blur_ksize
        self.alpha = alpha
        self.background = None
        self.is_initialized = False

    def capture(self, frame):

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, self.blur_ksize, 0)

        self.background = gray.astype(np.float32)
        self.is_initialized = True

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