# backend/routers/lawyers.py
from fastapi import APIRouter, Depends
from middleware.auth import get_current_user
import sys
import os
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
from utils.search import get_live_cases
from config import MODEL

router = APIRouter(prefix="/api/lawyers", tags=["lawyers"])


def _safe(prompt: str) -> str:
    try:
        resp = MODEL.generate_content(prompt)
        return resp.text if resp.parts else "⚠️ Response blocked by safety filters."
    except Exception as e:
        return f"❌ API Error: {e}"


@router.get("/find")
async def find_lawyers(
    case_type: str,
    location:  str,
    user=Depends(get_current_user)
):
    """Search for advocates specializing in this case type near location."""
    ctx, results = get_live_cases(
        f"best lawyer advocate {case_type} {location} contact"
    )
    summary = _safe(f"""
Based on these search results, list 3-5 advocates or law firms
specializing in {case_type} in {location}.

For each provide:
- Name / Firm name
- Specialization
- Contact details if available
- Why recommended for this case type

Search results: {ctx[:2000]}

If specific names not found, give general guidance on finding
{case_type} lawyers in {location} and what to look for.
""")
    return {
        "summary":     summary,
        "raw_results": results[:5],
        "case_type":   case_type,
        "location":    location
    }
