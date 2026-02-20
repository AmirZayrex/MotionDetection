import cv2
import numpy as np

class AutoROI():
    def __init__(self, threshold_ratio=0.6, min_area=5000):
        self.threshold_ratio = threshold_ratio
        self.min_area = min_area

    def extract(self, heatmap):
        heatmap_norm = cv2.normalize(
            heatmap,
            None,
            0,
            255,
            cv2.NORM_MINMAX).astype(np.uint8)

        max_val = np.max(heatmap_norm)
        _, binary = cv2.threshold(
            heatmap_norm,
            int(max_val * self.threshold_ratio),
            255,
            cv2.THRESH_BINARY
        )

        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)

        contours, _ = cv2.findContours(
            binary,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )
        if not contours:
            return None

        largest = max(contours, key=cv2.contourArea)
        if cv2.contourArea(largest) > self.min_area:
            return None

        epsilon = 0.02 * cv2.arcLength(largest, True)
        roi_polygon = cv2.approxPolyDP(largest, epsilon, True)
        return roi_polygon