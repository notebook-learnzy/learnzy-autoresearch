"""
sources.py — FIXED INFRASTRUCTURE (do not modify)

Analog to prepare.py in karpathy/autoresearch.
This file contains:
  - OpenAlex API client (single source, free, 250M+ works, no key needed)
  - The Paper dataclass
  - Fixed validation query set (analog to pinned val shard)
  - evaluate_evidence() — the ground-truth metric (analog to evaluate_bpb())

The agent (hypothesis.py) cannot and must not modify this file.
"""

from __future__ import annotations

import json
import math
import os
import time
from dataclasses import dataclass, asdict
from typing import Dict, List
import urllib.parse
import urllib.request
import urllib.error

# ─── TIME BUDGET (analog to TIME_BUDGET = 300 in prepare.py) ─────────────────
TIME_BUDGET = 300  # seconds of wall-clock search time per experiment run

# ─── OPENALEX BASE URL ────────────────────────────────────────────────────────
_OPENALEX_BASE = "https://api.openalex.org/works"
# Polite pool: add mailto to get priority rate limits (no key needed)
_OPENALEX_MAILTO = "research@learnzy.in"

# ─── FIXED VALIDATION QUERY SET (analog to pinned shard_06542) ───────────────
# These 6 queries ALWAYS run, regardless of what hypothesis.py specifies.
# The agent cannot remove or modify them. This prevents gaming the metric.
FIXED_VALIDATION_QUERIES: Dict[str, str] = {
    "A_hrv_cognition":     "heart rate variability cognitive performance",
    "B_sleep_cognition":   "sleep quality memory consolidation students",
    "C_cognition_grades":  "academic performance cognitive function longitudinal",
    "D1_focus_depression": "heart rate variability depression biomarker",
    "D2_focus_anxiety":    "heart rate variability anxiety disorder",
    "D3_focus_insomnia":   "sleep insomnia autonomic nervous system",
}

# ─── LINK WEIGHTS (fixed — reflects Focus Score composition + hypothesis) ─────
LINK_WEIGHTS: Dict[str, float] = {
    "A_hrv_cognition":     0.20,  # HRV (40% of Focus Score) → cognition
    "B_sleep_cognition":   0.20,  # Sleep (60% of Focus Score) → cognition
    "C_cognition_grades":  0.20,  # Cognition → academic grades
    "D1_focus_depression": 0.15,  # Focus Score → depression
    "D2_focus_anxiety":    0.15,  # Focus Score → anxiety
    "D3_focus_insomnia":   0.10,  # Focus Score → insomnia
}

# ─── STUDY TYPE QUALITY WEIGHTS ───────────────────────────────────────────────
STUDY_WEIGHTS: Dict[str, float] = {
    "meta_analysis":      5.0,
    "systematic_review":  4.5,
    "rct":                4.0,
    "prospective_cohort": 3.0,
    "cross_sectional":    1.5,
    "case_control":       2.0,
    "case_study":         0.5,
}

TOP_K_PAPERS = 10  # only top-10 papers per link count (prevents flooding)

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")


# ─── PAPER DATACLASS ──────────────────────────────────────────────────────────

@dataclass
class Paper:
    pmid: str
    title: str
    abstract: str
    year: int
    n: int                  # sample size (LLM-extracted)
    effect_size: float      # Cohen's d, r, or OR (LLM-extracted)
    study_type: str         # one of STUDY_WEIGHTS keys
    relevance_score: float  # 0.0–1.0, LLM-judged against hypothesis link
    journal: str
    doi: str = ""
    cited_by_count: int = 0

    def to_dict(self) -> dict:
        return asdict(self)


# ─── HTTP HELPER ──────────────────────────────────────────────────────────────

def _http_get(url: str, retries: int = 4) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "learnzy-autoresearch/1.0"})
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(2 ** attempt)
            else:
                raise
        except Exception:
            time.sleep(2 ** attempt)
    raise RuntimeError(f"Failed to fetch after {retries} attempts: {url[:80]}")


# ─── ABSTRACT RECONSTRUCTION ──────────────────────────────────────────────────

def _reconstruct_abstract(inverted_index: dict | None) -> str:
    """
    OpenAlex stores abstracts as an inverted index: {word: [position, ...], ...}
    This function reconstructs the readable text from that structure.
    """
    if not inverted_index:
        return ""
    try:
        length = max(pos for positions in inverted_index.values() for pos in positions) + 1
        words = [""] * length
        for word, positions in inverted_index.items():
            for pos in positions:
                if 0 <= pos < length:
                    words[pos] = word
        return " ".join(w for w in words if w)
    except Exception:
        return ""


# ─── OPENALEX SEARCH CLIENT ───────────────────────────────────────────────────

def search_openalex(query: str, max_results: int = 50, min_year: int = 2009) -> List[Paper]:
    """
    Search OpenAlex works endpoint.

    OpenAlex is free, no API key required. 250M+ works covering all major publishers
    (Nature, PubMed/MEDLINE, Elsevier, Wiley, Springer, etc.).
    Rate limit: 10 req/s, 100K calls/day — we sleep 0.1s between calls.

    Results sorted by OpenAlex relevance (BM25 on query text) — ensures query-specific
    papers surface first rather than generically high-cited papers in the domain.
    """
    params = {
        "search": query,
        "per-page": min(max_results, 200),
        "filter": f"publication_year:>{min_year},type:article",
        "select": "id,title,abstract_inverted_index,publication_year,doi,"
                  "primary_location,cited_by_count,ids",
        "mailto": _OPENALEX_MAILTO,
    }
    url = f"{_OPENALEX_BASE}?{urllib.parse.urlencode(params)}"

    try:
        data = json.loads(_http_get(url))
    except Exception as e:
        print(f"[sources] OpenAlex error for query '{query[:50]}': {e}", flush=True)
        return []

    papers = []
    for item in data.get("results", []):
        title = item.get("title") or ""
        abstract = _reconstruct_abstract(item.get("abstract_inverted_index"))
        year = item.get("publication_year") or 0
        doi = item.get("doi") or ""
        cited_by = item.get("cited_by_count") or 0

        # Journal name
        primary_loc = item.get("primary_location") or {}
        source = primary_loc.get("source") or {}
        journal = source.get("display_name") or ""

        # Use OpenAlex ID as unique key (some papers have no PMID)
        oa_id = item.get("id") or doi or title[:40]
        # Also try to get PubMed ID if available
        ids = item.get("ids") or {}
        pmid = ids.get("pmid") or oa_id

        if not title:
            continue

        # Use cited_by_count as n proxy (better than 0 — prevents filter-out if extraction fails)
        # LLM extraction will replace this with the actual sample size when available.
        # Floor of 20: ensures papers without explicit n in abstract pass default min_sample_size=20
        n_proxy = max(cited_by // 5, 20)
        papers.append(Paper(
            pmid=pmid,
            title=title,
            abstract=abstract,
            year=year,
            n=n_proxy,
            effect_size=0.0,
            study_type="cross_sectional",
            relevance_score=0.0,
            journal=journal,
            doi=doi,
            cited_by_count=cited_by,
        ))

    print(f"[sources]   OpenAlex returned {len(papers)} papers for query '{query[:60]}'", flush=True)
    return papers


# ─── LLM EXTRACTION (Claude extracts n, effect_size, study_type, relevance) ──

def _claude_extract_paper_stats(papers: List[Paper], link_name: str) -> List[Paper]:
    """
    Use GPT-4o-mini to extract n, effect_size, study_type, and relevance_score
    from paper abstracts for a given hypothesis link.

    Analog of the tokenizer processing raw text into model-ready tensors.
    Uses gpt-4o-mini for cost efficiency (~$0.001 per batch of 20 papers).
    """
    if not OPENAI_API_KEY or not papers:
        return papers

    # Rich link descriptions with vault knowledge — gives GPT-4o-mini the domain
    # context it needs to accurately score relevance (0.2 → 0.7+ improvement expected)
    LINK_DESCRIPTIONS = {
        "A_hrv_cognition": (
            "HRV (heart rate variability) predicts cognitive performance, memory, attention, or executive function. "
            "Key mechanisms: the neurovisceral integration model links the same brain network (PFC, anterior cingulate, insula, amygdala) "
            "that controls both HRV and cognition. High RMSSD/HF-HRV = strong vagal tone = better PFC function = better working memory, "
            "attention control, cognitive flexibility. Expected effect sizes: 0.3–0.5 SD improvement in high vs low HRV individuals. "
            "Target instruments: RMSSD, SDNN, HF power, LF/HF ratio, vagal tone. Target outcomes: working memory capacity, "
            "executive function, attention, decision-making, processing speed. Population: students, young adults, healthy."
        ),
        "B_sleep_cognition": (
            "Sleep quality or duration predicts memory consolidation, learning, or cognitive performance in students. "
            "Key mechanisms: sleep spindles (stage 2 NREM) coordinate hippocampus-neocortex dialogue for memory consolidation; "
            "slow-wave sleep orchestrates sharp-wave ripples; REM sleep integrates new with existing knowledge. "
            "Sleep deprivation causes 20-40% reduction in working memory, 40% reduction in memory encoding, "
            "0.07 GPA decrease per hour of sleep lost. Sleep quality accounts for 25% of academic performance variance. "
            "Target instruments: PSQI (Pittsburgh Sleep Quality Index), actigraphy, polysomnography, ISI, sleep diary. "
            "Target outcomes: GPA, exam scores, memory recall, cognitive test performance."
        ),
        "C_cognition_grades": (
            "Cognitive performance (working memory, attention, executive function) predicts academic grades, GPA, or exam scores. "
            "Key findings: stress-induced working memory impairment directly predicts lower academic achievement (each SD increase in stress "
            "correlates with 0.3–0.5 SD decrease in academic performance). Students in high-stress conditions score 18% lower on tests "
            "and recall 48% fewer items. Working memory capacity and academic achievement: strong meta-analytic evidence. "
            "High cognitive load subjects most affected: mathematics, physics, organic chemistry. "
            "Target measures: working memory tests, n-back tasks, executive function batteries, GPA, exam scores, academic achievement."
        ),
        "D1_focus_depression": (
            "HRV or sleep quality predicts or correlates with depression symptoms. "
            "Mechanisms: HPA axis dysregulation, elevated cortisol, reduced vagal tone → depression risk. "
            "Low HRV (especially reduced RMSSD) is a biomarker for depression. Sleep deprivation activates stress responses, "
            "keeps cortisol elevated, causes amygdala hyperactivity (37% increase) and reduced PFC control → depression. "
            "Target instruments for depression: PHQ-9, BDI-II, CES-D, Hamilton Depression Rating Scale, clinical diagnosis. "
            "Target HRV measures: RMSSD, HF power, vagal tone. Target sleep measures: PSQI, actigraphy, sleep efficiency."
        ),
        "D2_focus_anxiety": (
            "HRV or sleep quality predicts or correlates with anxiety symptoms. "
            "Mechanisms: low vagal tone (low HRV) = reduced ability to regulate emotional responses = heightened anxiety. "
            "Anticipatory stress drops HRV before stressful tasks, reflecting anxiety. Chronic stress causes persistently low baseline HRV. "
            "Sleep deprivation causes amygdala hyperactivity and reduced PFC control → more anxiety. "
            "Target instruments for anxiety: GAD-7, STAI (State-Trait Anxiety Inventory), BAI, HAM-A. "
            "Target HRV measures: RMSSD, HF power, LF/HF ratio, vagal tone. Target sleep: PSQI, sleep efficiency."
        ),
        "D3_focus_insomnia": (
            "HRV or autonomic nervous system markers predict or correlate with insomnia severity. "
            "Mechanisms: insomnia involves autonomic hyperarousal — elevated SNS activity, reduced parasympathetic (vagal) tone, "
            "increased LF/HF ratio, reduced RMSSD at night. HPA axis dysregulation raises cortisol → prevents sleep initiation. "
            "Sleep architecture changes: reduced slow-wave sleep, shortened REM, increased light sleep stage 1. "
            "Target instruments for insomnia: ISI (Insomnia Severity Index), PSQI, polysomnography, actigraphy, sleep diary. "
            "Target HRV measures: nocturnal RMSSD, HF power, LF/HF ratio, heart rate during sleep."
        ),
    }

    link_desc = LINK_DESCRIPTIONS.get(link_name, link_name)

    abstracts_text = ""
    for i, p in enumerate(papers[:20]):  # batch max 20
        abstracts_text += (
            f"\n[{i}] Title: {p.title}\n"
            f"Abstract: {p.abstract[:600] if p.abstract else '(no abstract)'}\n"
            f"Citations: {p.cited_by_count}\n"
        )

    prompt = (
        f"You are a research analyst scoring papers for evidence strength.\n\n"
        f"HYPOTHESIS LINK: {link_desc}\n\n"
        f"RELEVANCE SCORING GUIDE:\n"
        f"  1.0 = paper directly tests this exact hypothesis (e.g. measures HRV AND cognitive performance together)\n"
        f"  0.8 = paper strongly supports it (e.g. measures one component with outcome, student population)\n"
        f"  0.6 = paper provides good indirect evidence (e.g. adult population, related mechanism)\n"
        f"  0.4 = paper partially relevant (e.g. one variable studied in isolation)\n"
        f"  0.2 = paper tangentially related\n"
        f"  0.0 = paper is irrelevant to this link\n\n"
        f"Be GENEROUS: if a paper studies HRV AND any cognitive/mental health outcome, score it 0.6+.\n\n"
        f"For each paper extract:\n"
        f"1. n: sample size (integer, 0 if not stated)\n"
        f"2. effect_size: Cohen's d, Pearson r, or odds ratio magnitude (0.0 if not stated)\n"
        f"3. study_type: one of [meta_analysis, systematic_review, rct, prospective_cohort, cross_sectional, case_control, case_study]\n"
        f"4. relevance_score: float 0.0-1.0 using the guide above\n\n"
        f"Return ONLY a JSON array with EXACTLY {len(papers[:20])} objects:\n"
        f'[{{"n": int, "effect_size": float, "study_type": str, "relevance_score": float}}, ...]\n\n'
        f"Papers:\n{abstracts_text}"
    )

    payload = json.dumps({
        "model": "gpt-4o-mini",
        "max_tokens": 1024,
        "messages": [{"role": "user", "content": prompt}],
    }).encode()

    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=payload,
        headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "content-type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            response = json.loads(r.read())
        text = response["choices"][0]["message"]["content"].strip()
        start = text.find("[")
        end = text.rfind("]") + 1
        if start >= 0 and end > start:
            stats = json.loads(text[start:end])
            for i, s in enumerate(stats):
                if i < len(papers):
                    extracted_n = int(s.get("n") or 0)
                    # Only override proxy if LLM found an actual n
                    if extracted_n > 0:
                        papers[i].n = extracted_n
                    papers[i].effect_size = float(s.get("effect_size") or 0.0)
                    papers[i].study_type = s.get("study_type", "cross_sectional")
                    papers[i].relevance_score = float(s.get("relevance_score") or 0.0)
            print(f"[sources]   Extraction OK for {link_name}: {len(stats)} records", flush=True)
        else:
            print(f"[sources]   Extraction parse failed for {link_name} — no JSON array found", flush=True)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")[:300]
        print(f"[sources] OpenAI API HTTP {e.code} for {link_name}: {body}", flush=True)
    except Exception as e:
        print(f"[sources] Extraction error for {link_name}: {type(e).__name__}: {e}", flush=True)

    return papers


# ─── SCORING FUNCTIONS (FIXED — agent cannot change these) ───────────────────

def score_paper(paper: Paper) -> float:
    """Score a single paper. Analog to token-level cross-entropy in evaluate_bpb."""
    quality = STUDY_WEIGHTS.get(paper.study_type, 1.0)
    sample_wt = math.log(max(paper.n, 10) + 1)
    effect = min(abs(paper.effect_size), 1.0)   # cap at 1.0 — no outlier gaming
    # Most abstracts don't state an explicit effect size (Cohen's d / r).
    # When LLM returns 0.0, use a conservative study-type default so relevant
    # papers aren't silently zeroed out of the score.
    if effect == 0.0:
        _EFFECT_FALLBACKS = {
            "meta_analysis": 0.50, "systematic_review": 0.40, "rct": 0.35,
            "prospective_cohort": 0.25, "cross_sectional": 0.15,
            "case_control": 0.20, "case_study": 0.10,
        }
        effect = _EFFECT_FALLBACKS.get(paper.study_type, 0.15)
    relevance = max(0.0, min(paper.relevance_score, 1.0))
    return effect * sample_wt * quality * relevance


def compute_link_score(papers: List[Paper]) -> float:
    """Score a single hypothesis link from its papers. Top-K prevents flooding."""
    if not papers:
        return 0.0
    scores = sorted([score_paper(p) for p in papers], reverse=True)
    top_k = scores[:TOP_K_PAPERS]
    return sum(top_k) / len(top_k)


def evaluate_evidence(papers_by_link: Dict[str, List[Paper]]) -> float:
    """
    THE FIXED METRIC — analog to evaluate_bpb() in prepare.py.

    Takes a dict of {link_name: [Paper, ...]} and returns evidence_score ∈ [0, 1].
    Higher is better (opposite direction to val_bpb where lower is better).

    The agent CANNOT modify this function.
    """
    link_scores: Dict[str, float] = {
        link: compute_link_score(papers)
        for link, papers in papers_by_link.items()
    }
    total = sum(LINK_WEIGHTS.get(l, 0) * link_scores.get(l, 0.0) for l in LINK_WEIGHTS)
    # Normalize against theoretical ceiling.
    # compute_link_score returns an AVERAGE (not sum), so max link_score =
    # max_paper_score = 1.0 * log(10001) * 5.0 * 1.0. Do NOT multiply by TOP_K_PAPERS.
    max_possible = sum(LINK_WEIGHTS.values()) * (5.0 * math.log(10001) * 1.0)
    normalized = total / max_possible if max_possible > 0 else 0.0
    return round(min(normalized, 1.0), 6)


# ─── MAIN SEARCH RUNNER ───────────────────────────────────────────────────────

def run_searches(
    queries_by_link: Dict[str, List[str]],
    inclusion: dict,
    search_depth: Dict[str, int],
) -> Dict[str, List[Paper]]:
    """
    Run all searches (fixed validation + hypothesis.py queries) within TIME_BUDGET.
    Uses only OpenAlex. Returns papers_by_link after LLM stat extraction.
    """
    t_start = time.time()
    min_year = inclusion.get("min_year", 2009)
    min_n_inclusive = inclusion.get("min_sample_size", 0)
    allowed_study_types = set(inclusion.get("study_types", list(STUDY_WEIGHTS.keys())))

    papers_by_link: Dict[str, List[Paper]] = {link: [] for link in LINK_WEIGHTS}
    seen_ids: set = set()

    def _add_papers(link: str, new_papers: List[Paper]) -> None:
        for p in new_papers:
            uid = p.doi or p.pmid or p.title[:60]
            if uid in seen_ids:
                continue
            seen_ids.add(uid)
            papers_by_link[link].append(p)

    # 1. Always run FIXED validation queries first (analog to always eval on val shard)
    print("[sources] Running fixed validation queries...", flush=True)
    for link, query in FIXED_VALIDATION_QUERIES.items():
        if time.time() - t_start > TIME_BUDGET:
            break
        results = search_openalex(query, max_results=30, min_year=min_year)
        _add_papers(link, results)
        time.sleep(0.15)  # OpenAlex polite pool: stay well under 10 req/s

    # 2. Run hypothesis.py queries for each link
    print("[sources] Running hypothesis queries...", flush=True)
    for link, queries in queries_by_link.items():
        if link not in LINK_WEIGHTS:
            continue
        depth = search_depth.get(link, 30)
        per_query = max(10, depth // max(len(queries), 1))
        for query in queries:
            if time.time() - t_start > TIME_BUDGET:
                print(f"[sources] TIME_BUDGET hit at {time.time()-t_start:.0f}s", flush=True)
                break
            results = search_openalex(query, max_results=per_query, min_year=min_year)
            _add_papers(link, results)
            time.sleep(0.15)

    # 3. Pre-filter: drop no-abstract papers, then keep top 10 by citation count.
    # Papers without abstracts return empty relevance from LLM → score=0, wasted API call.
    # Keep OpenAlex relevance order (BM25) — do NOT re-sort by citation count here,
    # which would override query relevance ranking with domain-wide popularity
    # (e.g., cardiac HRV papers outranking cognitive HRV papers).
    # 10 papers = 1 LLM batch per link → eliminates token truncation risk entirely.
    _PRE_FILTER_N = 25
    for link in LINK_WEIGHTS:
        has_abstract = [p for p in papers_by_link[link] if p.abstract and len(p.abstract) > 200]
        no_abstract_count = len(papers_by_link[link]) - len(has_abstract)
        if no_abstract_count:
            print(f"[sources]   Dropped {no_abstract_count} no-abstract papers for {link}", flush=True)
        papers_by_link[link] = has_abstract[:_PRE_FILTER_N]

    raw_counts = {link: len(papers_by_link[link]) for link in LINK_WEIGHTS}
    print(f"[sources] Paper counts after pre-filter (top {_PRE_FILTER_N} by citations): {raw_counts}", flush=True)
    print("[sources] Extracting stats via OpenAI...", flush=True)
    for link in LINK_WEIGHTS:
        papers = papers_by_link[link]
        if not papers:
            continue
        enriched = []
        for i in range(0, len(papers), 20):
            enriched.extend(_claude_extract_paper_stats(papers[i:i + 20], link))
        # Apply post-LLM inclusion filters
        papers_by_link[link] = [
            p for p in enriched
            if p.n >= min_n_inclusive and p.study_type in allowed_study_types
        ]

    return papers_by_link


def print_summary(evidence_score: float, papers_by_link: Dict[str, List[Paper]],
                  best_score: float, run_seconds: float, status: str) -> None:
    """Print grep-friendly structured output. Analog to the print block in train.py."""
    total_papers = sum(len(v) for v in papers_by_link.values())
    link_scores = {l: compute_link_score(p) for l, p in papers_by_link.items()}
    strongest = max(link_scores, key=link_scores.get) if link_scores else "none"
    weakest = min(link_scores, key=link_scores.get) if link_scores else "none"

    print("---")
    print(f"evidence_score:   {evidence_score:.6f}")
    print(f"best_score:       {best_score:.6f}")
    print(f"total_papers:     {total_papers}")
    print(f"strongest_link:   {strongest} ({link_scores.get(strongest, 0):.3f})")
    print(f"weakest_link:     {weakest} ({link_scores.get(weakest, 0):.3f})")
    print(f"run_seconds:      {run_seconds:.1f}")
    print(f"status:           {status}")
    for link in LINK_WEIGHTS:
        n = len(papers_by_link.get(link, []))
        s = link_scores.get(link, 0.0)
        print(f"link_{link}:  n={n} score={s:.4f}")


if __name__ == "__main__":
    # Sanity check: run fixed validation queries only and print baseline score
    print("Running baseline (fixed validation queries only)...")
    dummy_queries = {link: [q] for link, q in FIXED_VALIDATION_QUERIES.items()}
    dummy_depth = {link: 20 for link in LINK_WEIGHTS}
    dummy_inclusion = {
        "min_year": 2009,
        "min_sample_size": 0,
        "study_types": list(STUDY_WEIGHTS.keys()),
    }
    t0 = time.time()
    papers_by_link = run_searches(dummy_queries, dummy_inclusion, dummy_depth)
    score = evaluate_evidence(papers_by_link)
    print_summary(score, papers_by_link, 0.0, time.time() - t0, "baseline")
