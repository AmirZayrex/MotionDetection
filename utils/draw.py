import cv2

def draw_text(frame, text, pos=(20,40),
              font_family=cv2.FONT_HERSHEY_SIMPLEX,
              font_scale=0.7, color=(0, 255, 0), thickness=2):
    cv2.putText(
        frame,
        text,
        pos,
        font_family,
        font_scale,
        color,
        thickness
    )