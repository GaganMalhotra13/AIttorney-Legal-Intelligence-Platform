# backend/middleware/rate_limit.py
from fastapi import Request, HTTPException
from collections import defaultdict
import time

request_counts: dict = defaultdict(list)


async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    now       = time.time()
    window    = 60  # 1 minute

    # Clean old requests outside window
    request_counts[client_ip] = [
        t for t in request_counts[client_ip]
        if now - t < window
    ]

    if len(request_counts[client_ip]) >= 30:  # 30 requests per minute
        raise HTTPException(
            status_code=429,
            detail="Too many requests. Please slow down."
        )

    request_counts[client_ip].append(now)
    response = await call_next(request)
    return response