import cv2
import numpy as np

cap = cv2.VideoCapture(0)
while True:
    # Read each frame from the webcam
    _, frame = cap.read()
    x , y, c = frame.shape
    # Flip the frame vertically
    frame = cv2.flip(frame, 1)
    # Show the final output
    cv2.imshow("Output", frame)
    if cv2.waitKey(1) == ord('q'):
        break

