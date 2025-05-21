import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, request, render_template
from backend.ml.model import match_jobs
from backend.ml.processes import process_resume
from backend.utilities.resume_parser import parse_resume

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        if "resume" not in request.files:
            return render_template("index.html", error="No resume uploaded.")
        resume = request.files["resume"]
        if resume.filename == "":
            return render_template("index.html", error="Empty filename. Please upload a valid file.")
        try:
            text = parse_resume(resume)
            processed_text = process_resume(text)
            matches = match_jobs(processed_text)
            return render_template("index.html", matches=matches)
        except Exception as e:
            return render_template("index.html", error=str(e))

    return render_template("index.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
