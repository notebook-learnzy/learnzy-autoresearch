"""
hypothesis.py — THE AGENT'S ONLY MUTABLE FILE

Analog to train.py in karpathy/autoresearch.

Everything in this file is fair game for the agent to modify each run.
The agent's goal: maximize evidence_score by finding higher-quality,
more relevant, larger-sample papers for each hypothesis link.

DO NOT modify sources.py, agent.py, or the GitHub Actions workflow.
"""

# ─── SEARCH QUERIES ───────────────────────────────────────────────────────────
# One list per hypothesis link. The agent modifies these to discover better papers.
# Fixed validation queries in sources.py ALWAYS run in addition to these.
#
# Hypothesis links:
#   A_hrv_cognition    : HRV → executive function / memory / attention
#   B_sleep_cognition  : Sleep → memory consolidation / learning / retention
#   C_cognition_grades : Cognition → academic grades / exam performance
#   D1_focus_depression: HRV + sleep → depression (PHQ-9)
#   D2_focus_anxiety   : HRV + sleep → anxiety (GAD-7)
#   D3_focus_insomnia  : HRV + sleep → insomnia (ISI)

QUERIES = {
    "A_hrv_cognition": [
        'resting heart rate variability executive function healthy adults',
        'baseline RMSSD working memory performance',
        'vagal tone cognitive performance prediction',
        'heart rate variability attention memory meta-analysis',
        'autonomic nervous system neurocognitive performance',
    ],

    "B_sleep_cognition": [
        '"sleep deprivation" AND "cognitive performance" AND "systematic review"',
        '"sleep quality" AND "memory consolidation" AND "meta-analysis"',
        '"slow wave sleep" AND "cognitive function" AND "review"',
        '"sleep duration" AND "learning outcome" AND "prospective cohort"',
        '"REM sleep" AND "executive function" AND "students"',
    ],

    "C_cognition_grades": [
        '"cognitive function" AND "academic performance" AND "longitudinal study"',
        '"working memory" AND "GPA" AND "meta-analysis"',
        '"executive function" AND "exam scores" AND "systematic review"',
        '"attention" AND "academic success" AND "cohort study"',
        '"cognitive abilities" AND "school performance" AND "university students"',
        '"neurocognitive performance" AND "academic achievement" AND "prospective study"',
        '"executive functioning" AND "academic success" AND "longitudinal analysis"',
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
        '"HRV" AND "insomnia severity" AND "meta-analysis"',
        '"autonomic function" AND "insomnia" AND "longitudinal study"',
        '"sleep efficiency" AND "HRV" AND "prospective cohort"',
        '"nocturnal HRV" AND "insomnia" AND "systematic review"',
        'HRV sleep insomnia severity index university students',
    ],
}

# ─── INCLUSION CRITERIA ────────────────────────────────────────────────────────
# Filters applied AFTER LLM extraction of paper metadata.
# Agent can tighten or loosen these to improve signal quality.

INCLUSION = {
    "min_sample_size": 20,      # HRV studies often n=20-40; 50 was filtering too much
    "min_year": 2010,           # broader window to include landmark papers
    "max_results_per_query": 50,
    "study_types": [            # which study designs to include
        "meta_analysis",
        "systematic_review",
        "rct",
        "prospective_cohort",
        "cross_sectional",
    ],
}

# ─── SEARCH DEPTH PER LINK ────────────────────────────────────────────────────
# Controls how many results to fetch per query for each link.
# Agent should allocate more depth to weaker links.
# Total across all links ideally stays under ~300 API calls to fit in TIME_BUDGET.

SEARCH_DEPTH = {
    "A_hrv_cognition":    20,
    "B_sleep_cognition":  20,
    "C_cognition_grades": 150,  # increase depth to focus on finding more substantial evidence
    "D1_focus_depression": 30,
    "D2_focus_anxiety":   40,
    "D3_focus_insomnia":  40,
}