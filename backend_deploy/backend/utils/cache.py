"""
backend/utils/cache.py
Redis-based caching with in-memory fallback.
If Redis is unavailable, falls back to the in-memory dict already in cases.py.
Zero crashes — graceful degradation always.
"""
import os
import json
import time
import hashlib
from typing import Any

# ── Try Redis first ───────────────────────────────────────────
_redis = None
_REDIS_URL = os.getenv("REDIS_URL", "")

if _REDIS_URL:
    try:
        import redis.asyncio as aioredis
        _redis = aioredis.from_url(
            _REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            socket_connect_timeout=3,
            socket_timeout=3,
        )
        print("✅ Redis cache initialized")
    except Exception as e:
        print(f"⚠️ Redis unavailable, using in-memory cache: {e}")
        _redis = None
else:
    print("⚠️ No REDIS_URL set — using in-memory cache")

# ── In-memory fallback ────────────────────────────────────────
_mem: dict = {}
_MEM_TTL = 1800  # 30 minutes


def make_key(prefix: str, *parts: str) -> str:
    """Create a consistent cache key from parts."""
    raw = ":".join(str(p) for p in parts)
    hsh = hashlib.md5(raw.encode()).hexdigest()
    return f"aittorney:{prefix}:{hsh}"


async def cache_get(key: str) -> Any | None:
    """Get a value from cache. Returns None if missing or expired."""
    # ── Redis ─────────────────────────────────────────────────
    if _redis:
        try:
            val = await _redis.get(key)
            if val:
                return json.loads(val)
            return None
        except Exception as e:
            print(f"⚠️ Redis get failed, trying memory: {e}")

    # ── In-memory fallback ────────────────────────────────────
    if key in _mem:
        data, ts = _mem[key]
        if time.time() - ts < _MEM_TTL:
            return data
        del _mem[key]
    return None


async def cache_set(key: str, value: Any, ttl: int = 1800) -> None:
    """Set a value in cache with TTL in seconds."""
    # ── Redis ─────────────────────────────────────────────────
    if _redis:
        try:
            await _redis.setex(key, ttl, json.dumps(value, default=str))
            return
        except Exception as e:
            print(f"⚠️ Redis set failed, writing to memory: {e}")

    # ── In-memory fallback ────────────────────────────────────
    _mem[key] = (value, time.time())


async def cache_delete(key: str) -> None:
    """Delete a specific cache key."""
    if _redis:
        try:
            await _redis.delete(key)
        except Exception:
            pass
    _mem.pop(key, None)


async def cache_ping() -> bool:
    """Check if Redis is reachable."""
    if not _redis:
        return False
    try:
        await _redis.ping()
        return True
    except Exception:
        return False