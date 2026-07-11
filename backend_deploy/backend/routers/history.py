"""
backend/routers/history.py
Unified history endpoint — cases, contracts, roadmaps, notices.
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime
from middleware.auth import get_current_user
from database import cases_col, audits_col, roadmaps_col, notices_col

router = APIRouter(prefix="/api/history", tags=["history"])


def _serialize(doc: dict) -> dict:
    doc["_id"] = str(doc["_id"])
    return doc


@router.get("/all")
async def get_all_history(
    user=Depends(get_current_user),
    limit: int = Query(default=10, ge=5, le=100),
):
    email = user["email"]
    fetch = limit * 2

    # ── Cases ─────────────────────────────────────────────────
    cases = []
    async for doc in cases_col.find(
        {"username": email},
        {"query": 1, "case_type": 1, "win_prob": 1, "grade": 1, "created_at": 1}
    ).sort("created_at", -1).limit(fetch):
        grade = doc.get("grade", "Moderate")
        color = "teal" if grade == "Strong" else "amber" if grade == "Moderate" else "coral"
        cases.append({
            "_id":         str(doc["_id"]),
            "type":        "case",
            "title":       doc.get("query", "")[:80],
            "subtitle":    doc.get("case_type", "General"),
            "badge":       f"{doc.get('win_prob', 0)}% · {grade}",
            "badge_color": color,
            "route":       "/dashboard/case-mirror",
            "result_id":   str(doc["_id"]),
            "created_at":  doc.get("created_at", datetime.utcnow()),
        })

    # ── Contract Audits ───────────────────────────────────────
    audits = []
    async for doc in audits_col.find(
        {"username": email},
        {"role": 1, "grade": 1, "risk_score": 1, "flag_count": 1,
         "text_preview": 1, "created_at": 1}
    ).sort("created_at", -1).limit(fetch):
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
    roadmaps = []
    async for doc in roadmaps_col.find(
        {"username": email},
        {"situation": 1, "jurisdiction": 1, "created_at": 1}
    ).sort("created_at", -1).limit(fetch):
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
    notices = []
    async for doc in notices_col.find(
        {"username": email},
        {"context": 1, "tone": 1, "created_at": 1}
    ).sort("created_at", -1).limit(fetch):
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

    # ── Merge + Sort + Slice ──────────────────────────────────
    merged = cases + audits + roadmaps + notices
    merged.sort(key=lambda x: x["created_at"], reverse=True)

    for item in merged:
        if isinstance(item["created_at"], datetime):
            item["created_at"] = item["created_at"].isoformat()

    return {
        "items": merged[:limit],
        "total": len(merged),
    }


@router.delete("/{item_type}/{item_id}")
async def delete_history_item(
    item_type: str,
    item_id:   str,
    user=Depends(get_current_user),
):
    col_map = {
        "case":     cases_col,
        "contract": audits_col,
        "roadmap":  roadmaps_col,
        "notice":   notices_col,
    }

    if item_type not in col_map:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown type '{item_type}'. Must be one of: case, contract, roadmap, notice"
        )

    try:
        oid = ObjectId(item_id)
    except (InvalidId, Exception):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid MongoDB ObjectId: {item_id}"
        )

    try:
        result = await col_map[item_type].delete_one({
            "_id":      oid,
            "username": user["email"],
        })
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database error during delete: {str(e)}"
        )

    # Idempotent — return 200 even if already deleted
    return {"deleted": result.deleted_count > 0}