# backend/routers/notices.py
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from middleware.auth import get_current_user
from database import notices_col
from datetime import datetime
import sys, os
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
from utils.ai import draft_notice

router = APIRouter(prefix="/api/notices", tags=["notices"])

class NoticeRequest(BaseModel):
    context:   str
    sender:    str = ""
    recipient: str = ""
    tone:      str = "Professional"

@router.post("/draft")
async def draft(body: NoticeRequest, user=Depends(get_current_user)):
    output = draft_notice(body.context, body.sender, body.recipient, body.tone)
    await notices_col.insert_one({
        "username":   user["email"],
        "context":    body.context[:500],
        "tone":       body.tone,
        "output":     output[:5000],
        "created_at": datetime.utcnow(),
    })
    return {"notice": output}
