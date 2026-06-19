from fastapi import APIRouter, Depends
from middleware.auth import get_current_user
import sys, os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from utils.search import get_live_cases
from config import MODEL

router = APIRouter(prefix="/api/lawyers", tags=["lawyers"])


def _safe(prompt: str) -> str:
    try:
        resp = MODEL.generate_content(prompt)
        if hasattr(resp, "text") and resp.text:
            return resp.text
        if hasattr(resp, "parts") and not resp.parts:
            return "Response blocked by safety filters."
        return str(resp)
    except Exception as e:
        return f"API Error: {e}"


@router.get("/find")
async def find_lawyers(
    case_type: str,
    location: str,
    user=Depends(get_current_user),
):
    ctx, results, _ = get_live_cases(
        f"best lawyer advocate {case_type} {location} contact"
    )

    prompt = (
        f"Based on these search results, list 3-5 advocates or law firms "
        f"specializing in {case_type} in {location}.\n\n"
        f"For each provide:\n"
        f"- Name or Firm name\n"
        f"- Specialization\n"
        f"- Contact details if available\n"
        f"- Why recommended for this case type\n\n"
        f"Search results: {ctx[:2000]}\n\n"
        f"If specific names not found, give general guidance on finding "
        f"{case_type} lawyers in {location} and what to look for."
    )

    summary = _safe(prompt)

    return {
        "summary": summary,
        "raw_results": results[:5],
        "case_type": case_type,
        "location": location,
    }