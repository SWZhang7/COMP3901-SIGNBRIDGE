from flask import Blueprint, request, jsonify
from flask_login import login_user
from flask import Blueprint, request, jsonify, session
from __init__ import bcrypt
from supabase_client import table
import re
from datetime import datetime
import base64
import cv2
import numpy as np
from sign_model import process_frame, clear_conversation

auth = Blueprint('auth', __name__)


def _validate_signup_fields(data):
    required_fields = ["first_name", "last_name", "date_of_birth", "jsl_level", "username", "email", "password"]
    for field in required_fields:
        if field not in data or not data[field]:
            return f"{field} is required"
    if len(data.get('password', '')) < 8:
        return "Password must be at least 8 characters"
    email_pattern = r"[^@]+@[^@]+\.[^@]+"
    if not re.match(email_pattern, data.get('email', '')):
        return "Invalid email format"
    valid_levels = ["Beginner", "Intermediate", "Advanced"]
    if data.get('jsl_level') not in valid_levels:
        return "Invalid JSL level"
    try:
        datetime.strptime(data.get('date_of_birth', ''), "%Y-%m-%d").date()
    except ValueError:
        return "Date of birth must be YYYY-MM-DD"
    return None


def _resp_error(res):
    # Safely extract error from various response shapes returned by supabase client
    try:
        return res.error
    except Exception:
        pass
    try:
        # dict-like
        return res.get('error')
    except Exception:
        pass
    # no error found
    return None


def _resp_data(res):
    try:
        return res.data
    except Exception:
        pass
    try:
        return res.get('data')
    except Exception:
        pass
    return None


@auth.route('/signup', methods=['POST'])
def signup():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be valid JSON"}), 400

    err = _validate_signup_fields(data)
    if err:
        return jsonify({"error": err}), 400

    # check existing username/email
    res = table('users').select('id').or_(f"username.eq.{data['username']},email.eq.{data['email']}").execute()
    err = _resp_error(res)
    if err:
        return jsonify({"error": "Database error checking existing user"}), 500
    existing = _resp_data(res)
    if existing and len(existing) > 0:
        return jsonify({"error": "Username or email already registered"}), 400

    # hash password
    pw_hash = bcrypt.generate_password_hash(data['password']).decode('utf-8')

    # insert into users table
    payload = {
        'first_name': data['first_name'],
        'last_name': data['last_name'],
        'date_of_birth': data['date_of_birth'],
        'jsl_level': data['jsl_level'],
        'username': data['username'],
        'email': data['email'],
        'password': pw_hash,
    }
    insert = table('users').insert(payload).execute()
    if _resp_error(insert):
        return jsonify({"error": "Database insert failed"}), 500

    # Attempt to set session (auto-login) if insert returned the new user
    inserted = _resp_data(insert)
    try:
        if inserted and isinstance(inserted, list) and len(inserted) > 0:
            new_user = inserted[0]
            session.clear()
            # prefer id field if present
            session['user_id'] = new_user.get('id') or new_user.get('user_id')
    except Exception:
        # ignore session set failures
        pass

    return jsonify({"message": "Account created successfully!"})


@auth.route('/login', methods=['POST'])
def login():
    data = request.get_json(silent=True)
    if not data or 'password' not in data:
        return jsonify({"error": "username/email and password required (JSON body)"}), 400

    identifier = data.get('username') or data.get('email') or data.get('identifier')
    if not identifier:
        return jsonify({"error": "username/email is required"}), 400

    # determine if identifier is email
    if '@' in identifier:
        res = table('users').select('*').eq('email', identifier).execute()
    else:
        res = table('users').select('*').eq('username', identifier).execute()
    if _resp_error(res):
        return jsonify({"error": "Database error"}), 500
    records = _resp_data(res)
    if not records or len(records) == 0:
        return jsonify({"message": "Invalid credentials"}), 401

    user = records[0]
    if bcrypt.check_password_hash(user['password'], data['password']):
        # store minimal session
        session.clear()
        session['user_id'] = user['id']
        return jsonify({"message": "Login successful!"})

    return jsonify({"message": "Invalid credentials"}), 401


@auth.route('/', methods=['GET'])
def home():
    return jsonify({"message": "Welcome to SignBridge backend!"})


@auth.route('/profile', methods=['GET'])
def profile():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401
    # include id so frontend can reference user_id if needed
    res = table('users').select('id, first_name, last_name, username, date_of_birth, jsl_level, email').eq('id', user_id).execute()
    if _resp_error(res):
        return jsonify({"error": "User not found"}), 404
    user_records = _resp_data(res)
    if not user_records or len(user_records) == 0:
        return jsonify({"error": "User not found"}), 404
    user = user_records[0]
    # fetch user_progress if present
    try:
        prog_res = table('user_progress').select('quizzes_taken, average_score').eq('user_id', user['id']).execute()
        prog_err = _resp_error(prog_res)
        progress = None
        if not prog_err:
            prog_data = _resp_data(prog_res)
            if prog_data and len(prog_data) > 0:
                p = prog_data[0]
                progress = {
                    'quizzesTaken': p.get('quizzes_taken', 0),
                    'averageScore': p.get('average_score', 0)
                }
    except Exception:
        progress = None

    return jsonify({
        "first_name": user['first_name'],
        "last_name": user['last_name'],
        "username": user['username'],
        "date_of_birth": user['date_of_birth'],
        "jsl_level": user['jsl_level'],
        "email": user['email'],
        "progress": progress or { 'quizzesTaken': 0, 'averageScore': 0 }
    })


@auth.route('/flashcards', methods=['GET'])
def get_flashcards():
    # Return flashcards stored in Supabase (if any)
    res = table('flashcards').select('*').order('id', desc=False).execute()
    if _resp_error(res):
        return jsonify({"error": "Failed to fetch flashcards"}), 500
    return jsonify(_resp_data(res) or [])


@auth.route('/quiz/results', methods=['POST'])
def submit_quiz_results():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body required"}), 400
    # expected fields: user_id (optional if logged in), quiz_name, score, total
    user_id = session.get('user_id') or data.get('user_id')
    payload = {
        'user_id': user_id,
        'quiz_name': data.get('quiz_name'),
        'score': data.get('score'),
        'total': data.get('total'),
        'percentage': data.get('percentage')
    }
    print("[submit_quiz_results] payload:", payload)
    res = table('quiz_results').insert(payload).execute()
    err = _resp_error(res)
    print("[submit_quiz_results] resp_error:", err)
    print("[submit_quiz_results] resp_data:", _resp_data(res))
    if err:
        return jsonify({"error": "Failed to save quiz result"}), 500
    return jsonify({"message": "Result saved", "data": _resp_data(res)})


@auth.route('/quiz/results', methods=['GET'])
def get_quiz_results():
    # Return quiz results for the logged-in user
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401
    try:
        res = table('quiz_results').select('id, quiz_name, score, total, percentage, created_at').eq('user_id', user_id).order('created_at', desc=True).execute()
        err = _resp_error(res)
        if err:
            return jsonify({"error": "Failed to fetch quiz history"}), 500
        data = _resp_data(res) or []
        return jsonify({"history": data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@auth.route('/user/progress', methods=['PUT'])
def update_user_progress():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body required"}), 400
    user_id = session.get('user_id') or data.get('user_id')
    if not user_id:
        return jsonify({"error": "User id required"}), 400
    # upsert into user_progress table
    payload = {
        'user_id': user_id,
        'quizzes_taken': data.get('quizzesTaken'),
        'average_score': data.get('averageScore')
    }
    print("[update_user_progress] payload:", payload)
    # supabase upsert can accept a list; using list to ensure correct behavior
    res = table('user_progress').upsert([payload], on_conflict='user_id').execute()
    err = _resp_error(res)
    print("[update_user_progress] resp_error:", err)
    print("[update_user_progress] resp_data:", _resp_data(res))
    if err:
        return jsonify({"error": "Failed to update progress"}), 500
    return jsonify({"message": "Progress updated", "data": _resp_data(res)})


@auth.route('/health', methods=['GET'])
def health():
    # simple Supabase check
    try:
        res = table('users').select('id').limit(1).execute()
        err = _resp_error(res)
        if err:
            return jsonify({"status": "error", "detail": str(err)}), 500
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"status": "error", "detail": str(e)}), 500
    
    
@auth.route('/predict-sign', methods=['POST'])
def predict_sign_route():
    try:
        data = request.get_json(silent=True)

        if not data:
            return jsonify({"error": "Request body required"}), 400

        image_data = data.get("image")

        if not image_data:
            return jsonify({"error": "No image received"}), 400

        encoded_data = image_data.split(",")[1]

        nparr = np.frombuffer(base64.b64decode(encoded_data), np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        result = process_frame(frame)

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@auth.route('/clear-translation', methods=['POST'])
def clear_translation_route():
    return jsonify(clear_conversation())