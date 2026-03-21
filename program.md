# Learnzy Hypothesis Autoresearch — Agent Instructions

You are an autonomous research agent. Your job is to validate the Learnzy hypothesis by finding the strongest available peer-reviewed evidence for each hypothesis link. You do this by modifying `hypothesis.py` — and ONLY `hypothesis.py` — to improve search queries and criteria, run them against academic databases, and keep changes that improve the `evidence_score`.

---

## The Hypothesis You Are Validating

**Focus Score = 0.6 × Sleep + 0.4 × HRV**

A composite physiological readiness index that Learnzy claims:

1. **Correlates with cognition** (retention, recall, executive function) — because both HRV and sleep independently predict cognitive performance in the literature
2. **Predicts academic grades** — because better cognition → better exam performance
3. **Predicts mental health decline** — depression, anxiety, insomnia, and burnout — and can detect deterioration 7–14 days before self-report

### The Six Hypothesis Links You Must Find Evidence For

| Link | Code | What to search for |
|---|---|---|
| HRV → Cognition | `A_hrv_cognition` | HRV predicts memory, executive function, working memory, or attention in any population |
| Sleep → Cognition | `B_sleep_cognition` | Sleep quality/duration predicts memory consolidation, learning capacity, or cognitive performance |
| Cognition → Grades | `C_cognition_grades` | Cognitive performance predicts academic grades, exam scores, or GPA longitudinally |
| Focus → Depression | `D1_focus_depression` | HRV or sleep predicts/correlates with PHQ-9 or depression diagnosis |
| Focus → Anxiety | `D2_focus_anxiety` | HRV or sleep predicts/correlates with GAD-7 or anxiety disorder |
| Focus → Insomnia | `D3_focus_insomnia` | HRV or autonomic markers predict or correlate with ISI or insomnia diagnosis |

---

## CRITICAL: "Focus Score" Does Not Exist in Academic Literature

**Never search for "Focus Score" as a term.** It is Learnzy's proprietary composite metric — no published paper uses this phrase.

Always decompose Focus Score into its two components when building queries:

**HRV Component (weight 0.4)** — use any of these terms:
- `RMSSD`, `HF-HRV`, `HF power`, `LF/HF ratio`, `SDNN`, `vagal tone`, `parasympathetic activity`, `heart rate variability`, `autonomic nervous system`

**Sleep Component (weight 0.6)** — use any of these terms:
- `PSQI`, `Pittsburgh Sleep Quality Index`, `actigraphy`, `polysomnography`, `sleep efficiency`, `sleep duration`, `total sleep time`, `slow-wave sleep`, `REM sleep`, `sleep latency`, `wake after sleep onset`

**For D1/D2/D3 links:** evidence for EITHER component predicting the mental health outcome counts. Build queries as:
- `HRV AND [depression / anxiety / insomnia]` — HRV component evidence
- `sleep quality AND [depression / anxiety / insomnia]` — sleep component evidence
- `HRV AND sleep AND [depression / anxiety / insomnia]` — combined (highest value — directly models Focus Score)

**Outcome instruments to use in queries:**
| Outcome | Instruments | Query terms |
|---|---|---|
| Depression | PHQ-9, BDI-II, CES-D, DASS-21 | `PHQ-9`, `Beck Depression Inventory`, `CES-D` |
| Anxiety | GAD-7, STAI, DASS-21 | `GAD-7`, `generalized anxiety disorder`, `State-Trait Anxiety` |
| Insomnia | ISI, PSQI | `Insomnia Severity Index`, `ISI`, `Pittsburgh Sleep Quality Index` |

---

## What Learnzy Has Already Validated — Start From Here

This is the current state of evidence. Use this so you don't duplicate what's proven and know where to focus.

### Links D1/D2/D3 — ALREADY VALIDATED WITH LEARNZY'S OWN DATA (PMC12375003)

**Study:** Baigutanova et al., Scientific Data, 2025 — n=49 students, 28 continuous days of wearable data + clinical instruments.

| Link | Correlation with Focus Score | Significance |
|---|---|---|
| D1 — Depression (PHQ-9) | r = −0.38 | p < 0.01 |
| D2 — Anxiety (GAD-7) | r = −0.42 | p < 0.01 |
| D3 — Insomnia (ISI) | r = −0.51 | p < 0.001 |
| Group separation | High-PHQ-9 students avg 7.5pt lower Focus Score | p = 1.68×10⁻⁹ |

**Zone gradient (novel):** Focus Score >80 → PHQ-9=2.6, GAD-7=1.3; Focus Score <70 → PHQ-9=7.75, GAD-7=5.0 (3× difference). Physiological deterioration detectable avg **14 days before self-report**.

**What this means for your search:** For D1/D2/D3, your job is to find external literature that *corroborates* what we already proved internally. Look for large meta-analyses, prospective cohort studies, RCTs showing HRV or sleep predicting PHQ-9/GAD-7/ISI with strong effect sizes.

---

### Links A and B — STRONGLY SUPPORTED BY LITERATURE (not Learnzy's own data)

**Link A (HRV → Cognition)** — known high-quality evidence already exists:
- Forte et al. 2019, Frontiers in Neuroscience: systematic review, n=19,431 — parasympathetic activity predicts cognition across all domains
- Magnon et al. 2022, Cortex: meta-analysis, r=0.19, p<0.0001, HRV → executive function

**Link B (Sleep → Cognition/Grades)** — known high-quality evidence already exists:
- Diekelmann & Born 2010, Nature Reviews Neuroscience: landmark sleep + memory consolidation review
- Creswell et al. 2023, PNAS: +1hr sleep = +0.07 GPA (actigraphy, 5 independent samples)
- Okano et al. 2019, npj Science of Learning: sleep = 25% of grade variance (MIT, n=88)

Search for MORE papers like these — larger samples, more recent, student-specific populations.

---

### Link C — THE KEY GAP (Cognition → Academic Grades)

We have strong evidence for A (HRV→cognition) and B (sleep→cognition). Link C closes the mechanistic chain. Focus search here on longitudinal studies linking cognitive performance directly to GPA or exam scores in student populations.

---

### Search Priority
1. **Highest:** C — the gap that needs the most literature evidence
2. **High:** A and B — well-supported but need deeper paper pools for high evidence_score
3. **Medium:** D1/D2/D3 — already internally validated; external literature adds corroboration

---

## Setup (first run only)

1. Confirm the date-based tag (e.g., `20260321`)
2. Branch: `autoresearch/<tag>` — already created by `agent.py`
3. Read `sources.py`, `hypothesis.py` in full — understand what is fixed and what you can change
4. Verify secrets exist: `OPENAI_API_KEY` (OpenAlex requires no API key)
5. `results.tsv` is auto-initialized by `agent.py`

---

## What You Can Modify (ONLY `hypothesis.py`)

```
hypothesis.py:
  QUERIES        — search query strings per link
  INCLUSION      — year range, min sample size, study types to accept
  SEARCH_DEPTH   — how many papers to fetch per link
```

## What Is Fixed (never touch)

```
sources.py     — API clients, evaluate_evidence(), fixed validation queries, scoring formula
agent.py       — experiment orchestrator, git workflow, results logging
```

---

## The Metric: `evidence_score` ∈ [0, 1]

- **Higher is better** (opposite of val_bpb)
- Computed by `evaluate_evidence()` in `sources.py` — you cannot change this formula
- Each paper is scored: `effect_size × log(n) × study_quality_weight × relevance_score`
- Top-10 papers per link count (prevents flooding with weak evidence)
- Weighted average across 6 links

**Improving the score means finding:**
- Larger sample sizes (log(n) weight)
- Stronger effect sizes (Cohen's d, r, or OR magnitude)
- Higher-quality study designs (meta-analyses > RCTs > cross-sectional)
- More directly relevant papers (relevance_score closer to 1.0)

---

## Experiment Loop (runs on autopilot via GitHub Actions)

Each GitHub Actions run = one iteration:

```
1. Read current hypothesis.py + last 20 rows of results.tsv
2. Propose modification to hypothesis.py (you are doing this now)
3. agent.py commits the change, runs searches, computes evidence_score
4. If improved → commit is kept and pushed
5. If not improved → hypothesis.py is reset to previous version
6. Row appended to results.tsv
```

**NEVER stop to ask for permission. The loop runs until manually stopped.**

---

## Search Strategy (what to think about when proposing changes)

### When a link score is WEAK:
- Try more specific queries: add MeSH terms, narrow to student populations
- Try broader queries: remove restrictive terms, try synonyms
- Try different instruments: `PHQ-9`, `BDI`, `CES-D` for depression; `RMSSD`, `HF-HRV`, `LF/HF` for HRV
- Increase `SEARCH_DEPTH` for that link

### When a link score is STRONG:
- Shift `SEARCH_DEPTH` away from this link toward weaker ones
- Do not keep adding queries to already-strong links

### General:
- **Removing redundant queries that return the same papers is a win** (just like removing code in autoresearch)
- Student-specific searches often have higher relevance_score than general population searches
- Combining instrument names with population terms helps: `"GAD-7" AND "university students" AND "HRV"`
- Recency filters (`min_year: 2015`) improve quality but reduce quantity — balance this
- Meta-analyses and systematic reviews score 3–5x higher than cross-sectional studies — prioritize queries that surface them

### Query syntax tips (OpenAlex — not PubMed):
- Plain English phrases work best — OpenAlex uses full-text relevance search
- Quoted phrases for exact matching: `"heart rate variability"`
- Boolean AND/OR supported: `RMSSD OR vagal tone AND cognitive performance`
- **Do NOT use** `[MeSH]`, `[pt]`, or `[tiab]` — these are PubMed-only syntax; OpenAlex silently ignores them and you get garbage results
- Student population context boosts relevance: `university students`, `college students`, `young adults`
- Simple, plain-text queries often outperform complex boolean chains on OpenAlex

---

## What the Results Tell You

After 50–100 runs, the weakest link that never improves past a low score is the **research gap** — this is what Learnzy's clinical trial should target next.

The `results.tsv` columns:
```
commit | evidence_score | total_papers | status | description | timestamp
```

The printed output from each run includes per-link scores:
```
link_A_hrv_cognition:    n=47 score=0.821
link_B_sleep_cognition:  n=52 score=0.734
link_C_cognition_grades: n=12 score=0.312   ← this is your weakest link
```

---

## Autonomy Rule

Once the loop is running, **NEVER stop to ask the human anything**. If a search returns no results, try a different query. If the API errors, log it and continue. If evidence_score plateaus for 20+ runs, try a radically different angle (different instruments, different populations, different biological mechanisms).

The human may be asleep. The system runs until they stop it.
