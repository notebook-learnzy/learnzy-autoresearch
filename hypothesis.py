"""
hypothesis.py — VAULT-DRIVEN CUSTOM QUERIES (5 per link)

Queries written directly from Learnzy's Obsidian hypothesis vault.
Each query targets a SPECIFIC mechanism identified in the vault notes.
"""

QUERIES = {
    # LINK A: HRV → Cognition
    # Vault mechanism: Neurovisceral integration — PFC controls vagal tone → HRV
    # Same brain network: PFC + ACC + insula + amygdala regulates HRV AND attention/WM
    # RMSSD = parasympathetic (PNS) marker; high RMSSD = better PFC function
    "A_hrv_cognition": [
        "RMSSD vagal tone prefrontal cortex working memory executive function students",
        "neurovisceral integration heart rate variability cognitive control attention meta-analysis",
        "HF-HRV high frequency power executive function working memory university students",
        "vagal tone parasympathetic nervous system cognitive flexibility attention control",
        "heart rate variability SDNN cognitive performance memory encoding university students systematic review",
    ],

    # LINK B: Sleep → Cognition
    # Vault mechanism: Sleep spindles (12-15 Hz stage 2) = memory consolidation
    # Sharp-wave ripples (150-200 Hz) = hippocampal replay → neocortical transfer
    # Slow oscillations stage 3 = hippocampus-neocortex dialogue
    # 40% reduction in memory formation with sleep deprivation
    "B_sleep_cognition": [
        "sleep spindles stage 2 NREM memory consolidation learning students",
        "slow-wave sleep hippocampus neocortex memory transfer sharp-wave ripples",
        "sleep deprivation working memory hippocampus encoding 40 percent students",
        "REM sleep memory integration learning cognitive performance university",
        "PSQI sleep efficiency memory consolidation academic performance longitudinal",
    ],

    # LINK C: Cognition → Academic Grades
    # Vault: working memory holds 7±2 items, manipulates for maths/physics/logic
    # Stress-induced WM impairment → 0.3–0.5 SD decrease in academics
    # Maths, physics, organic chemistry = highest cognitive load subjects
    "C_cognition_grades": [
        "working memory capacity GPA university students meta-analysis longitudinal",
        "executive function attention control academic achievement exam scores students",
        "cognitive load working memory mathematics physics academic performance",
        "stress working memory impairment academic grades university cohort study",
        "attention sustained concentration exam performance university students prospective",
    ],

    # LINK D1: HRV/Sleep → Depression
    # Vault: HPA axis → cortisol → GR receptors → hippocampus atrophy → depression
    # Chronic cortisol: 8-12% hippocampus volume reduction, 50% neurogenesis decrease
    # Low HRV = SNS dominance = elevated baseline cortisol = PHQ-9 scores
    "D1_focus_depression": [
        "heart rate variability RMSSD PHQ-9 depression students autonomic nervous system",
        "HPA axis cortisol depression hippocampus atrophy students longitudinal",
        "sleep quality depression PHQ-9 BDI cortisol HPA axis students",
        "vagal tone low HRV depression risk meta-analysis systematic review",
        "sleep deprivation cortisol elevated depression symptoms university students",
    ],

    # LINK D2: HRV/Sleep → Anxiety
    # Vault: amygdala hyperactivity (37% increase with sleep deprivation)
    # PFC loses control over amygdala when HRV low / sleep deprived
    # GAD-7, STAI instruments; baroreflex connects HRV to anxiety regulation
    "D2_focus_anxiety": [
        "heart rate variability GAD-7 anxiety disorder students autonomic regulation",
        "amygdala prefrontal cortex HRV anxiety emotional regulation students",
        "sleep deprivation amygdala reactivity anxiety GAD-7 university students",
        "vagal tone baroreflex anxiety management generalized anxiety disorder",
        "RMSSD HRV anxiety symptoms meta-analysis prospective cohort systematic review",
    ],

    # LINK D3: HRV/Sleep → Insomnia
    # Vault: sleep latency, WASO, sleep efficiency = ISI/PSQI instruments
    # Autonomic hyperarousal = elevated SNS at night = low nocturnal HRV = insomnia
    # HPA axis dysregulation prevents sleep initiation
    "D3_focus_insomnia": [
        "nocturnal heart rate variability HRV insomnia severity index ISI autonomic hyperarousal",
        "sleep efficiency WASO sleep latency HRV PSQI insomnia systematic review",
        "autonomic nervous system SNS hyperarousal insomnia treatment outcome",
        "HPA cortisol sleep initiation insomnia disorder university students",
        "RMSSD nocturnal HRV insomnia sleep quality PSQI prospective cohort",
    ],
}

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

SEARCH_DEPTH = {
    "A_hrv_cognition":     100,
    "B_sleep_cognition":   100,
    "C_cognition_grades":  100,
    "D1_focus_depression": 100,
    "D2_focus_anxiety":    100,
    "D3_focus_insomnia":   100,
}
