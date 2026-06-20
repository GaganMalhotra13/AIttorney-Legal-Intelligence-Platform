"""
utils/vector_store.py
Lightweight semantic search for contract chat.
Uses ChromaDB (local, free) + sentence-transformers.

Falls back gracefully if not installed — chat still works
via full-text method, just less precise.
"""
import hashlib

try:
    import chromadb
    _CLIENT = chromadb.Client()
    VECTOR_AVAILABLE = True
except ImportError:
    VECTOR_AVAILABLE = False
    _CLIENT = None

_embed_model = None


def get_embed_model():
    """Lazy-load the embedding model only when actually needed."""
    global _embed_model
    if _embed_model is None:
        from sentence_transformers import SentenceTransformer
        _embed_model = SentenceTransformer("all-MiniLM-L6-v2")
    return _embed_model


# ── Chunking ─────────────────────────────────────────────────
def _chunk_text(text: str, size: int = 500, overlap: int = 60) -> list[str]:
    """Split text into overlapping chunks for better retrieval."""
    chunks, i = [], 0
    while i < len(text):
        chunks.append(text[i:i + size])
        i += size - overlap
    return [c for c in chunks if len(c.strip()) > 40]


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

    try:
        model = get_embed_model()
        col = _CLIENT.get_or_create_collection("contracts")
        ids = [f"{doc_id}_c{i}" for i in range(len(chunks))]

        # Avoid re-indexing same document
        existing = col.get(ids=[ids[0]])
        if existing["ids"]:
            return doc_id

        embeddings = model.encode(chunks).tolist()
        col.add(
            ids=ids,
            documents=chunks,
            embeddings=embeddings,
            metadatas=[{"doc_id": doc_id, "chunk": i} for i in range(len(chunks))],
        )
    except Exception as e:
        print(f"⚠️ Vector indexing skipped: {e}")

    return doc_id


def semantic_search(query: str, doc_id: str, top_k: int = 4) -> list[str]:
    """
    Return top_k most relevant chunks for a question.
    Falls back to empty list if vector unavailable or fails.
    """
    if not VECTOR_AVAILABLE:
        return []

    try:
        model = get_embed_model()
        col = _CLIENT.get_or_create_collection("contracts")
        query_embed = model.encode([query]).tolist()

        results = col.query(
            query_embeddings=query_embed,
            n_results=top_k,
            where={"doc_id": doc_id},
        )
        return results["documents"][0] if results["documents"] else []
    except Exception as e:
        print(f"⚠️ Semantic search failed: {e}")
        return []


def is_available() -> bool:
    return VECTOR_AVAILABLE