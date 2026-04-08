import cv2
import mediapipe as mp
import joblib
import numpy as np
import pyttsx3
import math
import time
from collections import deque
import os

BASE_DIR = os.path.dirname(__file__)
STATIC_MODEL_FILE = os.path.join(BASE_DIR, "MODELS", "static_model.pkl")
WORD_MODEL_FILE = os.path.join(BASE_DIR, "MODELS", "word_model.pkl")
PHRASE_MODEL_FILE = os.path.join(BASE_DIR, "MODELS", "phrase_model.pkl")

SEQUENCE_LENGTH = 40
TWO_HAND_SEQUENCE_LENGTH = 40

WORD_CONF_THRESHOLD = 50.0
PHRASE_CONF_THRESHOLD = 50.0

mp_hands = mp.solutions.hands
mp_face_mesh = mp.solutions.face_mesh
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles


def distance(p1, p2):
    return math.sqrt(
        (p1.x - p2.x) ** 2 +
        (p1.y - p2.y) ** 2 +
        (p1.z - p2.z) ** 2
    )


def distance_2d(p1, p2):
    return math.sqrt(
        (p1.x - p2.x) ** 2 +
        (p1.y - p2.y) ** 2
    )


def normalize(value, reference):
    if reference == 0:
        return 0.0
    return value / reference


def midpoint(p1, p2):
    class Point:
        pass
    pt = Point()
    pt.x = (p1.x + p2.x) / 2
    pt.y = (p1.y + p2.y) / 2
    pt.z = (p1.z + p2.z) / 2
    return pt


def midpoint_2d(p1, p2):
    class Point:
        pass
    pt = Point()
    pt.x = (p1.x + p2.x) / 2
    pt.y = (p1.y + p2.y) / 2
    return pt


def speak_text(text):
    if not text.strip():
        return

    engine = pyttsx3.init()
    engine.setProperty("rate", 150)
    engine.say(text)
    engine.runAndWait()
    engine.stop()


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


def commit_output(conversation, text, now):
    conversation.appendleft(text)
    speak_text(text)
    return text, now


def sequence_has_enough_motion(sequence_buffer, threshold=0.12):
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


def sequence_has_enough_motion_2hand(sequence_buffer, threshold=0.18):
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
    static_model = joblib.load(STATIC_MODEL_FILE)
    word_model = joblib.load(WORD_MODEL_FILE)
    phrase_model = joblib.load(PHRASE_MODEL_FILE)

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    if not cap.isOpened():
        print("Could not open webcam.")
        return

    # Face baselines
    baseline_left_eye_open = None
    baseline_right_eye_open = None
    baseline_mouth_open = None
    baseline_left_face_width = None
    baseline_right_face_width = None
    baseline_eye_slope = None
    baseline_left_brow = None
    baseline_right_brow = None
    baseline_inner_brow_dist = None

    # Shoulder baselines
    baseline_left_shoulder_y = None
    baseline_right_shoulder_y = None
    baseline_shoulder_slope = None
    baseline_shoulder_hip_dist = None

    # Static output logic
    current_output = ""
    stable_output = ""
    stable_start_time = 0
    hold_seconds = 2.0
    last_committed_output = ""
    last_commit_time = 0
    repeat_cooldown_seconds = 1.5
    conversation = deque(maxlen=12)

    # 1-hand word motion logic
    word_buffer = deque(maxlen=SEQUENCE_LENGTH)
    word_last_commit = 0
    word_cooldown = 2.8

    # 2-hand phrase motion logic
    phrase_buffer = deque(maxlen=TWO_HAND_SEQUENCE_LENGTH)
    phrase_last_commit = 0
    phrase_cooldown = 2.8

    with mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=2,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    ) as hands, mp_face_mesh.FaceMesh(
        static_image_mode=False,
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    ) as face_mesh, mp_pose.Pose(
        static_image_mode=False,
        model_complexity=1,
        enable_segmentation=False,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    ) as pose:

        while True:
            success, frame = cap.read()
            if not success:
                print("Failed to read from webcam.")
                break

            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            hand_results = hands.process(rgb_frame)
            face_results = face_mesh.process(rgb_frame)
            pose_results = pose.process(rgb_frame)

            now = time.time()

            output_text = "Output: None"
            confidence_text = "Confidence: 0.00%"
            hold_text = f"Hold: 0.0 / {hold_seconds:.1f}"
            status_text = "Status: Waiting"

            mouth_state = "Mouth: N/A"
            left_eye_state = "Left Eye: N/A"
            right_eye_state = "Right Eye: N/A"
            head_turn_state = "Head Turn: N/A"
            head_tilt_state = "Head Tilt: N/A"
            brow_state = "Brows: N/A"

            shoulder_height_state = "Shoulder Height: N/A"
            shoulder_tilt_state = "Shoulder Tilt: N/A"
            shoulder_posture_state = "Shoulder Posture: N/A"

            current_prediction = ""
            current_confidence = 0.0
            word_output = ""
            word_conf = 0.0
            phrase_output = ""
            phrase_conf = 0.0
            num_hands_detected = 0

            # ---------------- HANDS ----------------
            if hand_results.multi_hand_landmarks:
                num_hands_detected = len(hand_results.multi_hand_landmarks)

                for hand_landmarks in hand_results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(
                        frame,
                        hand_landmarks,
                        mp_hands.HAND_CONNECTIONS
                    )

                if num_hands_detected == 1:
                    hand_landmarks = hand_results.multi_hand_landmarks[0]
                    landmarks = extract_landmarks(hand_landmarks)

                    if len(landmarks) == 63:
                        prediction = static_model.predict([landmarks])[0]
                        current_prediction = prediction

                        if hasattr(static_model, "predict_proba"):
                            probabilities = static_model.predict_proba([landmarks])[0]
                            current_confidence = float(np.max(probabilities)) * 100

                        word_buffer.append(landmarks)

                    phrase_buffer.clear()

                elif num_hands_detected == 2:
                    combined_landmarks = extract_two_hand_landmarks(hand_results)

                    if combined_landmarks and len(combined_landmarks) == 126:
                        phrase_buffer.append(combined_landmarks)

                    word_buffer.clear()

            else:
                current_prediction = ""
                current_confidence = 0.0
                word_buffer.clear()
                phrase_buffer.clear()

            # ---------------- 1-HAND WORD MOTION ----------------
            if len(word_buffer) == SEQUENCE_LENGTH and sequence_has_enough_motion(word_buffer):
                flattened = []
                for frame_data in word_buffer:
                    flattened.extend(frame_data)

                word_output = word_model.predict([flattened])[0]

                if hasattr(word_model, "predict_proba"):
                    probs = word_model.predict_proba([flattened])[0]
                    word_conf = float(np.max(probs)) * 100
                else:
                    word_conf = 0.0
            else:
                word_output = ""
                word_conf = 0.0

            # ---------------- 2-HAND PHRASE MOTION ----------------
            if len(phrase_buffer) == TWO_HAND_SEQUENCE_LENGTH and sequence_has_enough_motion_2hand(phrase_buffer):
                flattened_two_hand = []
                for frame_data in phrase_buffer:
                    flattened_two_hand.extend(frame_data)

                phrase_output = phrase_model.predict([flattened_two_hand])[0]

                if hasattr(phrase_model, "predict_proba"):
                    probs = phrase_model.predict_proba([flattened_two_hand])[0]
                    phrase_conf = float(np.max(probs)) * 100
                else:
                    phrase_conf = 0.0
            else:
                phrase_output = ""
                phrase_conf = 0.0

            # Default output = static
            current_output = current_prediction

            # Priority: 2-hand phrase > 1-hand word > static
            if phrase_output and phrase_conf > PHRASE_CONF_THRESHOLD:
                current_output = phrase_output
            elif word_output and word_conf > WORD_CONF_THRESHOLD:
                current_output = word_output

            if current_output:
                output_text = f"Output: {current_output}"
            if current_confidence:
                confidence_text = f"Confidence: {current_confidence:.2f}%"

            # ---------------- FACE ----------------
            current_left_eye_open = None
            current_right_eye_open = None
            current_mouth_open = None
            current_left_face_width = None
            current_right_face_width = None
            current_eye_slope = None
            current_left_brow = None
            current_right_brow = None
            current_inner_brow_dist = None

            if face_results.multi_face_landmarks:
                for face_landmarks in face_results.multi_face_landmarks:
                    mp_drawing.draw_landmarks(
                        image=frame,
                        landmark_list=face_landmarks,
                        connections=mp_face_mesh.FACEMESH_CONTOURS,
                        landmark_drawing_spec=None,
                        connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_contours_style()
                    )

                    lm = face_landmarks.landmark

                    left_eye_corner = lm[33]
                    right_eye_corner = lm[263]
                    face_width = distance(left_eye_corner, right_eye_corner)

                    upper_lip = lm[13]
                    lower_lip = lm[14]
                    current_mouth_open = normalize(distance(upper_lip, lower_lip), face_width)

                    left_eye_top = lm[159]
                    left_eye_bottom = lm[145]
                    current_left_eye_open = normalize(distance(left_eye_top, left_eye_bottom), face_width)

                    right_eye_top = lm[386]
                    right_eye_bottom = lm[374]
                    current_right_eye_open = normalize(distance(right_eye_top, right_eye_bottom), face_width)

                    nose_tip = lm[1]
                    left_face_edge = lm[234]
                    right_face_edge = lm[454]
                    current_left_face_width = normalize(distance(nose_tip, left_face_edge), face_width)
                    current_right_face_width = normalize(distance(nose_tip, right_face_edge), face_width)

                    left_eye_center = midpoint(lm[33], lm[133])
                    right_eye_center = midpoint(lm[263], lm[362])
                    current_eye_slope = right_eye_center.y - left_eye_center.y

                    left_brow_point = lm[105]
                    right_brow_point = lm[334]
                    current_left_brow = normalize(distance(left_brow_point, left_eye_top), face_width)
                    current_right_brow = normalize(distance(right_brow_point, right_eye_top), face_width)

                    inner_left = lm[107]
                    inner_right = lm[336]
                    current_inner_brow_dist = normalize(distance(inner_left, inner_right), face_width)

                    if baseline_mouth_open is not None:
                        mouth_delta = current_mouth_open - baseline_mouth_open
                        if mouth_delta > 0.015:
                            mouth_state = "Mouth: OPEN"
                        else:
                            mouth_state = "Mouth: CLOSED"

                        left_eye_delta = current_left_eye_open - baseline_left_eye_open
                        right_eye_delta = current_right_eye_open - baseline_right_eye_open

                        if left_eye_delta < -0.012:
                            left_eye_state = "Left Eye: CLOSED"
                        else:
                            left_eye_state = "Left Eye: OPEN"

                        if right_eye_delta < -0.012:
                            right_eye_state = "Right Eye: CLOSED"
                        else:
                            right_eye_state = "Right Eye: OPEN"

                        turn_balance = (
                            (current_right_face_width - baseline_right_face_width)
                            - (current_left_face_width - baseline_left_face_width)
                        )

                        if turn_balance > 0.03:
                            head_turn_state = "Head Turn: LEFT"
                        elif turn_balance < -0.03:
                            head_turn_state = "Head Turn: RIGHT"
                        else:
                            head_turn_state = "Head Turn: CENTER"

                        tilt_delta = current_eye_slope - baseline_eye_slope

                        if tilt_delta > 0.015:
                            head_tilt_state = "Head Tilt: RIGHT"
                        elif tilt_delta < -0.015:
                            head_tilt_state = "Head Tilt: LEFT"
                        else:
                            head_tilt_state = "Head Tilt: CENTER"

                        left_brow_delta = current_left_brow - baseline_left_brow
                        right_brow_delta = current_right_brow - baseline_right_brow
                        avg_brow_delta = (left_brow_delta + right_brow_delta) / 2
                        inward_delta = baseline_inner_brow_dist - current_inner_brow_dist

                        if avg_brow_delta > 0.010:
                            brow_state = "Brows: RAISED"
                        elif avg_brow_delta < -0.006 and inward_delta > 0.008:
                            brow_state = "Brows: FURROWED"
                        elif avg_brow_delta < -0.006:
                            brow_state = "Brows: LOWERED"
                        else:
                            brow_state = "Brows: NEUTRAL"

            # ---------------- SHOULDERS ----------------
            current_left_shoulder_y = None
            current_right_shoulder_y = None
            current_shoulder_slope = None
            current_shoulder_hip_dist = None

            if pose_results.pose_landmarks:
                mp_drawing.draw_landmarks(
                    frame,
                    pose_results.pose_landmarks,
                    mp_pose.POSE_CONNECTIONS
                )

                lm = pose_results.pose_landmarks.landmark

                left_shoulder = lm[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
                right_shoulder = lm[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
                left_hip = lm[mp_pose.PoseLandmark.LEFT_HIP.value]
                right_hip = lm[mp_pose.PoseLandmark.RIGHT_HIP.value]

                current_left_shoulder_y = left_shoulder.y
                current_right_shoulder_y = right_shoulder.y
                current_shoulder_slope = right_shoulder.y - left_shoulder.y

                shoulder_mid = midpoint_2d(left_shoulder, right_shoulder)
                hip_mid = midpoint_2d(left_hip, right_hip)
                current_shoulder_hip_dist = distance_2d(shoulder_mid, hip_mid)

                if baseline_left_shoulder_y is not None:
                    avg_current_y = (current_left_shoulder_y + current_right_shoulder_y) / 2
                    avg_baseline_y = (baseline_left_shoulder_y + baseline_right_shoulder_y) / 2
                    shoulder_height_delta = avg_baseline_y - avg_current_y

                    if shoulder_height_delta > 0.015:
                        shoulder_height_state = "Shoulder Height: RAISED"
                    elif shoulder_height_delta < -0.015:
                        shoulder_height_state = "Shoulder Height: DROPPED"
                    else:
                        shoulder_height_state = "Shoulder Height: NEUTRAL"

                    slope_delta = current_shoulder_slope - baseline_shoulder_slope

                    if slope_delta > 0.02:
                        shoulder_tilt_state = "Shoulder Tilt: RIGHT HIGHER"
                    elif slope_delta < -0.02:
                        shoulder_tilt_state = "Shoulder Tilt: LEFT HIGHER"
                    else:
                        shoulder_tilt_state = "Shoulder Tilt: LEVEL"

                    posture_delta = current_shoulder_hip_dist - baseline_shoulder_hip_dist

                    if posture_delta < -0.02:
                        shoulder_posture_state = "Shoulder Posture: SHOULDERS BACK"
                    elif posture_delta > 0.02:
                        shoulder_posture_state = "Shoulder Posture: HUNCHED"
                    else:
                        shoulder_posture_state = "Shoulder Posture: NEUTRAL"

            # ---------------- AUTO COMMIT ----------------
            if phrase_output and phrase_conf > PHRASE_CONF_THRESHOLD:
                can_commit_phrase = now - phrase_last_commit >= phrase_cooldown

                if can_commit_phrase:
                    last_committed_output, last_commit_time = commit_output(
                        conversation,
                        phrase_output,
                        now
                    )
                    status_text = f"Status: Phrase {phrase_output}"
                    phrase_last_commit = now
                    phrase_buffer.clear()
                    stable_output = ""
                    stable_start_time = 0
                else:
                    status_text = "Status: Phrase cooldown"

            elif word_output and word_conf > WORD_CONF_THRESHOLD:
                can_commit_word = now - word_last_commit >= word_cooldown

                if can_commit_word:
                    last_committed_output, last_commit_time = commit_output(
                        conversation,
                        word_output,
                        now
                    )
                    status_text = f"Status: Word {word_output}"
                    word_last_commit = now
                    word_buffer.clear()
                    stable_output = ""
                    stable_start_time = 0
                else:
                    status_text = "Status: Word cooldown"

            elif current_output:
                if current_output == stable_output:
                    held_time = now - stable_start_time if stable_start_time else 0
                else:
                    stable_output = current_output
                    stable_start_time = now
                    held_time = 0

                hold_text = f"Hold: {held_time:.1f} / {hold_seconds:.1f}"

                if held_time >= hold_seconds:
                    can_commit_static = (
                        current_output != last_committed_output
                        or now - last_commit_time >= repeat_cooldown_seconds
                    )

                    if can_commit_static:
                        last_committed_output, last_commit_time = commit_output(
                            conversation,
                            current_output,
                            now
                        )
                        status_text = f"Status: Added {current_output}"
                        stable_output = ""
                        stable_start_time = 0
                        word_buffer.clear()
                        phrase_buffer.clear()
                    else:
                        status_text = "Status: Waiting for repeat cooldown"
                else:
                    status_text = "Status: Holding..."
            else:
                stable_output = ""
                stable_start_time = 0
                hold_text = f"Hold: 0.0 / {hold_seconds:.1f}"
                status_text = "Status: Waiting"

            # ---------------- PANELS ----------------
            status_width = 320
            conversation_width = 300
            h, w, _ = frame.shape

            status_panel = np.zeros((h, status_width, 3), dtype=np.uint8)
            conversation_panel = np.zeros((h, conversation_width, 3), dtype=np.uint8)

            line_y = 35
            line_gap = 28

            cv2.putText(status_panel, output_text, (15, line_y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            line_y += line_gap

            cv2.putText(status_panel, confidence_text, (15, line_y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.58, (255, 255, 0), 2)
            line_y += line_gap

            cv2.putText(status_panel, f"Hands: {num_hands_detected}", (15, line_y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.56, (200, 255, 255), 1)
            line_y += line_gap

            cv2.putText(status_panel, f"Word: {word_output}", (15, line_y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.54, (255, 170, 0), 1)
            line_y += line_gap

            cv2.putText(status_panel, f"Word Conf: {word_conf:.1f}%", (15, line_y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.54, (255, 170, 0), 1)
            line_y += line_gap

            cv2.putText(status_panel, f"Phrase: {phrase_output}", (15, line_y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.54, (255, 180, 255), 1)
            line_y += line_gap

            cv2.putText(status_panel, f"Phrase Conf: {phrase_conf:.1f}%", (15, line_y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.54, (255, 180, 255), 1)
            line_y += line_gap

            cv2.putText(status_panel, hold_text, (15, line_y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.58, (255, 200, 0), 2)
            line_y += line_gap

            cv2.putText(status_panel, status_text, (15, line_y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.56, (0, 200, 255), 2)
            line_y += line_gap + 8

            cv2.putText(status_panel, mouth_state, (15, line_y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.54, (0, 255, 0), 1)
            line_y += line_gap

            cv2.putText(status_panel, brow_state, (15, line_y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.54, (255, 180, 0), 1)
            line_y += line_gap

            cv2.putText(status_panel, left_eye_state, (15, line_y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.54, (255, 255, 0), 1)
            line_y += line_gap

            cv2.putText(status_panel, right_eye_state, (15, line_y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.54, (255, 100, 255), 1)
            line_y += line_gap

            cv2.putText(status_panel, head_turn_state, (15, line_y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.54, (0, 200, 255), 1)
            line_y += line_gap

            cv2.putText(status_panel, head_tilt_state, (15, line_y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.54, (0, 180, 255), 1)
            line_y += line_gap

            cv2.putText(status_panel, shoulder_height_state, (15, line_y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.54, (0, 255, 150), 1)
            line_y += line_gap

            cv2.putText(status_panel, shoulder_tilt_state, (15, line_y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.54, (200, 255, 150), 1)
            line_y += line_gap

            cv2.putText(status_panel, shoulder_posture_state, (15, line_y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.54, (255, 150, 200), 1)

            cv2.putText(status_panel, "B=baseline  C=clear  Q=quit", (15, h - 15),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.48, (200, 200, 200), 1)

            cv2.putText(conversation_panel, "Conversation", (15, 35),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.72, (255, 255, 255), 2)

            conv_line_y = 75
            conv_gap = 28

            for item in conversation:
                cv2.putText(conversation_panel, item, (15, conv_line_y),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.68, (0, 220, 255), 2)
                conv_line_y += conv_gap

            combined = np.hstack((frame, status_panel, conversation_panel))
            cv2.imshow("Combined Monitor", combined)

            key = cv2.waitKey(1) & 0xFF

            if key == ord("b"):
                if (
                    current_left_eye_open is not None
                    and current_right_eye_open is not None
                    and current_mouth_open is not None
                    and current_left_face_width is not None
                    and current_right_face_width is not None
                    and current_eye_slope is not None
                    and current_left_brow is not None
                    and current_right_brow is not None
                    and current_inner_brow_dist is not None
                ):
                    baseline_left_eye_open = current_left_eye_open
                    baseline_right_eye_open = current_right_eye_open
                    baseline_mouth_open = current_mouth_open
                    baseline_left_face_width = current_left_face_width
                    baseline_right_face_width = current_right_face_width
                    baseline_eye_slope = current_eye_slope
                    baseline_left_brow = current_left_brow
                    baseline_right_brow = current_right_brow
                    baseline_inner_brow_dist = current_inner_brow_dist
                    print("Face baseline set.")

                if (
                    current_left_shoulder_y is not None
                    and current_right_shoulder_y is not None
                    and current_shoulder_slope is not None
                    and current_shoulder_hip_dist is not None
                ):
                    baseline_left_shoulder_y = current_left_shoulder_y
                    baseline_right_shoulder_y = current_right_shoulder_y
                    baseline_shoulder_slope = current_shoulder_slope
                    baseline_shoulder_hip_dist = current_shoulder_hip_dist
                    print("Shoulder baseline set.")

            elif key == ord("c"):
                conversation.clear()
                last_committed_output = ""
                last_commit_time = 0

            elif key == ord("q"):
                break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()