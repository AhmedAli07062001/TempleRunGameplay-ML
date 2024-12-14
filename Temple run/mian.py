import mediapipe as mp
import cv2
import pydirectinput

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)
cap.set(3, 720)
cap.set(4, 540)
pose = ""
status = 0
previous_pose = None

with mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands:
    while True:
        success, frame = cap.read()
        frame = cv2.flip(frame, 1)
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        results = hands.process(img)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        height, width, _ = img.shape

        try:
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    # Draw hand landmarks and connections
                    mp_drawing.draw_landmarks(
                        frame,
                        hand_landmarks,
                        mp_hands.HAND_CONNECTIONS,
                        mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=4),
                        mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=2)
                    )

                    # Get index finger position
                    index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                    x = int(index_finger_tip.x * width)
                    y = int(index_finger_tip.y * height)

                    line_x1 = width // 3
                    line_x2 = 2 * (width // 3)
                    line_y1 = height // 3
                    line_y2 = 1.5 * (height // 3)

                    # pose detection of finger
                    if x > line_x2 and y < line_y1:
                        pose = "Start"
                    elif x > line_x2 and line_y1 < y < line_y2 and status == 1:
                        pose = "Right"
                    elif x < line_x1 and line_y1 < y < line_y2 and status == 1:
                        pose = "Left"
                    elif y < line_y1 and status == 1:
                        pose = "Jump"
                    elif y > line_y2 and status == 1:
                        pose = "Slide"
                    elif status == 0:
                        pose = "Please start the game"
                    else:
                        pose = "Run"

                    # Execute action only if pose changes
                    if pose != previous_pose:
                        if pose == "Start":
                            pydirectinput.keyDown('space')
                            pydirectinput.keyUp('space')
                            status = 1
                            print("Pose: Start | Status set to 1")
                        elif pose == "Right":
                            pydirectinput.keyDown('right')
                            pydirectinput.keyUp('right')
                            print("Right")
                        elif pose == "Left":
                            pydirectinput.keyDown('left')
                            pydirectinput.keyUp('left')
                            print("Left")
                        elif pose == "Jump":
                            pydirectinput.keyDown('up')
                            pydirectinput.keyUp('up')
                            print("Jump")
                        elif pose == "Slide":
                            pydirectinput.keyDown('down')
                            pydirectinput.keyUp('down')
                            print("Slide")

                        previous_pose = pose

                    # Draw index finger  position on frame
                    cv2.circle(frame, (x, y), 10, (255, 0, 0), -1)

            else:
                print("No hands detected")
        except Exception as e:
            print(f"Error: {e}")

        cv2.putText(frame, pose, (10, 30), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 0), 2)
        # cv2.line(frame, (width // 3, 0), (width // 3, height), (255, 255, 255), 1)
        # cv2.line(frame, (2 * (width // 3), 0), (2 * (width // 3), height), (255, 255, 255), 1)
        # cv2.line(frame, (0, height // 3), (width, height // 3), (255, 255, 255), 1)
        # cv2.line(frame, (0, 2 * (height // 3)), (width, 2 * (height // 3)), (255, 255, 255), 1)

        cv2.imshow('image', frame)
        if cv2.waitKey(1) & 0xff == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
