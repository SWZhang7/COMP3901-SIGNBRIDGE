import cv2
import mediapipe as mp
import joblib
import numpy as np
import pyttsx3
import time

MODEL_FILE = "word_model.pkl"

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils


def speak_text(text):
    if not text.strip():
        return

    engine = pyttsx3.init()
    engine.setProperty("rate", 150)
    engine.say(text)
    engine.runAndWait()
    engine.stop()


def extract_two_hand_landmarks(results):
    left_hand = [0.0] * 63
    right_hand = [0.0] * 63

    if results.multi_hand_landmarks and results.multi_handedness:
        for hand_landmarks, handedness in zip(
            results.multi_hand_landmarks,
            results.multi_handedness
        ):
            label = handedness.classification[0].label

            wrist = hand_landmarks.landmark[0]
            values = []

            for landmark in hand_landmarks.landmark:
                values.extend([
                    landmark.x - wrist.x,
                    landmark.y - wrist.y,
                    landmark.z - wrist.z
                ])

            if label == "Left":
                left_hand = values
            else:
                right_hand = values

    return left_hand + right_hand


def main():
    model = joblib.load(MODEL_FILE)

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    if not cap.isOpened():
        print("Could not open webcam.")
        return

    output_text = ""
    current_prediction = ""
    current_confidence = 0.0

    stable_prediction = ""
    stable_start_time = 0
    ready_word = ""

    stability_seconds =0.6
    confidence_threshold = 55.0

    last_committed_word = ""
    last_commit_time = 0
    repeat_cooldown_seconds = 1.0

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
            status_text = "Status: Waiting"

            hands_detected = False
            now = time.time()

            if results.multi_hand_landmarks:
                hands_detected = True

                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(
                        frame,
                        hand_landmarks,
                        mp_hands.HAND_CONNECTIONS
                    )

                landmarks = extract_two_hand_landmarks(results)

                if len(landmarks) == 126:
                    prediction = model.predict([landmarks])[0]
                    current_prediction = prediction
                    prediction_text = f"Prediction: {prediction}"

                    if hasattr(model, "predict_proba"):
                        probabilities = model.predict_proba([landmarks])[0]
                        current_confidence = float(np.max(probabilities)) * 100
                        confidence_text = f"Confidence: {current_confidence:.2f}%"
                    else:
                        current_confidence = 0.0

                    if current_confidence >= confidence_threshold:
                        if prediction == stable_prediction:
                            if stable_start_time == 0:
                                stable_start_time = now

                            if now - stable_start_time >= stability_seconds:
                                ready_word = prediction
                                status_text = f"Status: Ready to save {ready_word}"
                            else:
                                status_text = f"Status: Stabilizing {prediction}"
                        else:
                            stable_prediction = prediction
                            stable_start_time = now
                            ready_word = ""
                            status_text = f"Status: New prediction {prediction}"
                    else:
                        stable_prediction = ""
                        stable_start_time = 0
                        ready_word = ""
                        status_text = "Status: Confidence too low"

            else:
                current_prediction = ""
                current_confidence = 0.0
                prediction_text = "No hand detected"
                confidence_text = "Confidence: 0.00%"

                if ready_word:
                    can_commit = (
                        ready_word != last_committed_word
                        or now - last_commit_time >= repeat_cooldown_seconds
                    )

                    if can_commit:
                        if output_text:
                            output_text += " " + ready_word
                        else:
                            output_text = ready_word

                        speak_text(ready_word)

                        last_committed_word = ready_word
                        last_commit_time = now
                        status_text = f"Status: Saved {ready_word}"
                    else:
                        status_text = f"Status: Ignored repeat {ready_word}"

                stable_prediction = ""
                stable_start_time = 0
                ready_word = ""

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
                status_text,
                (10, 105),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 200, 0),
                2
            )

            cv2.putText(
                frame,
                f"Output: {output_text}",
                (10, 140),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 200, 255),
                2
            )

            cv2.putText(
                frame,
                "C=clear  Q=quit",
                (10, 175),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (200, 200, 200),
                1
            )

            cv2.imshow("Word Recognition", frame)

            key = cv2.waitKey(1) & 0xFF

            if key == ord("c"):
                output_text = ""
                last_committed_word = ""
                last_commit_time = 0

            elif key == ord("q"):
                break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()