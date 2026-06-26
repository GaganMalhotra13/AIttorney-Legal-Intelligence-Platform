"""
backend/routers/cases.py
Case analysis with Redis caching + security fixes.
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from middleware.auth import get_current_user
from schemas.case import CaseRequest
from database import cases_col
from datetime import datetime
from bson import ObjectId
import sys, os, hashlib
from slowapi import Limiter
from slowapi.util import get_remote_address

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from utils.search import get_live_cases
from utils.ai import analyze_case_full
from utils.scoring import compute_win_probability
from utils.anonymize import anonymize
from utils.cache import cache_get, cache_set, make_key

router  = APIRouter(prefix="/api/cases", tags=["cases"])
limiter = Limiter(key_func=get_remote_address)

CACHE_TTL = 1800  # 30 minutes


# ── Analyze ───────────────────────────────────────────────────
@router.post("/analyze")
@limiter.limit("10/minute")
async def analyze(
    request:  Request,
    body:     CaseRequest,
    user=Depends(get_current_user),
):
    safe_query = anonymize(body.query)

    # ── Cache check ───────────────────────────────────────────
    cache_key = make_key(
        "analyze",
        safe_query,
        body.case_type,
        body.language or "English",
    )
    cached = await cache_get(cache_key)
    if cached:
        print(f"⚡ Cache hit — skipping pipeline for: {safe_query[:50]}")
        # Still save to MongoDB so it appears in user's history
        # but skip the expensive pipeline entirely
        cached_response = cached.copy()
        insert_result = await cases_col.insert_one({
            "username":        user["email"],
            "query":           body.query[:500],
            "case_type":       body.case_type,
            "result":          cached["analysis"][:4000],
            "win_prob":        cached["win_prob"],
            "grade":           cached["grade"],
            "laws":            cached["laws"][:1000],
            "sources_count":   len(cached.get("sources", [])),
            "landmarks_count": len(cached.get("landmarks", [])),
            "created_at":      datetime.utcnow(),
            "full_sources":    cached.get("sources", []),
            "full_landmarks":  cached.get("landmarks", []),
            "full_score_data": cached.get("score_data", {}),
            "from_cache":      True,
        })
        cached_response["id"] = str(insert_result.inserted_id)
        return cached_response

    # ── Full pipeline ─────────────────────────────────────────
    live_ctx, raw_results, landmarks = get_live_cases(safe_query)
    score_data = compute_win_probability(safe_query, live_ctx)

    result   = analyze_case_full(
        safe_query,
        live_ctx,
        body.language or "English",
        landmarks,
    )
    laws     = result["laws"]
    analysis = result["analysis"]

    insert_result = await cases_col.insert_one({
        "username":        user["email"],
        "query":           body.query[:500],
        "case_type":       body.case_type,
        "result":          analysis[:4000],
        "win_prob":        score_data["probability"],
        "grade":           score_data["grade"],
        "laws":            laws[:1000],
        "sources_count":   len(raw_results),
        "landmarks_count": len(landmarks),
        "created_at":      datetime.utcnow(),
        "full_sources":    raw_results[:6],
        "full_landmarks":  landmarks[:3],
        "full_score_data": score_data,
        "from_cache":      False,
    })

    response = {
        "id":         str(insert_result.inserted_id),
        "query":      body.query,
        "analysis":   analysis,
        "win_prob":   score_data["probability"],
        "grade":      score_data["grade"],
        "laws":       laws,
        "sources":    raw_results[:6],
        "landmarks":  landmarks[:3],
        "score_data": score_data,
    }

    # ── Cache the result for 30 minutes ──────────────────────
    await cache_set(cache_key, response, ttl=CACHE_TTL)
    return response


# ── History ───────────────────────────────────────────────────
@router.get("/history")
async def get_history(user=Depends(get_current_user)):
    cursor = (
        cases_col
        .find(
            {"username": user["email"]},
            {"query": 1, "case_type": 1, "win_prob": 1,
             "grade": 1, "created_at": 1}
        )
        .sort("created_at", -1)
        .limit(15)
    )
    cases = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        cases.append(doc)
    return cases


# ── Stats ─────────────────────────────────────────────────────
@router.get("/stats")
async def get_stats(user=Depends(get_current_user)):
    pipeline = [
        {"$match": {"username": user["email"]}},
        {"$group": {
            "_id":      None,
            "total":    {"$count": {}},
            "avg_prob": {"$avg": "$win_prob"},
            "strong":   {"$sum": {"$cond": [{"$eq": ["$grade", "Strong"]},   1, 0]}},
            "moderate": {"$sum": {"$cond": [{"$eq": ["$grade", "Moderate"]}, 1, 0]}},
            "weak":     {"$sum": {"$cond": [{"$eq": ["$grade", "Weak"]},     1, 0]}},
        }},
    ]
    result = await cases_col.aggregate(pipeline).to_list(1)
    stats  = result[0] if result else {}
    return {
        "total":    stats.get("total", 0),
        "avg_prob": round(stats.get("avg_prob") or 0, 1),
        "strong":   stats.get("strong", 0),
        "moderate": stats.get("moderate", 0),
        "weak":     stats.get("weak", 0),
    }


# ── Get saved result — MUST BE AFTER /history AND /stats ─────
@router.get("/{case_id}")
async def get_case_result(case_id: str, user=Depends(get_current_user)):
    try:
        oid = ObjectId(case_id)
    except Exception:
        raise HTTPException(400, "Invalid case ID format")

    doc = await cases_col.find_one({
        "_id":      oid,
        "username": user["email"],
    })
    if not doc:
        raise HTTPException(404, "Case not found")

    return {
        "id":         str(doc["_id"]),
        "query":      doc["query"],
        "analysis":   doc["result"],
        "win_prob":   doc["win_prob"],
        "grade":      doc["grade"],
        "laws":       doc["laws"],
        "sources":    doc.get("full_sources", []),
        "landmarks":  doc.get("full_landmarks", []),
        "score_data": doc.get("full_score_data", {}),
    }


# ── Delete ────────────────────────────────────────────────────
@router.delete("/{case_id}")
async def delete_case(case_id: str, user=Depends(get_current_user)):
    try:
        oid = ObjectId(case_id)
    except Exception:
        raise HTTPException(400, "Invalid case ID format")

    result = await cases_col.delete_one({
        "_id":      oid,
        "username": user["email"],
    })
    if result.deleted_count == 0:
        raise HTTPException(404, "Case not found")
    return {"deleted": True}