import logging

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from .config import settings
from .security import verify_backend_key
from .routes_ai import router as ai_router
from .routes_ats import router as ats_router
from .routes_job_match import router as job_match_router
from .routes_voice import router as voice_router


logger = logging.getLogger("cvpilot")
logging.basicConfig(level=logging.INFO)


# ---------------------------------------------------------
# RATE LIMITING
# ---------------------------------------------------------
# Keyed by client IP. This protects your Groq quota/cost even from a caller
# that DOES have a valid backend key (e.g. your own frontend under heavy
# load, or a leaked key) — pair with the X-Backend-Key check in security.py,
# don't rely on either alone.

limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])


app = FastAPI(
    title="CVPilot API",
    description="AI-powered CV and resume assistant",
    version="1.0.0",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)


# ---------------------------------------------------------
# CORS
# ---------------------------------------------------------
# Only GET/POST are actually used by this API, and only these specific
# origins should ever call it — tighten this list for production before
# deploying (add your real frontend domain, remove localhost).

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "X-Backend-Key"],
)


# ---------------------------------------------------------
# GLOBAL ERROR HANDLING
# ---------------------------------------------------------
# Any exception that isn't already an HTTPException (i.e. something we
# didn't anticipate) gets logged in full server-side, but the client only
# ever sees a generic message — never a stack trace, file path, or internal
# detail that could help an attacker.

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error. Please try again."},
    )


# ---------------------------------------------------------
# ROUTES
# ---------------------------------------------------------
# Every AI route requires the shared backend key AND is rate-limited.
# Health/config/root stay open since they carry no cost and no user data.

app.include_router(ai_router, dependencies=[Depends(verify_backend_key)])
app.include_router(ats_router, dependencies=[Depends(verify_backend_key)])
app.include_router(job_match_router, dependencies=[Depends(verify_backend_key)])
app.include_router(voice_router, dependencies=[Depends(verify_backend_key)])


# ---------------------------------------------------------
# ROOT
# ---------------------------------------------------------

@app.get("/")
def root():
    return {
        "name": "CVPilot API",
        "version": "1.0.0",
        "status": "online",
    }


# ---------------------------------------------------------
# HEALTH CHECK
# ---------------------------------------------------------

@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "model": settings.GROQ_MODEL,
        "groq_configured": bool(settings.GROQ_API_KEY),
    }


# ---------------------------------------------------------
# CONFIG CHECK
# ---------------------------------------------------------
# Never returns the actual keys — only enough to confirm they're set.

@app.get("/api/config")
def config_check():
    key = settings.GROQ_API_KEY
    return {
        "groq_configured": bool(key),
        "groq_key_prefix": key[:4] if key else None,
        "groq_model": settings.GROQ_MODEL,
        "cors_origins": settings.CORS_ORIGINS,
    }