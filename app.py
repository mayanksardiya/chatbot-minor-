from flask import Flask, render_template, request, jsonify, send_from_directory
import pickle
import json
import re
import os
from difflib import get_close_matches

from utils.nlp_utils import tokenize, bag_of_words
from db.db import get_colleges_by_marks, save_chat

app = Flask(__name__)

# Allowed origins for embedded websites. Keep "*" for easy setup.
# For production, replace with specific domains.
ALLOWED_ORIGIN = os.getenv("ALLOWED_ORIGIN", "*")

# -------------------------------
# Load ML model
# -------------------------------
def load_model_artifacts():
    try:
        loaded_model = pickle.load(open("model.pkl", "rb"))
        loaded_words = pickle.load(open("words.pkl", "rb"))
        loaded_classes = pickle.load(open("classes.pkl", "rb"))
        return loaded_model, loaded_words, loaded_classes
    except Exception as e:
        print("Model load warning:", e)
        return None, [], []

model, words, classes = load_model_artifacts()

# -------------------------------
# Load intents
# -------------------------------
with open("intents.json") as file:
    intents = json.load(file)

# -------------------------------
# User memory
# -------------------------------
user_profiles = {}

# -------------------------------
# Extract marks
# -------------------------------
def extract_marks(msg):
    numbers = re.findall(r'\d+', msg)
    if numbers:
        return int(numbers[0])
    return None

# -------------------------------
# Detect interest
# -------------------------------
def extract_interest(msg):
    msg = msg.lower()

    if "engineering" in msg or "btech" in msg or "cs" in msg:
        return "Engineering"
    elif "mba" in msg or "management" in msg:
        return "Management"
    elif "science" in msg or "bsc" in msg:
        return "Science"

    return None

# -------------------------------
# Predict intent
# -------------------------------
def predict_intent(msg):
    if model is None:
        return "model_unavailable", 0.0

    tokens = tokenize(msg)
    bag = bag_of_words(tokens, words)

    probs = model.predict_proba([bag])[0]
    max_prob = max(probs)
    index = probs.argmax()

    return classes[index], max_prob

# -------------------------------
# Fallback
# -------------------------------
def fallback_response(msg):
    all_patterns = []
    tag_map = {}

    for intent in intents["intents"]:
        for pattern in intent["patterns"]:
            all_patterns.append(pattern)
            tag_map[pattern] = intent

    matches = get_close_matches(msg, all_patterns, n=1, cutoff=0.5)

    if matches:
        intent_data = tag_map[matches[0]]
        if intent_data["responses"]:
            return " ".join(intent_data["responses"])

    return "I could not understand your request. Please rephrase."

# -------------------------------
# Main Chatbot Logic
# -------------------------------
def chatbot_response(msg, user_id="default"):
    if model is None:
        return "Chatbot model is not loaded yet. Please run train.py and redeploy with model.pkl, words.pkl, and classes.pkl files."

    intent, confidence = predict_intent(msg)

    if user_id not in user_profiles:
        user_profiles[user_id] = {}

    profile = user_profiles[user_id]
    response = ""

    # ---------------------------
    # PRIORITY RULES (IMPORTANT)
    # ---------------------------

    # Detect marks first
    marks = extract_marks(msg)
    if marks:
        profile["marks"] = marks
        response = f"Marks recorded: {marks}. Now tell your preferred field (Engineering, Management, Science)."

        save_chat(msg, response, intent, float(confidence))
        return response

    # Detect interest (cs, mba, etc)
    interest = extract_interest(msg)
    if interest:
        profile["interest"] = interest
        response = f"Interest noted: {interest}. Now you can ask for college suggestions."

        save_chat(msg, response, intent, float(confidence))
        return response

    # ---------------------------
    # ML LOGIC
    # ---------------------------
    if confidence < 0.6:
        response = fallback_response(msg)

    else:
        # College suggestion
        if intent == "college_suggestion":

            if "marks" not in profile:
                response = "Please tell your marks first."

            elif "interest" not in profile:
                response = "Please tell your preferred field."

            else:
                marks = profile["marks"]
                interest = profile["interest"]

                try:
                    colleges = get_colleges_by_marks(marks)

                    if not colleges:
                        response = "No colleges found based on your marks."
                    else:
                        response = f"Based on your marks ({marks}) and interest in {interest}, here are suitable colleges:\n"

                        count = 0
                        for c in colleges:
                            try:
                                name, location, course = c[0], c[1], c[2]

                                if interest.lower() in course.lower():
                                    response += f"{name} ({location}) - {course}\n"
                                    count += 1

                                if count >= 5:
                                    break

                            except:
                                continue

                        # Advice
                        response += "\nAdvice:\n"

                        if marks >= 90:
                            response += "- You have strong chances for top-tier colleges.\n"
                        elif marks >= 75:
                            response += "- You can secure good mid-tier colleges.\n"
                        else:
                            response += "- Consider backup colleges and explore all options.\n"

                        response += "- Focus on placement, location, and course quality before deciding."

                except Exception as e:
                    print("DB Error:", e)
                    response = "Error fetching college data."

        # Normal intents
        else:
            for i in intents["intents"]:
                if i["tag"] == intent:
                    response = " ".join(i["responses"])
                    break

    # ---------------------------
    # SAVE CHAT
    # ---------------------------
    try:
        save_chat(msg, response, intent, float(confidence))
    except Exception as e:
        print("DB Save Error:", e)

    return response

# -------------------------------
# Routes
# -------------------------------
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    msg = data["message"]

    response = chatbot_response(msg)

    return jsonify({"response": response})

@app.route("/chat", methods=["OPTIONS"])
def chat_options():
    # Handles browser CORS preflight for cross-site widget calls.
    return ("", 204)

@app.route("/widget.js")
def widget_script():
    return send_from_directory("static", "widget.js")

@app.after_request
def add_cors_headers(response):
    if request.path in ["/chat", "/widget.js"]:
        response.headers["Access-Control-Allow-Origin"] = ALLOWED_ORIGIN
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response

# -------------------------------
# Run server
# -------------------------------
if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug)