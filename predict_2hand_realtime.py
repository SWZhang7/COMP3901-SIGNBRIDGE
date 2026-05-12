import cv2
import mediapipe as mp
import joblib
import numpy as np
import time
from collections import deque
import os

BASE_DIR = os.path.dirname(__file__)
MODEL_FILE = os.path.join(BASE_DIR, "MODELS", "phrase_model.pkl")

SEQUENCE_LENGTH = 40
CONFIDENCE_THRESHOLD = 70.0
COOLDOWN = 2.8

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


def extract_two_hand_landmarks(results):
    if not results.multi_hand_landmarks or len(results.multi_hand_landmarks) != 2:
        return None

    hands_sorted = sorted(
        results.multi_hand_landmarks,
        key=lambda h: h.landmark[0].x
    )

    left_hand = extract_landmarks(hands_sorted[0])
    right_hand = extract_landmarks(hands_sorted[1])

    return left_hand + right_hand


def sequence_has_enough_motion(sequence_buffer, threshold=0.18):
    if len(sequence_buffer) < 2:
        return False

    total_motion = 0.0

    for i in range(1, len(sequence_buffer)):
        prev_frame = sequence_buffer[i - 1]
        curr_frame = sequence_buffer[i]

        frame_motion = 0.0
        for j in range(len(prev_frame)):
            frame_motion += abs(curr_frame[j] - prev_frame[j])

        total_motion += frame_motion

    average_motion = total_motion / len(sequence_buffer)
    return average_motion > threshold


def main():
    model = joblib.load(MODEL_FILE)

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cap.isOpened():
        print("Could not open webcam.")
        return

    sequence_buffer = deque(maxlen=SEQUENCE_LENGTH)

    current_prediction = ""
    current_confidence = 0.0
    status_text = "Status: Waiting for 2 hands"

    last_prediction = ""
    last_commit_time = 0.0
    committed_text = ""

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

            num_hands = 0
            current_prediction = ""
            current_confidence = 0.0

            if results.multi_hand_landmarks:
                num_hands = len(results.multi_hand_landmarks)

                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(
                        frame,
                        hand_landmarks,
                        mp_hands.HAND_CONNECTIONS
                    )

                if num_hands == 2:
                    combined_landmarks = extract_two_hand_landmarks(results)

                    if combined_landmarks and len(combined_landmarks) == 126:
                        sequence_buffer.append(combined_landmarks)
                        status_text = f"Status: Tracking 2-hand motion ({len(sequence_buffer)}/{SEQUENCE_LENGTH})"
                else:
                    sequence_buffer.clear()
                    status_text = "Status: Need exactly 2 hands"

            else:
                sequence_buffer.clear()
                status_text = "Status: Waiting for 2 hands"

            if len(sequence_buffer) == SEQUENCE_LENGTH and sequence_has_enough_motion(sequence_buffer):
                flattened = []
                for frame_data in sequence_buffer:
                    flattened.extend(frame_data)

                prediction = model.predict([flattened])[0]
                current_prediction = prediction

                if hasattr(model, "predict_proba"):
                    probabilities = model.predict_proba([flattened])[0]
                    current_confidence = float(np.max(probabilities)) * 100

                can_commit = (
                    current_confidence >= CONFIDENCE_THRESHOLD and
                    (prediction != last_prediction or time.time() - last_commit_time >= COOLDOWN)
                )

                if can_commit:
                    committed_text = prediction
                    last_prediction = prediction
                    last_commit_time = time.time()
                    status_text = f"Status: Detected {prediction}"
                    sequence_buffer.clear()
                elif current_confidence >= CONFIDENCE_THRESHOLD:
                    status_text = "Status: Cooldown active"

            cv2.putText(
                frame,
                f"Prediction: {current_prediction if current_prediction else 'None'}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2
            )

            cv2.putText(
                frame,
                f"Confidence: {current_confidence:.2f}%",
                (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 0),
                2
            )

            cv2.putText(
                frame,
                f"Hands Detected: {num_hands}",
                (10, 90),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 100, 255),
                2
            )

            cv2.putText(
                frame,
                status_text,
                (10, 120),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 200, 255),
                2
            )

            cv2.putText(
                frame,
                f"Committed: {committed_text if committed_text else 'None'}",
                (10, 150),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 220, 255),
                2
            )

            cv2.putText(
                frame,
                "C=clear  Q=quit",
                (10, 180),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (200, 200, 200),
                1
            )

            cv2.imshow("2-Hand Motion Recognition", frame)

            key = cv2.waitKey(1) & 0xFF

            if key == ord("c"):
                sequence_buffer.clear()
                current_prediction = ""
                current_confidence = 0.0
                committed_text = ""
                status_text = "Status: Cleared"

            elif key == ord("q"):
                break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()