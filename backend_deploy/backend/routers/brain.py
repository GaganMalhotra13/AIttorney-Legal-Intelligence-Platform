# backend/routers/brain.py
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from middleware.auth import get_current_user
from schemas.brain import (
    OpponentRequest, EvidenceRequest, SettlementRequest,
    JurisdictionRequest, TimelineRequest, BriefRequest,
    FIRRequest, MediationRequest, LimitationRequest, ComparatorRequest
)
from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request

limiter = Limiter(key_func=get_remote_address)

import sys
import os
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
from utils.legal_brain import (
    analyze_opponent, evidence_checklist, estimate_settlement,
    jurisdiction_advisor, case_strength_timeline, generate_legal_brief,
    fir_draft, mediation_script, limitation_checker, case_comparator
)
from config import MODEL

router = APIRouter(prefix="/api/brain", tags=["brain"])


def _safe(prompt: str) -> str:
    """Direct Gemini call for endpoints not in legal_brain.py."""
    try:
        resp = MODEL.generate_content(prompt)
        return resp.text if resp.parts else "⚠️ Response blocked by safety filters."
    except Exception as e:
        return f"❌ API Error: {e}"


# ── Existing 10 modules ───────────────────────────────────────

@router.post("/opponent")
@limiter.limit("20/minute")

async def opponent(request: Request, b: OpponentRequest, user=Depends(get_current_user)):
    return {"result": analyze_opponent(b.query, b.live_context)}

@router.post("/evidence")
@limiter.limit("20/minute")
async def evidence(request: Request, b: EvidenceRequest, user=Depends(get_current_user)):
    return {"result": evidence_checklist(b.query, b.case_type)}

@router.post("/settlement")
@limiter.limit("20/minute")
async def settlement(request: Request, b: SettlementRequest, user=Depends(get_current_user)):
    return {"result": estimate_settlement(b.query, b.claim_amount, b.case_type, b.live_context)}

@router.post("/jurisdiction")
@limiter.limit("20/minute")
async def jurisdiction(request: Request, b: JurisdictionRequest, user=Depends(get_current_user)):
    return {"result": jurisdiction_advisor(b.query, b.location)}

@router.post("/timeline")
@limiter.limit("20/minute")
async def timeline(request: Request, b: TimelineRequest, user=Depends(get_current_user)):
    return {"result": case_strength_timeline(b.query, b.score_data, b.case_type)}

@router.post("/brief")
@limiter.limit("20/minute")
async def brief(request: Request, b: BriefRequest, user=Depends(get_current_user)):
    return {"result": generate_legal_brief(
        b.query, b.live_context, b.score_data, b.laws_text, b.party_name
    )}

@router.post("/fir")
@limiter.limit("20/minute")
async def fir(request: Request, b: FIRRequest, user=Depends(get_current_user)):
    return {"result": fir_draft(b.query, b.complainant, b.accused_desc, b.location)}

@router.post("/mediation")
@limiter.limit("20/minute")
async def mediation(request: Request, b: MediationRequest, user=Depends(get_current_user)):
    return {"result": mediation_script(
        b.query, b.your_position, b.other_party, b.ideal_outcome
    )}

@router.post("/limitation")
@limiter.limit("20/minute")
async def limitation(request: Request, b: LimitationRequest, user=Depends(get_current_user)):
    return {"result": limitation_checker(b.case_type, b.incident_date, b.query)}

@router.post("/compare")
@limiter.limit("20/minute")
async def compare(request: Request, b: ComparatorRequest, user=Depends(get_current_user)):
    return {"result": case_comparator(b.query, b.live_context, b.case_type)}


# ── Module 11: WhatsApp Evidence Analyzer ────────────────────

class WhatsAppRequest(BaseModel):
    chat_export: str        # pasted WhatsApp export text
    case_type:   str
    your_number: str = ""


@router.post("/analyze-whatsapp")
@limiter.limit("20/minute")
async def analyze_whatsapp(request: Request, body: WhatsAppRequest, user=Depends(get_current_user)):
    """
    Analyzes WhatsApp chat exports for legally relevant admissions,
    threats, payment confirmations, or promises.
    Tells user how to make it admissible under IT Act Section 65B.
    """
    result = _safe(f"""
Analyze this WhatsApp chat export for legal relevance in an Indian court.
Case type: {body.case_type}
Chat: {body.chat_export[:3000]}

### Key Admissions Found
[Messages where the other party admitted fault, promised payment, or accepted liability]

### Legally Relevant Exchanges
[Specific messages that could serve as evidence — quote them exactly]

### Threats or Harassment (if any)
[Messages that constitute threats, coercion, or harassment under IPC/BNS]

### Timeline of Events
[Chronological reconstruction from the chat with dates]

### Payment Confirmations
[Any messages confirming amounts, transactions, or financial obligations]

### Admissibility Under IT Act Section 65B
[Exact steps to make this WhatsApp evidence admissible in Indian court]
[Who needs to certify it, what format, which court accepts it]

### Overall Evidence Strength
[Strong / Moderate / Weak — and why]
""")
    return {"analysis": result}
