import cv2
import mediapipe as mp
import joblib
import numpy as np
import pyttsx3
from collections import deque
import time

MODEL_FILE = "sign_model.pkl"

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils


def extract_landmarks(hand_landmarks):
    data = []

    wrist = hand_landmarks.landmark[0]

    for landmark in hand_landmarks.landmark:
        data.extend([
            landmark.x - wrist.x,
            landmark.y - wrist.y,
            landmark.z - wrist.z
        ])

    return data


def speak_text(text):
    if not text.strip():
        return

    engine = pyttsx3.init()
    engine.setProperty("rate", 150)
    engine.say(text)
    engine.runAndWait()
    engine.stop()


def detect_z_motion(trail):
    if len(trail) < 12:
        return False

    start = trail[0]
    mid1 = trail[len(trail) // 3]
    mid2 = trail[(2 * len(trail)) // 3]
    end = trail[-1]

    dx1 = mid1[0] - start[0]
    dy1 = mid1[1] - start[1]

    dx2 = mid2[0] - mid1[0]
    dy2 = mid2[1] - mid1[1]

    dx3 = end[0] - mid2[0]
    dy3 = end[1] - mid2[1]

    first_right = dx1 > 20 and abs(dy1) < 25
    diagonal_down_left = dx2 < -15 and dy2 > 10
    final_right = dx3 > 20 and abs(dy3) < 25

    return first_right and diagonal_down_left and final_right


def detect_j_motion(trail):
    if len(trail) < 12:
        return False

    start = trail[0]
    mid = trail[len(trail) // 2]
    end = trail[-1]

    dx1 = mid[0] - start[0]
    dy1 = mid[1] - start[1]

    dx2 = end[0] - mid[0]
    dy2 = end[1] - mid[1]

    total_down = end[1] - start[1]

    # J should mostly move downward first, then curve sideways
    downward_first = dy1 > 15
    sideways_hook = abs(dx2) > 10
    still_downward = dy2 > 5
    enough_total_down = total_down > 25

    return downward_first and sideways_hook and still_downward and enough_total_down


def main():
    model = joblib.load(MODEL_FILE)

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    if not cap.isOpened():
        print("Could not open webcam.")
        return

    output_text = ""
    current_prediction = ""
    current_confidence = 0.0
    fingertip_trail = deque(maxlen=35)

    motion_prediction = ""
    motion_expire_time = 0
    motion_hold_seconds = 3.0

    with mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=2,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    ) as hands:

        while True:
            success, frame = cap.read()
            if not success:
                print("Failed to read from webcam.")
                break

            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb_frame)

            prediction_text = "No hand detected"
            confidence_text = "Confidence: 0.00%"

            detected_motion = ""

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(
                        frame,
                        hand_landmarks,
                        mp_hands.HAND_CONNECTIONS
                    )

                    landmarks = extract_landmarks(hand_landmarks)

                    if len(landmarks) == 63:
                        prediction = model.predict([landmarks])[0]
                        current_prediction = prediction

                        if hasattr(model, "predict_proba"):
                            probabilities = model.predict_proba([landmarks])[0]
                            current_confidence = float(np.max(probabilities)) * 100
                            confidence_text = f"Confidence: {current_confidence:.2f}%"
                        else:
                            current_confidence = 0.0

                    fingertip = hand_landmarks.landmark[8]
                    h, w, _ = frame.shape
                    fx = int(fingertip.x * w)
                    fy = int(fingertip.y * h)

                    fingertip_trail.append((fx, fy))

                    for i in range(1, len(fingertip_trail)):
                        cv2.line(
                            frame,
                            fingertip_trail[i - 1],
                            fingertip_trail[i],
                            (255, 0, 255),
                            2
                        )

                    if detect_z_motion(fingertip_trail):
                        detected_motion = "Z"
                    elif detect_j_motion(fingertip_trail):
                        detected_motion = "J"

            else:
                current_prediction = ""
                current_confidence = 0.0
                fingertip_trail.clear()

            now = time.time()

            if detected_motion:
                motion_prediction = detected_motion
                motion_expire_time = now + motion_hold_seconds

            if motion_prediction and now < motion_expire_time:
                prediction_text = f"Prediction: {motion_prediction}"
            else:
                motion_prediction = ""
                if current_prediction:
                    prediction_text = f"Prediction: {current_prediction}"

            cv2.putText(
                frame,
                prediction_text,
                (10, 35),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2
            )

            cv2.putText(
                frame,
                confidence_text,
                (10, 70),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 255, 0),
                2
            )

            cv2.putText(
                frame,
                f"Output: {output_text}",
                (10, 110),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 200, 255),
                2
            )

            cv2.putText(
                frame,
                "SPACE=add  S=speak  BACKSPACE=delete  C=clear  X=clear trail  Q=quit",
                (10, 145),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.52,
                (200, 200, 200),
                1
            )

            cv2.imshow("Sign Recognition", frame)

            key = cv2.waitKey(1) & 0xFF

            if key == 32:  # SPACE
                if motion_prediction:
                    output_text += motion_prediction
                elif current_prediction:
                    output_text += current_prediction

            elif key == ord("s"):
                speak_text(output_text)

            elif key == 8:  # BACKSPACE
                output_text = output_text[:-1]

            elif key == ord("c"):
                output_text = ""

            elif key == ord("x"):
                fingertip_trail.clear()
                motion_prediction = ""
                motion_expire_time = 0

            elif key == ord("q"):
                break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()