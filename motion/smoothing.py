import numpy as np
from collections import deque

class AreaSmoother:
    def __init__(self, buffer_size):
        self.buffer = deque(maxlen=buffer_size)
        self.prev_value = None

    def update(self, value):
        self.buffer.append(value)
        smoothed = np.sum(self.buffer) / len(self.buffer)

        if self.prev_value is None:
            trend = 0
        else:
            trend = smoothed - self.prev_value

        self.prev_value = smoothed
        return int(smoothed), int(trend)