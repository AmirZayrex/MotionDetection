import cv2
from config import CAMERA_INDEX, CAMERA_WIDTH, CAMERA_HEIGHT

def open_camera():
    cap = cv2.VideoCapture(CAMERA_INDEX)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
    return cap


def read_frame(cap):
    ret, frm = cap.read()
    if not ret:
        return None
    return frm

def release_camera(cap):
    cap.release()
    cv2.destroyAllWindows()
