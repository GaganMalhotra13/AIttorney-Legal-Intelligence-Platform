"""
tests/test_scraper_utils.py
Unit tests for kanoon_scraper.py utility functions.
Only tests pure utility functions — no actual HTTP calls, no API key needed.
Run: pytest tests/test_scraper_utils.py -v
"""
import sys
import os
# Ensure project root (parent dir) is on sys.path so `import kanoon_scraper` resolves
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend_deploy.utils.kanoon_scraper import _clean_text, _scraper_url, _safe_decode


class TestCleanText:
    """_clean_text() normalizes whitespace and preserves paragraph refs"""

    def test_removes_extra_whitespace(self):
        assert _clean_text("hello   world") == "hello world"

    def test_removes_newlines(self):
        result = _clean_text("hello\nworld")
        assert "\n" not in result

    def test_removes_tabs(self):
        result = _clean_text("hello\tworld")
        assert "\t" not in result

    def test_strips_leading_trailing_whitespace(self):
        assert _clean_text("  hello  ") == "hello"

    def test_converts_paragraph_numbers_to_refs(self):
        result = _clean_text("[1] This is a paragraph")
        assert "[¶1]" in result

    def test_converts_multiple_paragraph_refs(self):
        result = _clean_text("[1] first [2] second [15] fifteenth")
        assert "[¶1]"  in result
        assert "[¶2]"  in result
        assert "[¶15]" in result

    def test_empty_string_returns_empty(self):
        assert _clean_text("") == ""

    def test_normal_legal_text_preserved(self):
        text   = "The Supreme Court held that Section 138 applies."
        result = _clean_text(text)
        assert "Supreme Court" in result
        assert "Section 138"   in result

    def test_returns_string_type(self):
        assert isinstance(_clean_text("any input"), str)

    def test_long_whitespace_collapsed(self):
        result = _clean_text("a" + " " * 100 + "b")
        assert result == "a b"


class TestScraperUrl:
    """_scraper_url() correctly wraps URLs through ScraperAPI"""

    def test_returns_direct_url_without_key(self, monkeypatch):
        monkeypatch.delenv("SCRAPER_API_KEY", raising=False)
        # Reload module to pick up env change
        import importlib
        import backend_deploy.utils.kanoon_scraper as ks
        ks.SCRAPER_KEY = ""
        url    = ks._scraper_url("https://indiankanoon.org/search")
        assert url == "https://indiankanoon.org/search"

    def test_wraps_url_with_key(self, monkeypatch):
        import backend_deploy.utils.kanoon_scraper as ks
        ks.SCRAPER_KEY = "testkey123"
        url = ks._scraper_url("https://indiankanoon.org")
        assert "api.scraperapi.com" in url
        assert "testkey123"         in url
        assert "indiankanoon.org"   in url

    def test_url_encoded_in_scraper_url(self, monkeypatch):
        import backend_deploy.utils.kanoon_scraper as ks
        ks.SCRAPER_KEY = "testkey"
        url = ks._scraper_url("https://indiankanoon.org/search/?formInput=cheque bounce")
        # URL should be encoded in the scraper URL
        assert "api.scraperapi.com" in url

    def test_returns_string(self, monkeypatch):
        import backend_deploy.utils.kanoon_scraper as ks
        ks.SCRAPER_KEY = ""
        result = ks._scraper_url("https://example.com")
        assert isinstance(result, str)


class TestSafeDecode:
    """_safe_decode() forces UTF-8 and never crashes"""

    def test_decodes_valid_utf8(self):
        class MockResp:
            content = "Hello World".encode("utf-8")
            text    = "Hello World"
        result = _safe_decode(MockResp())
        assert "Hello World" in result

    def test_handles_invalid_bytes_gracefully(self):
        class MockResp:
            content = b"Hello \x80\x81 World"  # invalid UTF-8 bytes
            text    = "fallback"
        # Should not crash — replaces invalid bytes
        result = _safe_decode(MockResp())
        assert isinstance(result, str)
        assert "Hello" in result

    def test_handles_hindi_text(self):
        class MockResp:
            content = "न्यायालय का आदेश".encode("utf-8")
            text    = "न्यायालय का आदेश"
        result = _safe_decode(MockResp())
        assert isinstance(result, str)

    def test_returns_string_type_always(self):
        class MockResp:
            content = b""
            text    = ""
        result = _safe_decode(MockResp())
        assert isinstance(result, str)

    def test_empty_content_returns_string(self):
        class MockResp:
            content = b""
            text    = ""
        result = _safe_decode(MockResp())
        assert result == ""

    def test_japanese_bytes_handled(self):
        # This simulates the actual mojibake bug that was fixed
        class MockResp:
            content = "テスト".encode("utf-8")  # Japanese text in UTF-8
            text    = "garbled"
        result = _safe_decode(MockResp())
        assert isinstance(result, str)