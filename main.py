import cv2
import numpy as np
import time

from config import CAMERA_INDEX, CAMERA_WIDTH, CAMERA_HEIGHT
from camera.camera import Camera
from motion.motion_detector import MotionDetector
from fsm.state_machine import FSM
from events.event_logger import EventLogger
from motion.motion_accumulator import MotionAccumulator
from motion.auto_roi import AutoROI
# ---------- ROI (تنها ناحیه مهم سیستم) ----------
ROI_POLYGON = np.array(
    [
        [80, 10],
        [500, 10],
        [500, 470],
        [80, 470]
    ],
    dtype=np.int32
)


def main():
    # ---------- Camera ----------
    camera = Camera(CAMERA_INDEX, CAMERA_WIDTH, CAMERA_HEIGHT)
    camera.open()

    frame = None
    while frame is None:
        frame = camera.read()
        time.sleep(0.02)
    h, w = frame.shape[:2]

    accumulator = MotionAccumulator(
        frame_shape=(h, w),
        decay=0.97)

    # ---------- Motion Detector ----------
    motion_detector = MotionDetector(
        roi_polygon=ROI_POLYGON,
        alpha=0.05,
        threshold=25,
        min_area=1500,
        area_buffer_size=5
    )

    # ---------- FSM & Logger ----------
    fsm = FSM()
    event_logger = EventLogger()

    # ---------- Warm-up ----------
    print("[INFO] Warming up background...")
    for _ in range(30):
        frame = camera.read()
        if frame is not None:
            motion_detector.initialize_background(frame)
        time.sleep(0.03)

    print("[INFO] System started")



    # ---------- Main Loop ----------
    while True:
        frame = camera.read()
        if frame is None:
            continue

        frame_display, motion_mask, smoothed_area = motion_detector.detect(frame)

        accumulator.update(motion_mask)

        heatmap = accumulator.get_heatmap()
        heatmap_color = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)

        event_type, state, exit_counter, last_exit_frame = fsm.update(
            smoothed_area,
            frame_display
        )

        if event_type == "EXIT":
            event_logger.log_event(
                event_type,
                last_exit_frame,
                smoothed_area
            )
        elif event_type is not None:
            event_logger.log_event(
                event_type,
                frame_display,
                smoothed_area
            )


        auto_roi = AutoROI()

        # هر مثلاً 300 فریم:
        roi_polygon = auto_roi.extract(accumulator.heatmap)

        if roi_polygon is not None:
            cv2.polylines(
                frame_display,
                [roi_polygon],
                isClosed=True,
                color=(0, 255, 0),
                thickness=2
            )
            motion_detector.roi_polygon = roi_polygon

        # ---------- Debug Overlay ----------
        cv2.putText(
            frame_display,
            f"Area: {int(smoothed_area)} | State: {state}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )

        # cv2.imshow("Motion Mask (ROI)", motion_mask)
        cv2.imshow("Live Camera", frame_display)
        cv2.imshow("Motion Heatmap", heatmap_color)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    camera.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()