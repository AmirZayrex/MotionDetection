import cv2
from camera.camera import open_camera, read_frame, release_camera
from background.background_model import capture_background
from motion.motion_detector import compute_motion_mask, compute_motion_area
from motion.smoothing import AreaSmoother
from utils.draw import draw_text
from config import AREA_BUFFER_SIZE

background = None
smoother = AreaSmoother(AREA_BUFFER_SIZE)

cap = open_camera()
print("Press 'b' to capture background | 'q' to quit")

while True:
    frame = read_frame(cap)
    if frame is None:
        continue

    display = frame.copy()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    if background is None:
        draw_text(display, "NO BACKGROUND")
        cv2.imshow("Live Camera", display)

    else:
        motion_mask = compute_motion_mask(gray, background)
        motion_area = compute_motion_area(motion_mask)

        smoothed_area, trend = smoother.update(motion_area)

        draw_text(
            display,
            f"Area: {smoothed_area}  Trend: {trend}"
        )

        cv2.imshow("Live Camera", display)
        cv2.imshow("Motion Mask", motion_mask)

    key = cv2.waitKey(1) & 0xFF

    if key == ord('b'):
        background = capture_background(frame)
        print("Background captured")

    elif key == ord('q'):
        break

release_camera(cap)