"""
app.py
-------
Flask web app for the Smart Resume Screening & Candidate Ranking Tool.

Run:
    python app.py

Then open http://127.0.0.1:5000
"""

import os
from flask import Flask, render_template, request, jsonify

from engine.parser import extract_text, UnsupportedFileType
from engine.ranker import rank_resumes

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 25 * 1024 * 1024  # 25 MB total upload cap

ALLOWED_EXTENSIONS = {"pdf", "docx", "txt"}
MAX_RESUMES = 30


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/rank", methods=["POST"])
def rank():
    job_description = (request.form.get("job_description") or "").strip()
    files = [f for f in request.files.getlist("resumes") if f and f.filename]

    errors = []
    if not job_description:
        errors.append("Please paste a job description.")
    if not files:
        errors.append("Please upload at least one resume.")
    if len(files) > MAX_RESUMES:
        errors.append(f"Please upload {MAX_RESUMES} resumes or fewer at a time.")

    if errors:
        return render_template("index.html", errors=errors, job_description=job_description)

    resumes = []
    skipped = []
    for f in files:
        if not allowed_file(f.filename):
            skipped.append(f"{f.filename} (unsupported type)")
            continue
        try:
            text = extract_text(f)
            if not text.strip():
                skipped.append(f"{f.filename} (no readable text found)")
                continue
            resumes.append({"filename": f.filename, "text": text})
        except UnsupportedFileType:
            skipped.append(f.filename)
        except Exception as e:
            skipped.append(f"{f.filename} (error: {e})")

    if not resumes:
        errors.append("None of the uploaded files could be read. Try .pdf, .docx, or .txt.")
        return render_template("index.html", errors=errors, job_description=job_description)

    results = rank_resumes(job_description, resumes)

    return render_template(
        "results.html",
        results=results,
        job_description=job_description,
        skipped=skipped,
        total=len(results),
    )


@app.route("/api/rank", methods=["POST"])
def api_rank():
    """JSON API: same logic as /rank, for programmatic use."""
    job_description = (request.form.get("job_description") or "").strip()
    files = [f for f in request.files.getlist("resumes") if f and f.filename]

    if not job_description or not files:
        return jsonify({"error": "job_description and at least one resume file are required"}), 400

    resumes = []
    for f in files:
        if not allowed_file(f.filename):
            continue
        try:
            text = extract_text(f)
            if text.strip():
                resumes.append({"filename": f.filename, "text": text})
        except Exception:
            continue

    if not resumes:
        return jsonify({"error": "no readable resumes"}), 400

    results = rank_resumes(job_description, resumes)
    return jsonify({"total": len(results), "results": results})


@app.route("/about")
def about():
    return render_template("about.html")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
