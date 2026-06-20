"""
config.py — AIttorney
Central configuration: API keys, model setup, app-wide constants.
"""

import os
import random
import time
from dotenv import load_dotenv

load_dotenv()

# ── App Meta ────────────────────────────────────────────────
APP_NAME       = "AIttorney"
APP_DEVELOPER  = "GAGAN MALHOTRA"
APP_VERSION    = "2.1"
APP_TAGLINE    = "Legal Intelligence Platform"
APP_DISCLAIMER = (
    "AIttorney provides general legal information for educational purposes only. "
    "It is NOT a substitute for advice from a licensed attorney. "
    "Always consult a qualified advocate for your specific situation."
)

# ── Gemini Setup ─────────────────────────────────────────────
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY_1") or os.getenv("GEMINI_API_KEY_2") or os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL   = "gemini-2.0-flash"

# ── Groq Setup ───────────────────────────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_CLIENT  = None
if GROQ_API_KEY:
    try:
        from groq import Groq
        GROQ_CLIENT = Groq(api_key=GROQ_API_KEY)
        print("✅ Groq client initialized")
    except Exception as e:
        print(f"⚠️  Groq init failed: {e}")

# ── Groq Response Shim ───────────────────────────────────────
# ── Groq Response Shim ───────────────────────────────────────
class _DummyPart:
    def __init__(self, text):
        self.text = text

class _GroqResponse:
    """Mimics Gemini response shape so all callers work unchanged."""
    def __init__(self, text: str):
        self.text = text
        self.parts = [_DummyPart(text)] # Prevents 'if response.parts:' from crashing

# ── Model Shim ───────────────────────────────────────────────
class _ModelShim:
    def __init__(self):
        self._gemini_client = None
        self._sdk_version = None
        self._client = None # Prevents the AttributeError you are seeing
        self._init_gemini()

    def _init_gemini(self):
        if not GEMINI_API_KEY:
            print("⚠️  No GEMINI_API_KEY found in .env")
            return

        # Attempt 1: Try the NEW SDK (google-genai)
        try:
            from google import genai
            self._gemini_client = genai.Client(api_key=GEMINI_API_KEY)
            self._sdk_version = "new"
            print(f"✅ Gemini initialized via NEW SDK ({GEMINI_MODEL})")
            return
        except ImportError:
            pass

        # Attempt 2: Try the OLD SDK (google-generativeai)
        try:
            import google.generativeai as genai_old
            genai_old.configure(api_key=GEMINI_API_KEY)
            self._gemini_client = genai_old.GenerativeModel(GEMINI_MODEL)
            self._sdk_version = "old"
            self._client = self._gemini_client._client # Bind the native client
            print(f"✅ Gemini initialized via OLD SDK ({GEMINI_MODEL})")
        except Exception as e:
            print(f"⚠️  Gemini init failed completely: {e}")

    def generate_content(self, prompt: str):
        # ── Fast execution (No 10-second wait loops) ──────────────
        try:
            if self._sdk_version == "new":
                return self._gemini_client.models.generate_content(
                    model=GEMINI_MODEL,
                    contents=prompt
                )
            elif self._sdk_version == "old":
                return self._gemini_client.generate_content(prompt)
        except Exception as e:
            print(f"⚠️  Gemini API failed: {e}. Falling back to Groq...")

        # ── Instant Fall back to Groq ────────────────────────────────
        if GROQ_CLIENT:
            try:
                resp = GROQ_CLIENT.chat.completions.create(
    model="llama-3.3-70b-versatile",   # ← changed
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=2000,
                    temperature=0.3,
                )
                return _GroqResponse(resp.choices[0].message.content)
            except Exception as e:
                return _GroqResponse(f"❌ API Error: {e}")

        return _GroqResponse("❌ No AI API available. Check GEMINI_API_KEY and GROQ_API_KEY in .env")

MODEL = _ModelShim()

# ── Also expose a simple function for direct use ─────────────
def get_gemini_response(prompt: str) -> str:
    result = MODEL.generate_content(prompt)
    return result.text if result else "❌ No response"

# ── Search Config ────────────────────────────────────────────
MAX_SEARCH_RESULTS = 3
PDF_TEXT_LIMIT     = 6000
CHAT_HISTORY_LIMIT = 20

# ── Jurisdiction Options ─────────────────────────────────────
JURISDICTIONS = [
    "India (General)", "Delhi NCR", "Maharashtra",
    "Karnataka", "Tamil Nadu", "West Bengal",
    "Gujarat", "Rajasthan", "Other State / UT",
]

# ── Role Options ─────────────────────────────────────────────
AUDIT_ROLES = [
    "Employee", "Tenant", "Freelancer / Contractor",
    "Buyer", "Seller", "Service Provider",
    "Borrower", "Investor",
]

# ── Notice Tones ─────────────────────────────────────────────
NOTICE_TONES = {
    "Professional":  "Measured, formal, and polite. Requests compliance with goodwill.",
    "Strict":        "Assertive and firm. Sets a hard deadline with clear consequences.",
    "Final Warning": "Last-chance language. Signals imminent legal action if ignored.",
}

# ── Quick Scenario Presets ────────────────────────────────────
QUICK_SCENARIOS = [
    "— Select a quick scenario —",
    "Landlord refusing to return security deposit",
    "Cheque bounce / NI Act §138",
    "Consumer product defect / service deficiency",
    "Wrongful termination / employment dispute",
    "Property fraud or encroachment",
    "Online fraud / cyber crime",
    "Domestic violence / protection order",
    "Divorce / matrimonial dispute",
]