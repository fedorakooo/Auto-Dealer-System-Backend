from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.application.exceptions.errors import BusinessError, NotFoundError
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


def exception_container(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        logger.warning(f"Request validation failed: {exc.errors()}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": "Request validation failed", "errors": exc.errors()},
        )

    @app.exception_handler(LoginError)
    async def login_exception_handler(request: Request, exc: LoginError):
        logger.warning(f"Login failed: {str(exc)}")
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Invalid password or login"},
        )

    @app.exception_handler(TokenError)
    async def token_exception_handler(request: Request, exc: TokenError):
        logger.warning(f"Token error: {str(exc)}")
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": str(exc)},
        )

    @app.exception_handler(UserBlockedError)
    async def user_blocked_exception_handler(request: Request, exc: UserBlockedError):
        logger.warning(f"User blocked: {str(exc)}")
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"detail": str(exc)},
        )

    @app.exception_handler(ForbiddenError)
    async def forbidden_exception_handler(request: Request, exc: ForbiddenError):
        logger.warning(f"Forbidden access: {str(exc)}")
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"detail": str(exc)},
        )

    @app.exception_handler(BusinessError)
    def business_error_handler(request: Request, exc: BusinessError):
        logger.warning(f"Business error: {str(exc)}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": str(exc)},
        )

    @app.exception_handler(NotFoundError)
    def not_found_exception_handler(request: Request, exc: NotFoundError):
        logger.debug(f"Resource not found: {str(exc)}")
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": str(exc)},
        )

    @app.exception_handler(HealthCheckError)
    def health_check_exception_handler(request: Request, exc: HealthCheckError):
        logger.error(f"Health check failed: {str(exc)}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"detail": str(exc)},
        )

    @app.exception_handler(DatabaseForeignKeyViolationError)
    def database_foreign_key_validation_exception_handler(request: Request, exc: DatabaseForeignKeyViolationError):
        logger.warning(f"Database foreign key violation: {str(exc)}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": str(exc)},
        )

    @app.exception_handler(DatabaseUniqueViolationError)
    def database_unique_validation_exception_handler(request: Request, exc: DatabaseUniqueViolationError):
        logger.warning(f"Database unique violation: {str(exc)}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": str(exc)},
        )

    @app.exception_handler(DatabaseError)
    def database_error_handler(request: Request, exc: DatabaseError):
        logger.error(f"Database error: {str(exc)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "An unexpected error occurred"},
        )

    @app.exception_handler(Exception)
    async def server_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unexpected server error: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "An unexpected error occurred"},
        )
