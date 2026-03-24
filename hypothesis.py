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
        "HRV RMSSD HF power vagal tone executive function attention working memory students",
        "heart rate variability cognitive performance college student RMSSD vagal tone neurovisceral integration",
        "vagal tone PFC working memory HRV academic performance",
        "autonomic nervous system cognitive function youth university",
        "neurovisceral integration theory cognitive performance RMSSD students"
    ],

    "B_sleep_cognition": [
        "sleep spindles slow-wave sleep PSQI actigraphy memory consolidation students",
        "NREM sleep sleep architecture memory retention learning outcomes",
        "sleep quality duration memory consolidation learning students PSQI actigraphy",
        "sleep and learning hippocampal-neocortical dialogue spindles students",
        "sleep duration sleep efficiency academic performance cognition students"
    ],

    "C_cognition_grades": [
        "working memory attention executive function GPA academic performance",
        "cognitive performance academic achievement exam scores stress attention",
        "stress cognitive function academic grades school performance students",
        "executive function academic outcomes university longitudinal",
        "academic performance neuropsychological predictors student success"
    ],

    "D1_focus_depression": [
        "HRV RMSSD PHQ-9 depression vagal tone sleep quality students",
        "sleep quality BDI HRV cortisol depression academic performance",
        "sleep architecture depression students HRV PHQ-9",
        "vagal regulation depression symptoms student populations",
        "autonomic dysfunction depression risk students meta-analysis"
    ],

    "D2_focus_anxiety": [
        "HRV RMSSD GAD-7 anxiety vagal tone autonomic regulation students",
        "sleep quality anxiety levels HRV GAD-7 STAI academic performance",
        "cortisol HRV anxiety stress regulatory mechanisms students",
        "vagal influence anxiety management young adults",
        "autonomic nervous system and anxiety disorders student populations"
    ],

    "D3_focus_insomnia": [
        "heart rate variability insomnia ISI PSQI autonomic markers students",
        "HRV insomnia ISI autonomic hyperarousal sleep disorder treatment",
        "autonomic regulation HRV sleep disorders insomnia ISI students",
        "insomnia autonomic markers HRV RMSSD PSQI academic performance",
        "HRV nocturnal sleep efficiency insomnia severity systematic review"
    ],
}

# ─── INCLUSION CRITERIA ────────────────────────────────────────────────────────
INCLUSION = {
    "min_sample_size": 20,      
    "min_year": 2010,           
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
    "A_hrv_cognition":     150, 
    "B_sleep_cognition":   100,
    "C_cognition_grades":  100,
    "D1_focus_depression": 80,
    "D2_focus_anxiety":    80,
    "D3_focus_insomnia":   150,
}