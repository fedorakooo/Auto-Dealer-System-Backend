import asyncio
import traceback
from collections.abc import Sequence
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.api.dependencies.mongodb import get_mongodb_client
from src.api.dependencies.services import create_log_service
from src.application.exceptions.errors import BusinessError, NotFoundError, ValidationError
from src.domain.exceptions.auth_errors import ForbiddenError, LoginError
from src.domain.exceptions.health_check_errors import HealthCheckError
from src.domain.exceptions.token_errors import TokenError
from src.domain.exceptions.user_errors import UserBlockedError
from src.infrastructure.database.exceptions import (
    DatabaseError,
    DatabaseForeignKeyViolationError,
    DatabaseUniqueViolationError,
)
from src.logger import get_logger

logger = get_logger(__name__)


def _errors_without_input(errors: Sequence[Any]) -> list[Any]:
    """Drops raw input values (passwords, emails) from validation errors before logging."""
    return [{k: v for k, v in e.items() if k != "input"} if isinstance(e, dict) else e for e in errors]


def _log_error_async(request: Request, exc: Exception) -> None:
    """Schedules persisting the error to MongoDB without blocking the response."""
    mongodb_client = get_mongodb_client(request)
    if mongodb_client.db is None:
        return
    try:
        log_service = create_log_service(mongodb_client)
        message = str(exc)
        if hasattr(exc, "errors") and callable(exc.errors):
            message = str(_errors_without_input(exc.errors()))

        asyncio.create_task(
            log_service.log_error(
                error_type=type(exc).__name__,
                message=message,
                traceback=traceback.format_exc(),
                path=request.url.path,
                user_id=getattr(request.state, "user_id", None),
            )
        )
    except Exception:
        # Error logging must never mask the original error response.
        logger.debug("Failed to schedule error log", exc_info=True)


def exception_container(app: FastAPI) -> None:
    """Registers handlers that map domain, application and database errors to HTTP responses."""

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        errors = _errors_without_input(exc.errors())
        logger.warning(f"Request validation failed: {errors}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": "Request validation failed", "errors": jsonable_encoder(errors)},
        )

    @app.exception_handler(LoginError)
    async def login_exception_handler(request: Request, exc: LoginError) -> JSONResponse:
        logger.warning(f"Login failed: {type(exc).__name__}")
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Invalid password or login"},
        )

    @app.exception_handler(TokenError)
    async def token_exception_handler(request: Request, exc: TokenError) -> JSONResponse:
        logger.warning(f"Token error: {type(exc).__name__}")
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": str(exc)},
        )

    @app.exception_handler(UserBlockedError)
    async def user_blocked_exception_handler(request: Request, exc: UserBlockedError) -> JSONResponse:
        logger.warning(f"User blocked: {type(exc).__name__}")
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"detail": str(exc)},
        )

    @app.exception_handler(ForbiddenError)
    async def forbidden_exception_handler(request: Request, exc: ForbiddenError) -> JSONResponse:
        _log_error_async(request, exc)
        logger.warning(f"Forbidden access: {exc!s}")
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"detail": str(exc)},
        )

    @app.exception_handler(ValidationError)
    async def application_validation_error_handler(request: Request, exc: ValidationError) -> JSONResponse:
        logger.warning(f"Validation error: {exc!s}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": str(exc)},
        )

    @app.exception_handler(BusinessError)
    async def business_error_handler(request: Request, exc: BusinessError) -> JSONResponse:
        _log_error_async(request, exc)
        logger.warning(f"Business error: {exc!s}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": str(exc)},
        )

    @app.exception_handler(NotFoundError)
    async def not_found_exception_handler(request: Request, exc: NotFoundError) -> JSONResponse:
        logger.debug(f"Resource not found: {exc!s}")
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": str(exc)},
        )

    @app.exception_handler(HealthCheckError)
    async def health_check_exception_handler(request: Request, exc: HealthCheckError) -> JSONResponse:
        logger.error(f"Health check failed: {exc!s}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"detail": str(exc)},
        )

    @app.exception_handler(DatabaseForeignKeyViolationError)
    async def database_foreign_key_validation_exception_handler(
        request: Request, exc: DatabaseForeignKeyViolationError
    ) -> JSONResponse:
        logger.warning(f"Database foreign key violation: {exc!s}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": str(exc)},
        )

    @app.exception_handler(DatabaseUniqueViolationError)
    async def database_unique_validation_exception_handler(
        request: Request, exc: DatabaseUniqueViolationError
    ) -> JSONResponse:
        logger.warning(f"Database unique violation: {exc!s}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": str(exc)},
        )

    @app.exception_handler(DatabaseError)
    async def database_error_handler(request: Request, exc: DatabaseError) -> JSONResponse:
        _log_error_async(request, exc)
        logger.error(f"Database error: {exc!s}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "An unexpected error occurred"},
        )

    @app.exception_handler(Exception)
    async def server_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        _log_error_async(request, exc)
        logger.error(f"Unexpected server error: {exc!s}", exc_info=exc)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "An unexpected error occurred"},
        )
