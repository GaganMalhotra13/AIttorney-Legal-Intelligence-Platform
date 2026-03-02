"""
utils/search.py — AIttorney v6
Vastly expanded: 18 Indian legal sources, 5 search strategies,
snippet enrichment, topic classification, fallback chains.
"""
from duckduckgo_search import DDGS
from config import MAX_SEARCH_RESULTS

# ── 18-source registry ──────────────────────────────────────
# (domain, tier 1-3, category)
LEGAL_SOURCES = [
    # Tier 3 — Primary case law & judgment databases
    ("indiankanoon.org",          3, "case_law"),
    ("livelaw.in",                3, "news_judgment"),
    ("barandbench.com",           3, "news_judgment"),
    ("sci.gov.in",                3, "official"),
    # Tier 2 — High courts, tribunals, government
    ("scobserver.in",             2, "sc_tracking"),
    ("hcservices.ecourts.gov.in", 2, "hc_official"),
    ("doj.gov.in",                2, "govt"),
    ("nclt.gov.in",               2, "tribunal"),
    ("rera.gov.in",               2, "tribunal"),
    ("lawyersclubindia.com",      2, "forum"),
    ("advocatekhoj.com",          2, "bare_act"),
    ("lawrato.com",               2, "legal_help"),
    ("kanoon.co.in",              2, "case_law"),
    # Tier 1 — Legal education, blogs, analysis
    ("ipleaders.in",              1, "education"),
    ("legalbites.in",             1, "education"),
    ("lawctopus.com",             1, "education"),
    ("latestlaws.com",            1, "bare_act"),
    ("legalserviceindia.com",     1, "legal_help"),
]

_TOP  = " OR ".join(f"site:{d}" for d,t,_ in LEGAL_SOURCES if t == 3)
_MID  = " OR ".join(f"site:{d}" for d,t,_ in LEGAL_SOURCES if t >= 2)
_ALL  = " OR ".join(f"site:{d}" for d,t,_ in LEGAL_SOURCES)
_ACTS = " OR ".join(f"site:{d}" for d,_,c in LEGAL_SOURCES if c in ("bare_act","official","education"))


def _weight(url: str) -> int:
    for d, t, _ in LEGAL_SOURCES:
        if d in url:
            return t
    return 0


def _dedup(results: list[dict]) -> list[dict]:
    seen_u, seen_t, out = set(), set(), []
    for r in results:
        uk = r.get("href","")[:65]
        tk = r.get("title","")[:45].lower().strip()
        if uk not in seen_u and tk not in seen_t and tk:
            seen_u.add(uk); seen_t.add(tk); out.append(r)
    return out


def _classify_query(query: str) -> str:
    q = query.lower()
    if any(w in q for w in ["cheque","bounce","138","negotiable"]): return "cheque_bounce"
    if any(w in q for w in ["consumer","product","defect","refund","ecommerce"]): return "consumer"
    if any(w in q for w in ["property","land","plot","flat","builder","rera"]): return "property"
    if any(w in q for w in ["labour","employment","fired","termination","salary","pf","esic"]): return "labour"
    if any(w in q for w in ["divorce","matrimonial","maintenance","custody","dowry"]): return "family"
    if any(w in q for w in ["cyber","fraud","online","hacking","phishing","upi"]): return "cyber"
    if any(w in q for w in ["motor","accident","mact","vehicle","insurance"]): return "motor"
    if any(w in q for w in ["rent","tenant","landlord","eviction","deposit"]): return "rent"
    if any(w in q for w in ["medical","doctor","hospital","negligence","treatment"]): return "medical"
    if any(w in q for w in ["fir","criminal","police","arrest","bail","ipc","bns"]): return "criminal"
    return "general"


# Topic-specific query boosters that dramatically improve retrieval
_TOPIC_BOOSTERS = {
    "cheque_bounce":  "NI Act section 138 dishonour cheque judgment",
    "consumer":       "Consumer Protection Act 2019 NCDRC SCDRC district forum",
    "property":       "RERA real estate registration sale deed title dispute judgment",
    "labour":         "Industrial Disputes Act wrongful termination labour court",
    "family":         "Hindu Marriage Act Special Marriage Act maintenance custody",
    "cyber":          "IT Act 2000 IPC 420 cyber crime fraud online",
    "motor":          "Motor Vehicles Act MACT compensation tribunal claim",
    "rent":           "Rent Control Act security deposit eviction tenant landlord",
    "medical":        "medical negligence Consumer Protection Act NCDRC hospital",
    "criminal":       "IPC BNS FIR bail Criminal Procedure Code CrPC BNSS",
    "general":        "civil court judgment India",
}


def _build_strategies(query: str, topic: str) -> list[tuple[str, int]]:
    """5 strategies, each with a max_results budget."""
    booster = _TOPIC_BOOSTERS.get(topic, "")
    q = query.strip()
    return [
        # Primary: topic-boosted, top sources, judgment focused
        (f"{q} {booster} judgment ({_TOP})", 4),
        # Secondary: section/statute angle, mid+top sources
        (f"{q} section act India court ({_MID})", 3),
        # Tertiary: recent (2022-2025) rulings
        (f"{q} ruling verdict 2022 OR 2023 OR 2024 OR 2025 ({_TOP})", 3),
        # Quaternary: bare act / explainer angle
        (f"{booster} bare act explanation India ({_ACTS})", 2),
        # Quinary: news & analysis, catches recent landmark rulings
        (f"{q} landmark case India High Court Supreme Court ({_TOP})", 2),
    ]


def get_live_cases(query: str) -> tuple[str, list[dict]]:
    """
    Multi-strategy, 18-source, deduplicated, authority-ranked search.
    Returns (llm_context_string, ui_result_list).
    """
    topic      = _classify_query(query)
    strategies = _build_strategies(query, topic)
    all_hits: list[dict] = []

    for sq, budget in strategies:
        try:
            with DDGS() as ddgs:
                hits = list(ddgs.text(sq, max_results=budget))
            all_hits.extend(hits)
        except Exception:
            continue

    # Hard fallback
    if not all_hits:
        try:
            with DDGS() as ddgs:
                all_hits = list(ddgs.text(f"{query} India law court", max_results=6))
        except Exception as e:
            return f"Search error: {e}", []

    cleaned = _dedup(all_hits)
    ranked  = sorted(cleaned, key=lambda r: _weight(r.get("href","")), reverse=True)
    top     = ranked[:MAX_SEARCH_RESULTS + 3]

    if not top:
        return "No results found.", []

    context = "\n\n".join(
        f"[{i+1}] {r.get('title','')}\nURL: {r.get('href','')}\n{r.get('body','')}"
        for i, r in enumerate(top)
    )
    # Attach topic to each result for UI
    for r in top:
        r["_topic"] = topic
        r["_weight"] = _weight(r.get("href",""))

    return context, top


def search_bare_act(text: str) -> tuple[str, list[dict]]:
    """Targeted bare-act lookup."""
    try:
        with DDGS() as ddgs:
            r = list(ddgs.text(
                f"{text[:120]} India bare act section explanation ({_ACTS})",
                max_results=4
            ))
        ctx = "\n\n".join(f"{x['title']}\n{x['body']}" for x in r)
        return ctx, r
    except Exception as e:
        return f"Error: {e}", []


def search_recent_judgments(topic: str, year_from: int = 2021) -> tuple[str, list[dict]]:
    """Recent SC/HC judgments on a topic."""
    years = " OR ".join(str(y) for y in range(year_from, 2026))
    try:
        with DDGS() as ddgs:
            r = list(ddgs.text(
                f"{topic} India Supreme Court OR High Court judgment ({years}) ({_TOP})",
                max_results=5
            ))
        ctx = "\n\n".join(f"{x['title']}\n{x['body']}" for x in r)
        return ctx, r
    except Exception as e:
        return f"Error: {e}", []


def get_source_registry() -> list[dict]:
    """Returns source metadata for UI display."""
    return [{"domain": d, "tier": t, "category": c} for d,t,c in LEGAL_SOURCES]