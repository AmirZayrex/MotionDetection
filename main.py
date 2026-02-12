import time
import cv2
from config import (
    CAMERA_INDEX, CAMERA_WIDTH, CAMERA_HEIGHT,
    ALPHA, MOTION_THRESHOLD, AREA_BUFFER_SIZE
)
from camera.camera import Camera
from motion.motion_detector import MotionDetector
from fsm.state_machine import FSM
from events.event_logger import EventLogger

camera = Camera(CAMERA_INDEX, CAMERA_WIDTH, CAMERA_HEIGHT)
camera.open()

motion_detector = MotionDetector(
    alpha=ALPHA,
    threshold=MOTION_THRESHOLD,
    buffer_size=AREA_BUFFER_SIZE,
    min_area=500,
    merge_dist=50
)

fsm = FSM()
event_logger = EventLogger()

print("Press 'b' to capture background")
while True:
    frame = camera.read()
    if frame is None:
        continue

    cv2.imshow("Live Camera", frame)
    if cv2.waitKey(1) & 0xFF == ord('b'):
        motion_detector.initialize_background(frame)
        print("Background Captured")
        break

time.sleep(0.5)

while True:
    frame = camera.read()
    if frame is None:
        continue

    frame_display, motion_mask, smoothed_area, trend = motion_detector.detect(frame)

    event_type, state, exit_counter, last_exit_frame = fsm.update(
        smoothed_area, frame_display
    )

    if event_type == "EXIT":
        event_logger.log_event(event_type, last_exit_frame, smoothed_area)
    elif event_type is not None:
        event_logger.log_event(event_type, frame_display, smoothed_area)

    cv2.putText(
        frame_display,
        f"Area:{int(smoothed_area)} State:{state} Trend:{int(trend)}",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 0),
        2
    )

    cv2.imshow("Live Camera", frame_display)
    cv2.imshow("Motion Mask", motion_mask)

    # if cv2.waitKey(1) & 0xFF == ord('q'):
    #     break
    if cv2.waitKey(1) == ord('q') or event_type == "EXIT":
        break
camera.release()
cv2.destroyAllWindows()