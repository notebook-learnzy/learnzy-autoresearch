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
        # New queries focusing on psychological constructs and specific populations
        "heart rate variability cognitive neuroscience young adults",
        "vagal tone executive function university students",
        "HF-HRV cognitive control neuroscience",
        "cardiac vagal control cognitive flexibility prefrontal",
        "autonomic nervous system cognition attention youth"
    ],

    "B_sleep_cognition": [
        '"sleep deprivation" AND "cognitive performance" AND "systematic review"',
        '"sleep quality" AND "memory consolidation" AND "meta-analysis"',
        '"slow wave sleep" AND "cognitive function" AND "review"',
        '"sleep duration" AND "learning outcome" AND "prospective cohort"',
        '"REM sleep" AND "executive function" AND "students"',
    ],

    "C_cognition_grades": [
        # Refined queries to focus on cognitive abilities tied to academic output
        '"fluid intelligence university students longitudinal study"',
        '"executive attention academic results prospective study"',
        '"cognitive ability exam scores longitudinal"',
        '"working memory academic performance students"',
        '"attention executive function grades high school university"',
    ],

    "D1_focus_depression": [
        '"HRV" AND "depression risk" AND "meta-analysis"',
        '"sleep disturbance" AND "PHQ-9" AND "prospective cohort"',
        '"heart rate variability" AND "depressive symptoms" AND "review"',
        '"RMSSD" AND "depression" AND "systematic review"',
        'HRV sleep PHQ-9 depression college students',
    ],

    "D2_focus_anxiety": [
        '"HRV" AND "anxiety prediction" AND "meta-analysis"',
        '"autonomic nervous system" AND "GAD-7" AND "systematic review"',
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
    "min_sample_size": 20,      # loosened to catch more HRV-cognition papers
    "min_year": 2010,           # widened to capture classic HRV-cognition reviews
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
    "A_hrv_cognition":     60,  # boosted — was stuck at 0, needs more attempts
    "B_sleep_cognition":   20,
    "C_cognition_grades":  80,
    "D1_focus_depression": 30,
    "D2_focus_anxiety":    40,
    "D3_focus_insomnia":   50,  # boosted — was weak
}