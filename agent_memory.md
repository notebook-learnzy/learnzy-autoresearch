Here's the updated memory file with your requested changes:

---

# Agent Memory — Directional Knowledge Per Link

This file is your persistent memory across runs. Read it BEFORE proposing any hypothesis.py change. It tells you what has been tried, what worked, and what to avoid re-trying.

The agent writes to this file after each run. Entries marked ✓ improved the score; entries marked ✗ did not.

---

## Link A — HRV → Cognition (current best score: 1.648)

### ✗ What has NOT worked (do not retry):
- Generic `"heart rate variability" AND "cognitive performance"` → returns cardiac disease/arrhythmia papers; LLM gives relevance=0 (wrong population)
- `"resting HRV"` / `"baseline RMSSD"` queries → papers have low citation counts, get pre-filtered out by top-10 citation filter before LLM sees them
- `"vagal tone" AND "working memory" AND "systematic review"` → no relevant papers found
- `"parasympathetic" AND "attention"` → returns autonomic physiology papers, not cognitive performance
- `"parasympathetic activity" AND "cognitive control" AND "neuroscience" AND "young adults"`
- `"cardiac vagal control" AND "cognitive function" AND "university students"`
- `"HF-HRV" AND "executive function" AND "neuroscience"`
- `"autonomic flexibility" AND "cognitive performance" AND "healthy young adults"`
- `"vagal tone" AND "cognitive function" AND "student population"`
- Queries from the previous run that did not improve results.

### ✗ What failed:
- No improvement from earlier run queries.

### ✓ What worked:
- Improvements observed in this run: Score increased from 1.539 to 1.648.

### ✓ Directions to try next:
- Search for the specific well-known papers: `Forte 2019 heart rate variability cognitive performance meta-analysis`
- Try: `HF-HRV prefrontal cortex cognitive control fMRI`
- Try: `cardiac vagal control cognitive function neuroscience`
- Try: `autonomic flexibility cognitive performance healthy young adults`
- Target specific journals: add `frontiers neuroscience` or `psychophysiology` to queries

---

## Link B — Sleep → Cognition (current best score: 0.492)

### ✗ What failed:
- Improvements not observed; score decreased from 1.988 to 0.492.
- Queries this run:
   - `"sleep deprivation" AND "cognitive performance" AND "systematic review"`
   - `"sleep quality" AND "memory consolidation" AND "meta-analysis"`
   - `"slow wave sleep" AND "cognitive function" AND "review"`
   - `"sleep duration" AND "learning outcome" AND "prospective cohort"`
   - `"REM sleep" AND "executive function" AND "students"`

### ✓ Directions to try next:
- `sleep duration academic performance GPA students`
- `Okano 2019 sleep academic achievement MIT` (known high-quality paper)

---

## Link C — Cognition → Grades (current best score: 1.304)

### ✗ What failed:
- Improvements not observed; score fell from 3.229 to 1.304.
- Queries this run:
   - `"cognitive talent metrics GPA predictive studies"`
   - `"working memory span academic success"`
   - `"exam scores cognitive baseline university"`
   - `"fluid intelligence university students longitudinal study"`
   - `"executive attention academic performance"`

### ✓ Directions to try next:
- Adjust specificity in queries to better target psychometric connections to grades.

---

## Link D1 — HRV/Sleep → Depression (current best score: 1.348)

### ✓ What has worked:
- Improvements not observed; score decreased from 1.551 to 1.348.

### ✗ What failed:
- Existing queries failed to improve: 
   - Previous successful ones that did not yield results this run.

### ✓ Directions to try next:
- Continue leveraging successful queries or seek additional query variations.

---

## Link D2 — HRV/Sleep → Anxiety (current best score: 2.815)

### ✓ What worked:
- Improvements observed in this run: Score increased from 2.481 to 2.815.
- Queries resulting in high-relevance papers were preserved.

### ⚠️ WARNING: D2 is the highest-scoring link. DO NOT change its queries unless you have a specific reason to believe a change will improve it.

---

## Link D3 — HRV/Sleep → Insomnia (current best score: 1.377)

### ✗ What failed:
- Improvements not observed; score decreased from 1.385 to 1.377.
- Queries this run did not yield improved results:
   - `"HRV" AND "insomnia severity" AND "meta-analysis"`
   - `"nocturnal HRV" AND "insomnia" AND "systematic review"`
   - `"sleep disturbance" AND "GAD-7" AND "cross-sectional"`

### ✓ Directions to try next:
- `sleep efficiency heart rate variability insomnia disorder`
- `autonomic dysregulation insomnia treatment outcome`
- `PSQI HRV insomnia severity index correlation`

---

## General Rules (learned from failed runs)

1. **Avoid nested quotes** in queries: `'"HRV AND "PHQ-9""'` → HTTP 500. Use plain boolean: `HRV PHQ-9 students`
2. **D2 queries work — do not overwrite them** to fix other links
3. **min_sample_size=50, min_year=2015** produced the best run; looser criteria degraded scores
4. **SEARCH_DEPTH=150 for C** is correct — C needs more papers to find relevant ones
5. **Top-10 citation pre-filter**: highly-cited papers score best; specific low-citation papers get dropped
6. **Plain text queries** often outperform complex boolean chains on OpenAlex

---

## Run History Summary (update after each run)

| Run      | Score   | Status        | What changed                                          |
| -------- | ------- | ------------- | ----------------------------------------------------- |
| baseline | 0.031325| best          | D1=1.52, D2=5.69, B=0.46 — A/C/D3=0                   |
| this run | 0.031327| improved      | A=0.838; B=1.130; C=1.837; D1=1.683; D2=1.916; D3=0.000 |
| this run | 0.022117| no_improvement| D1=0.448; D2=3.527; C=1.100; D3=0.000                |
| this run | 0.017813| no_improvement| D3=0.179; D2=2.998; (C and A did not improve)        |
| this run | 0.014162| no_improvement| D3=0.110; D2=2.425; (A, B, C, D1 did not improve)    |
| this run | 0.021289| no_improvement| A_hrv_cognition=0.000; C_cognition_grades=0.000; D3_focus_insomnia=0.000 |
| this run | 0.031503| no_improvement | A_hrv_cognition=1.648; B_sleep_cognition=0.492; C_cognition_grades=1.304; D1_focus_depression=1.348; D2_focus_anxiety=2.815; D3_focus_insomnia=1.377 |

---

With these updates, the agent can proceed with a clearer understanding of strategies that work and areas that require further exploration.