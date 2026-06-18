# backend/routers/documents.py
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from middleware.auth import get_current_user
from database import documents_col
from datetime import datetime
import hashlib, base64
import sys, os
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if ROOT not in sys.path: sys.path.insert(0, ROOT)
from config import MODEL

router = APIRouter(prefix="/api/documents", tags=["documents"])

def _summarize_doc(text: str) -> dict:
    """AI extracts metadata from any legal document."""
    try:
        resp = MODEL.generate_content(f"""
Extract metadata from this legal document. Respond ONLY in JSON:
{{
  "doc_type": "FIR/Contract/Judgment/Notice/Other",
  "parties": ["name1", "name2"],
  "key_dates": ["DD/MM/YYYY description"],
  "case_number": "if present or null",
  "court": "if mentioned or null",
  "summary": "2 sentences",
  "tags": ["tag1", "tag2", "tag3"]
}}
Document: {text[:3000]}
""")
        import json
        clean = resp.text.replace("```json","").replace("```","").strip()
        return json.loads(clean)
    except Exception:
        return {
            "doc_type": "Other", "parties": [], "key_dates": [],
            "case_number": None, "court": None,
            "summary": "Document uploaded", "tags": []
        }

@router.post("/upload")
async def upload_document(
    file:  UploadFile = File(...),
    label: str        = Form(""),
    user=Depends(get_current_user)
):
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:  # 10MB limit
        raise HTTPException(400, "File too large. Maximum 10MB.")

    # Extract text
    text = ""
    if file.filename.endswith(".pdf"):
        try:
            from pypdf import PdfReader
            import io
            reader = PdfReader(io.BytesIO(content))
            text   = "".join(p.extract_text() or "" for p in reader.pages)[:8000]
        except Exception:
            text = content.decode("utf-8", errors="ignore")[:8000]
    else:
        text = content.decode("utf-8", errors="ignore")[:8000]

    # AI metadata extraction
    metadata = _summarize_doc(text)

    # Store (base64 for small files, reference for large)
    doc_hash = hashlib.md5(content).hexdigest()

    doc = {
        "username":    user["email"],
        "filename":    file.filename,
        "label":       label or file.filename,
        "size_bytes":  len(content),
        "hash":        doc_hash,
        "content_b64": base64.b64encode(content).decode() if len(content) < 2*1024*1024 else None,
        "text_preview":text[:500],
        "metadata":    metadata,
        "created_at":  datetime.utcnow(),
    }
    result = await documents_col.insert_one(doc)
    return {"id": str(result.inserted_id), "metadata": metadata}


@router.get("/")
async def list_documents(user=Depends(get_current_user)):
    cursor = documents_col.find(
        {"username": user["email"]},
        {"content_b64": 0}  # don't return file bytes in list
    ).sort("created_at", -1)
    docs = []
    async for d in cursor:
        d["_id"] = str(d["_id"])
        docs.append(d)
    return docs


@router.post("/search")
async def search_documents(
    query: str,
    user=Depends(get_current_user)
):
    """AI-powered semantic search across user's documents."""
    # Get all docs for this user
    cursor = documents_col.find(
        {"username": user["email"]},
        {"text_preview": 1, "metadata": 1, "filename": 1, "label": 1, "_id": 1}
    )
    docs = []
    async for d in cursor:
        d["_id"] = str(d["_id"])
        docs.append(d)

    if not docs:
        return []

    # Ask Gemini to rank them
    doc_summaries = "\n".join([
        f"Doc {i+1} [{d['label']}]: {d.get('metadata',{}).get('summary','')}"
        for i, d in enumerate(docs)
    ])
    try:
        resp = MODEL.generate_content(f"""
User is searching for: "{query}"
Documents available:
{doc_summaries}
Return a JSON array of document indices (1-based) sorted by relevance, most relevant first.
Return ONLY the JSON array, e.g. [2, 1, 3]
""")
        import json
        indices = json.loads(resp.text.strip().replace("```json","").replace("```",""))
        ranked  = [docs[i-1] for i in indices if 0 < i <= len(docs)]
        return ranked[:5]
    except Exception:
        return docs[:5]