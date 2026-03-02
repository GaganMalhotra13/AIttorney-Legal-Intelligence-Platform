"""
config.py — AIttorney
Central configuration: API keys, model setup, app-wide constants.
"""

import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# ── App Meta ────────────────────────────────────────────────
APP_NAME        = "AIttorney"
APP_VERSION     = "2.1"
APP_TAGLINE     = "Legal Intelligence Platform"
APP_DISCLAIMER  = (
    "AIttorney provides general legal information for educational purposes only. "
    "It is NOT a substitute for advice from a licensed attorney. "
    "Always consult a qualified advocate for your specific situation."
)

# ── Gemini Setup ─────────────────────────────────────────────
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
genai.configure(api_key=GEMINI_API_KEY)

PREFERRED_MODELS = [
    "gemini-1.5-flash",
    "gemini-1.5-flash-latest",
    "gemini-1.5-pro",
    "gemini-pro",
]

def get_model():
    """Discover best available Gemini model, fall back gracefully."""
    try:
        available = [
            m.name.replace("models/", "")
            for m in genai.list_models()
            if "generateContent" in m.supported_generation_methods
        ]
        for preferred in PREFERRED_MODELS:
            if preferred in available:
                return genai.GenerativeModel(preferred)
        if available:
            return genai.GenerativeModel(available[0])
    except Exception:
        pass
    return genai.GenerativeModel("gemini-1.5-flash")

MODEL = get_model()

# ── Search Config ────────────────────────────────────────────
MAX_SEARCH_RESULTS  = 4
PDF_TEXT_LIMIT      = 15_000   # chars — keeps within free-tier token limits
CHAT_HISTORY_LIMIT  = 20       # max messages stored per session

# ── Jurisdiction Options ─────────────────────────────────────
JURISDICTIONS = [
    "India (General)",
    "Delhi NCR",
    "Maharashtra",
    "Karnataka",
    "Tamil Nadu",
    "West Bengal",
    "Gujarat",
    "Rajasthan",
    "Other State / UT",
]

# ── Role Options ─────────────────────────────────────────────
AUDIT_ROLES = [
    "Employee",
    "Tenant",
    "Freelancer / Contractor",
    "Buyer",
    "Seller",
    "Service Provider",
    "Borrower",
    "Investor",
]

# ── Notice Tones ─────────────────────────────────────────────
NOTICE_TONES = {
    "Professional":   "Measured, formal, and polite. Requests compliance with goodwill.",
    "Strict":         "Assertive and firm. Sets a hard deadline with clear consequences.",
    "Final Warning":  "Last-chance language. Signals imminent legal action if ignored.",
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