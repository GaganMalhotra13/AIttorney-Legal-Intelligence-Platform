"""
utils/contract_scorer.py
Real NLP-based contract risk scorer — regex-based for broader real-world matching.
"""
import re

# (regex_pattern, severity, weight, plain_english_description)
RED_FLAGS: list[tuple[str, str, int, str]] = [
    (r"terminat\w*\s+(this\s+)?(agreement|employment|contract)?\s*(at\s+any\s+time|without\s+(notice|cause)|for\s+any\s+reason)", "HIGH", 25, "Employer/party can exit for any reason with minimal notice"),
    (r"terminat\w*\s+at\s+will", "HIGH", 25, "At-will termination heavily favours the stronger party"),
    (r"non[\s-]?compet\w*", "HIGH", 22, "Likely unenforceable under S.27 Indian Contract Act"),
    (r"restraint\s+of\s+trade", "HIGH", 20, "Courts routinely void overbroad restraint clauses"),
    (r"intellectual\s+propert\w*", "HIGH", 18, "Overbroad IP assignment may include pre-employment work"),
    (r"all\s+(inventions|works|creations|developments)", "HIGH", 18, "Captures personal projects — negotiate explicit carve-outs"),
    (r"liquidated\s+damages", "MEDIUM", 14, "Pre-set penalty may exceed actual loss — challengeable"),
    (r"indemnif\w*\s+(and\s+hold\s+harmless)?", "MEDIUM", 12, "Unlimited indemnity clauses are risky"),
    (r"arbitrat\w*", "MEDIUM", 12, "Removes your right to approach civil courts directly"),
    (r"limitation\s+of\s+liabilit\w*", "MEDIUM", 10, "May cap your recovery far below actual damages"),
    (r"govern\w*\s+by\s+the\s+laws?\s+of", "MEDIUM", 8, "Foreign/inconvenient jurisdiction raises litigation cost"),
    (r"auto(matic)?[\s-]?renew\w*", "LOW", 6, "Silently renews — easy to miss, hard to exit"),
    (r"no\s+oral\s+(modification|amendment)", "LOW", 4, "All changes must be written — verbal agreements won't count"),
    (r"entire\s+agreement", "LOW", 3, "Prior negotiations and promises are wiped out"),
    (r"waiver\s+of\s+jury", "LOW", 3, "Not applicable in India but signals foreign template risk"),
    (r"force\s+majeure", "MEDIUM", 8, "Broad force majeure can let the other party off the hook"),
    (r"sole\s+discretion", "MEDIUM", 10, "Gives other party unchecked decision-making power"),
    (r"without\s+cause", "HIGH", 20, "Termination without reason — no recourse for you"),
    (r"assign\w*\s+(this\s+)?agreement", "MEDIUM", 10, "They can transfer your contract to any third party"),
    (r"background\s+check", "LOW", 3, "Ensure scope is proportionate — not blanket surveillance"),
]

GREEN_FLAGS: list[tuple[str, int]] = [
    (r"mutual\s+termination", -8),
    (r"30\s+days?\s+notice", -6),
    (r"60\s+days?\s+notice", -8),
    (r"90\s+days?\s+notice", -6),
    (r"severance", -8),
    (r"dispute\s+resolution", -4),
    (r"mediation", -4),
    (r"govern\w*\s+by\s+(the\s+laws?\s+of\s+)?india", -5),
    (r"as\s+per\s+applicable\s+law", -3),
]


def _find_excerpt(text: str, pattern: str, window: int = 220) -> str:
    match = re.search(pattern, text, re.IGNORECASE)
    if not match:
        return "Clause detected but exact excerpt unavailable."
    idx = match.start()
    start = max(0, idx - 40)
    end = min(len(text), idx + window)
    raw = text[start:end].replace("\n", " ").strip()
    return f"...{raw}..."


def score_contract(text: str, role: str) -> dict:
    total = 0
    found_flags = []
    green_found = []

    for pattern, severity, weight, desc in RED_FLAGS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            excerpt = _find_excerpt(text, pattern)
            total += weight
            found_flags.append({
                "clause":      match.group(0).title(),
                "severity":    severity,
                "weight":      weight,
                "description": desc,
                "excerpt":     excerpt,
            })

    for pattern, reduction in GREEN_FLAGS:
        if re.search(pattern, text, re.IGNORECASE):
            total = max(0, total + reduction)
            green_found.append(pattern.replace(r"\s+", " ").replace("\\", "").title())

    found_flags.sort(key=lambda x: x["weight"], reverse=True)
    final = min(95, total)
    grade = "HIGH" if final > 60 else "MODERATE" if final > 30 else "LOW"

    role_advice = {
        "Employee":               "Focus on non-compete, IP ownership, and termination asymmetry.",
        "Tenant":                 "Focus on deposit forfeiture clauses, unilateral eviction rights, and repair liability.",
        "Freelancer / Contractor":"Focus on IP assignment, payment timelines, and kill-fee clauses.",
        "Buyer":                  "Focus on 'as is' clauses, dispute jurisdiction, and hidden indemnity.",
        "Seller":                 "Focus on payment security, return/refund terms, and liability caps.",
        "Service Provider":       "Focus on scope creep language, IP ownership, and payment terms.",
        "Borrower":               "Focus on default triggers, interest compounding, and security clauses.",
        "Investor":               "Focus on anti-dilution, liquidation preference, and drag-along rights.",
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