# backend/main.py — AIttorney v7
import sys
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from fastapi import FastAPI
from fastapi import HTTPException, Request

from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, JSONResponse
from dotenv import load_dotenv

load_dotenv()

from routers import auth, cases, contracts, notices, brain, lawyers, roadmap
from routers import analytics, documents, tracker          # ← MISSING
from database import ping_db
from fastapi import Request
from fastapi.responses import Response
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from routers.history import router as history_router

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(
    title="AIttorney API",
    description="Legal Intelligence Platform — 11 AI Modules · 18+ Sources · Landmark Judgments",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8501",
        "https://aittorney-legalintelligence.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.middleware("http")
async def security_headers(request: Request, call_next):
    try:
        response = await call_next(request)
    except HTTPException as exc:
        response = JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )
    except Exception:
        response = JSONResponse(
            status_code=500,
            content={"detail": "Internal Server Error"},
        )
    response.headers["X-Content-Type-Options"]  = "nosniff"
    response.headers["X-Frame-Options"]          = "DENY"
    response.headers["X-XSS-Protection"]         = "1; mode=block"
    response.headers["Referrer-Policy"]           = "strict-origin-when-cross-origin"
    response.headers["Content-Type"]              = "application/json; charset=utf-8"
    response.headers["Access-Control-Allow-Origin"]      = "https://aittorney-legalintelligence.vercel.app"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"]     = "DELETE, GET, HEAD, OPTIONS, PATCH, POST, PUT"
    response.headers["Access-Control-Allow-Headers"]     = "Authorization, Content-Type, X-Requested-With"
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
app.include_router(history_router)

# ── Startup ───────────────────────────────────────────────────
@app.on_event("startup")
async def startup():
    # JWT secret validation
    jwt_secret = os.getenv("JWT_SECRET", "")
    if len(jwt_secret) < 32:
        raise RuntimeError(
            "JWT_SECRET must be at least 32 characters. "
            "Generate: python -c \"import secrets; print(secrets.token_hex(32))\""
        )

    # MongoDB
    try:
        await ping_db()
        print("✅ MongoDB connected")
    except Exception as e:
        print(f"❌ MongoDB failed: {e}")

    # Redis
    from utils.cache import cache_ping
    redis_ok = await cache_ping()
    print(f"{'✅' if redis_ok else '⚠️ '} Redis: {'connected' if redis_ok else 'using in-memory fallback'}")

    # Feature flags
    scraper = bool(os.getenv("SCRAPER_API_KEY"))
    groq    = bool(os.getenv("GROQ_API_KEY"))
    cohere  = bool(os.getenv("COHERE_API_KEY"))
    print(f"🔍 IndianKanoon: {'✅' if scraper else '⚠️  add SCRAPER_API_KEY'}")
    print(f"⚡ Groq:         {'✅' if groq   else '⚠️  add GROQ_API_KEY'}")
    print(f"🎯 Cohere:       {'✅' if cohere else '⚠️  add COHERE_API_KEY'}")

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
@app.get("/health/cache")
async def cache_health():
    from utils.cache import cache_ping
    ok = await cache_ping()
    return {
        "status":  "redis" if ok else "in-memory",
        "healthy": True,
    }
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
    # ─────────────────────────────────────────────
# AIttorney Legal Intelligence Platform
# Copyright © 2026 Gagan Malhotra
# All Rights Reserved — Unauthorized use prohibited
# ─────────────────────────────────────────────