# SkillGap Quest
### AI-Based Resume Skill Gap Analysis and Course Recommendation System

**Team:** Saakshi Krishnani (Roll 16) · Vaishnavi Khade (Roll 26) · Rutuj Bawankar (Roll 72)

**Semester:** 7th · **Subject:** MLOps

**GitHub repository:** `https://github.com/<your-username>/skillgap-quest` (replace with your real link after Section 15)

---

## 1. What does this project do? (in plain words)

You give it **your resume** and pick a **job you want** (for example "Data Analyst" or "Digital Marketer").
The system then:

1. **Reads** your resume (pasted text, PDF, DOCX or TXT).
2. **Finds the skills** written in it (Python, SQL, Excel, Communication ...).
3. **Compares** them with the skills that job needs.
4. **Shows the gaps** (skills you are missing) and gives you a **match score**.
5. **Recommends one free and one paid course** for every gap.
6. **Builds a dated study roadmap** you can tick off week by week.

It has 100 target jobs (50 tech + 50 non-tech) and a dashboard with a score ring, radar chart, "skill constellation", skill-gap table, course cards and a roadmap. It works in light and dark mode.

> **Honest note about "AI":** the matching is **rule-based keyword matching** (regular expressions + weights), not a trained machine-learning model. Section 12 explains how to upgrade it.

---

## 2. Step-by-step setup and execution

**What you need:** Python 3.9 or newer (check with `python --version`; on Windows try `py --version`). Git is only needed for Section 15.

### Step 1: Get the project
Unzip `skillgap-quest-project.zip` (or `git clone <your-repo-link>`), then open a terminal **inside the `skillgap` folder**.
- Windows: open the folder, click the address bar, type `cmd`, press Enter.
- macOS / Linux: `cd path/to/skillgap`

### Step 2A: Run the website (no installation)
```
python server.py
```
(Windows: `py server.py` if `python` is not recognised.) The browser opens `http://localhost:8000`. Choose a role, paste or upload a resume, press **Analyze resume**. Stop with **Ctrl + C**. If port 8000 is busy: `PORT=8001 python server.py` (macOS/Linux) or `set PORT=8001 && python server.py` (Windows).

### Step 2B: Run the Python version
```
cd python_backend
python -m venv .venv
# activate the virtual environment:
#   Windows:       .venv\Scripts\activate
#   macOS/Linux:   source .venv/bin/activate
pip install -r requirements.txt
python analyze_resume.py sample_resume.txt "Data Scientist"
```
Expected result: `Match score: 64%`, skills found, gaps (Statistics, Scikit-learn, Deep Learning) and recommended courses. Results are saved in `output/gap_report.csv`.

Use your own resume and choose free or paid courses:
```
python analyze_resume.py my_resume.pdf "Data Analyst" --pref free
```
`--pref` can be `free`, `paid` or `both`. Role names must match `data/roles.csv` exactly.

### Step 3: Run the automated tests
```
cd python_backend
pip install pytest
pytest -q
```
Expected: `12 passed`.

### Step 4 (optional): Run in Docker
```
docker build -t skillgap-quest .
docker run -p 8000:8000 skillgap-quest
```
Open `http://localhost:8000`. (The Dockerfile has not been tested on a Docker machine yet.)

### Troubleshooting
| Problem | Fix |
|---|---|
| `python` not recognised | use `py`, or reinstall Python with "Add to PATH" ticked |
| `No module named pandas` | run `pip install -r requirements.txt` inside `python_backend` |
| PDF upload says "No text found" | the PDF is a scanned image; paste the text instead |
| PDF upload fails on the website | check internet (PDF reader loads online) or paste the text |

---

## 3. Folder structure

```
skillgap/
├── README.md                  <- you are here
├── server.py                  <- tiny local web server (Python standard library only)
├── Dockerfile                 <- container image for the website
├── .gitignore
├── .github/workflows/ci.yml   <- continuous integration: runs the tests on every push
├── public/
│   └── index.html             <- the whole website: design + logic + data
└── python_backend/
    ├── analyze_resume.py      <- same analysis written in Python (beginner friendly)
    ├── requirements.txt       <- Python libraries to install
    ├── pytest.ini             <- test settings
    ├── sample_resume.txt      <- example resume for testing
    ├── tests/test_pipeline.py <- 12 automated tests
    └── data/
        ├── skills.csv         <- dataset 1: 76 skills + the pattern used to find them
        ├── roles.csv          <- dataset 2: 100 roles and the skills (with weights) each needs
        └── courses.csv        <- dataset 3: 152 courses (a free and a paid one per skill)
```

---

## 4. The dataset (what data does the project use?)

**There is no downloaded dataset** (no Kaggle file, no web scraping). The project runs on a **knowledge base that we built by hand**, stored as three simple tables. The only "live" data is the resume you give it, which is processed in your browser and never uploaded or saved.

| File | Rows | Columns | What it holds |
|---|---|---|---|
| `skills.csv` | 76 | `skill, category, pattern` | Every skill we can detect, its category (Programming, Data, ML & AI, Web, Cloud & DevOps, Business, Marketing & Sales, Creative, Security, Hardware, Soft Skills ...) and a **regex pattern** that finds it in text |
| `roles.csv` | 636 | `role, role_type, skill, weight` | For each of the 100 roles, the skills it needs. `weight` says how important: **3 = essential, 2 = important, 1 = nice to have** |
| `courses.csv` | 152 | `skill, type, title, provider, hours` | One **free** and one **paid** course for each skill, with provider and estimated hours |

Example rows:

```
skills.csv   : Python,Programming,\bpython\b
roles.csv    : Data Scientist,tech,Statistics,3
courses.csv  : Statistics,free,Statistics and Probability,Khan Academy,40
```

**How the data was prepared**
- Skills and patterns were written by us after studying common job requirements.
- Role-to-skill weights are **our judgement**, not taken from a job-market study.
- Courses were picked from well-known providers (Coursera, Udemy, freeCodeCamp, Kaggle Learn, Google, HubSpot, Khan Academy and others). Hours are estimates. Prices and availability change, so check the provider before enrolling.
- The same data lives inside `public/index.html` (the website) and in the CSV files (the Python version). The CSVs were exported from the website data so both versions give the same answers.

---

## 5. Data extraction (getting text out of the resume)

A computer cannot "see" a PDF like we do, so the first job is to turn the file into plain text.

| Input | Website uses | Python version uses |
|---|---|---|
| Pasted text | read directly | read directly |
| `.txt` | browser `File.text()` | `Path.read_text()` |
| `.pdf` | **pdf.js** reads every page and joins the text pieces | **pdfplumber** (`page.extract_text()`) |
| `.docx` | **mammoth.js** (`extractRawText`) | **python-docx** (reads each paragraph) |

Limits: a **scanned PDF** (a photo of a page) has no text inside, so nothing can be extracted. OCR is not included. Paste the text instead.

---

## 6. Data cleaning (making the text ready)

Raw resume text is messy: capital letters, bullets, extra spaces, blank lines. Cleaning makes matching reliable.

| Step | Why | Example |
|---|---|---|
| Lowercase everything | "Python" and "python" must count as the same word | `Python` -> `python` |
| Replace bullets, dashes and `|` with a space (Python version) | symbols are noise | `• Built` -> ` built` |
| Collapse many spaces into one | PDFs often add odd gaps | `Python    SQL` -> `python sql` |
| Remove blank-line clutter | keeps lines tidy | |
| Word-boundary patterns (`\b`) while matching | stops false hits | `\bgit\b` matches "git" but not "digital" |

The website does lowercasing and uses boundary-safe patterns. The Python version also does the symbol and space clean-up (function `clean_text`).

---

## 7. Skill detection (finding skills in the text)

For each of the 76 skills we run its **regular expression** (a search pattern) on the cleaned text and **count the matches**.

Example, the SQL pattern: `\bsql\b|mysql|postgres|sqlite`. It finds "SQL", "MySQL", "Postgres" ... so a resume that says "MySQL" still gets credit for SQL.

**Strength of a skill** depends on how many times it appears:

| Mentions | Credit |
|---|---|
| 1 | 70% of its weight |
| 2 | 85% |
| 3 or more | 100% |

Why? A skill mentioned once in a list is weaker evidence than one that appears in your skills, projects and experience.

---

## 8. Scoring (what the 41% / 64% means)

```
points earned = sum of (weight x strength) for every required skill found
total points  = sum of weights of all required skills
match score   = points earned / total points x 100
```

**Worked example** (included `sample_resume.txt`, role = Data Scientist, total weights = 23):

| Skill | Weight | Mentions | Credit | Points |
|---|---|---|---|---|
| Python | 3 | 3 | 100% | 3.00 |
| SQL | 3 | 1 | 70% | 2.10 |
| Machine Learning | 3 | 2 | 85% | 2.55 |
| Pandas | 2 | 2 | 85% | 1.70 |
| NumPy | 2 | 2 | 85% | 1.70 |
| Data Visualization | 2 | 4 | 100% | 2.00 |
| Git | 1 | 2 | 85% | 0.85 |
| Communication | 1 | 2 | 85% | 0.85 |
| Statistics, Scikit-learn, Deep Learning | 3, 2, 1 | 0 | 0% | 0 (these are the **gaps**) |

Points earned = **14.75** out of **23** -> **14.75 / 23 = 64%**.

The website calls the same number "XP out of 100" and uses levels: under 30 = Seedling, 30-54 = Rising Star, 55-79 = Role-Ready, 80+ = Hire-Me Legend.

---

## 9. Gap analysis, recommendations and roadmap

1. **Gap** = a required skill that was **not found** in the resume.
2. **Priority** comes from the weight: 3 = High, 2 = Medium, 1 = Low. Gaps are sorted High first, so the "Next quest" is the one that raises your score most.
3. **Course recommendation:** `courses.csv` gives a free and a paid course for each gap. You choose one (or filter "Free only" / "Paid only").
4. **Roadmap:** for every course you add, study time = course hours + 25% for practice. With your hours per week and a start date, the site lays out phases such as `Week 1-2 (6 Oct to 19 Oct)`. Each phase has 4 steps: learn, practise on a small project, add the skill to your resume, checkpoint.
5. **Projected score:** after you finish the planned courses, each new skill is counted at 70% of its weight (as if mentioned once), giving the "64% -> 73%" style estimate.

---

## 10. Complete workflow

```
 Resume (paste / PDF / DOCX / TXT)         Target role (1 of 100)
              |                                     |
              v                                     |
   [1] EXTRACT text  (pdf.js / mammoth.js           |
                      or pdfplumber / python-docx)  |
              |                                     |
              v                                     |
   [2] CLEAN text    (lowercase, remove symbols,    |
                      fix spaces)                   |
              |                                     |
              v                                     v
   [3] DETECT skills  ----->  [4] COMPARE with role needs (roles.csv, weights)
       (skills.csv regex)                |
                                         v
                          [5] SCORE + find GAPS + set PRIORITY
                                         |
                                         v
                          [6] RECOMMEND courses (courses.csv: free + paid)
                                         |
                                         v
                          [7] BUILD roadmap (hours, weeks, dates, steps)
                                         |
                                         v
                          [8] SHOW dashboard (ring, radar, constellation,
                                              gap table, courses, roadmap)
```

---

## 11. Libraries and tools used

**Website (JavaScript, runs in the browser)**

| Tool | Used for |
|---|---|
| HTML, CSS, JavaScript (no framework) | pages, styling, all logic |
| Inline SVG (hand-written) | score ring, radar chart, skill constellation |
| **pdf.js 3.11.174** | reading PDF text |
| **mammoth.js 1.6.0** | reading DOCX text |

**Python version**

| Library | Type | Used for |
|---|---|---|
| **pandas** | install | loading the three CSV tables and sorting results |
| **pdfplumber** | install | reading PDF text |
| **python-docx** | install | reading DOCX text |
| `re` | built in | regular-expression skill matching and cleaning |
| `argparse` | built in | command-line options (`--pref`) |
| `pathlib` | built in | file paths |
| `http.server`, `socketserver`, `webbrowser`, `os` | built in | `server.py`, the local web server |

**Testing:** the website logic was checked in a headless browser (jsdom) by opening all 100 roles and every tab; the Python pipeline was run on TXT, DOCX and PDF copies of the sample resume and produced the same 64% as the website.

---

## 12. Limitations and future work

**Limitations**
- Keyword matching cannot understand meaning: "built prediction models" will not count as "Machine Learning" unless a keyword appears.
- Skill weights and role lists are our own estimates.
- Scanned PDFs cannot be read (no OCR).
- Courses are suggestions; availability and price change.

**Future work (how to make it truly "AI")**
- Use **spaCy** or **sentence-transformers** to match skills by meaning, not exact words.
- Train/learn role skill profiles from a real job-postings dataset.
- Add OCR (for example Tesseract) for scanned resumes.
- Pull live course data from provider APIs and show ratings.
- Add user accounts to save progress and a FastAPI backend.

---

## 13. Glossary for beginners

- **Regex (regular expression):** a short pattern that finds text, like `\bpython\b`.
- **Weight:** how important a skill is for a role (1 to 3).
- **Skill gap:** a skill the role needs that your resume does not show.
- **Extraction:** pulling text out of a file.
- **Cleaning:** tidying text so the computer can match it reliably.
- **CSV:** a simple table saved as text, openable in Excel.
- **pandas:** a Python library for working with tables.

---

## 14. MLOps practices in this project

MLOps means running a data/ML pipeline in a repeatable, tested and deployable way. The analysis here is rule-based, not a trained model, but the same practices apply.

| MLOps stage | What we did | Where |
|---|---|---|
| Data management and versioning | Knowledge base kept as three CSV files tracked in Git | `python_backend/data/` |
| Reproducible pipeline | One command runs extract, clean, detect, score, recommend | `analyze_resume.py` |
| Automated testing | 12 tests: data integrity, patterns, scoring, cleaning, recommendations | `python_backend/tests/` |
| Continuous integration | GitHub Actions installs dependencies and runs the tests on every push | `.github/workflows/ci.yml` |
| Packaging and deployment | Dockerfile for the website; also a single HTML file | `Dockerfile`, `public/index.html` |
| Monitoring (proposed) | Track score distribution and unknown-skill rate to detect drift | see the project report |

---

## 15. Publish to GitHub (step by step)

1. Sign in at github.com, click **New repository**, name it `skillgap-quest`, leave "Add a README" **unticked**, click **Create repository**.
2. In the `skillgap` folder run:
```
git init
git add .
git commit -m "SkillGap Quest: initial commit"
git branch -M main
git remote add origin https://github.com/<your-username>/skillgap-quest.git
git push -u origin main
```
3. Open the **Actions** tab on GitHub: the CI workflow runs the tests automatically.
4. Copy the repository link and paste it at the top of this README and into the project report.
