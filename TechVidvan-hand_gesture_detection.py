# TechVidvan hand Gesture Recognizer

# import necessary packages

import cv2
import numpy as np
import mediapipe as mp
import tensorflow as tf
from tensorflow.keras.models import load_model
import pyautogui

# initialize mediapipe
mpHands = mp.solutions.hands
hands = mpHands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mpDraw = mp.solutions.drawing_utils

# Load the gesture recognizer model
model = load_model('mp_hand_gesture')

# Load class names
f = open('gesture.names', 'r')
classNames = f.read().split('\n')
f.close()
print(classNames)


# Initialize the webcam
cap = cv2.VideoCapture(0)

# need to keep track of the previous mouse position to calculate the movement
prevmouseX, prevmouseY = None, None

while True:
    # Read each frame from the webcam
    _, frame = cap.read()

    x, y, c = frame.shape

    # get the position of the mouse
    mouseX, mouseY = pyautogui.position()


    # Flip the frame vertically
    frame = cv2.flip(frame, 1)
    framergb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Get hand landmark prediction
    result = hands.process(framergb)

    # print(result)
    
    className = ''

    # post process the result
    if result.multi_hand_landmarks:
        landmarks = []
        i = 0
        for handslms in result.multi_hand_landmarks:
            for lm in handslms.landmark:
                # print(id, lm)
                lmx = int(lm.x * x)
                lmy = int(lm.y * y)
                # index 8 should be the tip of the index finger, we will use this to control the mouse
                if i == 8:
                    index = [lmx, lmy]
                    i += 1

                landmarks.append([lmx, lmy])

            if prevmouseX is not None and prevmouseY is not None:
                # calculate the movement of the mouse
                dx = index[0] - prevmouseX
                dy = index[1] - prevmouseY

                # move the mouse
                pyautogui.moveRel(dx, dy)

            # set the mouse position of this frame as the previous mouse position for the next frame
            prevmouseX, prevmouseY = mouseX, mouseY
            

            # Drawing landmarks on frames
            mpDraw.draw_landmarks(frame, handslms, mpHands.HAND_CONNECTIONS)


            # Predict gesture
            prediction = model.predict([landmarks])
            # print(prediction)
            classID = np.argmax(prediction)
            className = classNames[classID]

    # show the prediction on the frame
    cv2.putText(frame, className, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 
                   1, (0,0,255), 2, cv2.LINE_AA)

    # Show the final output
    cv2.imshow("Output", frame) 

    if cv2.waitKey(1) == ord('q'):
        break

# release the webcam and destroy all active windows
cap.release()

cv2.destroyAllWindows()