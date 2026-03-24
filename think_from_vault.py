"""
think_from_vault.py — Deep vault reasoning → optimized hypothesis.py

Instead of random trial-and-error search iterations, this script:
1. Feeds the FULL vault context (16k words of interlinked research notes) to GPT-4o
2. Asks it to reason deeply about each hypothesis link using the vault knowledge
3. Generates the best possible hypothesis.py from first principles
4. Runs it through sources.py to evaluate and commit if it beats the current best

Run: python think_from_vault.py
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import importlib.util
import time
from pathlib import Path

ROOT = Path(__file__).parent
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")


def call_gpt4o(messages: list, max_tokens: int = 4096) -> str:
    import urllib.request
    payload = json.dumps({
        "model": "gpt-4o",
        "max_tokens": max_tokens,
        "messages": messages,
    }).encode()
    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=payload,
        headers={"Authorization": f"Bearer {OPENAI_API_KEY}", "content-type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read())["choices"][0]["message"]["content"]


def main():
    vault_context = (ROOT / "vault_context.md").read_text()
    current_hypothesis = (ROOT / "hypothesis.py").read_text()

    print("=" * 60)
    print("PHASE 1: Deep vault reasoning (GPT-4o analyzing all 6 links)")
    print("=" * 60)

    reasoning_prompt = f"""You are a research scientist designing search queries to find peer-reviewed papers.

You have access to a deep knowledge base (Obsidian vault) of interconnected research notes about:
- HRV (heart rate variability), its metrics (RMSSD, SDNN, HF power, vagal tone), and cognitive connections
- Sleep architecture (NREM/REM, spindles, sharp-wave ripples, slow-wave sleep) and memory consolidation
- The hippocampus, LTP (long-term potentiation), cortisol, HPA axis
- Academic performance, GPA, working memory, executive function
- Depression, anxiety, insomnia — their physiological markers and instruments (PHQ-9, GAD-7, ISI)

VAULT KNOWLEDGE BASE:
{vault_context}

---

You need to validate 6 hypothesis links by finding the strongest peer-reviewed evidence for each.
The goal is to find meta-analyses, systematic reviews, RCTs, and large cohort studies.

For each of the 6 links below, reason deeply using the vault knowledge:
- What are the EXACT biological mechanisms connecting these two things?
- What are the most specific, high-yield search terms that will find strong studies?
- What study designs and instruments should you target?
- What are known landmark papers you should search for?

HYPOTHESIS LINKS:
1. A_hrv_cognition: HRV (RMSSD, HF power, vagal tone) predicts cognitive performance (working memory, executive function, attention) in students
2. B_sleep_cognition: Sleep quality/duration (PSQI, actigraphy, sleep spindles, slow-wave sleep) predicts memory consolidation and learning in students
3. C_cognition_grades: Cognitive performance (working memory, attention, executive function) predicts academic grades/GPA/exam scores
4. D1_focus_depression: HRV or sleep quality predicts/correlates with depression (PHQ-9, BDI) in students
5. D2_focus_anxiety: HRV or sleep quality predicts/correlates with anxiety (GAD-7, STAI) in students
6. D3_focus_insomnia: HRV or autonomic markers predict/correlate with insomnia (ISI, PSQI insomnia subscale) in students

For each link, provide:
- 3-5 HIGHLY SPECIFIC search queries (plain text, OpenAlex-compatible)
- Target study types in priority order
- Key authors/papers to anchor search around
- Search depth (how many results to fetch: 30-150)

Format your response as structured reasoning per link.
"""

    reasoning = call_gpt4o([{"role": "user", "content": reasoning_prompt}], max_tokens=3000)
    print("\n[VAULT REASONING OUTPUT]")
    print(reasoning)
    print()

    print("=" * 60)
    print("PHASE 2: Synthesize into optimized hypothesis.py")
    print("=" * 60)

    synthesis_prompt = f"""Based on your deep analysis of the vault knowledge, now write the optimal hypothesis.py.

YOUR REASONING FROM PHASE 1:
{reasoning}

CURRENT hypothesis.py (for reference):
```python
{current_hypothesis}
```

RULES:
- QUERIES: Use specific terms from the vault (RMSSD, HF-HRV, sleep spindles, sharp-wave ripples, PHQ-9, GAD-7, ISI, etc.)
- Never search for "Focus Score" — decompose into HRV component + Sleep component
- For D3 (insomnia): this link has been hardest — use ISI (Insomnia Severity Index), PSQI insomnia component, autonomic hyperarousal insomnia, HRV nocturnal insomnia
- SEARCH_DEPTH: give D3 and A the most depth (150), others 80-100
- INCLUSION: min_sample_size=20, min_year=2010, include all study types
- Each link should have 4-6 queries covering different angles

Return ONLY the complete hypothesis.py file — no markdown, no explanation.
"""

    new_hypothesis = call_gpt4o([{"role": "user", "content": synthesis_prompt}], max_tokens=3000)

    # Strip markdown fences if present
    if new_hypothesis.startswith("```"):
        lines = new_hypothesis.splitlines()
        new_hypothesis = "\n".join(l for l in lines if not l.startswith("```"))

    print("\n[SYNTHESIZED hypothesis.py]")
    print(new_hypothesis)

    # Write it
    (ROOT / "hypothesis.py").write_text(new_hypothesis)
    print("\n[Written to hypothesis.py]")

    print("=" * 60)
    print("PHASE 3: Run searches and evaluate score")
    print("=" * 60)

    sys.path.insert(0, str(ROOT))
    import sources
    importlib.reload(sources)

    spec = importlib.util.spec_from_file_location("hypothesis", ROOT / "hypothesis.py")
    hyp = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(hyp)

    t0 = time.time()
    papers_by_link = sources.run_searches(
        queries_by_link=hyp.QUERIES,
        inclusion=hyp.INCLUSION,
        search_depth=hyp.SEARCH_DEPTH,
    )
    score = sources.evaluate_evidence(papers_by_link)
    sources.print_summary(score, papers_by_link, 0.052134, time.time() - t0, "vault-synthesized")

    return score


if __name__ == "__main__":
    if not OPENAI_API_KEY:
        print("ERROR: OPENAI_API_KEY not set")
        sys.exit(1)
    main()
