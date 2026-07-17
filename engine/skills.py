"""
engine/skills.py
-----------------
A curated skills taxonomy plus small regex-based extractors for contact
info and years of experience. No external NLP model is required, which
keeps the project fully offline and dependency-light.
"""

import re

# ---------------------------------------------------------------------
# Curated skill taxonomy, grouped for readability. Matching is case
# insensitive and word-boundary aware (so "R" doesn't match "HR").
# ---------------------------------------------------------------------
SKILL_GROUPS = {
    "Programming Languages": [
        "Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "C",
        "Go", "Rust", "Ruby", "PHP", "Swift", "Kotlin", "Scala", "R",
        "MATLAB", "Perl", "SQL",
    ],
    "Web & Frameworks": [
        "React", "Angular", "Vue", "Next.js", "Node.js", "Express",
        "Django", "Flask", "FastAPI", "Spring Boot", "Ruby on Rails",
        "ASP.NET", "HTML", "CSS", "Tailwind", "Bootstrap", "GraphQL",
        "REST API",
    ],
    "Data & Machine Learning": [
        "Machine Learning", "Deep Learning", "NLP", "Computer Vision",
        "TensorFlow", "PyTorch", "Keras", "Scikit-learn", "Pandas",
        "NumPy", "OpenCV", "Data Analysis", "Data Visualization",
        "Statistics", "Tableau", "Power BI", "ETL", "Big Data",
        "Spark", "Hadoop",
    ],
    "Cloud & DevOps": [
        "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Terraform",
        "Jenkins", "CI/CD", "Linux", "Git", "GitHub", "GitLab",
        "Ansible", "Nginx", "Microservices",
    ],
    "Databases": [
        "MySQL", "PostgreSQL", "MongoDB", "Redis", "SQLite",
        "Oracle", "Elasticsearch", "Firebase", "DynamoDB",
    ],
    "Project & Product": [
        "Agile", "Scrum", "Kanban", "JIRA", "Product Management",
        "Stakeholder Management", "Roadmapping",
    ],
    "Soft Skills": [
        "Communication", "Leadership", "Teamwork", "Problem Solving",
        "Time Management", "Critical Thinking", "Collaboration",
        "Adaptability", "Mentoring", "Presentation",
    ],
}

ALL_SKILLS = [skill for group in SKILL_GROUPS.values() for skill in group]

# Pre-compile one regex per skill for fast, accurate matching.
_SKILL_PATTERNS = {
    skill: re.compile(r"(?<![\w+#.]){}(?![\w+#.])".format(re.escape(skill)), re.IGNORECASE)
    for skill in ALL_SKILLS
}

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
PHONE_RE = re.compile(r"(\+?\d{1,3}[\s-]?)?(\(?\d{3,4}\)?[\s-]?)\d{3,4}[\s-]?\d{3,4}")
EXPERIENCE_RE = re.compile(r"(\d{1,2})\+?\s*(?:years|yrs)\b", re.IGNORECASE)


def extract_skills(text: str) -> list:
    """Return the list of known skills found in the given text."""
    found = [skill for skill, pattern in _SKILL_PATTERNS.items() if pattern.search(text)]
    return sorted(found)


def extract_email(text: str) -> str:
    match = EMAIL_RE.search(text)
    return match.group(0) if match else ""


def extract_phone(text: str) -> str:
    match = PHONE_RE.search(text)
    return match.group(0).strip() if match else ""


def extract_years_experience(text: str) -> int:
    """Best-effort heuristic: take the largest 'X years' mention in the text."""
    matches = [int(m) for m in EXPERIENCE_RE.findall(text)]
    return max(matches) if matches else 0


def guess_candidate_name(text: str, fallback: str) -> str:
    """
    Heuristic: the candidate's name is usually the first non-empty line
    of the resume, as long as it looks like a name (short, no @ or digits).
    Falls back to the filename if nothing plausible is found.
    """
    for line in text.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        if "@" in line or any(ch.isdigit() for ch in line):
            break
        words = line.split()
        if 1 <= len(words) <= 4 and all(w.replace(".", "").isalpha() for w in words):
            return line.title()
        break
    return fallback
