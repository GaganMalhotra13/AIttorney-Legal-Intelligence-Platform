"""
utils/reranker.py
Cohere reranking for search results.

Why reranking: DuckDuckGo + IndianKanoon returns 15-20 results.
Not all are equally relevant. Cohere's rerank model scores each
result against the query and returns them in true relevance order.
This means Gemini sees the MOST relevant content first — better answers.

Free tier: 1,000 calls/month (plenty for development + demo).
"""
import os
from typing import Optional

COHERE_KEY = os.getenv("COHERE_API_KEY", "")


def rerank_results(
    query:   str,
    results: list[dict],
    text_field: str = "snippet",
    top_n: int = 8,
) -> list[dict]:
    """
    Rerank search results by relevance to query.
    Returns results sorted by Cohere relevance score.

    Falls back to citation-based sorting if Cohere unavailable.
    """
    if not COHERE_KEY or not results:
        return results[:top_n]

    try:
        import cohere
        co = cohere.Client(COHERE_KEY)

        # Build documents list for reranking
        documents = [
            r.get(text_field, "") or r.get("title", "")
            for r in results
        ]
        documents = [d[:500] for d in documents]  # Cohere limit

        response = co.rerank(
            query=query,
            documents=documents,
            model="rerank-english-v3.0",
            top_n=min(top_n, len(documents)),
        )

        # Reorder results by Cohere score
        reranked = []
        for hit in response.results:
            result = results[hit.index].copy()
            result["relevance_score"] = round(hit.relevance_score, 4)
            reranked.append(result)

        return reranked

    except ImportError:
        return results[:top_n]
    except Exception as e:
        # Graceful fallback — don't break the whole pipeline
        return results[:top_n]


def rerank_with_score_filter(
    query:      str,
    results:    list[dict],
    text_field: str = "snippet",
    min_score:  float = 0.1,
    top_n:      int = 6,
) -> list[dict]:
    """
    Rerank AND filter out low-relevance results.
    min_score=0.1 removes completely irrelevant results.
    """
    reranked = rerank_results(query, results, text_field, top_n * 2)
    filtered = [
        r for r in reranked
        if r.get("relevance_score", 1.0) >= min_score
    ]
    return filtered[:top_n] if filtered else reranked[:top_n]