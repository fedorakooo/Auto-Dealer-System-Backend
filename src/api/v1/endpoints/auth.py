from typing import Annotated

from fastapi import APIRouter, Depends, Form, status
from pydantic import SecretStr

from src.api.dependencies.services import get_auth_service, get_user_service
from src.api.v1.models.tokens import TokenResponse
from src.api.v1.models.user_models import UserCreateRequest, UserResponse
from src.application.dtos.auth_dto import LoginDTO, RefreshTokenDTO
from src.application.services.auth_service import AuthService
from src.application.services.user_service import UserService
from src.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/signup",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Unique constraint violation"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
async def signup(
    user_create: UserCreateRequest,
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> UserResponse:
    logger.info(f"Signup request for email: {user_create.email}")
    user_dto = user_create.to_dto()
    created_user = await user_service.create_user(user_dto)
    logger.info(f"User created successfully with id: {created_user.id}")
    return UserResponse.from_dto(created_user)


@router.post(
    "/signin",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid password or login"},
        status.HTTP_403_FORBIDDEN: {"description": "User is blocked"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
async def signin(
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    username: str = Form(...),
    password: SecretStr = Form(...),
) -> TokenResponse:
    logger.info(f"Login attempt for username: {username}")
    login_dto = LoginDTO(email=username, password=password.get_secret_value())
    token_info = await auth_service.login(login_dto)
    logger.info(f"Login successful for username: {username}")
    return TokenResponse.from_dto(token_info)


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid password or login"},
        status.HTTP_403_FORBIDDEN: {"description": "User is blocked"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
async def login(
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    username: str = Form(...),
    password: SecretStr = Form(...),
) -> TokenResponse:
    """Alias for /signin endpoint for better compatibility."""
    logger.info(f"Login attempt for username: {username}")
    login_dto = LoginDTO(email=username, password=password.get_secret_value())
    token_info = await auth_service.login(login_dto)
    logger.info(f"Login successful for username: {username}")
    return TokenResponse.from_dto(token_info)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid or expired refresh token"},
        status.HTTP_403_FORBIDDEN: {"description": "User is blocked"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
async def auth_refresh(
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    refresh_token: str = Form(...),
) -> TokenResponse:
    logger.debug("Refresh token request received")
    refresh_dto = RefreshTokenDTO(refresh_token=refresh_token)
    token_info = await auth_service.refresh_token(refresh_dto)
    logger.debug("Token refreshed successfully")
    return TokenResponse.from_dto(token_info)
