# backend/routers/tracker.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from middleware.auth import get_current_user
from database import db
from datetime import datetime
from bson import ObjectId
import sys, os
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if ROOT not in sys.path: sys.path.insert(0, ROOT)
from config import MODEL

tracker_col = db["court_dates"]
router      = APIRouter(prefix="/api/tracker", tags=["tracker"])


class CourtDateBody(BaseModel):
    case_title:   str
    court_name:   str
    hearing_date: str   # "DD/MM/YYYY"
    hearing_time: str   # "10:30 AM"
    case_type:    str
    notes:        str = ""
    case_number:  str = ""


@router.post("/")
async def add_court_date(body: CourtDateBody, user=Depends(get_current_user)):
    # AI: what to prepare for this hearing
    prep = ""
    try:
        resp = MODEL.generate_content(f"""
Court hearing in 7 days. Case type: {body.case_type}
Case: {body.case_title}
Notes: {body.notes}

Give a 5-item preparation checklist for this hearing type.
Format as bullet points. Be specific and actionable.
""")
        prep = resp.text
    except Exception:
        pass

    result = await tracker_col.insert_one({
        "username":        user["email"],
        "case_title":      body.case_title,
        "court_name":      body.court_name,
        "hearing_date":    body.hearing_date,
        "hearing_time":    body.hearing_time,
        "case_type":       body.case_type,
        "notes":           body.notes,
        "case_number":     body.case_number,
        "preparation":     prep,
        "status":          "upcoming",
        "created_at":      datetime.utcnow(),
        "reminder_sent":   False,
    })
    return {"id": str(result.inserted_id), "preparation": prep}


@router.get("/")
async def get_court_dates(user=Depends(get_current_user)):
    cursor = tracker_col.find(
        {"username": user["email"]}
    ).sort("hearing_date", 1)
    dates = []
    async for d in cursor:
        d["_id"] = str(d["_id"])
        dates.append(d)
    return dates


@router.patch("/{date_id}/status")
async def update_status(
    date_id: str,
    status:  str,
    user=Depends(get_current_user),
):
    valid = ["upcoming", "completed", "postponed", "cancelled"]
    if status not in valid:
        raise HTTPException(400, f"Status must be one of: {valid}")
    result = await tracker_col.update_one(
        {"_id": ObjectId(date_id), "username": user["email"]},  # ← ADD username
        {"$set": {"status": status}}
    )
    if result.matched_count == 0:
        raise HTTPException(404, "Court date not found")
    return {"updated": True}

@router.delete("/{date_id}")
async def delete_date(date_id: str, user=Depends(get_current_user)):
    result = await tracker_col.delete_one({
        "_id":      ObjectId(date_id),
        "username": user["email"],          # ← ADD username
    })
    if result.deleted_count == 0:
        raise HTTPException(404, "Court date not found")
    return {"deleted": True}