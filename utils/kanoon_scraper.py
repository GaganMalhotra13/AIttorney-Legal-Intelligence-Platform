"""
utils/kanoon_scraper.py
Direct IndianKanoon scraper via ScraperAPI.
Returns structured judgment objects with full text, not snippets.

Why ScraperAPI: IndianKanoon blocks direct requests with 403.
ScraperAPI rotates IPs and handles JS rendering for us.
"""
import httpx
import os
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
import re

SCRAPER_KEY = os.getenv("SCRAPER_API_KEY", "")
BASE_URL    = "https://indiankanoon.org"


def _scraper_url(target_url: str) -> str:
    """Wrap any URL through ScraperAPI."""
    if not SCRAPER_KEY:
        return target_url  # fallback to direct (may fail)
    return f"https://api.scraperapi.com?api_key={SCRAPER_KEY}&url={quote_plus(target_url)}&render=false"


def _clean_text(raw: str) -> str:
    """Remove HTML artifacts, normalize whitespace."""
    text = re.sub(r'\s+', ' ', raw)
    text = re.sub(r'\[(\d+)\]', r'[¶\1]', text)  # preserve paragraph refs
    return text.strip()


def search_indiankanoon(query: str, max_results: int = 8) -> list[dict]:
    """
    Search IndianKanoon and return structured judgment objects.
    Each result has: title, url, snippet, citation_count, court, date, doc_id
    """
    if not SCRAPER_KEY:
        return []

    search_url = f"{BASE_URL}/search/?formInput={quote_plus(query)}&pagenum=0"

    try:
        resp = httpx.get(
            _scraper_url(search_url),
            timeout=25,
            headers={"Accept": "text/html"}
        )
        resp.raise_for_status()
    except Exception as e:
        return []

    soup    = BeautifulSoup(resp.text, "lxml")
    results = []

    for result_div in soup.select(".result")[:max_results]:
        try:
            # Title + URL
            title_el = result_div.select_one(".result_title a")
            if not title_el:
                continue
            title    = title_el.get_text(strip=True)
            href     = title_el.get("href", "")
            full_url = BASE_URL + href if href.startswith("/") else href
            doc_id   = re.search(r"/doc/(\d+)/", href)
            doc_id   = doc_id.group(1) if doc_id else ""

            # Snippet
            snippet_el = result_div.select_one(".snippet")
            snippet    = _clean_text(snippet_el.get_text()) if snippet_el else ""

            # Citation count
            cite_el    = result_div.select_one(".cited_by_count")
            citations  = 0
            if cite_el:
                nums = re.findall(r'\d+', cite_el.get_text())
                citations = int(nums[0]) if nums else 0

            # Court & date from metadata
            meta_el = result_div.select_one(".docsource_main")
            court   = ""
            date    = ""
            if meta_el:
                meta_text = meta_el.get_text(strip=True)
                # Format: "Supreme Court of India|15 Jan 2020"
                parts = meta_text.split("|")
                court = parts[0].strip() if parts else ""
                date  = parts[1].strip() if len(parts) > 1 else ""

            results.append({
                "title":      title,
                "url":        full_url,
                "doc_id":     doc_id,
                "snippet":    snippet,
                "citations":  citations,
                "court":      court,
                "date":       date,
                "source":     "indiankanoon.org",
                "tier":       3,  # highest authority
            })
        except Exception:
            continue

    # Sort by citation count — most-cited = most landmark
    results.sort(key=lambda x: x["citations"], reverse=True)
    return results


def fetch_judgment_text(doc_id: str, max_chars: int = 6000) -> str:
    """
    Fetch the full text of a specific judgment by doc_id.
    Used for landmark cases where we need the actual ruling text.
    """
    if not doc_id or not SCRAPER_KEY:
        return ""

    url = f"{BASE_URL}/doc/{doc_id}/"
    try:
        resp = httpx.get(_scraper_url(url), timeout=30)
        resp.raise_for_status()
    except Exception:
        return ""

    soup = BeautifulSoup(resp.text, "lxml")

    # Remove noise elements
    for el in soup.select(".docsource, .doc_citations, script, style, nav"):
        el.decompose()

    # Get main judgment body
    body = soup.select_one("#judgment") or soup.select_one(".judgments")
    if not body:
        body = soup.select_one("body")

    text = _clean_text(body.get_text()) if body else ""
    return text[:max_chars]


def get_landmark_judgments(query: str, case_type: str = "general") -> list[dict]:
    """
    Specifically targets landmark/frequently-cited cases.
    Returns top 3-5 highly-cited judgments with full text snippets.
    """
    # Search with 'landmark' qualifier
    landmark_query = f"{query} landmark judgment"
    results        = search_indiankanoon(landmark_query, max_results=5)

    # Filter for high citation count (landmark = cited many times)
    landmarks = [r for r in results if r["citations"] >= 5]

    # If not enough landmarks found, use regular top results
    if len(landmarks) < 2:
        landmarks = results[:3]

    # Fetch fuller text for top 2
    for i, lm in enumerate(landmarks[:2]):
        if lm["doc_id"]:
            full_text = fetch_judgment_text(lm["doc_id"], max_chars=2000)
            landmarks[i]["full_text"] = full_text
        else:
            landmarks[i]["full_text"] = landmarks[i]["snippet"]

    return landmarks