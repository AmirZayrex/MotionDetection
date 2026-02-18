import time
import cv2
import numpy as np

from config import CAMERA_INDEX, CAMERA_WIDTH, CAMERA_HEIGHT
from camera.camera import Camera
from motion.motion_detector import MotionDetector
from events.event_logger import EventLogger

# ---------- ROI ----------
ROI_POLYGON = np.array(
    [
        [100, 200],
        [500, 200],
        [500, 400],
        [100, 400]
    ],
    dtype=np.int32
)

# ---------- Init ----------
camera = Camera(CAMERA_INDEX, CAMERA_WIDTH, CAMERA_HEIGHT)
camera.open()

motion_detector = MotionDetector(
    min_area=500,
    roi_polygon=ROI_POLYGON
)

event_logger = EventLogger()

# ---------- Main Loop ----------
while True:
    frame = camera.read()
    if frame is None:
        continue

    frame_display, motion_mask, event = motion_detector.detect(frame)

    # --------- Event logging ---------
    if event is not None:
        event_logger.log_event(event, frame_display, 0)

        # اگر خروجی هست برنامه متوقف شود
        if event == "EXIT":
            break

    cv2.imshow("Live Camera", frame_display)
    # cv2.imshow("Motion Mask", motion_mask)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

camera.release()
cv2.destroyAllWindows()