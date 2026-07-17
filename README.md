# Shortlist — Smart Resume Screening & Candidate Ranking Tool

A complete, self-contained Flask + scikit-learn web app that ranks a batch
of resumes (PDF, DOCX, or TXT) against a job description, using an
explainable two-part AI score — no external API keys, no cloud calls,
everything runs locally.

## What's inside

```
smart_resume_screening/
├── app.py                          # Flask app (routes: /, /rank, /api/rank, /about)
├── requirements.txt
├── engine/
│   ├── parser.py                   # Extracts text from .pdf / .docx / .txt uploads
│   ├── skills.py                   # Curated skills taxonomy + email/phone/experience extraction
│   └── ranker.py                   # TF-IDF similarity + skill-overlap scoring & ranking
├── sample_data/
│   ├── job_description_sample.txt
│   └── resumes/                    # 5 sample resumes (.txt / .docx / .pdf) to try immediately
├── templates/
│   ├── base.html
│   ├── index.html                  # Upload form (job description + resumes)
│   ├── results.html                # Ranked candidate list
│   └── about.html                  # Scoring methodology
└── static/
    ├── css/style.css
    └── js/script.js                # Drag-and-drop upload interactivity
```

## Setup (VS Code)

1. Unzip this folder and open it in VS Code (`File → Open Folder`).
2. Open a terminal (`` Ctrl+` ``) and create a virtual environment:

   ```bash
   python -m venv venv
   ```

   Activate it:
   - Windows: `venv\Scripts\activate`
   - macOS / Linux: `source venv/bin/activate`

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Run the app:

   ```bash
   python app.py
   ```

5. Open **http://127.0.0.1:5000** in your browser.

## Try it immediately with the sample data

No real resumes handy? Use what's included:
- Paste the contents of `sample_data/job_description_sample.txt` into the job description box.
- Upload all 5 files in `sample_data/resumes/` (mix of .txt, .docx, .pdf).

You should see the backend-focused candidates rank at the top and the
marketing-focused resume rank at the bottom — a quick sanity check that
everything is wired correctly.

## How scoring works

Each candidate gets one combined score from two signals:

- **JD relevance (60%)** — TF-IDF cosine similarity between the job
  description and the resume's full text (captures phrasing and context,
  not just keywords).
- **Skill coverage (40%)** — the percentage of the job description's
  required skills (matched against a curated ~120-skill taxonomy in
  `engine/skills.py`) that are actually present in the resume.

The results page shows both sub-scores and the exact matched/missing
skills, so the ranking is explainable rather than a black box. Full
details are on the app's `/about` page.

You can change the 60/40 weighting in `engine/ranker.py` (the `WEIGHTS`
dict at the top of the file).

## Extending it

- **Bigger skill list**: add entries to `SKILL_GROUPS` in `engine/skills.py`.
- **Different scoring weights**: edit `WEIGHTS` in `engine/ranker.py`.
- **Persisting results**: currently nothing is saved — each `/rank`
  request is processed in memory and discarded. Add a database if you
  want to store screening history.
- **JSON API**: `POST /api/rank` accepts the same `job_description` +
  `resumes` fields as multipart form data and returns JSON — useful for
  hooking this up to another frontend or an ATS integration.

## Honest limitations

This is a heuristic screening aid, not a hiring decision-maker:
- It can't judge quality or depth of experience, only presence of terms.
- PDF text extraction can struggle with heavily designed, multi-column
  resume templates or text embedded in images.
- The skill taxonomy is a fixed list — skills phrased in unusual ways
  may be missed.

Always have a human review the shortlist before making hiring decisions.
