# backend/database.py
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

load_dotenv()

client = AsyncIOMotorClient(os.getenv("MONGO_URL"))
db     = client[os.getenv("MONGO_DB")]

# Collections
users_col    = db["users"]
cases_col    = db["case_searches"]
audits_col   = db["contract_audits"]
notices_col  = db["notices"]
roadmaps_col = db["roadmaps"]
refresh_tokens_col = db["refresh_tokens"]
documents_col       = db["documents"]      # ← ADD
tracker_col         = db["court_dates"]    # ← ADD

async def ping_db():
    await refresh_tokens_col.create_index(
        "expires_at",
        expireAfterSeconds=0
    )