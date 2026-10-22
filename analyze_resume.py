"""SkillGap Quest - Python version of the analysis pipeline.
Usage:  python analyze_resume.py sample_resume.txt "Data Scientist"
        python analyze_resume.py my_resume.pdf "Data Analyst" --pref free
"""
import argparse, re
from pathlib import Path
import pandas as pd

DATA = Path(__file__).parent / "data"

# STEP 1: EXTRACTION - get raw text out of PDF / DOCX / TXT
def extract_text(path):
    p = Path(path)
    if p.suffix.lower() == ".pdf":
        import pdfplumber
        with pdfplumber.open(p) as pdf:
            return "\n".join(page.extract_text() or "" for page in pdf.pages)
    if p.suffix.lower() == ".docx":
        import docx
        return "\n".join(par.text for par in docx.Document(p).paragraphs)
    return p.read_text(encoding="utf-8", errors="ignore")

# STEP 2: CLEANING - make text uniform so keyword matching is reliable
def clean_text(text):
    text = text.lower()                          # "Python" and "python" become the same
    text = re.sub(r"[\u2022\u25cf\u2013\u2014|]", " ", text)  # bullets, dashes, pipes -> space
    text = re.sub(r"[ \t]+", " ", text)          # many spaces -> one space
    text = re.sub(r"\s*\n\s*", "\n", text)       # remove blank-line clutter
    return text.strip()

# STEP 3: SKILL DETECTION - count regex matches for every skill in skills.csv
def detect_skills(text, skills):
    found = {}
    for row in skills.itertuples():
        n = len(re.findall(row.pattern, text))
        if n:
            found[row.skill] = n
    return found

def strength(n):                                 # 1 mention = 70%, 2 = 85%, 3+ = 100%
    return 1.0 if n >= 3 else 0.85 if n == 2 else 0.7

# STEP 4: GAP ANALYSIS - compare found skills with what the role needs
def analyze(text, role, skills, roles):
    req = roles[roles.role == role].set_index("skill")["weight"]
    if req.empty:
        raise SystemExit(f"Unknown role: {role}. See data/roles.csv for the 100 roles.")
    found = detect_skills(clean_text(text), skills)
    earned = sum(w * strength(found[s]) for s, w in req.items() if s in found)
    score = int(earned / req.sum() * 100 + 0.5)
    gaps = req[~req.index.isin(found)].sort_values(ascending=False)
    return score, found, req, gaps

# STEP 5: RECOMMENDATION - one free and one paid course per gap
def recommend(gaps, courses, pref):
    rows = courses[courses.skill.isin(gaps.index)].copy()
    rows["weight"] = rows.skill.map(gaps)
    rows["priority"] = rows.weight.map({1: "Low", 2: "Medium", 3: "High"})
    if pref != "both":
        rows = rows[rows.type == pref]
    return rows.sort_values(["weight", "skill", "type"], ascending=[False, True, True])

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("resume"); ap.add_argument("role")
    ap.add_argument("--pref", choices=["free", "paid", "both"], default="both")
    a = ap.parse_args()
    skills, roles, courses = (pd.read_csv(DATA / f"{n}.csv") for n in ("skills", "roles", "courses"))
    score, found, req, gaps = analyze(extract_text(a.resume), a.role, skills, roles)
    print(f"\nRole: {a.role}\nMatch score: {score}%")
    print("Skills found  :", ", ".join(f"{k}({v}x)" for k, v in found.items() if k in req.index) or "none")
    print("Skill gaps    :", ", ".join(f"{k} (weight {v})" for k, v in gaps.items()) or "none")
    recs = recommend(gaps, courses, a.pref)
    print("\nRecommended courses:\n", recs[["priority", "skill", "type", "title", "provider", "hours"]].to_string(index=False))
    Path("output").mkdir(exist_ok=True)
    recs.to_csv("output/gap_report.csv", index=False)
    print("\nSaved: output/gap_report.csv")
