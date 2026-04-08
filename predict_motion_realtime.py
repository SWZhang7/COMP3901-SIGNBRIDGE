import cv2
import mediapipe as mp
import joblib
import numpy as np
from collections import deque

MODEL_FILE = "motion_model.pkl"
SEQUENCE_LENGTH = 40

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


def main():
    model = joblib.load(MODEL_FILE)

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    if not cap.isOpened():
        print("Could not open webcam.")
        return

    sequence_buffer = deque(maxlen=SEQUENCE_LENGTH)
    current_prediction = "No sequence yet"
    current_confidence = 0.0

    with mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
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

            status_text = f"Frames: {len(sequence_buffer)}/{SEQUENCE_LENGTH}"

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(
                        frame,
                        hand_landmarks,
                        mp_hands.HAND_CONNECTIONS
                    )

                    landmarks = extract_landmarks(hand_landmarks)

                    if len(landmarks) == 63:
                        sequence_buffer.append(landmarks)

            if len(sequence_buffer) == SEQUENCE_LENGTH:
                flattened_sequence = []
                for frame_data in sequence_buffer:
                    flattened_sequence.extend(frame_data)

                prediction = model.predict([flattened_sequence])[0]
                current_prediction = prediction

                if hasattr(model, "predict_proba"):
                    probabilities = model.predict_proba([flattened_sequence])[0]
                    current_confidence = float(np.max(probabilities)) * 100
                else:
                    current_confidence = 0.0

            cv2.putText(
                frame,
                f"Prediction: {current_prediction}",
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
                status_text,
                (10, 90),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 100, 255),
                2
            )

            cv2.putText(
                frame,
                "C=clear sequence  Q=quit",
                (10, 120),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (200, 200, 200),
                1
            )

            cv2.imshow("Motion Recognition", frame)

            key = cv2.waitKey(1) & 0xFF

            if key == ord("c"):
                sequence_buffer.clear()
                current_prediction = "No sequence yet"
                current_confidence = 0.0

            elif key == ord("q"):
                break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()