from fastapi import APIRouter, Depends
from middleware.auth import get_current_user
from database import roadmaps_col
from datetime import datetime
import sys, os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from utils.ai import generate_roadmap

router = APIRouter(prefix="/api/roadmap", tags=["roadmap"])


async def _generate_and_save(situation: str, jurisdiction: str, user_email: str) -> dict:
    result = generate_roadmap(situation, jurisdiction)

    insert_result = await roadmaps_col.insert_one({
        "username":     user_email,
        "situation":    situation[:500],
        "jurisdiction": jurisdiction,
        "steps":        result,              # ← full steps string saved
        "created_at":   datetime.utcnow(),
    })
    return {
        "steps":      result,
        "roadmap_id": str(insert_result.inserted_id),
    }


@router.post("/")
async def create_roadmap(body: dict, user=Depends(get_current_user)):
    return await _generate_and_save(
        body.get("situation",    ""),
        body.get("jurisdiction", "India (General)"),
        user["email"],
    )


@router.post("/generate")
async def create_roadmap_generate(body: dict, user=Depends(get_current_user)):
    return await _generate_and_save(
        body.get("situation",    ""),
        body.get("jurisdiction", "India (General)"),
        user["email"],
    )


@router.get("/{roadmap_id}")
async def get_roadmap(roadmap_id: str, user=Depends(get_current_user)):
    """Instant replay of a saved roadmap."""
    from bson import ObjectId
    from fastapi import HTTPException
    try:
        oid = ObjectId(roadmap_id)
    except Exception:
        raise HTTPException(400, "Invalid roadmap ID")

    doc = await roadmaps_col.find_one({
        "_id":      oid,
        "username": user["email"],
    })
    if not doc:
        raise HTTPException(404, "Roadmap not found")

    return {
        "roadmap_id":  str(doc["_id"]),
        "situation":   doc.get("situation",    ""),
        "jurisdiction":doc.get("jurisdiction", ""),
        "steps":       doc.get("steps",        ""),
    }