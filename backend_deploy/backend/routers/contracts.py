# backend/routers/contracts.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from middleware.auth import get_current_user
from schemas.contract import AuditRequest, ChatRequest
from database import audits_col
from datetime import datetime
import sys, os, io

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from utils.ai import audit_contract, audit_contract_structured, chat_with_contract, summarize_for_layman
from utils.contract_scorer import score_contract
from utils.vector_store import index_contract, semantic_search

router = APIRouter(prefix="/api/contracts", tags=["contracts"])


@router.post("/audit")
async def audit_contract_route(body: AuditRequest, user=Depends(get_current_user)):
    regex_score = score_contract(body.text, body.role)
    ai_result   = audit_contract_structured(body.text, body.role)

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
        "score":       total_score,
        "grade":       grade,
        "flags":       merged_flags,
        "green_flags": list(set(regex_score["green_flags"] + ai_result.get("green_flags", []))),
        "flag_count":  len(merged_flags),
        "summary":     ai_result.get("overall_verdict") or regex_score["summary"],
    }

    gemini_analysis = audit_contract(body.text, body.role)

    doc_id = None
    try:
        doc_id = index_contract(body.text, "uploaded")
    except Exception as e:
        print(f"⚠️ Vector indexing skipped: {e}")

    # ── Save FULL result for history replay ──────────────────
    insert_result = await audits_col.insert_one({
        "username":      user["email"],
        "role":          body.role,
        "risk_score":    final_score["score"],
        "grade":         final_score["grade"],
        "full_score":    final_score,          # ← complete flags + green_flags
        "full_analysis": gemini_analysis,      # ← full prose analysis
        "text_preview":  body.text[:300],      # ← first 300 chars as title hint
        "flag_count":    final_score["flag_count"],
        "created_at":    datetime.utcnow(),
    })

    return {
        "score":    final_score,
        "analysis": gemini_analysis,
        "doc_id":   doc_id,
        "audit_id": str(insert_result.inserted_id),   # ← return ID for replay
    }


@router.get("/{audit_id}")
async def get_audit_result(audit_id: str, user=Depends(get_current_user)):
    """Instant replay of a saved contract audit."""
    from bson import ObjectId
    try:
        oid = ObjectId(audit_id)
    except Exception:
        raise HTTPException(400, "Invalid audit ID")

    doc = await audits_col.find_one({
        "_id":      oid,
        "username": user["email"],
    })
    if not doc:
        raise HTTPException(404, "Audit not found")

    return {
        "audit_id": str(doc["_id"]),
        "score":    doc.get("full_score",    {}),
        "analysis": doc.get("full_analysis", ""),
        "role":     doc.get("role",          "Employee"),
        "grade":    doc.get("grade",         "LOW"),
    }


@router.post("/chat")
async def chat_contract_route(body: ChatRequest, user=Depends(get_current_user)):
    relevant = semantic_search(body.question, body.doc_id) if body.doc_id else []
    context  = "\n\n".join(relevant) if relevant else body.context
    return {"answer": chat_with_contract(body.question, context)}


@router.post("/simplify")
async def simplify_contract_route(body: AuditRequest, user=Depends(get_current_user)):
    return {"result": summarize_for_layman(body.text)}


@router.post("/extract-pdf")
async def extract_pdf(file: UploadFile = File(...), user=Depends(get_current_user)):
    contents = await file.read()
    try:
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(contents))
        text   = "".join(p.extract_text() or "" for p in reader.pages)
        return {"text": text[:15000]}
    except Exception as e:
        raise HTTPException(400, f"PDF extraction failed: {e}")


@router.post("/ocr-audit")
async def ocr_audit_route(
    file: UploadFile = File(...),
    role: str        = Form(...),
    user=Depends(get_current_user)
):
    contents  = await file.read()
    mime_type = file.content_type or "image/jpeg"
    filename  = (file.filename or "").lower()

    if filename.endswith(".pdf"):
        try:
            from pypdf import PdfReader
            reader = PdfReader(io.BytesIO(contents))
            text   = "".join(p.extract_text() or "" for p in reader.pages)
        except Exception as e:
            raise HTTPException(400, f"PDF extraction failed: {e}")
    else:
        from utils.ai import extract_text_from_image
        text = extract_text_from_image(contents, mime_type)
        if not text or len(text.strip()) < 50:
            raise HTTPException(400, "Could not extract enough text from image.")

    score   = score_contract(text, role)
    gemini  = audit_contract(text, role)
    return {"extracted_text": text[:500], "score": score, "analysis": gemini}