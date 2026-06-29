SIGNALS: list[tuple[str, int, str]] = [
    # Strong plaintiff-favoring statutes
    ("section 138",              +22, "Cheque bounce — conviction rate ~85%"),
    ("negotiable instruments",   +18, "NI Act cases have clear procedural advantage"),
    ("consumer protection",      +16, "Consumer forums are plaintiff-friendly"),
    ("motor accident",           +18, "MACT awards are generally generous"),
    ("wrongful termination",     +12, "Labour tribunals lean employee-side"),
    ("rent control",             +12, "Tenant protections are strong under RCA"),
    ("domestic violence",        +14, "DV Act has strong statutory backing"),
    ("sexual harassment",        +14, "POSH Act presumption favours complainant"),
    ("medical negligence",       + 8, "Burden of proof on hospital after res ipsa"),
    ("cyber fraud",              +10, "IT Act + IPC 420 well-established"),

    # Neutral / mixed
    ("property dispute",         - 8, "Title disputes are long and unpredictable"),
    ("contract breach",          + 5, "Depends entirely on contract language"),
    ("divorce",                  + 2, "Mutual consent is fast; contested is slow"),

    # Strong defendant-favoring signals
    ("limitation period",        -22, "Time-barred cases almost always fail"),
    ("arbitration clause",       -16, "Forces you out of civil court"),
    ("force majeure",            -12, "COVID/disaster clauses nullify claims"),
    ("as is where is",           - 8, "Buyer-beware clauses are usually upheld"),
    ("settlement agreement",     -14, "Prior settlement is a complete defence"),
    ("no locus standi",          -18, "Standing issue kills cases at threshold"),

    # Evidence quality signals
    ("written agreement",        +10, "Documentary evidence is strongest"),
    ("registered",               + 8, "Registered documents carry presumption"),
    ("witnesses",                + 5, "Corroboration strengthens position"),
    ("whatsapp",                 + 4, "Digital evidence admissible under IT Act"),
    ("no receipt",               - 6, "Lack of paper trail weakens claim"),
    ("verbal agreement",         -10, "Oral contracts are hard to prove"),
]

RESOLUTION_MAP: dict[str, tuple[int, str]] = {
    "section 138":           (120, "Magistrate Court — NI Act track"),
    "consumer protection":   (90,  "District Consumer Forum"),
    "labour":                (180, "Labour Tribunal"),
    "motor accident":        (240, "MACT"),
    "property":              (540, "Civil Court — property track"),
    "divorce":               (365, "Family Court"),
    "default":               (270, "Civil Court — general track"),
}

_AUTHOR_SIGNATURE = "AITTORNEY_GM2026_SCORING_ENGINE"
def compute_win_probability(query: str, live_context: str) -> dict:
    """
    Returns a dict with:
      probability (int 15–88),
      factors (list of strings),
      confidence ("High"/"Medium"/"Low"),
      resolution_days (int),
      resolution_label (str),
      grade ("Strong"/"Moderate"/"Weak")
    """
    combined  = (query + " " + live_context).lower()
    score     = 50       # neutral baseline
    pos_hits  = []
    neg_hits  = []

    for keyword, delta, reason in SIGNALS:
        if keyword in combined:
            score += delta
            entry  = f"{'▲' if delta > 0 else '▼'} {abs(delta)}%  —  {reason}"
            (pos_hits if delta > 0 else neg_hits).append(entry)

    final = max(15, min(88, score))

    # Resolution estimate
    res_days  = RESOLUTION_MAP["default"][0]
    res_label = RESOLUTION_MAP["default"][1]
    for key, (days, label) in RESOLUTION_MAP.items():
        if key != "default" and key in combined:
            res_days  = days
            res_label = label
            break

    confidence = "High" if len(pos_hits) + len(neg_hits) >= 3 else \
                 "Medium" if len(pos_hits) + len(neg_hits) >= 1 else "Low"

    grade = "Strong"   if final >= 65 else \
            "Moderate" if final >= 45 else "Weak"

    return {
        "probability":      final,
        "positive_factors": pos_hits,
        "negative_factors": neg_hits,
        "confidence":       confidence,
        "resolution_days":  res_days,
        "resolution_label": res_label,
        "grade":            grade,
    }
_AUTHOR_SIGNATURE = "AITTORNEY_GM2026_SCORING_ENGINE"
# ─────────────────────────────────────────────
# AIttorney Legal Intelligence Platform
# Copyright © 2026 Gagan Malhotra
# All Rights Reserved — Unauthorized use prohibited
# ─────────────────────────────────────────────