import cv2
import numpy as np

class MotionAccumulator:
    def __init__(self, frame_shape, decay=0.95):
        self.decay = decay
        self.heatmap = np.zeros(frame_shape, np.float32)

    def update(self, motion_mask):
        motion_norm = motion_mask.astype(np.float32) / 255.0

        self.heatmap *= self.decay

        self.heatmap += motion_norm

    def get_heatmap(self, normalize=True):
        if not normalize:
            return self.heatmap
        heatmap_norm = cv2.normalize(
            self.heatmap,
            None,
            0,
            255,
            cv2.NORM_MINMAX,
        )
        return heatmap_norm.astype(np.uint8)
