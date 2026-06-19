# backend/routers/cases.py — upgraded for 3-value search return
from fastapi import APIRouter, Depends, HTTPException
from middleware.auth import get_current_user
from schemas.case import CaseRequest
from database import cases_col
from datetime import datetime
from bson import ObjectId
import sys, os
import hashlib
import time

# Simple in-memory cache — survives for server lifetime
_cache: dict = {}
_CACHE_TTL = 1800  # 30 minutes

def _cache_get(key: str):
    if key in _cache:
        data, ts = _cache[key]
        if time.time() - ts < _CACHE_TTL:
            return data
        del _cache[key]
    return None

def _cache_set(key: str, data: dict):
    _cache[key] = (data, time.time())
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if ROOT not in sys.path: sys.path.insert(0, ROOT)

from utils.search import get_live_cases
from utils.ai import  analyze_case_full
from utils.scoring import compute_win_probability
from utils.anonymize import anonymize

router = APIRouter(prefix="/api/cases", tags=["cases"])


@router.post("/analyze")
async def analyze(body: CaseRequest, user=Depends(get_current_user)):
    safe_query = anonymize(body.query)

    # New pipeline — 3 return values
    live_ctx, raw_results, landmarks = get_live_cases(safe_query)

    score_data = compute_win_probability(safe_query, live_ctx)
    result   = analyze_case_full(safe_query, live_ctx, body.language or "English", landmarks)
    laws     = result["laws"]
    analysis = result["analysis"]

    await cases_col.insert_one({
        "username":   user["email"],
        "query":      body.query[:500],
        "case_type":  body.case_type,
        "result":     analysis[:4000],
        "win_prob":   score_data["probability"],
        "grade":      score_data["grade"],
        "laws":       laws[:1000],
        "sources_count": len(raw_results),
        "landmarks_count": len(landmarks),
        "created_at": datetime.utcnow(),
    })

    return {
        "query":      body.query,
        "analysis":   analysis,
        "win_prob":   score_data["probability"],
        "grade":      score_data["grade"],
        "laws":       laws,
        "sources":    raw_results[:6],
        "landmarks":  landmarks[:3],       # ← NEW: landmark judgments
        "score_data": score_data,
    }


@router.get("/history")
async def get_history(user=Depends(get_current_user)):
    cursor = cases_col.find(
        {"username": user["email"]},
        {"query": 1, "case_type": 1, "win_prob": 1, "grade": 1, "created_at": 1}
    ).sort("created_at", -1).limit(15)
    return [
        {**doc, "_id": str(doc["_id"])}
        async for doc in cursor
    ]


@router.get("/stats")
async def get_stats(user=Depends(get_current_user)):
    pipeline = [
        {"$match": {"username": user["email"]}},
        {"$group": {
            "_id":      None,
            "total":    {"$count": {}},
            "avg_prob": {"$avg": "$win_prob"},
            "strong":   {"$sum": {"$cond": [{"$eq": ["$grade","Strong"]},   1, 0]}},
            "moderate": {"$sum": {"$cond": [{"$eq": ["$grade","Moderate"]}, 1, 0]}},
            "weak":     {"$sum": {"$cond": [{"$eq": ["$grade","Weak"]},     1, 0]}},
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


@router.delete("/{case_id}")
async def delete_case(case_id: str, user=Depends(get_current_user)):
    result = await cases_col.delete_one({
        "_id":      ObjectId(case_id),
        "username": user["email"]
    })
    if result.deleted_count == 0:
        raise HTTPException(404, "Case not found")
    return {"deleted": True}