"""
Global exception handlers for FastAPI.

Includes custom logic for:
- Validation errors (422)
- Uncaught application errors (500)
"""
from typing import Awaitable
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.core.logging_config import logger
from starlette.responses import Response


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
) -> Response:
    """
    Handles Pydantic validation errors raised during request parsing.

    Args:
        request (Request): The incoming FastAPI request.
        exc (RequestValidationError): The validation error exception.

    Returns:
        Response: JSON 422 response with error details.
    """
    logger.warning("❌ Validation error: %s", exc)
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": exc.body},
    )


async def global_exception_handler(
    request: Request,
    exc: Exception
) -> Response:
    """
    Handles unexpected exceptions in the application.

    Args:
        request (Request): The incoming request object.
        exc (Exception): The uncaught exception.

    Returns:
        Response: A generic 500 error response.
    """
    logger.exception("Unhandled exception: %s", exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error"},
    )
