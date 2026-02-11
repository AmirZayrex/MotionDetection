import cv2
import numpy as np

class MotionDetector:
    def __init__(self, alpha=0.05, threshold=25, buffer_size=5, min_area=500, merge_dist=50):
        self.alpha = alpha
        self.threshold = threshold
        self.buffer_size = buffer_size
        self.min_area = min_area
        self.merge_dist = merge_dist

        self.background = None
        self.area_buffer = []
        self.prev_smoothed_area = None

    def initialize_background(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        self.background = cv2.GaussianBlur(gray, (5, 5), 0)

    def detect(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray_blur = cv2.GaussianBlur(gray, (5, 5), 0)

        diff = cv2.absdiff(gray_blur, self.background)
        motion_mask = diff > self.threshold
        motion_mask_uint8 = (motion_mask.astype(np.uint8) * 255)

        contours, _ = cv2.findContours(
            motion_mask_uint8,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        boxes = []
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < self.min_area:
                continue
            x, y, w, h = cv2.boundingRect(cnt)
            boxes.append([x, y, x + w, y + h])

        merged_boxes = self.merge_boxes(boxes)

        for box in merged_boxes:
            x1, y1, x2, y2 = box
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        motion_area = sum((x2 - x1) * (y2 - y1) for x1, y1, x2, y2 in merged_boxes)

        self.area_buffer.append(motion_area)
        if len(self.area_buffer) > self.buffer_size:
            self.area_buffer.pop(0)
        smoothed_area = np.mean(self.area_buffer)

        if self.prev_smoothed_area is None:
            trend = 0
        else:
            trend = smoothed_area - self.prev_smoothed_area
        self.prev_smoothed_area = smoothed_area

        #Adaptive Background Update
        self.background = cv2.addWeighted(
            self.background.astype(np.float32),
            1 - self.alpha,
            gray_blur.astype(np.float32),
            self.alpha,
            0
        ).astype(np.uint8)

        return frame, motion_mask_uint8, smoothed_area, trend

    def merge_boxes(self, boxes):
        if not boxes:
            return []

        merged = True
        while merged:
            merged = False
            new_boxes = []
            used = [False] * len(boxes)

            for i, box1 in enumerate(boxes):
                if used[i]:
                    continue
                x1a, y1a, x2a, y2a = box1
                merged_box = box1.copy()

                for j, box2 in enumerate(boxes):
                    if i == j or used[j]:
                        continue
                    x1b, y1b, x2b, y2b = box2
                    if self.boxes_close(merged_box, box2):
                        merged_box = [
                            min(merged_box[0], x1b),
                            min(merged_box[1], y1b),
                            max(merged_box[2], x2b),
                            max(merged_box[3], y2b)
                        ]
                        used[j] = True
                        merged = True

                new_boxes.append(merged_box)
                used[i] = True

            boxes = new_boxes

        return boxes

    def boxes_close(self, box1, box2):
        x1a, y1a, x2a, y2a = box1
        x1b, y1b, x2b, y2b = box2

        dist_x = max(0, max(x1a - x2b, x1b - x2a))
        dist_y = max(0, max(y1a - y2b, y1b - y2a))

        return dist_x < self.merge_dist and dist_y < self.merge_dist