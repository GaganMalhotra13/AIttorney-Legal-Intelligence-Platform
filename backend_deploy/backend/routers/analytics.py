# backend/routers/analytics.py
from fastapi import APIRouter, Depends
from middleware.auth import get_current_user
from database import cases_col, audits_col, notices_col, db
from datetime import datetime, timedelta

tracker_col = db["court_dates"]
router      = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/overview")
async def get_overview(user=Depends(get_current_user)):
    """Single endpoint for full dashboard — reduces frontend API calls."""
    email = user["email"]

    # Parallel counts
    total_cases = await cases_col.count_documents({"username": email})
    total_audits  = await audits_col.count_documents({"username": email})
    total_notices = await notices_col.count_documents({"username": email})
    upcoming_dates= await tracker_col.count_documents({
        "username": email, "status": "upcoming"
    })

    # Win probability average
    prob_agg = await cases_col.aggregate([
        {"$match": {"username": email}},
        {"$group": {"_id": None, "avg": {"$avg": "$win_prob"}}},
    ]).to_list(1)
    avg_prob = round(prob_agg[0]["avg"] if prob_agg else 0, 1)

    # Grade distribution
    grade_agg = await cases_col.aggregate([
        {"$match": {"username": email}},
        {"$group": {"_id": "$grade", "count": {"$count": {}}}},
    ]).to_list(10)
    grades = {g["_id"]: g["count"] for g in grade_agg if g["_id"]}

    # Recent cases (last 5)
    recent = []
    cursor = cases_col.find(
        {"username": email},
        {"query": 1, "win_prob": 1, "grade": 1, "created_at": 1}
    ).sort("created_at", -1).limit(5)
    async for c in cursor:
        c["_id"] = str(c["_id"])
        recent.append(c)

    # Weekly activity (last 8 weeks)
    eight_weeks_ago = datetime.utcnow() - timedelta(weeks=8)
    weekly_agg = await cases_col.aggregate([
        {"$match": {"username": email, "created_at": {"$gte": eight_weeks_ago}}},
        {"$group": {
            "_id":   {"week": {"$week": "$created_at"}, "year": {"$year": "$created_at"}},
            "count": {"$count": {}},
        }},
        {"$sort": {"_id.year": 1, "_id.week": 1}},
    ]).to_list(8)

    return {
        "totals": {
            "cases":          total_cases,
            "audits":         total_audits,
            "notices":        total_notices,
            "upcoming_dates": upcoming_dates,
            "avg_win_prob":   avg_prob,
        },
        "grades":       grades,
        "recent_cases": recent,
        "weekly_trend": [
            {"label": f"W{w['_id']['week']}", "count": w["count"]}
            for w in weekly_agg
        ],
    }