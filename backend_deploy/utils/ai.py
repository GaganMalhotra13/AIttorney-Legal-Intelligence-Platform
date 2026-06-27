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
    return _safe(f"""You are a strict legal auditor reviewing a contract for a {role} in India.

Find exactly 3 critical issues. For EACH issue use EXACTLY this format with no deviation:

SEVERITY: [HIGH/MEDIUM/LOW]
CLAUSE: [Short clause name]
PROBLEM: [Why this hurts a {role} specifically — one concrete sentence]
EXCERPT: [Quote the exact relevant text from contract — max one sentence]
FAIR VERSION: [What a balanced clause would say instead — one sentence]

After the 3 issues, add:
OVERALL VERDICT: [One sentence summary of the contract overall]
TOP PRIORITY TO NEGOTIATE: [Single most important clause to push back on]

Rules:
- Do NOT use markdown headers, bullets, or bold
- Do NOT add any text outside this exact format
- Each SEVERITY/CLAUSE/PROBLEM/EXCERPT/FAIR VERSION must be on its own line
- Leave one blank line between each issue

Contract text ({role} perspective):
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


def draft_notice(context: str, sender: str, recipient: str, tone: str) -> str:
    tone_instructions = {
        "Professional": "formal and measured tone, leaving room for amicable resolution",
        "Strict": "firm and assertive tone, with a hard deadline and clear legal consequences",
        "Final Warning": "final warning tone — this is the last communication before legal action, unambiguous",
    }.get(tone, "professional tone")

    return _safe(f"""You are a senior Indian legal advocate drafting a formal legal notice.

Use this information:
{context}

Draft a complete, professionally formatted legal notice following EXACTLY this structure:

[City], [Date: use today's date or leave as __________]

TO,
[Recipient name and designation]
[Recipient address — use provided address or "__________, __________, __________"]

SUBJECT: LEGAL NOTICE FOR [NOTICE TYPE IN CAPS]

Sir/Madam,

Under instructions from and on behalf of my client, [Sender Full Name], [Sender Address], 
I [Advocate Name — leave as "__________"] do hereby serve upon you this legal notice:

1. FACTS OF THE CASE:
[Write 2-3 numbered paragraphs detailing the facts chronologically, using provided details.
Include specific dates, amounts, and actions. Use "on __________ (date)" where date unknown.]

2. LEGAL VIOLATIONS:
[Cite 2-3 specific applicable Indian laws/sections violated, e.g.:
- Section ___ of the [Relevant Act]
- Consumer Protection Act, 2019 (if applicable)
- Indian Contract Act, 1872 Section 73 (if breach of contract)]

3. DEMAND / RELIEF SOUGHT:
[State the exact relief demanded clearly — use provided relief sought.
Include specific amounts where provided, or "₹__________" where unknown.]

4. NOTICE PERIOD:
You are hereby called upon to comply with the above demands within [X] days of receipt 
of this notice, failing which my client shall be constrained to initiate appropriate 
legal proceedings before the competent court/forum at your risk, cost and consequences.

Yours faithfully,

[Advocate Name]
[Advocate's Office Address]
[Bar Council Enrollment No: __________]

On behalf of: {sender}

---
NOTE: This notice has been prepared for educational reference. Underlined blank spaces 
(__________) require manual completion with verified information before dispatch.
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