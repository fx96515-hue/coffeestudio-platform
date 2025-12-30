from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from prometheus_fastapi_instrumentator import Instrumentator
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from sqlalchemy.exc import IntegrityError, OperationalError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.router import api_router
from app.core.config import settings
from app.core.logging import setup_logging
from app.core.error_handlers import (
    validation_exception_handler,
    http_exception_handler,
    integrity_error_handler,
    operational_error_handler,
    generic_exception_handler,
)
from app.middleware import InputValidationMiddleware, SecurityHeadersMiddleware

setup_logging()

app = FastAPI(title="CoffeeStudio API", version="0.1.0")

# Rate limiter setup
limiter = Limiter(key_func=get_remote_address, default_limits=["200/minute"])
app.state.limiter = limiter


# Custom rate limit handler
# Note: exc is typed as Exception for FastAPI compatibility but will be RateLimitExceeded
async def rate_limit_exceeded_handler(request: Request, exc: Exception) -> Response:
    return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded"})


app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# Add comprehensive error handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore[arg-type]
app.add_exception_handler(StarletteHTTPException, http_exception_handler)  # type: ignore[arg-type]
app.add_exception_handler(IntegrityError, integrity_error_handler)  # type: ignore[arg-type]
app.add_exception_handler(OperationalError, operational_error_handler)  # type: ignore[arg-type]
app.add_exception_handler(Exception, generic_exception_handler)

# Add security middleware
# Note: Middleware execution order matters in FastAPI
# Middleware added first executes last on the way out (response)
# Middleware added last executes first on the way in (request)
# So: InputValidation -> CORS -> Security Headers (on request)
#     Security Headers -> CORS -> InputValidation (on response)
app.add_middleware(SecurityHeadersMiddleware)  # Applied last to responses
app.add_middleware(InputValidationMiddleware)  # Applied first to requests

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

Instrumentator().instrument(app).expose(app)
