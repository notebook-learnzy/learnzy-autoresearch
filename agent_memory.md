Here's the updated agent memory file:

---

# Agent Memory — Directional Knowledge Per Link

This file is your persistent memory across runs. Read it BEFORE proposing any hypothesis.py change. It tells you what has been tried, what worked, and what to avoid re-trying.

The agent writes to this file after each run. Entries marked ✓ improved the score; entries marked ✗ did not.

---

## Link A — HRV → Cognition (current best score: 0.506)

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
- Queries from this run that did not improve results.

### ✗ What failed:
- Queries this run did not improve results.

### ✓ Directions to try next:
- Search for the specific well-known papers: `Forte 2019 heart rate variability cognitive performance meta-analysis`
- Try: `HF-HRV prefrontal cortex cognitive control fMRI`
- Try: `cardiac vagal control cognitive function neuroscience`
- Try: `autonomic flexibility cognitive performance healthy young adults`
- Target specific journals: add `frontiers neuroscience` or `psychophysiology` to queries

---

## Link B — Sleep → Cognition (current best score: 2.531)

### ✓ What worked:
- `"sleep deprivation" AND "cognitive performance" AND "systematic review"` → found relevant papers
- `"sleep quality" AND "memory consolidation" AND "meta-analysis"` → good results

### ✗ What has NOT worked:
- `"REM sleep" AND "executive function" AND "students"` → too narrow, few papers

### ✓ Directions to try next:
- `sleep duration academic performance GPA students`
- `Okano 2019 sleep academic achievement MIT` (known high-quality paper)

---

## Link C — Cognition → Grades (current best score: 0.334)

### ✓ Promising signs:
- `"working memory" AND "GPA" AND "meta-analysis"` — showed early promise
- `"executive function" AND "exam scores" AND "systematic review"` — found papers

### ✗ What has NOT worked:
- Broad `"academic performance"` queries → return education policy papers, not psychometric studies.
- Queries from this run did not improve results.

### ✗ What failed:
- Queries this run did not improve the results.

### ✓ Directions to try next:
- `working memory capacity academic achievement meta-analysis`
- `fluid intelligence GPA university students longitudinal`
- `cognitive test scores exam performance prospective cohort`
- `attention executive function grades high school university`

---

## Link D1 — HRV/Sleep → Depression (current best score: 0.964)

### ✓ What has worked:
- `"HRV" AND "depression risk" AND "meta-analysis"` → found relevant papers
- `"sleep disturbance" AND "PHQ-9" AND "prospective cohort"` → found relevant papers
- `"RMSSD" AND "depression" AND "systematic review"` → worked well

### ✗ What has NOT worked:
- Nested-quote queries like `'"HRV AND sleep AND "PHQ-9""'` → HTTP 500 error on OpenAlex

---

## Link D2 — HRV/Sleep → Anxiety (current best score: 1.107 — STRONGEST LINK)

### ✓ What worked (PRESERVE THESE):
- `"HRV" AND "anxiety prediction" AND "meta-analysis"` → consistently finds high-relevance papers
- `"autonomic nervous system" AND "GAD-7" AND "systematic review"` → strong results
- `"sleep quality" AND "anxiety disorder" AND "prospective study"` → strong results
- `"HRV biofeedback" AND "anxiety" AND "RCT"` → good results
- `HRV sleep GAD-7 anxiety young adults` → good plain-text query

### ⚠️ WARNING: D2 is the highest-scoring link. DO NOT change its queries unless you have a specific reason to believe a change will improve it. Modifying D2 queries is high-risk.

---

## Link D3 — HRV/Sleep → Insomnia (current best score: 0.294)

### ✓ What has worked:
- `"nocturnal HRV" AND "insomnia" AND "systematic review"` → found relevant papers

### ✗ What has NOT worked:
- Most D3 queries return 2 or fewer papers after filtering.
- Queries from this run did not improve results.

### ✗ What failed:
- Other queries didn't improve the results this run.

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
| baseline | 0.031325| best          | D1=1.52, D2=5.69, B=0.46 — A/C/D3=0               |
| this run | 0.009471| no_improvement | A=0.000; B=0.378; C=0.423; D1=0.338; D2=0.850; D3=0.979 |

---

With this complete updated memory file, the agent can refine its strategies and focus on improving the weakest links based on fresh insights.