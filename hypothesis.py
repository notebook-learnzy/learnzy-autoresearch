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
        # Plain-text queries targeting COGNITIVE HRV (not cardiac disease)
        "heart rate variability cognitive performance meta-analysis healthy adults",
        "vagal tone prefrontal cortex cognitive control neuroscience",
        "cardiac vagal control working memory attention executive function",
        "RMSSD HF-HRV cognitive flexibility attention university students",
        "parasympathetic nervous system cognitive function systematic review",
        "heart rate variability memory attention executive function review",
    ],

    "B_sleep_cognition": [
        '"sleep deprivation" AND "cognitive performance" AND "systematic review"',
        '"sleep quality" AND "memory consolidation" AND "meta-analysis"',
        '"slow wave sleep" AND "cognitive function" AND "review"',
        '"sleep duration" AND "learning outcome" AND "prospective cohort"',
        '"REM sleep" AND "executive function" AND "students"',
    ],

    "C_cognition_grades": [
        '"neuropsychological scores" AND "GPA" AND "prospective study"',
        '"cognitive function" AND "standardized test scores" AND "longitudinal"',
        '"executive cognitive functions" AND "academic success" AND "prospective cohort"',
        '"working memory" AND "exam performance" AND "university students"',
        '"attention" AND "academic achievement" AND "cohort study"',
        '"fluid intelligence" AND "academic results" AND "education outcomes"',
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
