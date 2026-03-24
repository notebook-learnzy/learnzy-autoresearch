"""
build_vault_context.py — Obsidian Vault → vault_context.md

Reads all .md files from the hypothesis folder of the Obsidian vault,
resolves [[wikilinks]] one level deep to preserve concept connections,
and outputs vault_context.md for the agent to use as a knowledge base.

Run locally:  python build_vault_context.py
Output:       vault_context.md (committed to repo, read by agent.py each run)
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from collections import defaultdict

VAULT_DIR = Path("/Users/hg/Documents/Obsidian Vault/hypothesis")
OUTPUT_FILE = Path(__file__).parent / "vault_context.md"

# Which vault files map to each hypothesis link
LINK_FILE_MAP = {
    "A_hrv_cognition": [
        "hrv.md", "rmssd.md", "sdnn.md", "pNN50.md", "hf.md", "lf.md",
        "lf-hf ratio.md", "vagal.md", "neurovisceral.md", "ans.md",
        "sns.md", "pns.md", "cognitive.md", "executive-function.md",
        "working memory.md", "attention.md", "processing.md",
        "pfc.md", "anterior cingulate cortex.md", "HRV Readiness Score.md",
    ],
    "B_sleep_cognition": [
        "sleep.md", "sleep architecture.md", "rem.md", "n-rem.md",
        "stage 1 (light sleep).md", "stage 2 (light sleep).md",
        "stage 3 (slow wave, deep sleep).md", "spindles.md",
        "sharp-wave ripples.md", "hippocampus.md", "ltp.md",
        "consolidation.md", "sleep efficiency.md", "sleep latency.md",
        "waso.md", "sleep debt.md", "deprivation.md",
        "Sleep Recovery Score.md", "memory.md",
    ],
    "C_cognition_grades": [
        "academics.md", "gpa.md", "exam.md", "performance.md",
        "retention.md", "recall.md", "learning.md", "focus.md",
        "reasoning.md", "problem-solving.md", "decision-making.md",
        "students.md", "neet.md", "aspirants.md", "test.md",
        "maths.md", "physics.md", "organic chemistry.md",
    ],
    "D1_focus_depression": [
        "depression.md", "hpa.md", "cortisol.md", "stress.md",
        "hormones.md", "hypothalamus.md", "GR.md", "amygdala.md",
        "emotional regulation.md",
    ],
    "D2_focus_anxiety": [
        "anxiety.md", "stress.md", "amygdala.md", "emotional regulation.md",
        "hpa.md", "cortisol.md", "baroreflex.md", "heart-rate.md",
    ],
    "D3_focus_insomnia": [
        "sleep.md", "disorders.md", "nighmare.md", "sleep debt.md",
        "deprivation.md", "sleep latency.md", "waso.md", "quality.md",
        "duration.md", "sleep efficiency.md",
    ],
}


def read_file(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8").strip()
    except Exception:
        return ""


def resolve_wikilinks(content: str, vault_dir: Path) -> str:
    """Replace [[link]] with bold name + 1-line summary from linked file."""
    def replace_link(match):
        link_name = match.group(1).strip()
        linked_file = vault_dir / f"{link_name}.md"
        if linked_file.exists():
            linked_content = read_file(linked_file)
            summary_lines = [l for l in linked_content.splitlines() if l.strip()][:2]
            summary = " | ".join(summary_lines)[:180] if summary_lines else ""
            return f"**{link_name}**({summary})" if summary else f"**{link_name}**"
        return f"**{link_name}**"
    return re.sub(r"\[\[([^\]|#]+?)(?:\|[^\]]+)?\]\]", replace_link, content)


def build_connection_map(vault_dir: Path) -> dict[str, list[str]]:
    graph: dict[str, list[str]] = defaultdict(list)
    for md_file in vault_dir.glob("*.md"):
        content = read_file(md_file)
        links = re.findall(r"\[\[([^\]|#]+?)(?:\|[^\]]+)?\]\]", content)
        for link in links:
            graph[md_file.stem].append(link)
    return dict(graph)


def build_vault_context(vault_dir: Path) -> str:
    if not vault_dir.exists():
        return f"# Vault Context\n\nVault not found at: {vault_dir}\n"

    lines = [
        "# Learnzy Hypothesis Vault — Knowledge Context",
        "",
        "Auto-generated from Obsidian vault. [[wikilinks]] resolved one level deep to preserve connections.",
        "Use this to build precise search queries — every concept here maps to real peer-reviewed literature.",
        "",
        "**Focus Score = 0.6 × Sleep Recovery Score + 0.4 × HRV Readiness Score**",
        "Focus Score is Learnzy's proprietary term — search for its COMPONENTS, never the term itself.",
        "",
        "---",
        "",
    ]

    link_labels = {
        "A_hrv_cognition":     "LINK A — HRV → Cognition",
        "B_sleep_cognition":   "LINK B — Sleep → Cognition & Memory",
        "C_cognition_grades":  "LINK C — Cognition → Academic Grades",
        "D1_focus_depression": "LINK D1 — Focus Score → Depression",
        "D2_focus_anxiety":    "LINK D2 — Focus Score → Anxiety",
        "D3_focus_insomnia":   "LINK D3 — Focus Score → Insomnia",
    }

    seen = set()
    for link_key, label in link_labels.items():
        lines += [f"## {label}", ""]
        for fname in LINK_FILE_MAP.get(link_key, []):
            fpath = vault_dir / fname
            if not fpath.exists():
                continue
            content = read_file(fpath)
            if not content:
                continue
            seen.add(fpath.stem)
            resolved = resolve_wikilinks(content, vault_dir)
            lines += [f"### `{fpath.stem}`", resolved, ""]
        lines += ["---", ""]

    # Remaining files not yet included
    remaining = [(f.stem, read_file(f)) for f in sorted(vault_dir.glob("*.md"))
                 if f.stem not in seen and read_file(f)]
    if remaining:
        lines += ["## ADDITIONAL CONCEPTS", ""]
        for stem, content in remaining:
            resolved = resolve_wikilinks(content, vault_dir)
            lines += [f"### `{stem}`", resolved[:600], ""]
        lines += ["---", ""]

    # Connection map
    lines += ["## CONNECTION MAP", ""]
    graph = build_connection_map(vault_dir)
    for node, links in sorted(graph.items()):
        if links:
            lines.append(f"- **{node}** → {', '.join(sorted(set(links)))}")
    lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    vault_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else VAULT_DIR
    print(f"Reading vault: {vault_dir}")
    context = build_vault_context(vault_dir)
    OUTPUT_FILE.write_text(context, encoding="utf-8")
    print(f"Written: {OUTPUT_FILE} ({len(context.split())} words)")
