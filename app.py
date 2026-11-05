import os
import requests
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

BOT_TOKEN = os.getenv("6506189895:AAHuMhk2nVqU0UDO5fITFFXAyyGM2rC5e-s")
CHAT_ID = os.getenv("6895524607")
TG_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

GRADES = {
    "first_secondary": {
        "label": "الصف الأول الثانوي",
        "courses": ["JavaScript 42"],
    },
    "second_secondary_bac": {
        "label": "الصف الثاني الثانوي بكالوريا",
        "courses": ["JavaScript 54", "Python 25", "الثقافة المالية"],
    },
}

@app.route("/")
def index():
    return render_template("index.html", grades=GRADES)

@app.route("/submit", methods=["POST"])
def submit():
    grade_key = request.form.get("grade")
    name = request.form.get("full_name", "").strip()
    username = request.form.get("username", "").strip()
    selected = request.form.getlist("courses")

    if grade_key not in GRADES:
        return jsonify(ok=False, error="المرحلة غير صحيحة"), 400
    if len(name.split()) < 4:
        return jsonify(ok=False, error="اكتب الاسم رباعي"), 400
    if not username or not selected:
        return jsonify(ok=False, error="اكمل البيانات واختار مادة واحدة على الأقل"), 400

    allowed = GRADES[grade_key]["courses"]
    selected = [c for c in selected if c in allowed]
    if not selected:
        return jsonify(ok=False, error="مادة غير صالحة"), 400

    text = (
        f"🆕 تسليم جديد\n"
        f"🏫 المرحلة: {GRADES[grade_key]['label']}\n"
        f"👤 الاسم: {name}\n"
        f"🔑 اسم المستخدم بالمنصة: {username}\n"
        f"📚 المواد: {', '.join(selected)}"
    )
    requests.post(f"{TG_API}/sendMessage", data={"chat_id": CHAT_ID, "text": text})

    for course in selected:
        file = request.files.get(f"proof_{course}")
        if not file:
            return jsonify(ok=False, error=f"ارفع صورة إثبات لمادة {course}"), 400
        requests.post(
            f"{TG_API}/sendPhoto",
            data={"chat_id": CHAT_ID, "caption": f"{name} - {course}"},
            files={"photo": (file.filename, file.stream, file.mimetype)},
        )

    return jsonify(ok=True)

if __name__ == "__main__":
    app.run(debug=False)
