# AIttorney — Legal Intelligence Platform

> AI-powered legal research for the Indian legal system. Describe a legal situation in plain English, get win probability, applicable laws, real landmark judgments, and 11 on-demand AI modules — built for the 50 million Indians who can't afford an advocate just to ask "where do I stand?"

**Live Demo:** [aittorney.vercel.app](#) · **API Docs:** [/docs](#) · **Status:** 9.1/10, locally functional, deployed

---

## What This Is

India has over 50 million pending court cases. Most people facing a legal situation — a bounced cheque, a defective product, an unfair termination — cannot afford an advocate just to understand their options. AIttorney takes a plain-language description of a legal situation and returns a structured intelligence report instead of a chatbot response.

This is explicitly educational. Every output carries a disclaimer. It is not a substitute for a licensed advocate.

---

## Core Features

| Feature | What It Does |
|---|---|
| **Case Mirror** | Win probability, applicable laws, landmark judgments, full analysis from one query |
| **11 AI Modules** | Opponent steelmanning, FIR drafting, settlement estimation, mediation scripts, limitation checker, case comparator, and more |
| **Contract Audit** | NLP risk scoring across 19 clause patterns + Gemini analysis + semantic chat |
| **Notice Drafter** | Formally structured legal notices in 3 tones, PDF export |
| **Legal Roadmap** | 4-step procedural action plan with laws and timelines |
| **Document Vault** | Upload legal docs, AI extracts metadata, semantic search |
| **Case Tracker** | Court date tracking with AI-generated preparation checklists |
| **Advocate Finder** | AI-curated advocate recommendations by case type and location |
| **Analytics** | MongoDB aggregation dashboard — win probability trends, usage patterns |

---

## Why This Isn't an API Wrapper

**A 4-stage RAG pipeline runs before the LLM sees a single token:**

```
18-source search (DuckDuckGo, parallelized)
        ↓
Direct IndianKanoon scraping (ScraperAPI — real judgments, real citation counts)
        ↓
Cohere semantic reranking (relevance, not SEO rank)
        ↓
Groq Llama3 compression (15,000 tokens → ~700 tokens, <1 second)
        ↓
Gemini 2.0 Flash — final legal reasoning
```

**A fully deterministic, explainable scoring engine** — not an LLM guess:

- 28 keyword signals with directional weights (Section 138 → +22, expired limitation period → -22)
- Baseline 50, clamped to [15, 88] — no case is ever "certain"
- 22 pytest unit tests across 8 test classes verify identical input always produces identical output

**Real vector RAG for contract chat** — not "paste the whole document":

- Contracts chunked into 500-char overlapping segments
- Embedded with `sentence-transformers` (all-MiniLM-L6-v2, 384 dimensions)
- ChromaDB cosine similarity retrieves top 3 relevant chunks per question
- Gemini answers only from retrieved chunks — grounded, not hallucinated

---

## Tech Stack

```
Frontend:   Next.js 14 (App Router) · TypeScript · Tailwind CSS · Framer Motion · Zustand
Backend:    FastAPI · Motor (async MongoDB) · python-jose · bcrypt
AI:         Gemini 2.0 Flash · Groq Llama 3.3 70B · Cohere rerank-english-v3.0
Search:     duckduckgo-search (parallelized) · ScraperAPI → IndianKanoon
Database:   MongoDB Atlas (Mumbai region)
Vector:     ChromaDB · sentence-transformers (contract chat only)
PDF:        ReportLab (generate) · pypdf (extract)
```

**Total operating cost: $0.** Every API runs on its free tier.

---

## Architecture

```
E:\aittorney\
├── config.py              # _ModelShim — Gemini SDK abstraction layer
├── utils/                  # Shared AI intelligence layer
│   ├── ai.py                # All Gemini calls
│   ├── scoring.py            # 28-signal win probability engine (22 tests)
│   ├── search.py              # 4-stage RAG pipeline (parallelized DDG)
│   ├── legal_brain.py          # 11 AI modules
│   ├── kanoon_scraper.py        # Direct IndianKanoon scraping
│   ├── reranker.py               # Cohere reranking
│   ├── compressor.py              # Groq context compression
│   ├── contract_scorer.py          # 19 NLP clause patterns
│   └── vector_store.py              # ChromaDB + sentence-transformers
├── backend/                # FastAPI REST API
│   ├── main.py               # App entry, CORS, router registration
│   ├── database.py            # MongoDB collections + indexes
│   ├── middleware/auth.py      # JWT + direct bcrypt
│   └── routers/                # auth, cases, brain, contracts, notices,
│                                 roadmap, analytics, documents, tracker, lawyers
└── frontend/                # Next.js 14 App Router
    ├── app/dashboard/         # 10 pages
    ├── lib/api.ts               # Axios + token refresh interceptor
    └── store/useStore.ts         # Zustand (persisted user only)
```

`utils/` lives outside `backend/` because the AI intelligence layer is decoupled from the API layer by design — every router adds the project root to `sys.path` to import it.

---

## Quick Start

### Prerequisites

```
Python 3.11+
Node 18+
MongoDB Atlas account (free M0 tier)
```

### 1. Clone and install

```bash

cd AIttorney-Legal-Intelligence-Platform

# Backend
pip install -r backend/requirements.txt

# Frontend
cd frontend && npm install && cd ..
```

### 2. Environment variables

Create `backend/.env`:

```env
MONGO_URL=mongodb+srv://user:pass@cluster.mongodb.net/
MONGO_DB=aittorney
JWT_SECRET=run: python -c "import secrets; print(secrets.token_hex(32))"
JWT_EXPIRE_HOURS=24
GEMINI_API_KEY_1=AIza...
GROQ_API_KEY=gsk_...
COHERE_API_KEY=...
SCRAPER_API_KEY=...
```

Create `frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Run

```bash
# Terminal 1 — backend
cd backend
uvicorn main:app --reload --port 8000

# Terminal 2 — frontend
cd frontend
npm run dev
```

Visit `http://localhost:3000`. Sign up with any email, or try the demo credentials shown on the login screen.

### 4. Run tests

```bash
pytest tests/test_scoring.py -v
```

---

## API Overview

Full interactive docs at `/docs` once running. Key endpoints:

```
POST   /api/auth/register          Create account
POST   /api/auth/login             Get JWT access + refresh tokens
POST   /api/cases/analyze          Full case analysis pipeline
POST   /api/brain/{module}         11 AI modules (opponent, fir, settlement, ...)
POST   /api/contracts/audit        NLP + AI contract risk analysis
POST   /api/contracts/chat         Semantic contract Q&A
POST   /api/notices/draft          Generate legal notice + PDF
POST   /api/roadmap/generate       4-step procedural plan
GET    /api/analytics/overview     Usage aggregation
GET    /api/lawyers/find           AI-curated advocate search
```

All routes except `/auth/*` require `Authorization: Bearer <token>`.

---

## Free APIs Used

| Service | Purpose | Free Tier |
|---|---|---|
| [Google AI Studio](https://aistudio.google.com) | Gemini 2.0 Flash — core reasoning | 1,500 req/day |
| [Groq Console](https://console.groq.com) | Llama 3.3 70B — context compression | 500 tok/sec, generous limits |
| [Cohere Dashboard](https://dashboard.cohere.com) | rerank-english-v3.0 — search ranking | Free trial tier |
| [ScraperAPI](https://scraperapi.com) | IndianKanoon direct scraping | 1,000 req/month |
| [MongoDB Atlas](https://mongodb.com/atlas) | Database (M0, Mumbai region) | 512MB forever |

---

## Engineering Decisions Worth Knowing

**Why not one model for everything** — Groq and Cohere don't do reasoning. They do fast mechanical tasks (compress text, rank documents) that Gemini would do slower and more expensively for the same result.

**Why direct bcrypt instead of passlib** — Python 3.13 removed an internal attribute passlib's bcrypt backend depends on. Direct `bcrypt.hashpw()` / `bcrypt.checkpw()` bypasses the dependency entirely.

**Why a `_ModelShim` in config.py** — Google deprecated `google.generativeai` mid-project. Rather than rewrite 50+ callers, a shim class translates the old `MODEL.generate_content(prompt)` pattern to the new `google.genai` SDK. Zero regression, one file changed.

**Why MongoDB over PostgreSQL** — No joins exist anywhere in this app. Every document (case analysis, contract audit, document metadata) is self-contained with variable nested structure. Forcing that into relational tables adds complexity with no benefit.

**Why the scoring engine is the only tested component** — it's the only deterministic one. Every other output is non-deterministic LLM output; 22 unit tests guard the one place where "same input → same output" is a hard requirement.

---

## Known Limitations

- PDF text extraction uses `pypdf` — works on text-based PDFs only, not scanned/image PDFs (no OCR engine wired in yet)
- ChromaDB runs in-memory — contract embeddings reset on server restart
- Free-tier API rate limits mean rapid testing can exhaust Gemini quota (mitigated with Groq fallback + key rotation)
- Render free tier cold-starts after 15 min idle — mitigated with UptimeRobot health pings

---

## Roadmap

- [ ] Redis caching for identical case queries (wrapper already built, not yet applied)
- [ ] OCR support for scanned contracts (Tesseract/Google Vision)
- [ ] Pinecone for persistent vector storage
- [ ] Hindi/regional language voice input
- [ ] SMS court date reminders

---

## Disclaimer

AIttorney provides general legal information for educational purposes only. It is **not** a substitute for advice from a licensed attorney. Always consult a qualified advocate for your specific situation.

---

## License

This project is a personal portfolio project. See repository for usage terms.

---

Built by [Gagan Malhotra](https://github.com/GaganMalhotra13)