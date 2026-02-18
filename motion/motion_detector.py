import cv2
import numpy as np
from collections import deque

class MotionDetector:
    def __init__(
        self,
        min_area=1500,
        roi_polygon=None,
        line_ratio=0.4
    ):
        self.min_area = min_area
        self.roi_polygon = roi_polygon
        self.centroid_buffer = deque(maxlen=3)

        # MOG2
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(
            history=500,
            varThreshold=80,
            detectShadows=False
        )

        # Line crossing
        self.line_ratio = line_ratio
        self.prev_side = None

    def initialize_background(self, frame):
        self.bg_subtractor.apply(frame)

    def detect(self, frame):
        fg_mask = self.bg_subtractor.apply(frame)
        _, motion_mask = cv2.threshold(fg_mask, 200, 255, cv2.THRESH_BINARY)

        contours, _ = cv2.findContours(
            motion_mask,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        largest_contour = None
        largest_area = 0

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < self.min_area:
                continue

            if area > largest_area:
                largest_area = area
                largest_contour = cnt

        # centroid = None
        event = None

        h, w = frame.shape[:2]
        line_x = int(w * self.line_ratio)

        # رسم خط
        cv2.line(frame, (line_x, 0), (line_x, h), (255, 0, 0), 2)

        if largest_contour is not None:
            m = cv2.moments(largest_contour)
            if m["m00"] != 0:
                cx = int(m["m10"] / m["m00"])
                cy = int(m["m01"] / m["m00"])
                # centroid = (cx, cy)

                self.centroid_buffer.append((cx, cy))

                avg_cx = int(np.mean([c[0] for c in self.centroid_buffer]))
                avg_cy = int(np.mean([c[1] for c in self.centroid_buffer]))

                centroid = (avg_cx, avg_cy)


                cv2.circle(frame, centroid, 6, (0, 0, 255), -1)

                if self.roi_polygon is not None:
                    if cv2.pointPolygonTest(self.roi_polygon, centroid, False) < 0:
                        return frame, motion_mask, None

                current_side = "left" if cx < line_x else "right"

                if self.prev_side is None:
                    self.prev_side = current_side
                    return frame, motion_mask, None

                if current_side != self.prev_side:
                    if self.prev_side == "left" and current_side == "right":
                        event = "ENTER"
                    elif self.prev_side == "right" and current_side == "left":
                        event = "EXIT"

                self.prev_side = current_side
        return frame, motion_mask, event