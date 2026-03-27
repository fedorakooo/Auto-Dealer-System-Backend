from typing import Annotated

from fastapi import Depends

from src.api.dependencies.auth import get_password_handler, get_token_handler
from src.api.dependencies.database import get_unit_of_work
from src.api.dependencies.redis import get_redis_client
from src.api.dependencies.s3 import get_s3_client
from src.application.abstractions.auth_service import IAuthService
from src.application.abstractions.city_service import ICityService
from src.application.abstractions.custom_order_service import ICustomOrderService
from src.application.abstractions.customer_service import ICustomerService
from src.application.abstractions.dealership_service import IDealershipService
from src.application.abstractions.favorite_service import IFavoriteService
from src.application.abstractions.feature_service import IFeatureService
from src.application.abstractions.model_media_service import IModelMediaService
from src.application.abstractions.model_service import IModelService
from src.application.abstractions.order_service import IOrderService
from src.application.abstractions.review_service import IReviewService
from src.application.abstractions.testdrive_service import ITestDriveService
from src.application.abstractions.user_service import IUserService
from src.application.abstractions.vehicle_media_service import IVehicleMediaService
from src.application.abstractions.vehicle_service import IVehicleService
from src.application.services.auth_service import AuthService
from src.application.services.city_service import CityService
from src.application.services.log_service import LogService
from src.infrastructure.mongodb.repositories.log_repository import LogRepository
from src.infrastructure.mongodb.client import mongodb_client
from src.application.services.custom_order_service import CustomOrderService
from src.application.services.customer_service import CustomerService
from src.application.services.dealership_service import DealershipService
from src.application.services.favorite_service import FavoriteService
from src.application.services.feature_service import FeatureService
from src.application.services.model_media_service import ModelMediaService
from src.application.services.model_service import ModelService
from src.application.services.order_service import OrderService
from src.application.services.review_service import ReviewService
from src.application.services.testdrive_service import TestDriveService
from src.application.services.user_service import UserService
from src.application.services.vehicle_media_service import VehicleMediaService
from src.application.services.vehicle_service import VehicleService
from src.domain.abstractions.auth.password_handler import IPasswordHandler
from src.domain.abstractions.auth.token_handler import ITokenHandler
from src.domain.abstractions.database.uow import IUnitOfWork
from src.domain.abstractions.redis.redis_client import IRedisClient
from src.domain.abstractions.s3.s3_client import IS3Client


def get_auth_service(
    uow: Annotated[IUnitOfWork, Depends(get_unit_of_work)],
    password_handler: Annotated[IPasswordHandler, Depends(get_password_handler)],
    token_handler: Annotated[ITokenHandler, Depends(get_token_handler)],
    redis_client: Annotated[IRedisClient, Depends(get_redis_client)],
) -> IAuthService:
    return AuthService(
        uow=uow,
        password_handler=password_handler,
        token_handler=token_handler,
        redis_client=redis_client,
    )


def get_user_service(
    uow: Annotated[IUnitOfWork, Depends(get_unit_of_work)],
    password_handler: Annotated[IPasswordHandler, Depends(get_password_handler)],
    redis_client: Annotated[IRedisClient, Depends(get_redis_client)],
) -> IUserService:
    return UserService(
        uow=uow,
        password_handler=password_handler,
        redis_client=redis_client,
    )


def get_model_media_service(
    uow: Annotated[IUnitOfWork, Depends(get_unit_of_work)],
    s3_client: Annotated[IS3Client | None, Depends(get_s3_client)],
) -> IModelMediaService:
    return ModelMediaService(uow=uow, s3_client=s3_client)


def get_vehicle_service(
    uow: Annotated[IUnitOfWork, Depends(get_unit_of_work)],
    model_media_service: Annotated[IModelMediaService | None, Depends(get_model_media_service)],
) -> IVehicleService:
    return VehicleService(uow=uow, model_media_service=model_media_service)


def get_city_service(
    uow: Annotated[IUnitOfWork, Depends(get_unit_of_work)],
    redis_client: Annotated[IRedisClient, Depends(get_redis_client)],
) -> ICityService:
    return CityService(uow=uow, redis_client=redis_client)


def get_customer_service(
    uow: Annotated[IUnitOfWork, Depends(get_unit_of_work)],
    password_handler: Annotated[IPasswordHandler, Depends(get_password_handler)],
) -> ICustomerService:
    return CustomerService(uow=uow, password_handler=password_handler)


def get_dealership_service(
    uow: Annotated[IUnitOfWork, Depends(get_unit_of_work)],
    redis_client: Annotated[IRedisClient, Depends(get_redis_client)],
) -> IDealershipService:
    return DealershipService(uow=uow, redis_client=redis_client)


def get_feature_service(
    uow: Annotated[IUnitOfWork, Depends(get_unit_of_work)],
) -> IFeatureService:
    return FeatureService(uow=uow)


def get_model_service(
    uow: Annotated[IUnitOfWork, Depends(get_unit_of_work)],
) -> IModelService:
    return ModelService(uow=uow)


def get_order_service(
    uow: Annotated[IUnitOfWork, Depends(get_unit_of_work)],
) -> IOrderService:
    return OrderService(uow=uow)


def get_custom_order_service(
    uow: Annotated[IUnitOfWork, Depends(get_unit_of_work)],
) -> ICustomOrderService:
    return CustomOrderService(uow=uow)


def get_review_service(
    uow: Annotated[IUnitOfWork, Depends(get_unit_of_work)],
) -> IReviewService:
    return ReviewService(uow=uow)


def get_test_drive_service(
    uow: Annotated[IUnitOfWork, Depends(get_unit_of_work)],
) -> ITestDriveService:
    return TestDriveService(uow=uow)


def get_vehicle_media_service(
    uow: Annotated[IUnitOfWork, Depends(get_unit_of_work)],
    s3_client: Annotated[IS3Client | None, Depends(get_s3_client)],
) -> IVehicleMediaService:
    return VehicleMediaService(uow=uow, s3_client=s3_client)


def get_favorite_service(
    uow: Annotated[IUnitOfWork, Depends(get_unit_of_work)],
) -> IFavoriteService:
    return FavoriteService(uow=uow)


def get_log_service() -> LogService:
    log_repository = LogRepository(mongodb_client.db.logs)
    return LogService(log_repository=log_repository)
