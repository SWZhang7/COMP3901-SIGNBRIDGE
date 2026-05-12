import cv2
import mediapipe as mp
import joblib
import numpy as np
import time
from collections import deque
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(BASE_DIR, "MODELS")

STATIC_MODEL_FILE = os.path.join(MODEL_DIR, "static_model.pkl")
WORD_MODEL_FILE = os.path.join(MODEL_DIR, "word_model.pkl")
PHRASE_MODEL_FILE = os.path.join(MODEL_DIR, "phrase_model.pkl")

SEQUENCE_LENGTH = 40
TWO_HAND_SEQUENCE_LENGTH = 40

WORD_CONF_THRESHOLD = 50.0
PHRASE_CONF_THRESHOLD = 50.0

STATIC_HOLD_SECONDS = 2.0
REPEAT_COOLDOWN_SECONDS = 1.5
WORD_COOLDOWN = 2.8
PHRASE_COOLDOWN = 2.8

DISPLAY_HOLD_SECONDS = 3.5

mp_hands = mp.solutions.hands

static_model = joblib.load(STATIC_MODEL_FILE)
word_model = joblib.load(WORD_MODEL_FILE)
phrase_model = joblib.load(PHRASE_MODEL_FILE)

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.4,
    min_tracking_confidence=0.4
)

word_buffer = deque(maxlen=SEQUENCE_LENGTH)
phrase_buffer = deque(maxlen=TWO_HAND_SEQUENCE_LENGTH)
conversation = deque(maxlen=12)

stable_output = ""
stable_start_time = 0

last_committed_output = ""
last_commit_time = 0

word_last_commit = 0
phrase_last_commit = 0

display_text = ""
display_until = 0


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


def sequence_has_enough_motion(sequence_buffer, threshold=0.045):
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


def sequence_has_enough_motion_2hand(sequence_buffer, threshold=0.06):
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


def commit_output(text, now):
    global last_committed_output
    global last_commit_time
    global display_text
    global display_until

    conversation.appendleft(text)
    last_committed_output = text
    last_commit_time = now

    display_text = text
    display_until = now + DISPLAY_HOLD_SECONDS

    return text


def process_frame(frame):
    global stable_output
    global stable_start_time
    global last_committed_output
    global last_commit_time
    global word_last_commit
    global phrase_last_commit
    global display_text
    global display_until

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    hand_results = hands.process(rgb_frame)

    now = time.time()

    current_prediction = ""
    current_confidence = 0.0

    word_output = ""
    word_conf = 0.0

    phrase_output = ""
    phrase_conf = 0.0

    current_output = ""
    committed_output = ""

    status_text = "Waiting"
    hold_text = f"Hold: 0.0 / {STATIC_HOLD_SECONDS:.1f}"
    num_hands_detected = 0

    # ---------------- HAND DETECTION ----------------
    if hand_results.multi_hand_landmarks:
        num_hands_detected = len(hand_results.multi_hand_landmarks)

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

    # ---------------- 1-HAND MOTION MODEL ----------------
    if len(word_buffer) == SEQUENCE_LENGTH and sequence_has_enough_motion(word_buffer):
        flattened = []

        for frame_data in word_buffer:
            flattened.extend(frame_data)

        word_output = word_model.predict([flattened])[0]

        if hasattr(word_model, "predict_proba"):
            probs = word_model.predict_proba([flattened])[0]
            word_conf = float(np.max(probs)) * 100

    # ---------------- 2-HAND MOTION MODEL ----------------
    if len(phrase_buffer) == TWO_HAND_SEQUENCE_LENGTH and sequence_has_enough_motion_2hand(phrase_buffer):
        flattened_two_hand = []

        for frame_data in phrase_buffer:
            flattened_two_hand.extend(frame_data)

        phrase_output = phrase_model.predict([flattened_two_hand])[0]

        if hasattr(phrase_model, "predict_proba"):
            probs = phrase_model.predict_proba([flattened_two_hand])[0]
            phrase_conf = float(np.max(probs)) * 100

    # ---------------- PRIORITY ----------------
    # Matches additioncore priority:
    # 2-hand motion > 1-hand motion > 1-hand static
    current_output = current_prediction
    display_confidence = current_confidence

    if phrase_output and phrase_conf > PHRASE_CONF_THRESHOLD:
        current_output = phrase_output
        display_confidence = phrase_conf

    elif word_output and word_conf > WORD_CONF_THRESHOLD:
        current_output = word_output
        display_confidence = word_conf

    # ---------------- AUTO COMMIT ----------------
    if phrase_output and phrase_conf > PHRASE_CONF_THRESHOLD:
        can_commit_phrase = now - phrase_last_commit >= PHRASE_COOLDOWN

        if can_commit_phrase:
            committed_output = commit_output(phrase_output, now)
            status_text = f"Phrase added: {phrase_output}"
            phrase_last_commit = now
            phrase_buffer.clear()
            stable_output = ""
            stable_start_time = 0
        else:
            status_text = "Phrase cooldown"

    elif word_output and word_conf > WORD_CONF_THRESHOLD:
        can_commit_word = now - word_last_commit >= WORD_COOLDOWN

        if can_commit_word:
            committed_output = commit_output(word_output, now)
            status_text = f"Word added: {word_output}"
            word_last_commit = now
            word_buffer.clear()
            stable_output = ""
            stable_start_time = 0
        else:
            status_text = "Word cooldown"

    elif current_output:
        if current_output == stable_output:
            held_time = now - stable_start_time if stable_start_time else 0
        else:
            stable_output = current_output
            stable_start_time = now
            held_time = 0

        hold_text = f"Hold: {held_time:.1f} / {STATIC_HOLD_SECONDS:.1f}"

        if held_time >= STATIC_HOLD_SECONDS:
            can_commit_static = (
                current_output != last_committed_output
                or now - last_commit_time >= REPEAT_COOLDOWN_SECONDS
            )

            if can_commit_static:
                committed_output = commit_output(current_output, now)
                status_text = f"Static added: {current_output}"
                stable_output = ""
                stable_start_time = 0
                word_buffer.clear()
                phrase_buffer.clear()
            else:
                status_text = "Repeat cooldown"
        else:
            status_text = "Holding..."

    else:
        stable_output = ""
        stable_start_time = 0
        hold_text = f"Hold: 0.0 / {STATIC_HOLD_SECONDS:.1f}"
        status_text = "Waiting"

    # Keep the committed output visible briefly on the frontend
    shown_prediction = current_output

    if now < display_until and display_text:
        shown_prediction = display_text

    return {
        "prediction": str(shown_prediction) if shown_prediction else "",
        "current_prediction": str(current_output) if current_output else "",
        "committed": str(committed_output) if committed_output else "",
        "confidence": round(display_confidence / 100, 4),
        "confidence_percent": round(display_confidence, 2),
        "static_prediction": str(current_prediction) if current_prediction else "",
        "static_confidence": round(current_confidence, 2),
        "word": str(word_output) if word_output else "",
        "word_confidence": round(word_conf, 2),
        "phrase": str(phrase_output) if phrase_output else "",
        "phrase_confidence": round(phrase_conf, 2),
        "hands": num_hands_detected,
        "hold": hold_text,
        "status": status_text,
        "conversation": list(conversation)
    }


def clear_conversation():
    global last_committed_output
    global last_commit_time
    global stable_output
    global stable_start_time
    global display_text
    global display_until
    global word_last_commit
    global phrase_last_commit

    conversation.clear()
    word_buffer.clear()
    phrase_buffer.clear()

    last_committed_output = ""
    last_commit_time = 0
    stable_output = ""
    stable_start_time = 0
    display_text = ""
    display_until = 0
    word_last_commit = 0
    phrase_last_commit = 0

    return {
        "message": "Conversation cleared"
    }