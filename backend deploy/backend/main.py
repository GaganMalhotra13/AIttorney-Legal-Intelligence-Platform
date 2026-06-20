# backend/main.py — AIttorney v7
import sys
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from fastapi import FastAPI
from fastapi import Request

from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from routers import auth, cases, contracts, notices, brain, lawyers, roadmap
from routers import analytics, documents, tracker          # ← MISSING
from database import ping_db

app = FastAPI(
    title="AIttorney API",
    description="Legal Intelligence Platform — 11 AI Modules · 18+ Sources · Landmark Judgments",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8501",
        "https://aittorney-legalintelligence.vercel.app/",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.middleware("http")
async def utf8_middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    return response
# ── Routers ───────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(cases.router)
app.include_router(contracts.router)
app.include_router(notices.router)
app.include_router(brain.router)
app.include_router(lawyers.router)
app.include_router(roadmap.router)
app.include_router(analytics.router)                       # ← MISSING
app.include_router(documents.router)                       # ← MISSING
app.include_router(tracker.router)                         # ← MISSING

# ── Startup ───────────────────────────────────────────────────
@app.on_event("startup")
async def startup():
    try:
        await ping_db()
        print("✅ MongoDB connected")
    except Exception as e:
        print(f"❌ MongoDB failed: {e}")

    scraper = bool(os.getenv("SCRAPER_API_KEY"))
    groq    = bool(os.getenv("GROQ_API_KEY"))
    cohere  = bool(os.getenv("COHERE_API_KEY"))
    print(f"🔍 IndianKanoon scraping:    {'✅ Active' if scraper else '⚠️  Disabled'}")
    print(f"⚡ Groq compression:         {'✅ Active' if groq   else '⚠️  Disabled'}")
    print(f"🎯 Cohere reranking:         {'✅ Active' if cohere else '⚠️  Disabled'}")

# ── Health ────────────────────────────────────────────────────
@app.get("/")
async def root():
    return {
        "app":     "AIttorney API",
        "version": "2.0.0",
        "modules": 11,
        "sources": 18,
        "enhanced": {
            "kanoon_scraping":  bool(os.getenv("SCRAPER_API_KEY")),
            "groq_compression": bool(os.getenv("GROQ_API_KEY")),
            "cohere_reranking": bool(os.getenv("COHERE_API_KEY")),
        },
        "docs": "/docs",
    }

@app.api_route("/health", methods=["GET", "HEAD"])
async def health():
    return {"status": "ok"}

@app.get("/health/scraper")
async def scraper_health():
    try:
        from utils.kanoon_scraper import search_indiankanoon
        results = search_indiankanoon("cheque bounce", 1)
        return {
            "status":  "ok" if results else "degraded",
            "results": len(results),
            "scraper_api_key_set": bool(os.getenv("SCRAPER_API_KEY")),
        }
    except Exception as e:
        return {"status": "error", "detail": str(e)}