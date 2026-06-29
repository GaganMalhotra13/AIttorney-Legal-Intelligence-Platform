"""
utils/search.py — AIttorney v7
Upgraded pipeline:
  1. DuckDuckGo multi-strategy (18 sources, 5 strategies) — PARALLELIZED
  2. IndianKanoon direct scrape via ScraperAPI
  3. Cohere reranking
  4. Groq compression
  5. Landmark judgment extraction

Result: Gemini gets real judgment text, ranked by relevance,
compressed to fit cleanly in context.
"""
from duckduckgo_search import DDGS
from config import MAX_SEARCH_RESULTS
from concurrent.futures import ThreadPoolExecutor, as_completed
import os

# New utils — import with graceful fallback
try:
    from utils.kanoon_scraper import search_indiankanoon, get_landmark_judgments
    KANOON_AVAILABLE = bool(os.getenv("SCRAPER_API_KEY"))
except ImportError:
    KANOON_AVAILABLE = False

try:
    from utils.reranker import rerank_with_score_filter
    COHERE_AVAILABLE = bool(os.getenv("COHERE_API_KEY"))
except ImportError:
    COHERE_AVAILABLE = False

try:
    from utils.compressor import compress_legal_context, extract_landmark_holdings
    GROQ_AVAILABLE = bool(os.getenv("GROQ_API_KEY"))
except ImportError:
    GROQ_AVAILABLE = False


# ── Source registry (unchanged) ──────────────────────────────
LEGAL_SOURCES = [
    ("indiankanoon.org",          3, "case_law"),
    ("livelaw.in",                3, "news_judgment"),
    ("barandbench.com",           3, "news_judgment"),
    ("sci.gov.in",                3, "official"),
    ("scobserver.in",             2, "sc_tracking"),
    ("hcservices.ecourts.gov.in", 2, "hc_official"),
    ("doj.gov.in",                2, "govt"),
    ("nclt.gov.in",               2, "tribunal"),
    ("lawyersclubindia.com",      2, "forum"),
    ("advocatekhoj.com",          2, "bare_act"),
    ("lawrato.com",               2, "legal_help"),
    ("ipleaders.in",              1, "education"),
    ("legalbites.in",             1, "education"),
    ("latestlaws.com",            1, "bare_act"),
    ("legalserviceindia.com",     1, "legal_help"),
]

_TOP = " OR ".join(f"site:{d}" for d, t, _ in LEGAL_SOURCES if t == 3)
_MID = " OR ".join(f"site:{d}" for d, t, _ in LEGAL_SOURCES if t >= 2)

_TOPIC_BOOSTERS = {
    "cheque_bounce":  "NI Act section 138 dishonour cheque judgment",
    "consumer":       "Consumer Protection Act 2019 NCDRC forum",
    "property":       "RERA real estate registration sale deed",
    "labour":         "Industrial Disputes Act wrongful termination",
    "family":         "Hindu Marriage Act maintenance custody",
    "cyber":          "IT Act 2000 IPC 420 cyber crime fraud",
    "motor":          "Motor Vehicles Act MACT compensation",
    "rent":           "Rent Control Act security deposit eviction",
    "medical":        "medical negligence Consumer Protection NCDRC",
    "criminal":       "IPC BNS FIR Criminal Procedure Code",
    "general":        "civil court judgment India",
}


def _classify(query: str) -> str:
    q = query.lower()
    if any(w in q for w in ["cheque", "bounce", "138", "negotiable"]): return "cheque_bounce"
    if any(w in q for w in ["consumer", "product", "defect", "refund"]): return "consumer"
    if any(w in q for w in ["property", "land", "flat", "builder", "rera"]): return "property"
    if any(w in q for w in ["labour", "employment", "fired", "salary"]): return "labour"
    if any(w in q for w in ["divorce", "matrimonial", "maintenance"]): return "family"
    if any(w in q for w in ["cyber", "fraud", "online", "upi", "phishing"]): return "cyber"
    if any(w in q for w in ["motor", "accident", "mact", "vehicle"]): return "motor"
    if any(w in q for w in ["rent", "tenant", "landlord", "deposit"]): return "rent"
    if any(w in q for w in ["medical", "doctor", "hospital", "negligence"]): return "medical"
    if any(w in q for w in ["fir", "criminal", "police", "ipc", "bns"]): return "criminal"
    return "general"


def _weight(url: str) -> int:
    for d, t, _ in LEGAL_SOURCES:
        if d in url: return t
    return 0


def _dedup(results: list[dict]) -> list[dict]:
    seen_u, seen_t, out = set(), set(), []
    for r in results:
        uk = r.get("href", r.get("url", ""))[:65]
        tk = r.get("title", "")[:45].lower().strip()
        if uk not in seen_u and tk not in seen_t and tk:
            seen_u.add(uk); seen_t.add(tk); out.append(r)
    return out


def _normalize(hits: list[dict]) -> list[dict]:
    normalized = []
    for r in hits:
        normalized.append({
            "title":   r.get("title", ""),
            "snippet": r.get("body", ""),
            "url":     r.get("href", ""),
            "href":    r.get("href", ""),
            "source":  r.get("href", "").split("/")[2].replace("www.", "") if r.get("href") else "",
            "tier":    _weight(r.get("href", "")),
        })
    return normalized


def _single_ddg_query(sq: str, budget: int) -> list[dict]:
    """Run one DDG query — used by parallel executor."""
    try:
        with DDGS() as ddgs:
            return list(ddgs.text(sq, max_results=budget))
    except Exception:
        return []


def _ddg_search(query: str, topic: str) -> list[dict]:
    """
    DuckDuckGo multi-strategy search — NOW PARALLELIZED.
    Runs all 5 strategies concurrently using a thread pool
    instead of sequentially. Cuts ~4s down to ~1s.
    """
    booster = _TOPIC_BOOSTERS.get(topic, "")
    strategies = [
        (f"{query} {booster} judgment ({_TOP})", 4),
        (f"{query} section act India court ({_MID})", 3),
        (f"{query} ruling verdict 2022 OR 2023 OR 2024 ({_TOP})", 3),
        (f"{booster} bare act explanation India", 2),
        (f"{query} landmark case India Supreme Court ({_TOP})", 2),
    ]

    all_hits: list[dict] = []

    # ── PARALLEL EXECUTION ────────────────────────────────────
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_query = {
            executor.submit(_single_ddg_query, sq, budget): sq
            for sq, budget in strategies
        }
        for future in as_completed(future_to_query, timeout=8):
            try:
                hits = future.result(timeout=3)
                all_hits.extend(hits)
            except Exception:
                continue

    # Fallback if everything failed
    if not all_hits:
        all_hits = _single_ddg_query(f"{query} India law court", 6)

    return _normalize(all_hits)


# ══════════════════════════════════════════════════════════════
# MAIN SEARCH FUNCTION
# ══════════════════════════════════════════════════════════════
def get_live_cases(query: str) -> tuple[str, list[dict], list[dict]]:
    """
    Full upgraded pipeline.
    Returns:
      context_str   — compressed, ranked context for LLM
      ui_results    — list for source cards in UI
      landmarks     — list of landmark judgment objects
    """
    topic = _classify(query)

    # ── Stage 1: Gather from all sources (DDG now parallel) ──
    ddg_results = _ddg_search(query, topic)
    kanoon_results: list[dict] = []
    landmarks: list[dict] = []

    if KANOON_AVAILABLE:
        kanoon_results = search_indiankanoon(query, max_results=8)
        landmarks = get_landmark_judgments(query, topic)

    # Merge and deduplicate
    all_results = ddg_results + kanoon_results
    cleaned = _dedup(all_results)

    # ── Stage 2: Rerank by relevance ─────────────────────────
    if COHERE_AVAILABLE and cleaned:
        ranked = rerank_with_score_filter(
            query=query,
            results=cleaned,
            text_field="snippet",
            min_score=0.05,
            top_n=MAX_SEARCH_RESULTS + 4,
        )
    else:
        ranked = sorted(cleaned, key=lambda r: r.get("tier", 0), reverse=True)
        ranked = ranked[:MAX_SEARCH_RESULTS + 4]

    # ── Stage 3: Build raw context ────────────────────────────
    raw_context = "\n\n".join([
        f"[Source {i+1}] {r.get('title','')}\n"
        f"URL: {r.get('url', r.get('href',''))}\n"
        f"Court: {r.get('court','')}\n"
        f"Date: {r.get('date','')}\n"
        f"Citations: {r.get('citations',0)}\n"
        f"{r.get('snippet','')}"
        for i, r in enumerate(ranked)
    ])

    # Add landmark holdings if available
    landmark_holdings = ""
    if GROQ_AVAILABLE and landmarks:
        landmark_holdings = extract_landmark_holdings(landmarks, query)
        if landmark_holdings:
            raw_context = f"LANDMARK JUDGMENTS:\n{landmark_holdings}\n\n---\n\nSEARCH RESULTS:\n{raw_context}"

    # ── Stage 4: Compress context ─────────────────────────────
    if GROQ_AVAILABLE and len(raw_context) > 2000:
        final_context = compress_legal_context(raw_context, query, max_words=700)
    else:
        final_context = raw_context[:4000]

    # ── UI results: top 6, with href normalized ───────────────
    ui_results = []
    for r in ranked[:6]:
        ui_results.append({
            "title":     r.get("title", ""),
            "href":      r.get("url", r.get("href", "")),
            "snippet":   r.get("snippet", "")[:200],
            "court":     r.get("court", ""),
            "date":      r.get("date", ""),
            "citations": r.get("citations", 0),
            "source":    r.get("source", ""),
            "_weight":   r.get("tier", 0),
            "_score":    r.get("relevance_score", 0),
        })

    return final_context, ui_results, landmarks


def search_bare_act(text: str) -> tuple[str, list[dict]]:
    """Targeted bare-act lookup — unchanged."""
    try:
        with DDGS() as ddgs:
            r = list(ddgs.text(
                f"{text[:120]} India bare act section explanation site:indiankanoon.org OR site:advocatekhoj.com",
                max_results=4
            ))
        ctx = "\n\n".join(f"{x['title']}\n{x['body']}" for x in r)
        return ctx, r
    except Exception as e:
        return f"Error: {e}", []


def search_recent_judgments(topic: str, year_from: int = 2021) -> tuple[str, list[dict]]:
    """Recent SC/HC judgments — upgraded with direct kanoon scraping."""
    if KANOON_AVAILABLE:
        results = search_indiankanoon(
            f"{topic} Supreme Court High Court {year_from} OR 2022 OR 2023 OR 2024",
            max_results=5
        )
        if results:
            ctx = "\n\n".join(
                f"{r['title']} ({r['court']}, {r['date']})\n{r['snippet']}"
                for r in results
            )
            return ctx, results

    # Fallback to DuckDuckGo
    years = " OR ".join(str(y) for y in range(year_from, 2026))
    try:
        with DDGS() as ddgs:
            r = list(ddgs.text(
                f"{topic} India Supreme Court OR High Court judgment ({years}) site:indiankanoon.org OR site:livelaw.in",
                max_results=5
            ))
        ctx = "\n\n".join(f"{x['title']}\n{x['body']}" for x in r)
        return ctx, r
    except Exception as e:
        return f"Error: {e}", []


def get_source_registry() -> list[dict]:
    return [{"domain": d, "tier": t, "category": c} for d, t, c in LEGAL_SOURCES]
# ─────────────────────────────────────────────
# AIttorney Legal Intelligence Platform
# Copyright © 2026 Gagan Malhotra
# All Rights Reserved — Unauthorized use prohibited
# ─────────────────────────────────────────────