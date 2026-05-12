import os
import csv
import cv2
import mediapipe as mp

SIGN_LABEL = "small"
CATEGORY = "selcon"
NUM_SAMPLES = 50
SEQUENCE_LENGTH = 40
OUTPUT_DIR = "1_SIGNBRIDGE_FINAL/ALL_DATA/phrase_data"

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
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    output_file = os.path.join(
        OUTPUT_DIR,
        f"{SIGN_LABEL}_{CATEGORY}.csv"
    )

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    sample_count = 0
    sequence_data = []
    collecting = False

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
                    break

                frame = cv2.flip(frame, 1)
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = hands.process(rgb_frame)

                status_text = "Press SPACE to start"

                if results.multi_hand_landmarks and len(results.multi_hand_landmarks) == 2:

                    # Sort hands to keep consistency
                    hands_sorted = sorted(
                        results.multi_hand_landmarks,
                        key=lambda h: h.landmark[0].x
                    )

                    left_hand = extract_landmarks(hands_sorted[0])
                    right_hand = extract_landmarks(hands_sorted[1])

                    combined = left_hand + right_hand

                    for hand_landmarks in results.multi_hand_landmarks:
                        mp_drawing.draw_landmarks(
                            frame,
                            hand_landmarks,
                            mp_hands.HAND_CONNECTIONS
                        )

                    if collecting:
                        sequence_data.extend(combined)

                        frames_collected = len(sequence_data) // 126
                        status_text = f"Recording {frames_collected}/{SEQUENCE_LENGTH}"

                        if frames_collected == SEQUENCE_LENGTH:
                            writer.writerow([SIGN_LABEL] + sequence_data)
                            sample_count += 1

                            print(f"Saved {sample_count}/{NUM_SAMPLES}")

                            sequence_data = []
                            collecting = False

                cv2.putText(frame, status_text, (10, 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

                cv2.imshow("2-Hand Motion Collection", frame)

                key = cv2.waitKey(1) & 0xFF

                if key == 32:
                    collecting = True
                    sequence_data = []

                elif key == ord("q"):
                    break

                if sample_count >= NUM_SAMPLES:
                    break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()