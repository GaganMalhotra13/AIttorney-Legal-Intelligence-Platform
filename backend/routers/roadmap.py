from fastapi import APIRouter, Depends
from middleware.auth import get_current_user
import sys, os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from utils.ai import generate_roadmap

router = APIRouter(prefix="/api/roadmap", tags=["roadmap"])

@router.post("/")
async def create_roadmap(
    body: dict,
    user=Depends(get_current_user)
):
    result = generate_roadmap(
        body.get("situation", ""),
        body.get("jurisdiction", "India (General)")
    )
    return {"steps": result}
@router.post("/generate")
async def create_roadmap_generate(body: dict, user=Depends(get_current_user)):
    result = generate_roadmap(
        body.get("situation", ""),
        body.get("jurisdiction", "India (General)")
    )
    return {"steps": result}