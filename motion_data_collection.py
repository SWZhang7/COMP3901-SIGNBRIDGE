import os
import csv
import cv2
import mediapipe as mp

SIGN_LABEL = "water"          
CATEGORY = "lefthandselcon"
NUM_SAMPLES = 100
SEQUENCE_LENGTH = 40
OUTPUT_DIR = "1_SIGNBRIDGE_FINAL/ALL_DATA/word_data"

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

    if not cap.isOpened():
        print("Could not open webcam.")
        return

    sample_count = 0
    sequence_data = []
    collecting = False

    with open(output_file, mode="a", newline="") as f:
        writer = csv.writer(f)

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

                status_text = "Press SPACE to start recording"
                progress_text = f"Samples: {sample_count}/{NUM_SAMPLES}"

                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        mp_drawing.draw_landmarks(
                            frame,
                            hand_landmarks,
                            mp_hands.HAND_CONNECTIONS
                        )

                        if collecting:
                            landmarks = extract_landmarks(hand_landmarks)

                            if len(landmarks) == 63:
                                sequence_data.extend(landmarks)

                                status_text = (
                                    f"Recording {SIGN_LABEL}: "
                                    f"{len(sequence_data) // 63}/{SEQUENCE_LENGTH} frames"
                                )

                                if len(sequence_data) == SEQUENCE_LENGTH * 63:
                                    row = [SIGN_LABEL] + sequence_data
                                    writer.writerow(row)
                                    sample_count += 1
                                    print(f"Saved sequence {sample_count}/{NUM_SAMPLES}")

                                    sequence_data = []
                                    collecting = False
                                    status_text = f"Saved {SIGN_LABEL} sequence"

                cv2.putText(
                    frame,
                    f"Motion Label: {SIGN_LABEL}",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 0),
                    2
                )

                cv2.putText(
                    frame,
                    status_text,
                    (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 0),
                    2
                )

                cv2.putText(
                    frame,
                    progress_text,
                    (10, 90),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 100, 255),
                    2
                )

                cv2.putText(
                    frame,
                    "SPACE=start  R=reset current  Q=quit",
                    (10, 120),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.55,
                    (200, 200, 200),
                    1
                )

                cv2.imshow("Motion Data Collection", frame)

                key = cv2.waitKey(1) & 0xFF

                if key == 32:  # SPACE
                    if not collecting:
                        sequence_data = []
                        collecting = True
                        print(f"Started recording {SIGN_LABEL} sequence")

                elif key == ord("r"):
                    sequence_data = []
                    collecting = False
                    print("Current sequence reset")

                elif key == ord("q"):
                    break

                if sample_count >= NUM_SAMPLES:
                    print(f"Finished collecting {SIGN_LABEL}.")
                    break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()