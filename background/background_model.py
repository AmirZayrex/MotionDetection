# import cv2
# from config import BACKGROUND_BLUR_KERNEL
#
# def capture_background(frame):
#     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#     gray_blur = cv2.GaussianBlur(gray, BACKGROUND_BLUR_KERNEL, 0)
#     return gray_blur


import cv2
import numpy as np

class BackgroundModel:
    def __init__(self, alpha=0.05):
        self.alpha = alpha
        self.background = None

    def initialize(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        self.background = cv2.GaussianBlur(gray, (5, 5), 0)

    def update(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)

        self.background = cv2.addWeighted(
            self.background.astype("float32"),
            1 - self.alpha,
            gray.astype("float32"),
            self.alpha,
            0
        ).astype("uint8")

    def diff(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)
        return cv2.absdiff(gray, self.background)