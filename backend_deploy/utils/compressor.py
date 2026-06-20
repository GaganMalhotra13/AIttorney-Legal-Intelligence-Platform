"""
utils/compressor.py
Groq-powered context compression using Llama 3 70B.

Why: After scraping + reranking, we have 6-10 results with full text.
That's potentially 15,000+ tokens — too much for Gemini's context window
and expensive. Groq compresses it to ~600 focused words in <1 second
(Groq runs at 500 tokens/sec on Llama 3).

Result: Gemini gets a dense, relevant, accurate summary instead of
raw search soup. Better analysis, faster, cheaper.

Free tier: Unlimited on Groq free plan.
"""
import os
import httpx

GROQ_KEY  = os.getenv("GROQ_API_KEY", "")
GROQ_URL  = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"


def compress_legal_context(
    raw_context: str,
    query:       str,
    max_words:   int = 600,
) -> str:
    """
    Compress raw search results into a focused legal summary.
    Preserves: case names, section numbers, court names, dates, key rulings.
    Removes: navigation text, ads, repeated boilerplate.

    Falls back to truncation if Groq unavailable.
    """
    if not GROQ_KEY:
        return raw_context[:4000]  # simple truncation fallback

    prompt = f"""You are a legal research assistant. Compress these Indian court search results 
into a focused {max_words}-word summary for the query: "{query}"

Rules:
- Preserve ALL case names (e.g. "Maneka Gandhi v. Union of India")
- Preserve ALL section numbers (e.g. "Section 138 NI Act", "Article 21")
- Preserve ALL court names and years
- Preserve ALL key legal principles and rulings
- Remove navigation text, ads, repeated boilerplate
- Write in dense, information-rich prose
- If a case is directly relevant, quote the key holding in one sentence

Search results to compress:
{raw_context[:8000]}

Compressed summary:"""

    try:
        resp = httpx.post(
            GROQ_URL,
            headers={
                "Authorization": f"Bearer {GROQ_KEY}",
                "Content-Type":  "application/json",
            },
            json={
                "model":       GROQ_MODEL,
                "messages":    [{"role": "user", "content": prompt}],
                "max_tokens":  800,
                "temperature": 0.1,  # low temp for factual compression
            },
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"].strip()

    except Exception:
        return raw_context[:4000]  # fallback


def extract_landmark_holdings(
    judgment_texts: list[dict],
    query:          str,
) -> str:
    """
    Given a list of landmark judgment full texts,
    extract the key holding from each one.
    Returns a structured summary of what each landmark decided.
    """
    if not GROQ_KEY or not judgment_texts:
        return ""

    cases_block = "\n\n---\n\n".join([
        f"CASE: {j.get('title', 'Unknown')}\n"
        f"COURT: {j.get('court', '')}\n"
        f"DATE: {j.get('date', '')}\n"
        f"TEXT: {j.get('full_text', j.get('snippet', ''))[:1500]}"
        for j in judgment_texts[:3]
    ])

    prompt = f"""For the legal query: "{query}"

Extract the KEY HOLDING from each of these Indian court cases.
Format each as:
[Case Name] ([Court], [Year]): [One sentence on what was decided and why it matters for this query]

Cases:
{cases_block}

Key holdings:"""

    try:
        resp = httpx.post(
            GROQ_URL,
            headers={"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"},
            json={
                "model":       GROQ_MODEL,
                "messages":    [{"role": "user", "content": prompt}],
                "max_tokens":  400,
                "temperature": 0.1,
            },
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"].strip()
    except Exception:
        return ""