"""
agent.py — FIXED ORCHESTRATOR (do not modify)

Analog to the training loop orchestrator in karpathy/autoresearch.
One execution of this script = one experiment iteration.

Flow (mirrors autoresearch program.md loop exactly):
  1. Set up git branch for this session tag
  2. Read hypothesis.py + recent results.tsv
  3. Call Claude API → get modified hypothesis.py
  4. Commit modified hypothesis.py (tentative)
  5. Run searches via sources.py (5-min wall-clock budget)
  6. Compute evidence_score via evaluate_evidence()
  7. If improved → keep commit | If not → git reset hypothesis.py
  8. Append row to results.tsv
  9. Print grep-friendly structured output

GitHub Actions runs this script once per cron tick (every 10 min).
Git state (which hypothesis.py won) persists across runs via the repo.
"""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import time
import urllib.request
from datetime import datetime
from pathlib import Path

# ─── PATHS ────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent
HYPOTHESIS_FILE = ROOT / "hypothesis.py"
RESULTS_FILE = ROOT / "results.tsv"
PROGRAM_FILE = ROOT / "program.md"
MEMORY_FILE = ROOT / "agent_memory.md"
VAULT_CONTEXT_FILE = ROOT / "vault_context.md"
RUN_LOG = ROOT / "run.log"

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
AGENT_MODEL = "gpt-4o"  # main reasoning model for hypothesis modification


# ─── GIT HELPERS ──────────────────────────────────────────────────────────────

def git(cmd: str, check: bool = True) -> str:
    result = subprocess.run(
        f"git {cmd}", shell=True, capture_output=True, text=True, cwd=ROOT
    )
    if check and result.returncode != 0:
        raise RuntimeError(f"git {cmd} failed:\n{result.stderr}")
    return result.stdout.strip()


def current_branch() -> str:
    """Return the current git branch name."""
    return git("rev-parse --abbrev-ref HEAD")


def get_best_score() -> float:
    """Read the best evidence_score seen so far from results.tsv."""
    if not RESULTS_FILE.exists():
        return 0.0
    best = 0.0
    for line in RESULTS_FILE.read_text().splitlines()[1:]:  # skip header
        parts = line.split("\t")
        if len(parts) >= 2:
            try:
                score = float(parts[1])
                best = max(best, score)
            except ValueError:
                pass
    return best


def append_result(commit: str, score: float, total_papers: int,
                  status: str, description: str) -> None:
    """Append a row to results.tsv (not committed to git)."""
    header = "commit\tevidence_score\ttotal_papers\tstatus\tdescription\ttimestamp"
    if not RESULTS_FILE.exists() or RESULTS_FILE.stat().st_size == 0:
        RESULTS_FILE.write_text(header + "\n")
    timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    row = f"{commit}\t{score:.6f}\t{total_papers}\t{status}\t{description}\t{timestamp}"
    with RESULTS_FILE.open("a") as f:
        f.write(row + "\n")


# ─── LOAD HYPOTHESIS MODULE ───────────────────────────────────────────────────

def load_hypothesis():
    """Dynamically import hypothesis.py to get QUERIES, INCLUSION, SEARCH_DEPTH."""
    spec = importlib.util.spec_from_file_location("hypothesis", HYPOTHESIS_FILE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ─── CLAUDE API CALL (hypothesis modification) ────────────────────────────────

def _claude_api(messages: list, model: str = AGENT_MODEL, max_tokens: int = 4096) -> str:
    payload = json.dumps({
        "model": model,
        "max_tokens": max_tokens,
        "messages": messages,
    }).encode()
    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=payload,
        headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "content-type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        response = json.loads(r.read())
    return response["choices"][0]["message"]["content"]


def propose_hypothesis_modification(
    current_hypothesis: str,
    recent_results: str,
    program_instructions: str,
    best_score: float,
    agent_memory: str,
    vault_context: str = "",
) -> tuple[str, str]:
    """
    Ask GPT-4o to reason about the current state THEN propose a modified hypothesis.py.
    Returns (new_hypothesis_py_text, reasoning_text).

    Two-step approach (mirrors karpathy/autoresearch):
      Step 1 — Reasoning: analyse weakest links, consult memory, decide strategy
      Step 2 — Implementation: write the new hypothesis.py

    The reasoning is saved to agent_memory.md so future runs learn from it.
    """
    vault_section = f"""
---
LEARNZY HYPOTHESIS VAULT (your knowledge base — use this to build precise queries):
{vault_context[:8000]}
""" if vault_context else ""

    # Step 1: Ask for explicit chain-of-thought reasoning
    reasoning_prompt = f"""{program_instructions}
{vault_section}
---
AGENT MEMORY (what has been tried across ALL previous runs — read before reasoning):
{agent_memory}

---
CURRENT HYPOTHESIS.PY:
```python
{current_hypothesis}
```

RECENT RESULTS (most recent last):
```
{recent_results}
```

CURRENT BEST EVIDENCE SCORE: {best_score:.6f}

Before writing any code, reason through the following questions:
1. Which hypothesis links have the lowest scores right now? Why might they be low?
2. What strategies from AGENT MEMORY have already been tried and failed for those links?
3. What NEW search direction (not yet tried) do you propose, and why do you think it will work?
4. What is the single highest-leverage change to make this run?

Write your reasoning clearly — it will be saved and used by future runs to avoid repeated mistakes.
Format: <reasoning>your analysis here</reasoning>
"""
    reasoning_response = _claude_api([{"role": "user", "content": reasoning_prompt}], max_tokens=1024)

    # Extract reasoning block
    reasoning = ""
    if "<reasoning>" in reasoning_response and "</reasoning>" in reasoning_response:
        start = reasoning_response.index("<reasoning>") + len("<reasoning>")
        end = reasoning_response.index("</reasoning>")
        reasoning = reasoning_response[start:end].strip()
    else:
        reasoning = reasoning_response.strip()

    print(f"[agent] Reasoning: {reasoning[:300]}...", flush=True)

    # Step 2: Ask for the actual hypothesis.py implementation
    implementation_prompt = f"""{program_instructions}

---
AGENT MEMORY:
{agent_memory}

---
CURRENT HYPOTHESIS.PY:
```python
{current_hypothesis}
```

RECENT RESULTS:
```
{recent_results}
```

YOUR REASONING FROM STEP 1:
{reasoning}

Now implement the change. Return ONLY the complete new hypothesis.py file content — no explanation, no markdown fences, just the Python file.
"""
    new_hypothesis = _claude_api([{"role": "user", "content": implementation_prompt}], max_tokens=4096)
    return new_hypothesis, reasoning


def update_agent_memory(
    memory_content: str,
    evidence_score: float,
    best_score: float,
    status: str,
    papers_by_link: dict,
    current_hypothesis: str,
    reasoning: str = "",
) -> str:
    """Ask GPT-4o-mini to append a concise memory entry for this run."""
    import sources as _sources
    link_scores = {l: _sources.compute_link_score(p) for l, p in papers_by_link.items()}
    scores_str = " | ".join(f"{l}={s:.3f}" for l, s in link_scores.items())

    prompt = f"""You are updating an agent memory file that tracks which search strategies work or fail for each hypothesis link.

CURRENT MEMORY FILE:
{memory_content}

THIS RUN:
- status: {status}
- evidence_score: {evidence_score:.6f} (best so far: {best_score:.6f})
- link scores: {scores_str}

AGENT REASONING THIS RUN (why it made the changes it made):
{reasoning[:800] if reasoning else "(no reasoning recorded)"}

HYPOTHESIS.PY USED:
```python
{current_hypothesis[:1500]}
```

Task:
1. Append a row to the "Run History Summary" table
2. For any link whose score IMPROVED this run: add a "✓ What worked" bullet under that link's section
3. For any link whose score is still 0 or got worse: add a "✗ What failed" bullet with the specific queries that didn't work
4. If the reasoning revealed a new insight, add it to the relevant link section

Return the COMPLETE updated memory file. Keep it concise — prune outdated bullets if memory grows too long."""

    try:
        result = _claude_api(
            [{"role": "user", "content": prompt}],
            model="gpt-4o-mini",
            max_tokens=3000,
        )
        # Strip markdown fences if added
        if result.startswith("```"):
            lines = result.splitlines()
            result = "\n".join(l for l in lines if not l.startswith("```"))
        return result
    except Exception as e:
        print(f"[agent] Memory update failed: {e}", flush=True)
        return memory_content


# ─── MAIN EXPERIMENT LOOP ─────────────────────────────────────────────────────

def main() -> None:
    t_run_start = time.time()

    # 1. Determine session tag from date
    tag = datetime.utcnow().strftime("%Y%m%d")
    print(f"[agent] Starting experiment — tag={tag}", flush=True)

    # 2. Log current branch (no switching — stays on whatever Actions checked out)
    branch = current_branch()
    print(f"[agent] Branch: {branch}", flush=True)

    # 3. Read current state
    current_hypothesis = HYPOTHESIS_FILE.read_text()
    program_instructions = PROGRAM_FILE.read_text() if PROGRAM_FILE.exists() else ""
    agent_memory = MEMORY_FILE.read_text() if MEMORY_FILE.exists() else ""
    vault_context = VAULT_CONTEXT_FILE.read_text() if VAULT_CONTEXT_FILE.exists() else ""
    if vault_context:
        print(f"[agent] Vault context loaded: {len(vault_context.split())} words", flush=True)

    # Read last 20 rows of results.tsv for context
    recent_results = ""
    if RESULTS_FILE.exists():
        lines = RESULTS_FILE.read_text().splitlines()
        recent_results = "\n".join(lines[-21:])  # header + last 20

    best_score = get_best_score()
    print(f"[agent] Best score so far: {best_score:.6f}", flush=True)
    print(f"[agent] Memory size: {len(agent_memory)} chars", flush=True)

    # 4. Ask Claude to propose modification
    if not OPENAI_API_KEY:
        print("[agent] WARNING: No OPENAI_API_KEY — skipping hypothesis modification", flush=True)
        new_hypothesis = current_hypothesis
        description = "no-api-key (baseline)"
    else:
        print("[agent] Calling Claude to reason + propose hypothesis modification...", flush=True)
        try:
            new_hypothesis, reasoning = propose_hypothesis_modification(
                current_hypothesis, recent_results, program_instructions,
                best_score, agent_memory, vault_context
            )
            # Strip markdown fences if Claude added them
            if new_hypothesis.startswith("```"):
                lines = new_hypothesis.splitlines()
                new_hypothesis = "\n".join(
                    l for l in lines if not l.startswith("```")
                )
            description = "claude-proposed"
        except Exception as e:
            print(f"[agent] Claude API error: {e} — using current hypothesis", flush=True)
            new_hypothesis = current_hypothesis
            reasoning = f"API error: {e}"
            description = f"api-error: {e}"

    # 5. Write modified hypothesis.py and commit tentatively
    HYPOTHESIS_FILE.write_text(new_hypothesis)
    git('add hypothesis.py')
    commit_msg = f"experiment {tag}-{int(time.time())}"
    git(f'commit -m "{commit_msg}" --allow-empty')
    commit_hash = git("rev-parse --short HEAD")
    print(f"[agent] Committed: {commit_hash}", flush=True)

    # 6. Import the new hypothesis and run searches
    print("[agent] Running searches...", flush=True)
    t_search_start = time.time()

    # Import sources (fixed infra)
    sys.path.insert(0, str(ROOT))
    import sources
    importlib.reload(sources)

    hyp = load_hypothesis()

    try:
        papers_by_link = sources.run_searches(
            queries_by_link=hyp.QUERIES,
            inclusion=hyp.INCLUSION,
            search_depth=hyp.SEARCH_DEPTH,
        )
        evidence_score = sources.evaluate_evidence(papers_by_link)
        total_papers = sum(len(v) for v in papers_by_link.values())
        search_status = "ok"
    except Exception as e:
        print(f"[agent] Search failed: {e}", flush=True)
        papers_by_link = {l: [] for l in sources.LINK_WEIGHTS}
        evidence_score = 0.0
        total_papers = 0
        search_status = f"error: {e}"

    run_seconds = time.time() - t_run_start

    # 7. Keep or reset based on evidence_score
    if evidence_score > best_score:
        status = "improved"
        print(f"[agent] IMPROVED: {best_score:.6f} → {evidence_score:.6f} — keeping commit", flush=True)
        # In GitHub Actions, the push step in research.yml handles the push
    else:
        status = "no_improvement" if evidence_score > 0 else "failed"
        print(f"[agent] No improvement ({evidence_score:.6f} ≤ {best_score:.6f}) — resetting hypothesis.py", flush=True)
        # Reset hypothesis.py to previous state
        git(f"checkout HEAD~1 -- hypothesis.py", check=False)
        # Amend the commit to restore original hypothesis.py
        git("add hypothesis.py")
        git(f'commit --amend -m "{commit_msg} [reset]" --allow-empty')

    # 8. Append to results.tsv
    append_result(commit_hash, evidence_score, total_papers, status, description)

    # 9. Update agent_memory.md with this run's reasoning + outcomes
    if OPENAI_API_KEY and MEMORY_FILE.exists():
        print("[agent] Updating agent memory...", flush=True)
        updated_memory = update_agent_memory(
            memory_content=agent_memory,
            evidence_score=evidence_score,
            best_score=best_score,
            status=status,
            papers_by_link=papers_by_link,
            current_hypothesis=new_hypothesis,
            reasoning=reasoning,
        )
        MEMORY_FILE.write_text(updated_memory)
        git("add agent_memory.md")
        git(f'commit --amend -m "{commit_msg}{" [reset]" if status != "improved" else ""} [+memory]" --allow-empty')
        print(f"[agent] Memory updated ({len(updated_memory)} chars)", flush=True)

    # 10. Print structured summary (grep-friendly, analog to train.py summary block)
    sources.print_summary(
        evidence_score=evidence_score,
        papers_by_link=papers_by_link,
        best_score=best_score,
        run_seconds=run_seconds,
        status=status,
    )


if __name__ == "__main__":
    main()
