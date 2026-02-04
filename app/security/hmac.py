import hmac, hashlib, logging
from app.config import settings

log = logging.getLogger(__name__)

def verify_hmac(payload: bytes, signature: str) -> bool:
    expected = hmac.new(settings.HMAC_SECRET.encode(), payload, hashlib.sha256).hexdigest()
    valid = hmac.compare_digest(expected, signature)
    if not valid:
        log.warning("HMAC verification failed")
    return valid
