# backend/routers/contracts.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from middleware.auth import get_current_user
from schemas.contract import AuditRequest, ChatRequest
from database import audits_col
from datetime import datetime
import sys
import os
import io

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from utils.ai import audit_contract, chat_with_contract, summarize_for_layman
from utils.contract_scorer import score_contract
from utils.vector_store import index_contract, semantic_search
from utils.ai import audit_contract, audit_contract_structured, chat_with_contract, summarize_for_layman

router = APIRouter(prefix="/api/contracts", tags=["contracts"])


@router.post("/audit")
async def audit_contract_route(body: AuditRequest, user=Depends(get_current_user)):
    # Layer 1 — fast deterministic regex (catches exact legal terms)
    regex_score = score_contract(body.text, body.role)

    # Layer 2 — AI structured detection (catches euphemisms/soft phrasing)
    ai_result = audit_contract_structured(body.text, body.role)

    # Merge — combine flags from both, dedupe by clause name
    seen_clauses = {f["clause"].lower() for f in regex_score["flags"]}
    merged_flags = list(regex_score["flags"])

    for flag in ai_result.get("flags", []):
        if flag["clause"].lower() not in seen_clauses:
            merged_flags.append(flag)
            seen_clauses.add(flag["clause"].lower())

    merged_flags.sort(key=lambda x: x["weight"], reverse=True)
    total_score = min(95, sum(f["weight"] for f in merged_flags))
    grade = "HIGH" if total_score > 60 else "MODERATE" if total_score > 30 else "LOW"

    final_score = {
        "score": total_score,
        "grade": grade,
        "flags": merged_flags,
        "green_flags": list(set(regex_score["green_flags"] + ai_result.get("green_flags", []))),
        "flag_count": len(merged_flags),
        "summary": ai_result.get("overall_verdict") or regex_score["summary"],
    }

    gemini_analysis = audit_contract(body.text, body.role)

    doc_id = None
    try:
        doc_id = index_contract(body.text, "uploaded")
    except Exception as e:
        print(f"⚠️ Vector indexing skipped: {e}")

    await audits_col.insert_one({
        "username":   user["email"],
        "role":       body.role,
        "risk_score": final_score["score"],
        "grade":      final_score["grade"],
        "created_at": datetime.utcnow(),
    })

    return {"score": final_score, "analysis": gemini_analysis, "doc_id": doc_id}

    await audits_col.insert_one({
        "username":   user["email"],
        "role":       body.role,
        "risk_score": score["score"],
        "grade":      score["grade"],
        "created_at": datetime.utcnow(),
    })
    return {"score": score, "analysis": gemini, "doc_id": doc_id}


@router.post("/chat")
async def chat_contract_route(body: ChatRequest, user=Depends(get_current_user)):
    relevant = semantic_search(body.question, body.doc_id) if body.doc_id else []
    context  = "\n\n".join(relevant) if relevant else body.context
    return {"answer": chat_with_contract(body.question, context)}


@router.post("/simplify")
async def simplify_contract_route(body: AuditRequest, user=Depends(get_current_user)):
    return {"result": summarize_for_layman(body.text)}
@router.post("/extract-pdf")
async def extract_pdf(
    file: UploadFile = File(...),
    user=Depends(get_current_user)
):
    contents = await file.read()
    try:
        from pypdf import PdfReader
        import io
        reader = PdfReader(io.BytesIO(contents))
        text = "".join(p.extract_text() or "" for p in reader.pages)
        return {"text": text[:15000]}
    except Exception as e:
        raise HTTPException(400, f"PDF extraction failed: {e}")

@router.post("/ocr-audit")
async def ocr_audit_route(
    file: UploadFile = File(...),
    role: str        = Form(...),
    user=Depends(get_current_user)
):
    """Upload scanned contract image -> extract text -> audit it."""
    try:
        from PIL import Image
        import pytesseract
    except ImportError:
        raise HTTPException(
            status_code=400,
            detail="OCR not available. Install: pip install pytesseract Pillow"
        )

    contents = await file.read()
    image    = Image.open(io.BytesIO(contents))
    text     = pytesseract.image_to_string(image)

    if len(text.strip()) < 100:
        raise HTTPException(
            status_code=400,
            detail="Could not extract enough text from image"
        )

    score  = score_contract(text, role)
    gemini = audit_contract(text, role)
    return {
        "extracted_text": text[:500],
        "score":          score,
        "analysis":       gemini
    }