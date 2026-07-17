"""
engine/ranker.py
------------------
The core "AI" of the tool: ranks candidate resumes against a job
description using two signals combined into one explainable score:

  1. TF-IDF cosine similarity  — how textually/semantically close the
     resume is to the job description as a whole (captures phrasing,
     responsibilities, domain language beyond a fixed skill list).

  2. Skill overlap             — what fraction of the skills explicitly
     asked for in the job description are actually present in the resume,
     using the curated taxonomy in skills.py. This keeps the ranking
     explainable: you can show a recruiter exactly which skills matched.

final_score = 0.6 * tfidf_similarity + 0.4 * skill_overlap
(weights are tunable via the WEIGHTS constant below)
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from engine.skills import (
    extract_skills,
    extract_email,
    extract_phone,
    extract_years_experience,
    guess_candidate_name,
)

WEIGHTS = {"tfidf": 0.6, "skills": 0.4}


def _tfidf_similarities(job_description: str, resume_texts: list) -> list:
    """Returns a cosine-similarity score (0-1) for each resume vs the JD."""
    corpus = [job_description] + resume_texts
    vectorizer = TfidfVectorizer(stop_words="english", max_features=5000)
    tfidf_matrix = vectorizer.fit_transform(corpus)

    jd_vector = tfidf_matrix[0:1]
    resume_vectors = tfidf_matrix[1:]

    if resume_vectors.shape[0] == 0:
        return []

    sims = cosine_similarity(jd_vector, resume_vectors)[0]
    return sims.tolist()


def rank_resumes(job_description: str, resumes: list) -> list:
    """
    resumes: list of dicts, each {"filename": str, "text": str}
    Returns a list of result dicts sorted by final_score descending, e.g.:

      {
        "filename": "jane_doe.pdf",
        "candidate_name": "Jane Doe",
        "email": "jane@example.com",
        "phone": "+1 555-123-4567",
        "years_experience": 4,
        "final_score": 78.3,
        "tfidf_score": 71.0,
        "skill_score": 88.9,
        "matched_skills": ["Python", "Flask", "SQL", ...],
        "missing_skills": ["Docker", "AWS"],
      }
    """
    jd_skills = set(extract_skills(job_description))
    resume_texts = [r["text"] for r in resumes]

    tfidf_scores = _tfidf_similarities(job_description, resume_texts)

    results = []
    for resume, tfidf_sim in zip(resumes, tfidf_scores):
        text = resume["text"]
        resume_skills = set(extract_skills(text))

        matched = sorted(jd_skills & resume_skills)
        missing = sorted(jd_skills - resume_skills)

        skill_overlap = (len(matched) / len(jd_skills)) if jd_skills else 0.0

        final_score = (
            WEIGHTS["tfidf"] * tfidf_sim + WEIGHTS["skills"] * skill_overlap
        ) * 100

        results.append({
            "filename": resume["filename"],
            "candidate_name": guess_candidate_name(text, fallback=resume["filename"]),
            "email": extract_email(text),
            "phone": extract_phone(text),
            "years_experience": extract_years_experience(text),
            "final_score": round(final_score, 1),
            "tfidf_score": round(tfidf_sim * 100, 1),
            "skill_score": round(skill_overlap * 100, 1),
            "matched_skills": matched,
            "missing_skills": missing,
            "extra_skills": sorted(resume_skills - jd_skills),
        })

    results.sort(key=lambda r: r["final_score"], reverse=True)
    for i, r in enumerate(results, start=1):
        r["rank"] = i

    return results
