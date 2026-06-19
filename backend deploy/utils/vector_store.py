"""
utils/vector_store.py
Lightweight semantic search for contract chat.
Uses ChromaDB (local, free) + sentence-transformers.
Install: pip install chromadb sentence-transformers

Falls back gracefully if not installed — chat still works
via full-text method, just less precise.
"""
import hashlib
import re

try:
    import chromadb
    # from sentence_transformers import SentenceTransformer
    # _EMBED_MODEL = SentenceTransformer("all-MiniLM-L6-v2")  # 80MB, runs locally
    _embed_model = None

    _CLIENT      = chromadb.Client()
    VECTOR_AVAILABLE = True
except ImportError:
    VECTOR_AVAILABLE = False
    _EMBED_MODEL = None
    _CLIENT      = None


# ── Chunking ─────────────────────────────────────────────────
def get_embed_model():
    global _embed_model
    if _embed_model is None:
        from sentence_transformers import SentenceTransformer
        _embed_model = SentenceTransformer("all-MiniLM-L6-v2")
    return _embed_model
def _chunk_text(text: str, size: int = 500, overlap: int = 60) -> list[str]:
    """Split text into overlapping chunks for better retrieval."""
    chunks, i = [], 0
    while i < len(text):
        chunks.append(text[i:i + size])
        i += size - overlap
    return [c for c in chunks if len(c.strip()) > 40]  # drop tiny trailing chunks


def _doc_id(filename: str, text: str) -> str:
    """Stable ID for a document based on name + content hash."""
    h = hashlib.md5((filename + text[:200]).encode()).hexdigest()[:10]
    return f"doc_{h}"


# ── Public API ───────────────────────────────────────────────

def index_contract(text: str, filename: str) -> str:
    """
    Chunk and embed a contract. Returns doc_id.
    If vector libs unavailable, returns doc_id anyway (fallback path).
    """
    doc_id = _doc_id(filename, text)
    if not VECTOR_AVAILABLE:
        return doc_id

    chunks = _chunk_text(text)
    if not chunks:
        return doc_id

    col  = _CLIENT.get_or_create_collection("contracts")
    ids  = [f"{doc_id}_c{i}" for i in range(len(chunks))]

    # Avoid re-indexing same document
    existing = col.get(ids=[ids[0]])
    if existing["ids"]:
        return doc_id  # already indexed

    embeddings = _EMBED_MODEL.encode(chunks).tolist()
    col.add(
        ids=ids,
        documents=chunks,
        embeddings=embeddings,
        metadatas=[{"doc_id": doc_id, "chunk": i} for i in range(len(chunks))],
    )
    return doc_id


def semantic_search(query: str, doc_id: str, top_k: int = 4) -> list[str]:
    """
    Return top_k most relevant chunks for a question.
    Falls back to empty list if vector unavailable.
    """
    if not VECTOR_AVAILABLE:
        return []

    col         = _CLIENT.get_or_create_collection("contracts")
    query_embed = _EMBED_MODEL.encode([query]).tolist()

    try:
        results = col.query(
            query_embeddings=query_embed,
            n_results=top_k,
            where={"doc_id": doc_id},
        )
        return results["documents"][0] if results["documents"] else []
    except Exception:
        return []


def is_available() -> bool:
    return VECTOR_AVAILABLE