import cv2
import mediapipe as mp
import time
from collections import deque
from pathlib import Path
import os
import tkwindow
import pyautogui

# ---------------- Configuration ----------------
MODEL_PATH = Path(__file__).with_name("hand_landmarker.task")

WINDOW_SECONDS = 0.45
SWIPE_THRESHOLD = 0.22   # Normalized image distance
COOLDOWN_SECONDS = 0.8

COMMANDS = {}

# MediaPipe setup
BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
RunningMode = mp.tasks.vision.RunningMode

options = HandLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=str(MODEL_PATH)),
    running_mode=RunningMode.VIDEO,
    num_hands=1,
    min_hand_detection_confidence=0.5,
    min_tracking_confidence=0.5,
)

# Each entry stores (time, x, y)
positions = deque()
last_gesture_time = 0.0
gesture_text = "Show your hand"


pointers = {"prev": None, "curr": None}


def recognize_gesture(landmarks):
    """Recognize a gesture based on hand landmarks."""
    # Fist: All fingers are curled
    if all(
        landmarks[i].y > landmarks[i - 2].y
        for i in [8, 12, 16, 20]
    ):
        return "Fist"

    # Peace: Index and middle fingers are up, others are down
    if (landmarks[8].y < landmarks[6].y and
        landmarks[12].y < landmarks[10].y and
        landmarks[16].y > landmarks[14].y and
        landmarks[20].y > landmarks[18].y
    ):
        return "Peace"

    # Point: Index finger is up, others are down
    if (landmarks[8].y < landmarks[6].y and
        landmarks[12].y > landmarks[10].y and
        landmarks[16].y > landmarks[14].y and
        landmarks[20].y > landmarks[18].y
    ):
        return "Point"

    return None

def recognize_motion(history, now):
    """Recognize a swipe using hand movement over time."""
    if len(history) < 2:
        return None

    start_t, start_x, start_y = history[0]
    end_t, end_x, end_y = history[-1]

    if end_t - start_t < 0.20:
        return None

    dx = end_x - start_x
    dy = end_y - start_y

    # Pick the dominant direction of movement
    if abs(dx) >= abs(dy):
        if abs(dx) >= SWIPE_THRESHOLD:     
            return "Swipe Right" if dx > 0 else "Swipe Left"
    else:
        if abs(dy) >= SWIPE_THRESHOLD:
            # Image y coordinates increase downwards
            return "Swipe Down" if dy > 0 else "Swipe Up"

    return None

# moves the mouse if the pointer gesture is detected
def move_mouse(pointers):
    # just return if this is the first frame 
    try:
        if pointers["prev"] == None:
            return

        dx = pointers["curr"].x - pointers["prev"].x
        dy = pointers["curr"].y - pointers["prev"].y

        pyautogui.moveRel(dx*4000, dy*4000)
    except:
        pass


def main():
    global gesture_text, last_gesture_time

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Model not found: {MODEL_PATH}\n"
            "Download hand_landmarker.task and place it "
            "beside main.py."
        )

    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        raise RuntimeError("Could not open webcam.")

    start_time = time.monotonic()
    previous_timestamp_ms = -1

    windows = tkwindow.MainWindow()
    windows.run()

    with open("savedSettings.txt", "r") as f:
        for line in f:
            gesture, command = line.strip().split(":", 1)
            COMMANDS[gesture.strip()] = command.strip()

    try:
        with HandLandmarker.create_from_options(options) as detector:
            while True:
                success, frame = camera.read()

                if not success:
                    print("Could not read webcam frame.")
                    break

                # Mirror the image for a more natural webcam view
                frame = cv2.flip(frame, 1)
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # MediaPipe VIDEO mode requires increasing timestamps
                timestamp_ms = int(
                    (time.monotonic() - start_time) * 1000
                )
                timestamp_ms = max(
                    timestamp_ms, previous_timestamp_ms + 1
                )
                previous_timestamp_ms = timestamp_ms

                mp_image = mp.Image(
                    image_format=mp.ImageFormat.SRGB,
                    data=rgb
                )
                result = detector.detect_for_video(
                    mp_image, timestamp_ms
                )

                now = time.monotonic()

                if result.hand_landmarks:
                    landmarks = result.hand_landmarks[0]

                    # Landmark 0 is the wrist
                    wrist = landmarks[0]
                    x, y = wrist.x, wrist.y

                    pointers["curr"] = landmarks[8]

                    positions.append((now, x, y))

                    # Keep only recent positions
                    while (
                        positions
                        and now - positions[0][0] > WINDOW_SECONDS
                    ):
                        positions.popleft()

                    # Draw the hand's landmarks
                    height, width = frame.shape[:2]

                    for point in landmarks:
                        px = int(point.x * width)
                        py = int(point.y * height)
                        cv2.circle(
                            frame, (px, py), 4, (0, 255, 0), -1
                        )

                    detected = recognize_motion(positions, now)
                    gesture = recognize_gesture(landmarks)

                    if now - last_gesture_time >= COOLDOWN_SECONDS:


                        if detected and gesture != "Point":
                            gesture_text = detected
                            last_gesture_time = now
                            os.system(COMMANDS.get(gesture_text))
                            positions.clear()
                        

                        if gesture and gesture != "Point":
                            gesture_text = gesture   
                            last_gesture_time = now
                            os.system(COMMANDS.get(gesture_text))
                            positions.clear()

                    #last_gesture = gesture_text

                    if gesture == "Point":
                        move_mouse(pointers)
                        pointers["prev"] = pointers["curr"]
                        gesture_text = "Point"
                        last_gesture_time = now
                        positions.clear()
                    else:
                        pointers["prev"] = None 

                    

                else:
                    positions.clear()
                    gesture_text = "Show your hand"

                cv2.putText(
                    frame,
                    gesture_text,
                    (20, 45),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 255),
                    2
                )

                cv2.putText(
                    frame,
                    "Press Q to quit",
                    (20, frame.shape[0] - 20),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 255),
                    1
                )

                cv2.imshow("Motion Gesture Recognition", frame)

                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

    finally:
        camera.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()