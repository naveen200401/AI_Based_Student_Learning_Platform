import os, json, re
from flask import render_template, request, redirect, url_for, flash, session
from flask_login import login_required, current_user
from quiz import quiz_bp
from models import Document, QuizResult, db
import google.generativeai as genai

# ---- Gemini setup ----
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
GEN_MODEL = "models/gemini-2.5-flash"   # fast and good for MCQs

# ---- helpers ----
def get_latest_doc(user_id: int):
    return Document.query.filter_by(user_id=user_id).order_by(Document.id.desc()).first()

def clamp(n, lo, hi):
    return max(lo, min(n, hi))

def extract_json_block(text: str) -> str:
    """
    Gemini sometimes wraps JSON in code fences or adds prose.
    This extracts the first JSON array block.
    """
    # strip code fences if present
    fenced = re.search(r"```(?:json)?(.*?)```", text, re.S | re.I)
    if fenced:
        text = fenced.group(1).strip()
    # find first [...] block
    start = text.find("[")
    end = text.rfind("]")
    if start != -1 and end != -1 and end > start:
        return text[start:end+1]
    return text  # fallback; let json.loads handle or fail

# =========================================================
#  START QUIZ: show form (GET) / generate (POST)
# =========================================================
@quiz_bp.route("/quiz/start", methods=["GET", "POST"])
@login_required
def start_quiz():
    latest = get_latest_doc(current_user.id)
    if not latest or not (latest.extracted_text or "").strip():
        flash("Please upload a document first.", "warning")
        return redirect(url_for("docs_bp.upload"))

    if request.method == "POST":
        # ---- collect inputs ----
        try:
            num = int(request.form.get("num_questions", "5"))
        except Exception:
            num = 5
        num = clamp(num, 1, 50)  # MAX = 50 as requested

        difficulty = (request.form.get("difficulty") or "medium").lower()
        if difficulty not in ("easy", "medium", "hard"):
            difficulty = "medium"

        text = latest.extracted_text

        # ---- build prompt ----
        prompt = f"""
You are an expert MCQ quiz generator.

Generate {num} multiple-choice questions strictly based on the DOCUMENT TEXT below.
Difficulty: {difficulty}

Rules:
- Each question must have exactly 4 options labeled "A)", "B)", "C)", "D)".
- Provide which option letter is correct via the "correct" field (e.g., "B").
- Provide a one-sentence explanation for the correct answer.
- Output ONLY a valid JSON array (no extra text, no markdown fence).

JSON schema example:
[
  {{
    "question": "....",
    "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
    "correct": "B",
    "explanation": "one sentence explanation"
  }}
]

DOCUMENT TEXT:
{text}
"""

        model = genai.GenerativeModel(GEN_MODEL)
        resp = model.generate_content(prompt)
        raw = getattr(resp, "text", "").strip()

        # ---- robust parse ----
        json_str = extract_json_block(raw)
        try:
            data = json.loads(json_str)
            assert isinstance(data, list) and len(data) > 0
        except Exception:
            flash("Quiz generation failed to parse JSON. Please try again.", "danger")
            return redirect(url_for("quiz_bp.start_quiz"))

        # normalize options to ensure ["A) ..", "B) ..", ...]
        for q in data:
            opts = q.get("options", [])
            # ensure strings and trimmed
            q["options"] = [str(o).strip() for o in opts[:4]]
            # if options don't start with A)/B) etc., add them
            labels = ["A)", "B)", "C)", "D)"]
            for i, o in enumerate(q["options"]):
                if not o.strip().upper().startswith(labels[i]):
                    q["options"][i] = f"{labels[i]} {o}"

            # ensure correct is one of A/B/C/D
            corr = (q.get("correct") or "").strip().upper()
            if corr not in ("A", "B", "C", "D"):
                q["correct"] = "A"

            # ensure explanation exists
            if not q.get("explanation"):
                q["explanation"] = "No explanation provided."

        # ---- init session state ----
        session["quiz_data"] = data
        session["quiz_index"] = 0
        session["quiz_score"] = 0

        return redirect(url_for("quiz_bp.show_question"))

    # GET → render form
    return render_template("quiz_start.html")

# =========================================================
#  SHOW QUESTION (GET) / SUBMIT ANSWER (POST)
# =========================================================
@quiz_bp.route("/quiz/q", methods=["GET"])
@login_required
def show_question():
    data = session.get("quiz_data")
    idx  = session.get("quiz_index", 0)
    if not data:
        flash("Please generate a quiz first.", "warning")
        return redirect(url_for("quiz_bp.start_quiz"))

    # end guard
    if idx >= len(data):
        return redirect(url_for("quiz_bp.show_result"))

    q = data[idx]
    return render_template(
        "quiz_question.html",
        qnum=idx + 1,
        total=len(data),
        question=q
    )

@quiz_bp.route("/quiz/answer", methods=["POST"])
@login_required
def submit_answer():
    data = session.get("quiz_data", [])
    idx  = session.get("quiz_index", 0)
    score = session.get("quiz_score", 0)

    if idx >= len(data):
        return redirect(url_for("quiz_bp.show_result"))

    selected = (request.form.get("answer") or "").strip().upper()
    correct  = (data[idx].get("correct") or "").strip().upper()

    if selected == correct:
        score += 1

    # store per-question feedback to show instantly (optional)
    session["last_explanation"] = data[idx].get("explanation", "")

    idx += 1
    session["quiz_index"] = idx
    session["quiz_score"] = score

    if idx >= len(data):
        return redirect(url_for("quiz_bp.show_result"))
    return redirect(url_for("quiz_bp.show_question"))

# =========================================================
#  RESULT PAGE (stores in DB as requested)
# =========================================================
@quiz_bp.route("/quiz/result", methods=["GET"])
@login_required
def show_result():
    data = session.get("quiz_data", [])
    total = len(data)
    score = session.get("quiz_score", 0)

    # Save to DB as requested
    if total > 0:
        rec = QuizResult(user_id=current_user.id, score=score, total=total)
        db.session.add(rec)
        db.session.commit()

    percent = (score / total * 100) if total else 0
    if percent < 40:
        feedback = "Needs Practice"
    elif percent < 70:
        feedback = "Good, keep improving"
    else:
        feedback = "Excellent!"

    # (optional) clear quiz session
    # session.pop("quiz_data", None)
    # session.pop("quiz_index", None)
    # session.pop("quiz_score", None)

    return render_template("quiz_result.html",
                           score=score, total=total, feedback=feedback)
