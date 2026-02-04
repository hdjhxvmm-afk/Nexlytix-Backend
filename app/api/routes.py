import logging
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.config import settings
from app.database import query
from app.security import limiter, verify_api_key, validate_device_id

log = logging.getLogger(__name__)

app = FastAPI(title="Nexlytix API", version="1.0")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["X-API-Key", "Content-Type"],
)

@app.get("/")
def health():
    return {"status": "ok"}

@app.get("/api/telemetry/{device_id}")
@limiter.limit(settings.RATE_LIMIT)
def get_data(request: Request, device_id: str, _: str = Depends(verify_api_key)):
    if not validate_device_id(device_id):
        log.warning(f"Invalid device_id: {device_id}")
        raise HTTPException(400, "Invalid device_id format")
    
    try:
        data = query(device_id)
        log.info(f"Query: {device_id} | records={len(data)}")
        return {"device_id": device_id, "count": len(data), "data": data} if data else {"device_id": device_id, "data": []}
    except Exception as e:
        log.error(f"Query error: {e}")
        raise HTTPException(500, "Internal error")
