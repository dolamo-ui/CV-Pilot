import hmac

from fastapi import Header, HTTPException

from .config import settings


def verify_backend_key(x_backend_key: str = Header(default="")) -> None:
    """
    FastAPI dependency: require the caller to send the shared secret in an
    X-Backend-Key header. Attach this to any route that should only be
    callable by your own frontend server, not the public internet.

    Uses hmac.compare_digest instead of == to avoid leaking timing info
    about how much of the key matched.
    """
    expected = settings.BACKEND_API_KEY

    if not expected or not x_backend_key:
        raise HTTPException(status_code=401, detail="Missing backend credentials.")

    if not hmac.compare_digest(x_backend_key, expected):
        raise HTTPException(status_code=401, detail="Invalid backend credentials.")