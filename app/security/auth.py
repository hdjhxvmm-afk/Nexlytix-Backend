import logging
from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader
from app.config import settings

log = logging.getLogger(__name__)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def verify_api_key(api_key: str = Security(api_key_header)):
    if not api_key or api_key != settings.API_KEY:
        log.warning("Invalid API key attempt")
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return api_key
