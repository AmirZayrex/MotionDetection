import cv2
import numpy as np
from config import MOTION_THRESHOLD

def compute_motion_mask(gray_frame, background_gray):
    diff = cv2.absdiff(gray_frame, background_gray)
    motion_mask = diff > MOTION_THRESHOLD
    motion_mask_uint8 = (motion_mask.astype(np.uint8) * 255)
    return motion_mask_uint8

def compute_motion_area(motion_mask_uint8):
    return int(np.sum(motion_mask_uint8 > 0))
