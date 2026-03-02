"""utils/anonymize.py — PII redaction before sending to LLM."""
import re

def anonymize(text: str) -> str:
    """Scrub phone numbers, emails, and Aadhaar-like numbers from text."""
    text = re.sub(r'\b\d{10}\b', '[PHONE REDACTED]', text)
    text = re.sub(r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}\b', '[AADHAAR REDACTED]', text)
    text = re.sub(r'\S+@\S+\.\S+', '[EMAIL REDACTED]', text)
    text = re.sub(r'\b[A-Z]{5}\d{4}[A-Z]\b', '[PAN REDACTED]', text)
    return text