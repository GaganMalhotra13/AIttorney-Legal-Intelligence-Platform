# backend/routers/documents.py
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Query
import json
from bson import ObjectId
from middleware.auth import get_current_user
from database import documents_col
from datetime import datetime
import hashlib, base64
import sys, os, re
import re as _re

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
def _extract_snippet(text: str, query: str, window: int = 200) -> str:
    """Find where query terms appear and return surrounding context."""
    if not text or not query:
        return ""
    text_lower = text.lower()
    query_words = [w for w in query.lower().split() if len(w) > 2]

    best_idx = -1
    for word in query_words:
        idx = text_lower.find(word)
        if idx != -1:
            best_idx = idx
            break

    if best_idx == -1:
        return text[:200].replace("\n", " ").strip() + "…"

    start   = max(0, best_idx - 50)
    end     = min(len(text), best_idx + window)
    snippet = text[start:end].replace("\n", " ").strip()
    return ("…" if start > 0 else "") + snippet + ("…" if end < len(text) else "")


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
    safe_filename = os.path.basename(file.filename or "unknown")
    safe_filename = re.sub(r"[^\w\s\-_\.]", "", safe_filename)[:255]
    doc = {
        "username":    user["email"],
        "filename":    safe_filename,
        "label":       label or safe_filename,
        "size_bytes":  len(content),
        "content_text": text[:8000],    # ← must be saved here

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


@router.get("/search")
async def search_documents(
    q: str = Query(..., min_length=2, max_length=200),
    user=Depends(get_current_user),
):
    # Fetch all user documents including stored text
    cursor = documents_col.find(
        {"username": user["email"]},
        {"label": 1, "metadata": 1, "size_bytes": 1,
         "created_at": 1, "content_text": 1}   # ← include content_text
    )
    docs = await cursor.to_list(length=100)

    if not docs:
        return []

    # Build summaries for Gemini ranking
    summaries = "\n".join([
        f"{i+1}. {doc.get('label','')}: {doc.get('metadata',{}).get('summary','')}"
        for i, doc in enumerate(docs)
    ])

    ranking_prompt = f"""You are a document search engine.
Query: "{q}"
Documents:
{summaries}

Return ONLY a JSON array of document numbers in relevance order (most relevant first).
Example: [3, 1, 5, 2, 4]
Return only the JSON array, nothing else."""

    try:
        from config import MODEL
        result  = MODEL.generate_content(ranking_prompt)
        raw     = result.text.strip()
        clean   = _re.sub(r"```json\s*|\s*```", "", raw).strip()
        ranking = json.loads(clean)
        ranked_docs = []
        for rank in ranking:
            if 1 <= rank <= len(docs):
                ranked_docs.append(docs[rank - 1])
        # Add any missed docs at end
        ranked_ids = {str(docs[r-1]["_id"]) for r in ranking if 1 <= r <= len(docs)}
        for doc in docs:
            if str(doc["_id"]) not in ranked_ids:
                ranked_docs.append(doc)
    except Exception:
        ranked_docs = docs  # fallback: unranked

    # Build response with snippet
    response = []
    for doc in ranked_docs:
        content_text = doc.get("content_text", "")
        snippet      = _extract_snippet(content_text, q)
        entry = {
            "_id":        str(doc["_id"]),
            "label":      doc.get("label", ""),
            "size_bytes": doc.get("size_bytes", 0),
            "created_at": doc.get("created_at", ""),
            "metadata":   doc.get("metadata", {}),
            "snippet":    snippet,   # ← matched excerpt with context
        }
        response.append(entry)

    return response

@router.delete("/{document_id}")
async def delete_document(document_id: str, user=Depends(get_current_user)):
    try:
        oid = ObjectId(document_id)
    except Exception:
        raise HTTPException(400, "Invalid document ID format")

    result = await documents_col.delete_one({
        "_id": oid,
        "username": user["email"],
    })
    if result.deleted_count == 0:
        raise HTTPException(404, "Document not found")

    return {"status": "deleted"}