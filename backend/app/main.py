from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.api.router import api_router
from app.core.config import settings
from app.core.logging import setup_logging

setup_logging()

app = FastAPI(title="CoffeeStudio API", version="0.1.0")

# Rate limiter setup
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200/minute"]
)
app.state.limiter = limiter


# Custom rate limit handler
# Note: exc is typed as Exception for FastAPI compatibility but will be RateLimitExceeded
async def rate_limit_exceeded_handler(request: Request, exc: Exception) -> Response:
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded"}
    )


app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

Instrumentator().instrument(app).expose(app)
