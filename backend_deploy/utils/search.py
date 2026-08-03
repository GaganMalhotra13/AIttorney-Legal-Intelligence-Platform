"""
utils/search.py — AIttorney v7
Fixed pipeline:
  - Hard domain blocklist filters irrelevant results
  - Guaranteed 3 from IndianKanoon + 3 from LiveLaw
  - DDG used only for supplementary results
  - Relevance filter before any result reaches UI
"""
from duckduckgo_search import DDGS
from config import MAX_SEARCH_RESULTS
from concurrent.futures import ThreadPoolExecutor, as_completed
import os

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


# ── Hard block list — these domains NEVER appear in results ──
BLOCKED_DOMAINS = {
    # Software / tech companies
    "builder.io", "vercel.com", "netlify.com", "heroku.com",
    "github.com", "stackoverflow.com", "medium.com",
    # Real estate listings (not legal)
    "rishita.in", "99acres.com", "magicbricks.com", "housing.com",
    "makaan.com", "nobroker.com", "commonfloor.com", "proptiger.com",
    "squareyards.com", "nestaway.com", "olx.in", "quikr.com",
    # Shopping / ecommerce
    "amazon.", "flipkart.", "meesho.", "myntra.", "snapdeal.",
    "indiamart.", "justdial.com", "sulekha.com", "tradeindia.",
    # Entertainment / social
    "youtube.", "instagram.", "facebook.", "twitter.", "tiktok.",
    "reddit.com", "quora.com", "pinterest.", "linkedin.com",
    # Foreign sites
    "ikuina.com", "azlyrics.", "genius.com", "lyrics.",
    # News (non-legal)
    "ndtv.com", "timesofindia.", "hindustantimes.", "indiatoday.",
    "theprint.", "thewire.", "scroll.in", "firstpost.",
    # Directories / rankings
    "justia.com", "law360.", "findlaw.", "avvo.com",
    # Wikipedia
    "wikipedia.org", "wikihow.",
}

# ── Known good Indian legal domains ──────────────────────────
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
    ("verdictum.in",              2, "case_law"),
    ("manupatra.com",             2, "case_law"),
]

LEGAL_DOMAIN_SET = {d for d, _, _ in LEGAL_SOURCES}

# ── Required legal signals — result must contain at least one ─
LEGAL_SIGNALS = [
    "india", "indian", "court", "judgment", "judgement",
    "section", " act ", "ipc", "crpc", "cpc", "bnss",
    "supreme court", "high court", "tribunal", "petition",
    "plaintiff", "defendant", "advocate", "lawyer",
    "indiankanoon", "livelaw", "barandbench",
    "rera", "consumer forum", "lok adalat",
    "arbitration", "legal", "law",
    "vs ", "v/s", "versus", "petitioner", "respondent",
    "order", "verdict", "ruled", "bench",
]

_TOPIC_BOOSTERS = {
    "cheque_bounce":  "NI Act section 138 dishonour cheque judgment",
    "consumer":       "Consumer Protection Act 2019 NCDRC forum",
    "property":       "RERA real estate builder delay possession judgment",
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
    if any(w in q for w in ["property", "land", "flat", "builder", "rera", "possession"]): return "property"
    if any(w in q for w in ["labour", "employment", "fired", "salary", "termination"]): return "labour"
    if any(w in q for w in ["divorce", "matrimonial", "maintenance", "custody"]): return "family"
    if any(w in q for w in ["cyber", "fraud", "online", "upi", "phishing"]): return "cyber"
    if any(w in q for w in ["motor", "accident", "mact", "vehicle"]): return "motor"
    if any(w in q for w in ["rent", "tenant", "landlord", "deposit"]): return "rent"
    if any(w in q for w in ["medical", "doctor", "hospital", "negligence"]): return "medical"
    if any(w in q for w in ["fir", "criminal", "police", "ipc", "bns"]): return "criminal"
    return "general"


def _weight(url: str) -> int:
    for d, t, _ in LEGAL_SOURCES:
        if d in url:
            return t
    return 0


def _is_blocked(url: str, title: str = "") -> bool:
    """Returns True if this result should be excluded."""
    url_lower   = url.lower()
    title_lower = title.lower()
    combined    = url_lower + " " + title_lower

    # Check hard block list
    for blocked in BLOCKED_DOMAINS:
        if blocked in url_lower:
            return True

    # Block results with zero legal signals in title
    # (catches foreign sites, random listings, etc.)
    has_signal = any(sig in combined for sig in LEGAL_SIGNALS)
    return not has_signal


def _dedup(results: list[dict]) -> list[dict]:
    seen_u, seen_t, out = set(), set(), []
    for r in results:
        uk = r.get("href", r.get("url", ""))[:65]
        tk = r.get("title", "")[:45].lower().strip()
        if uk not in seen_u and tk not in seen_t and tk:
            seen_u.add(uk)
            seen_t.add(tk)
            out.append(r)
    return out


def _normalize(hits: list[dict], source_tag: str = "") -> list[dict]:
    out = []
    for r in hits:
        url = r.get("href", r.get("url", ""))
        title = r.get("title", "")
        if _is_blocked(url, title):
            continue
        out.append({
            "title":     title,
            "snippet":   r.get("body", r.get("snippet", "")),
            "url":       url,
            "href":      url,
            "source":    r.get("source") or (url.split("/")[2].replace("www.", "") if url else ""),
            "tier":      r.get("tier", _weight(url)),
            "citations": r.get("citations", 0),
            "court":     r.get("court", ""),
            "date":      r.get("date", ""),
        })
    return out


def _single_ddg_query(sq: str, budget: int) -> list[dict]:
    """Single DDG query with error handling."""
    try:
        with DDGS() as ddgs:
            return list(ddgs.text(sq, max_results=budget))
    except Exception:
        return []


def _search_livelaw(query: str, max_results: int = 3) -> list[dict]:
    """
    Fetch LiveLaw results — multiple strategies since site: operator
    is unreliable on DDG free tier.
    """
    strategies = [
        f"livelaw.in {query} court judgment India",
        f'"{query}" livelaw court India',
        f"livelaw India {query} legal ruling",
    ]

    for strategy in strategies:
        try:
            with DDGS() as ddgs:
                raw = list(ddgs.text(strategy, max_results=max_results * 3))

            results = []
            for r in raw:
                url   = r.get("href", "")
                title = r.get("title", "")
                # Only keep actual livelaw results
                if "livelaw.in" not in url.lower():
                    continue
                if _is_blocked(url, title):
                    continue
                results.append({
                    "title":     title,
                    "snippet":   r.get("body", ""),
                    "url":       url,
                    "href":      url,
                    "source":    "livelaw.in",
                    "tier":      3,
                    "citations": 0,
                    "court":     "",
                    "date":      "",
                })
                if len(results) >= max_results:
                    break

            if results:
                return results
        except Exception:
            continue

    return []


def _search_barandbench(query: str, max_results: int = 2) -> list[dict]:
    """
    Fetch Bar & Bench results with fallback strategies.
    """
    strategies = [
        f"barandbench.com {query} court India",
        f'"{query}" bar and bench court India legal',
        f"barandbench India {query} judgment",
    ]

    for strategy in strategies:
        try:
            with DDGS() as ddgs:
                raw = list(ddgs.text(strategy, max_results=max_results * 3))

            results = []
            for r in raw:
                url   = r.get("href", "")
                title = r.get("title", "")
                if "barandbench.com" not in url.lower():
                    continue
                if _is_blocked(url, title):
                    continue
                results.append({
                    "title":     title,
                    "snippet":   r.get("body", ""),
                    "url":       url,
                    "href":      url,
                    "source":    "barandbench.com",
                    "tier":      3,
                    "citations": 0,
                    "court":     "",
                    "date":      "",
                })
                if len(results) >= max_results:
                    break

            if results:
                return results
        except Exception:
            continue

    return []
def _ddg_supplementary(query: str, topic: str) -> list[dict]:
    """
    DDG supplementary search — uses domain names as keywords
    instead of site: operator (more reliable on free tier).
    """
    booster = _TOPIC_BOOSTERS.get(topic, "")

    strategies = [
        (f"{query} {booster} judgment India court legal", 5),
        (f"{query} India Supreme Court High Court ruling verdict", 4),
        (f"{booster} India court order 2022 2023 2024", 3),
    ]

    all_hits: list[dict] = []
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {
            executor.submit(_single_ddg_query, sq, budget): sq
            for sq, budget in strategies
        }
        for future in as_completed(futures, timeout=8):
            try:
                hits = future.result(timeout=3)
                all_hits.extend(hits)
            except Exception:
                continue

    # Normalize + filter (this is where blocked domains get removed)
    return _normalize(all_hits)

# ══════════════════════════════════════════════════════════════
# MAIN SEARCH FUNCTION
# ══════════════════════════════════════════════════════════════
def get_live_cases(query: str) -> tuple[str, list[dict], list[dict]]:
    """
    Fixed pipeline — guaranteed Indian legal sources only.

    Priority order:
      1. IndianKanoon direct scrape (3 results — actual judgments)
      2. LiveLaw direct search    (3 results — legal news/analysis)
      3. Bar & Bench              (2 results — supplementary)
      4. DDG on legal-only domains (fills remaining slots)
      5. Rerank → Compress → Return

    Returns (context_str, ui_results, landmarks)
    """
    topic     = _classify(query)
    landmarks: list[dict] = []
    all_results: list[dict] = []
    seen_urls: set[str] = set()

    def add_results(new_results: list[dict], label: str):
        """Add results avoiding duplicates."""
        added = 0
        for r in new_results:
            url = r.get("url") or r.get("href") or ""
            key = url.lower().strip("/")[:80]
            if key and key not in seen_urls:
                seen_urls.add(key)
                all_results.append(r)
                added += 1
        if added:
            print(f"✅ {label}: +{added} results")
        else:
            print(f"⚠️  {label}: 0 results")

    # ── Priority 1: IndianKanoon direct scrape ────────────────
    if KANOON_AVAILABLE:
        try:
            kanoon = search_indiankanoon(query, max_results=3)
            # Normalize kanoon results
            for r in kanoon:
                r["tier"] = 3
            add_results(kanoon, "IndianKanoon")

            landmarks = get_landmark_judgments(query, topic)
        except Exception as e:
            print(f"⚠️ IndianKanoon failed: {e}")

    # ── Priority 2: LiveLaw direct ────────────────────────────
    try:
        livelaw = _search_livelaw(query, max_results=3)
        add_results(livelaw, "LiveLaw")
    except Exception as e:
        print(f"⚠️ LiveLaw failed: {e}")

    # ── Priority 3: Bar & Bench ───────────────────────────────
    try:
        bb = _search_barandbench(query, max_results=2)
        add_results(bb, "Bar & Bench")
    except Exception as e:
        print(f"⚠️ Bar&Bench failed: {e}")

    # ── Priority 4: DDG supplementary (site-locked) ───────────
    # Only run if we have fewer than 5 results so far
    if len(all_results) < 5:
        try:
            ddg = _ddg_supplementary(query, topic)
            add_results(ddg, "DDG supplementary")
        except Exception as e:
            print(f"⚠️ DDG supplementary failed: {e}")

    # ── Final filter: remove any blocked results ──────────────
    # (double check — _normalize already filters but kanoon results bypass it)
    clean = [
        r for r in all_results
        if not _is_blocked(r.get("url", r.get("href", "")), r.get("title", ""))
    ]

    if not clean:
        print("⚠️ All results filtered — returning empty context")
        return "", [], []

    # ── Dedup ─────────────────────────────────────────────────
    deduped = _dedup(clean)

    # ── Rerank ────────────────────────────────────────────────
    if COHERE_AVAILABLE and deduped:
        try:
            ranked = rerank_with_score_filter(
                query=query,
                results=deduped,
                text_field="snippet",
                min_score=0.05,
                top_n=MAX_SEARCH_RESULTS + 4,
            )
        except Exception:
            ranked = sorted(deduped, key=lambda r: r.get("tier", 0), reverse=True)
    else:
        ranked = sorted(deduped, key=lambda r: r.get("tier", 0), reverse=True)

    # ── Build context ─────────────────────────────────────────
    raw_context = "\n\n".join([
        f"[Source {i+1}] {r.get('title', '')}\n"
        f"URL: {r.get('url', r.get('href', ''))}\n"
        f"Court: {r.get('court', '')}\n"
        f"Date: {r.get('date', '')}\n"
        f"Citations: {r.get('citations', 0)}\n"
        f"{r.get('snippet', '')}"
        for i, r in enumerate(ranked)
    ])

    # Add landmark holdings
    if GROQ_AVAILABLE and landmarks:
        try:
            landmark_holdings = extract_landmark_holdings(landmarks, query)
            if landmark_holdings:
                raw_context = (
                    f"LANDMARK JUDGMENTS:\n{landmark_holdings}\n\n"
                    f"---\n\nSEARCH RESULTS:\n{raw_context}"
                )
        except Exception:
            pass

    # ── Compress ──────────────────────────────────────────────
    if GROQ_AVAILABLE and len(raw_context) > 2000:
        try:
            final_context = compress_legal_context(raw_context, query, max_words=700)
        except Exception:
            final_context = raw_context[:4000]
    else:
        final_context = raw_context[:4000]

    # ── UI results ────────────────────────────────────────────
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
    """Targeted bare-act lookup."""
    try:
        with DDGS() as ddgs:
            r = list(ddgs.text(
                f"{text[:120]} India bare act section explanation "
                f"site:indiankanoon.org OR site:advocatekhoj.com",
                max_results=4
            ))
        ctx = "\n\n".join(f"{x['title']}\n{x['body']}" for x in r)
        return ctx, r
    except Exception as e:
        return f"Error: {e}", []


def search_recent_judgments(topic: str, year_from: int = 2021) -> tuple[str, list[dict]]:
    """Recent SC/HC judgments."""
    if KANOON_AVAILABLE:
        try:
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
        except Exception:
            pass

    years = " OR ".join(str(y) for y in range(year_from, 2026))
    try:
        with DDGS() as ddgs:
            r = list(ddgs.text(
                f"{topic} India Supreme Court OR High Court judgment ({years}) "
                f"site:indiankanoon.org OR site:livelaw.in",
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