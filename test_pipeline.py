"""Automated tests for the SkillGap Quest Python pipeline. Run from python_backend:  pytest -q"""
import re
from pathlib import Path
import pandas as pd
import pytest
import analyze_resume as ar

ROOT = Path(__file__).parent.parent
SAMPLE = (ROOT / "sample_resume.txt").read_text(encoding="utf-8")

@pytest.fixture(scope="module")
def tables():
    return tuple(pd.read_csv(ROOT / "data" / f"{n}.csv") for n in ("skills", "roles", "courses"))

def test_table_sizes(tables):
    skills, roles, courses = tables
    assert len(skills) == 76 and roles.role.nunique() == 100 and len(courses) == 152

def test_role_split_is_50_50(tables):
    roles = tables[1].drop_duplicates("role")
    assert roles.role_type.value_counts().to_dict() == {"tech": 50, "non-tech": 50}

def test_all_patterns_compile(tables):
    for pattern in tables[0].pattern:
        re.compile(pattern)

def test_referential_integrity(tables):
    skills, roles, courses = tables
    assert set(roles.skill) <= set(skills.skill)
    assert set(courses.skill) == set(skills.skill)

def test_weights_are_1_to_3(tables):
    assert set(tables[1].weight) <= {1, 2, 3}

def test_every_skill_has_free_and_paid_course(tables):
    types = tables[2].groupby("skill").type.apply(set)
    assert all(t == {"free", "paid"} for t in types)

def test_strength_factor():
    assert (ar.strength(1), ar.strength(2), ar.strength(3), ar.strength(9)) == (0.7, 0.85, 1.0, 1.0)

def test_clean_text():
    assert ar.clean_text("\u2022 Python   SQL\n\n  Git") == "python sql\ngit"

def test_sample_resume_data_scientist(tables):
    skills, roles, _ = tables
    score, found, req, gaps = ar.analyze(SAMPLE, "Data Scientist", skills, roles)
    assert score == 64
    assert set(gaps.index) == {"Statistics", "Scikit-learn", "Deep Learning"}

def test_unknown_role_exits(tables):
    with pytest.raises(SystemExit):
        ar.analyze(SAMPLE, "Astronaut", tables[0], tables[1])

def test_recommend_free_only(tables):
    skills, roles, courses = tables
    _, _, _, gaps = ar.analyze(SAMPLE, "Data Scientist", skills, roles)
    recs = ar.recommend(gaps, courses, "free")
    assert set(recs.type) == {"free"} and len(recs) == 3

def test_score_is_between_0_and_100_for_every_role(tables):
    skills, roles, _ = tables
    for role in roles.role.unique():
        assert 0 <= ar.analyze(SAMPLE, role, skills, roles)[0] <= 100
