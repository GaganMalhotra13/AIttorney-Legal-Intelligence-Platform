"""
utils/contract_scorer.py
Real NLP-based contract risk scorer.
Replaces 65 + (len(text) % 25) with actual clause detection.
"""
import re

# (search_phrase, severity, weight, plain_english_description)
RED_FLAGS: list[tuple[str, str, int, str]] = [
    ("unilateral termination",    "HIGH",   25, "Employer/party can exit for any reason with minimal notice"),
    ("terminate at will",         "HIGH",   25, "At-will termination heavily favours the stronger party"),
    ("non-compete",               "HIGH",   22, "Likely unenforceable under S.27 Indian Contract Act"),
    ("restraint of trade",        "HIGH",   20, "Courts routinely void overbroad restraint clauses"),
    ("intellectual property",     "HIGH",   18, "Overbroad IP assignment may include pre-employment work"),
    ("all inventions",            "HIGH",   18, "Captures personal projects — negotiate explicit carve-outs"),
    ("liquidated damages",        "MEDIUM", 14, "Pre-set penalty may exceed actual loss — challengeable"),
    ("indemnify and hold",        "MEDIUM", 12, "Unlimited indemnity clauses are risky"),
    ("arbitration",               "MEDIUM", 12, "Removes your right to approach civil courts directly"),
    ("limitation of liability",   "MEDIUM", 10, "May cap your recovery far below actual damages"),
    ("governing law",             "MEDIUM",  8, "Foreign/inconvenient jurisdiction raises litigation cost"),
    ("auto renewal",              "LOW",     6, "Silently renews — easy to miss, hard to exit"),
    ("no oral modification",      "LOW",     4, "All changes must be written — verbal agreements won't count"),
    ("entire agreement",          "LOW",     3, "Prior negotiations and promises are wiped out"),
    ("waiver of jury",            "LOW",     3, "Not applicable in India but signals foreign template risk"),
    ("force majeure",             "MEDIUM",  8, "Broad force majeure can let the other party off the hook"),
    ("sole discretion",           "MEDIUM", 10, "Gives other party unchecked decision-making power"),
    ("without cause",             "HIGH",   20, "Termination without reason — no recourse for you"),
    ("assign this agreement",     "MEDIUM", 10, "They can transfer your contract to any third party"),
    ("background check",          "LOW",     3, "Ensure scope is proportionate — not blanket surveillance"),
]

# Positive clauses that reduce risk score
GREEN_FLAGS: list[tuple[str, int]] = [
    ("mutual termination",    -8),
    ("30 days notice",        -6),
    ("60 days notice",        -8),
    ("90 days notice",        -6),
    ("severance",             -8),
    ("dispute resolution",    -4),
    ("mediation",             -4),
    ("governed by indian",    -5),
    ("as per applicable law", -3),
]


def _find_excerpt(text: str, phrase: str, window: int = 220) -> str:
    idx = text.lower().find(phrase)
    if idx == -1:
        return "Clause detected but exact excerpt unavailable."
    start = max(0, idx - 40)
    end   = min(len(text), idx + window)
    raw   = text[start:end].replace("\n", " ").strip()
    return f"...{raw}..."


def score_contract(text: str, role: str) -> dict:
    """
    Returns:
      score (0-95 int),
      grade ("HIGH"/"MODERATE"/"LOW"),
      flags (list of dicts),
      green_flags (list of str),
      flag_count (int),
      summary (str)
    """
    text_lower  = text.lower()
    total       = 0
    found_flags = []
    green_found = []

    for phrase, severity, weight, desc in RED_FLAGS:
        if phrase in text_lower:
            excerpt = _find_excerpt(text, phrase)
            total  += weight
            found_flags.append({
                "clause":      phrase.title(),
                "severity":    severity,
                "weight":      weight,
                "description": desc,
                "excerpt":     excerpt,
            })

    for phrase, reduction in GREEN_FLAGS:
        if phrase in text_lower:
            total      = max(0, total + reduction)
            green_found.append(phrase.title())

    found_flags.sort(key=lambda x: x["weight"], reverse=True)
    final = min(95, total)
    grade = "HIGH" if final > 60 else "MODERATE" if final > 30 else "LOW"

    role_advice = {
        "Employee":              "Focus on non-compete, IP ownership, and termination asymmetry.",
        "Tenant":                "Focus on deposit forfeiture clauses, unilateral eviction rights, and repair liability.",
        "Freelancer / Contractor":"Focus on IP assignment, payment timelines, and kill-fee clauses.",
        "Buyer":                 "Focus on 'as is' clauses, dispute jurisdiction, and hidden indemnity.",
        "Seller":                "Focus on payment security, return/refund terms, and liability caps.",
        "Service Provider":      "Focus on scope creep language, IP ownership, and payment terms.",
        "Borrower":              "Focus on default triggers, interest compounding, and security clauses.",
        "Investor":              "Focus on anti-dilution, liquidation preference, and drag-along rights.",
    }

    summary = (
        f"Found {len(found_flags)} risk clauses for a {role}. "
        f"Risk score: {final}/95. "
        + role_advice.get(role, "Review all flagged clauses carefully.")
    )

    return {
        "score":       final,
        "grade":       grade,
        "flags":       found_flags,
        "green_flags": green_found,
        "flag_count":  len(found_flags),
        "summary":     summary,
    }