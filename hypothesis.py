"""
hypothesis.py — THE AGENT'S ONLY MUTABLE FILE

Analog to train.py in karpathy/autoresearch.

Everything in this file is fair game for the agent to modify each run.
The agent's goal: maximize evidence_score by finding higher-quality,
more relevant, larger-sample papers for each hypothesis link.

DO NOT modify sources.py, agent.py, or the GitHub Actions workflow.
"""

# ─── SEARCH QUERIES ───────────────────────────────────────────────────────────
QUERIES = {
    "A_hrv_cognition": [
        "vagal tone executive function young adults neuroscience",
        "HF-HRV cognitive flexibility neuropsychology students",
        "cardiac vagal control cognitive performance youth psychology",
        "RMSSD cognitive function university populations",
        "autonomic nervous system attention students fMRI study"
    ],

    "B_sleep_cognition": [
        '"slow wave sleep" AND "memory consolidation" AND "student study"',
        '"REM sleep" AND "cognitive enhancement" AND "academic performance"',
        '"sleep efficiency" AND "learning capacity" AND "review students"',
        '"actigraphy" AND "sleep quality" AND "cognitive outcomes"',
        '"Pittsburgh Sleep Quality Index" AND "executive function" AND "campus study"',
    ],

    "C_cognition_grades": [
        '"fluid intelligence" AND "longitudinal GPA" university students',
        '"executive function" AND "academic performance" AND "longitudinal study"',
        '"cognitive ability" AND "exam scores" AND "prospective cohort"',
        '"working memory" AND "academic achievement" university',
        '"attention" AND "GPA" AND "longitudinal student research"',
    ],

    "D1_focus_depression": [
        '"HRV" AND "depression risk" AND "systematic review"',
        '"sleep disturbance" AND "PHQ-9" AND "prospective cohort"',
        '"heart rate variability" AND "depressive symptoms" AND "meta-analysis"',
        '"RMSSD" AND "depression" AND "review"',
        'HRV sleep PHQ-9 depression university students',
    ],

    "D2_focus_anxiety": [
        '"HRV" AND "anxiety prediction" AND "systematic review"',
        '"autonomic nervous system" AND "GAD-7" AND "meta-analysis"',
        '"sleep quality" AND "anxiety disorder" AND "prospective study"',
        '"HRV biofeedback" AND "anxiety" AND "RCT"',
        'HRV sleep GAD-7 anxiety young adults',
    ],

    "D3_focus_insomnia": [
        "heart rate variability insomnia disorder autonomic",
        "HRV nocturnal sleep quality insomnia severity systematic review",
        "autonomic dysregulation insomnia treatment outcome RCT",
        "PSQI HRV insomnia severity index correlation meta-analysis",
        "sleep efficiency heart rate variability insomnia longitudinal",
    ],
}

# ─── INCLUSION CRITERIA ────────────────────────────────────────────────────────
INCLUSION = {
    "min_sample_size": 50,      
    "min_year": 2015,           
    "max_results_per_query": 50,
    "study_types": [
        "meta_analysis",
        "systematic_review",
        "rct",
        "prospective_cohort",
        "cross_sectional",
    ],
}

# ─── SEARCH DEPTH PER LINK ────────────────────────────────────────────────────
SEARCH_DEPTH = {
    "A_hrv_cognition":     80, 
    "B_sleep_cognition":   30,
    "C_cognition_grades":  100,
    "D1_focus_depression": 30,
    "D2_focus_anxiety":    40,
    "D3_focus_insomnia":   50,
}