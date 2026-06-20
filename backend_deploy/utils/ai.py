"""
utils/ai.py — AIttorney v7
All Gemini calls upgraded to use landmark judgments + compressed context.
"""
from config import MODEL
import json
import re


def _safe(prompt: str) -> str:
    try:
        r = MODEL.generate_content(prompt)
        if hasattr(r, 'text') and r.text:
            return r.text
        if hasattr(r, 'parts') and not r.parts:
            return "⚠️ Response blocked by safety filters."
        return str(r)
    except Exception as e:
        return f"❌ API Error: {e}"

def analyze_case_full(
    query: str,
    live_context: str,
    language: str,
    landmarks: list[dict] | None = None,
) -> dict:
    """Single Gemini call returning both laws and analysis."""
    landmark_block = ""
    if landmarks:
        landmark_block = "\n\nLANDMARK PRECEDENTS:\n"
        for lm in landmarks[:3]:
            landmark_block += (
                f"- {lm.get('title','Unknown')} "
                f"({lm.get('court','')}, {lm.get('date','')})"
                f" Citations: {lm.get('citations',0)}\n"
                f"  {lm.get('snippet','')[:200]}\n"
            )

    result = _safe(f"""
You are an educational legal assistant for India.
Language: {language}

Search context:
{live_context}
{landmark_block}

User situation: {query}

Respond with EXACTLY this structure:

LAWS:
- [Act Name, Year] Section [X] - [what it covers]
- [Act Name, Year] Section [X] - [what it covers]
- [Act Name, Year] Section [X] - [what it covers]

ANALYSIS:
### Summary
2-3 sentences on what this legally is.

### Your Legal Position
Strong or weak and specifically why.

### Landmark Cases That Apply
Name relevant cases or say none found.

### What You Should Do
1. [Most urgent action]
2. [Second action]
3. [Third action]
4. [Final step]

### Realistic Expectation
Timeline, cost, probable outcome.

Educational information only. Consult a licensed advocate.
""")

    # Split laws and analysis
    laws = ""
    analysis = ""
    if "ANALYSIS:" in result:
        parts = result.split("ANALYSIS:", 1)
        laws_raw = parts[0].replace("LAWS:", "").strip()
        laws = laws_raw
        analysis = parts[1].strip()
    else:
        analysis = result

    return {"laws": laws, "analysis": analysis}

def get_similar_cases(query: str, context: str) -> str:
    return _safe(f"""
Situation: "{query}"
Context: {context[:2000]}

Name 1-2 specific Indian court cases with relevant precedent from the context.
For each: Full case name, court, year, and one sentence on why it directly applies.
If none found in context, say so explicitly. Never fabricate case names or citations.
""")


def audit_contract(text: str, role: str) -> str:
    return _safe(f"""
Strict legal auditor reviewing a contract for a {role} in India.

Find exactly 3 critical issues. For each use EXACTLY this format:

SEVERITY: [HIGH/MEDIUM/LOW]
CLAUSE: [Name of clause]
PROBLEM: [Why this hurts a {role} specifically — be concrete]
EXCERPT: [Quote the relevant part of the contract — max 1 sentence]
FAIR VERSION: [What a balanced clause would say instead]

Then:
OVERALL VERDICT: [One sentence]
TOP PRIORITY TO NEGOTIATE: [The single most important clause to push back on]

Contract text:
{text[:6000]}
""")
def audit_contract_structured(text: str, role: str) -> dict:
    """
    AI-based clause risk detection — returns structured data instead of prose.
    Catches euphemistic/soft-worded risk clauses that regex patterns miss.
    Falls back to Groq if Gemini quota is exhausted.
    """
    prompt = f"""You are a contract risk analyzer for a {role} reviewing this contract.

Find ALL clauses that could disadvantage a {role}, including softly-worded
or euphemistic ones (e.g. "may be reassigned" = unilateral transfer risk,
"shall be considered final" = no appeal mechanism, "discretionary" = no
guaranteed pay).

Respond ONLY with valid JSON, no markdown, no commentary:

{{
  "flags": [
    {{
      "clause": "Short name for the clause",
      "severity": "HIGH" or "MEDIUM" or "LOW",
      "weight": <number 3-25 based on severity>,
      "description": "Why this disadvantages a {role}, one sentence",
      "excerpt": "The exact quoted text from the contract, max 200 chars"
    }}
  ],
  "green_flags": ["short phrase for any genuinely protective clause found"],
  "overall_verdict": "One sentence summary"
}}

Find every real risk, even subtle ones. If genuinely no risks exist, return empty flags array.

Contract text:
{text[:6000]}
"""

    def _parse(raw: str) -> dict | None:
        try:
            clean = re.sub(r"```json\s*|\s*```", "", raw).strip()
            parsed = json.loads(clean)
            if "flags" in parsed:
                return parsed
        except Exception:
            pass
        return None

    # ── Try Gemini first (via existing MODEL shim with its own retry/backoff) ──
    try:
        result = MODEL.generate_content(prompt)
        raw = result.text if hasattr(result, 'text') else str(result)
        parsed = _parse(raw)
        if parsed:
            return parsed
        print("⚠️ Gemini returned unparseable JSON, trying Groq fallback...")
    except Exception as e:
        print(f"⚠️ Gemini structured audit failed: {e}, trying Groq fallback...")

    # ── Groq fallback — direct call, bypasses MODEL shim's Gemini-first logic ──
    try:
        from config import GROQ_CLIENT
        if GROQ_CLIENT:
            resp = GROQ_CLIENT.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1500,
                temperature=0.2,
            )
            raw = resp.choices[0].message.content
            parsed = _parse(raw)
            if parsed:
                return parsed
            print("⚠️ Groq also returned unparseable JSON")
    except Exception as e:
        print(f"⚠️ Groq structured audit failed: {e}")

    # ── Both failed — return empty, regex layer still provides baseline ──
    return {"flags": [], "green_flags": [], "overall_verdict": ""}


def chat_with_contract(question: str, context: str) -> str:
    return _safe(f"""
Answer this question about the contract. Be direct and specific.
If the answer is in the document, cite the relevant clause.
If not addressed: say "This isn't addressed in the contract."
Do not speculate beyond what the document says.

Contract:
{context[:5000]}

Question: {question}
""")


def summarize_for_layman(text: str) -> str:
    return _safe(f"""
Translate this legal text to plain English for a non-lawyer.
Short sentences. Explain every piece of jargon in plain terms.

Legal text:
{text[:4000]}

Format:
**Plain Summary:** [2-3 sentences]

**Key Points:**
• [point]
• [point]
• [point]

**Jargon Explained:**
[term]: [meaning in 5 words]
[term]: [meaning]

**What This Means For You:**
[1-2 sentences on practical impact]
""")


def draft_notice(
    context: str,
    sender: str,
    recipient: str,
    tone: str,
) -> str:
    tones = {
        "Professional": "Formal and measured. Requests compliance with goodwill. Polite but firm.",
        "Strict":       "Assertive. Hard 15-day deadline. Consequences clearly implied.",
        "Final Warning":"Last chance. Imminent legal action. No ambiguity whatsoever.",
    }
    return _safe(f"""
Draft a formal legal notice. Educational purposes only.
Issue: {context}
From: {sender or '[Sender Full Name]'}
To:   {recipient or '[Recipient Full Name]'}
Tone: {tones.get(tone, tones['Professional'])}
Jurisdiction: India

Use EXACTLY this structure:

[SENDER NAME]
[Address]
[Date]

TO,
[RECIPIENT NAME]
[Address]

SUBJECT: Legal Notice regarding [brief subject]

Sir/Madam,

[BACKGROUND — 2 sentences on the facts]

[GRIEVANCE — What went wrong, specific dates and amounts if mentioned]

[LEGAL BASIS — Reference applicable law without being overly technical]

[DEMAND — Exactly what you want them to do and by when]

[CONSEQUENCE — What happens if they don't comply]

Yours faithfully,
[Sender Name]

---
Generated by AIttorney for educational purposes only.
Have this reviewed by a licensed advocate before sending.
""")


def generate_roadmap(situation: str, jurisdiction: str) -> str:
    return _safe(f"""
Legal issue in {jurisdiction}: "{situation}"

Create an exact 4-step procedural plan.
Format EXACTLY as shown — no deviation:

STEP 1: [Short title]
Action: [What to do — 2 concrete sentences with specific next steps]
Law: [Exact section/act that governs this step, or N/A]
Timeline: [How long this step takes]

STEP 2: [Short title]
Action: [...]
Law: [...]
Timeline: [...]

STEP 3: [Short title]
Action: [...]
Law: [...]
Timeline: [...]

STEP 4: [Short title]
Action: [...]
Law: [...]
Timeline: [...]

India-specific. Educational only. Be concrete — no generic advice.
""")