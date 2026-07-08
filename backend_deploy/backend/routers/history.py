"""
backend/routers/history.py
Unified history endpoint — merges cases, audits, roadmaps, notices
sorted by date with pagination.
"""
from fastapi import APIRouter, Depends, Query
from middleware.auth import get_current_user
from database import cases_col, audits_col, roadmaps_col, notices_col
from bson import ObjectId
from datetime import datetime

router = APIRouter(prefix="/api/history", tags=["history"])


def _str_id(doc: dict) -> dict:
    doc["_id"] = str(doc["_id"])
    return doc


@router.get("/all")
async def get_all_history(
    user=Depends(get_current_user),
    limit: int = Query(default=10, ge=5, le=100),
):
    """
    Returns unified history across all features, sorted by date desc.
    Each item has a consistent shape for the frontend to render.
    """
    email = user["email"]
    fetch = limit * 2   # fetch more per collection so merge has enough after sort+slice

    # ── Cases ────────────────────────────────────────────────
    cases_cursor = cases_col.find(
        {"username": email},
        {"query": 1, "case_type": 1, "win_prob": 1, "grade": 1, "created_at": 1}
    ).sort("created_at", -1).limit(fetch)

    cases = []
    async for doc in cases_cursor:
        grade = doc.get("grade", "Moderate")
        color = "teal" if grade == "Strong" else "amber" if grade == "Moderate" else "coral"
        cases.append({
            "_id":        str(doc["_id"]),
            "type":       "case",
            "title":      doc.get("query", "")[:80],
            "subtitle":   doc.get("case_type", "General"),
            "badge":      f"{doc.get('win_prob', 0)}% · {grade}",
            "badge_color": color,
            "route":      "/dashboard/case-mirror",
            "result_id":  str(doc["_id"]),
            "created_at": doc.get("created_at", datetime.utcnow()),
        })

    # ── Contract Audits ───────────────────────────────────────
    audits_cursor = audits_col.find(
        {"username": email},
        {"role": 1, "grade": 1, "risk_score": 1, "flag_count": 1,
         "text_preview": 1, "created_at": 1}
    ).sort("created_at", -1).limit(fetch)

    audits = []
    async for doc in audits_cursor:
        grade = doc.get("grade", "LOW")
        color = "coral" if grade == "HIGH" else "amber" if grade == "MODERATE" else "teal"
        preview = doc.get("text_preview", "Contract audit")[:60]
        audits.append({
            "_id":         str(doc["_id"]),
            "type":        "contract",
            "title":       preview or "Contract audit",
            "subtitle":    doc.get("role", "Employee"),
            "badge":       f"{grade} RISK · {doc.get('flag_count', 0)} flags",
            "badge_color": color,
            "route":       "/dashboard/contract-audit",
            "result_id":   str(doc["_id"]),
            "created_at":  doc.get("created_at", datetime.utcnow()),
        })

    # ── Roadmaps ──────────────────────────────────────────────
    roadmaps_cursor = roadmaps_col.find(
        {"username": email},
        {"situation": 1, "jurisdiction": 1, "created_at": 1}
    ).sort("created_at", -1).limit(fetch)

    roadmaps = []
    async for doc in roadmaps_cursor:
        roadmaps.append({
            "_id":         str(doc["_id"]),
            "type":        "roadmap",
            "title":       doc.get("situation", "Legal roadmap")[:80],
            "subtitle":    doc.get("jurisdiction", "India (General)"),
            "badge":       "4-Step Plan",
            "badge_color": "blue",
            "route":       "/dashboard/roadmap",
            "result_id":   str(doc["_id"]),
            "created_at":  doc.get("created_at", datetime.utcnow()),
        })

    # ── Notices ───────────────────────────────────────────────
    notices_cursor = notices_col.find(
        {"username": email},
        {"context": 1, "tone": 1, "created_at": 1}
    ).sort("created_at", -1).limit(fetch)

    notices = []
    async for doc in notices_cursor:
        notices.append({
            "_id":         str(doc["_id"]),
            "type":        "notice",
            "title":       doc.get("context", "Legal notice")[:80],
            "subtitle":    doc.get("tone", "Professional"),
            "badge":       f"{doc.get('tone', 'Professional')} Tone",
            "badge_color": "purple",
            "route":       "/dashboard/notice-drafter",
            "result_id":   str(doc["_id"]),
            "created_at":  doc.get("created_at", datetime.utcnow()),
        })

    # ── Merge + Sort + Paginate ───────────────────────────────
    all_items = cases + audits + roadmaps + notices
    all_items.sort(key=lambda x: x["created_at"], reverse=True)

    # Convert datetime to ISO string for JSON
    for item in all_items:
        if isinstance(item["created_at"], datetime):
            item["created_at"] = item["created_at"].isoformat()

    return {
        "items": all_items[:limit],
        "total": len(all_items),
    }


@router.delete("/{item_type}/{item_id}")
async def delete_history_item(
    item_type: str,
    item_id:   str,
    user=Depends(get_current_user),
):
    """Delete any history item by type and ID."""
    from fastapi import HTTPException
    col_map = {
        "case":     cases_col,
        "contract": audits_col,
        "roadmap":  roadmaps_col,
        "notice":   notices_col,
    }
    col = col_map.get(item_type)
    if not col:
        raise HTTPException(400, f"Unknown type: {item_type}")

    try:
        oid = ObjectId(item_id)
    except Exception:
        raise HTTPException(400, "Invalid ID format")

    result = await col.delete_one({
        "_id":      oid,
        "username": user["email"],
    })
    if result.deleted_count == 0:
        raise HTTPException(404, "Item not found")

    return {"deleted": True}