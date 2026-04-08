import os
import csv
import cv2
import mediapipe as mp

SIGN_LABEL = "X with wrist"
NUM_SAMPLES = 100
OUTPUT_DIR = "data"

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils


def extract_two_hand_landmarks(results):
    left_hand = [0.0] * 63
    right_hand = [0.0] * 63

    if results.multi_hand_landmarks and results.multi_handedness:
        for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
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
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_file = os.path.join(OUTPUT_DIR, f"{SIGN_LABEL}.csv")

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    if not cap.isOpened():
        print("Could not open webcam.")
        return

    sample_count = 0

    with open(output_file, mode="a", newline="") as f:
        writer = csv.writer(f)

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

                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        mp_drawing.draw_landmarks(
                            frame,
                            hand_landmarks,
                            mp_hands.HAND_CONNECTIONS
                        )

                        landmarks = extract_landmarks(hand_landmarks)

                        if len(landmarks) == 126 and sample_count < NUM_SAMPLES:
                            row = [SIGN_LABEL] + landmarks
                            writer.writerow(row)
                            sample_count += 1
                            print(f"Saved sample {sample_count}/{NUM_SAMPLES}")

                cv2.putText(
                    frame,
                    f"Letter: {SIGN_LABEL} | Samples: {sample_count}/{NUM_SAMPLES}",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 0),
                    2
                )

                cv2.imshow("Collect Data", frame)

                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

                if sample_count >= NUM_SAMPLES:
                    print(f"Finished collecting {SIGN_LABEL}.")
                    break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()