from uuid import UUID, uuid4

from src.application.abstractions.user_service import IUserService
from src.application.dtos.user_dto import UserCreateDTO, UserDTO, UserUpdateDTO
from src.application.exceptions.errors import BusinessError, NotFoundError
from src.application.mappers.user_mapper import UserMapper
from src.application.utils.cache_manager import CacheManager
from src.domain.abstractions.auth.password_handler import IPasswordHandler
from src.domain.abstractions.database.uow import IUnitOfWork
from src.domain.abstractions.pubsub.manager import IPubSubManager
from src.domain.abstractions.redis.redis_client import IRedisClient
from src.domain.entities.customer import Customer
from src.domain.value_objects.filters import UserFilter
from src.domain.value_objects.user_role import UserRole
from src.config import settings
from src.logger import get_logger

logger = get_logger(__name__)


class UserService(IUserService):
    def __init__(
        self,
        uow: IUnitOfWork,
        password_handler: IPasswordHandler,
        redis_client: IRedisClient,
        pubsub: IPubSubManager,
    ):
        self._uow = uow
        self._password_handler = password_handler
        self._cache = CacheManager(redis_client)
        self._pubsub = pubsub

    async def _invalidate_user_caches(self, user_id: UUID | None = None) -> None:
        await self._cache.invalidate_namespace("users")
        if user_id:
            await self._cache.delete_cached(f"user:{user_id}")
            await self._cache.delete_cached(f"user:session:{user_id}")

    async def create_user(self, create_dto: UserCreateDTO) -> UserDTO:
        logger.debug(f"Creating user with email: {create_dto.email}")
        async with self._uow as uow:
            existing_user = await uow.user_repository.get_by_email(create_dto.email)
            if existing_user:
                logger.warning(f"User creation failed: email {create_dto.email} already exists")
                raise BusinessError(f"User with email {create_dto.email} already exists")

            existing_user = await uow.user_repository.get_by_phone_number(create_dto.phone_number)
            if existing_user:
                logger.warning(f"User creation failed: phone number {create_dto.phone_number} already exists")
                raise BusinessError(f"User with phone number {create_dto.phone_number} already exists")

            hashed_password = self._password_handler.hash_password(create_dto.password)
            user = UserMapper.from_create_dto_to_entity(create_dto, hashed_password)
            created_user = await uow.user_repository.create(user)
            logger.info(f"User created successfully with id: {created_user.id}, email: {create_dto.email}")

            # Если роль пользователя - CUSTOMER, создаем также запись в таблице customers
            if created_user.role == UserRole.CUSTOMER:
                existing_customer = await uow.customer_repository.get_by_user_id(created_user.id)
                if not existing_customer:
                    customer = Customer(
                        id=uuid4(),
                        user_id=created_user.id,
                        date_of_birth=None,
                    )
                    created_customer = await uow.customer_repository.create(customer)
                    logger.info(
                        f"Customer created successfully with id: {created_customer.id}, user_id: {created_user.id}"
                    )
                else:
                    logger.warning(f"Customer already exists for user {created_user.id}, skipping creation")

        dto = UserMapper.from_entity_to_dto(created_user)
        await self._invalidate_user_caches(created_user.id)
        
        await self._pubsub.publish(
            settings.pubsub_settings.data_changes_channel, {"entity": "user", "action": "create", "id": str(created_user.id)}
        )
        
        return dto

    async def get_user(self, user_id: UUID) -> UserDTO:
        logger.debug(f"Getting user with id: {user_id}")
        cache_key = f"user:{user_id}"
        cached_user = await self._cache.get_cached(cache_key, UserDTO)
        if cached_user:
            return cached_user

        async with self._uow as uow:
            user = await uow.user_repository.get_by_id(user_id)
            if not user:
                logger.warning(f"User not found with id: {user_id}")
                raise NotFoundError("User", str(user_id))
        
        dto = UserMapper.from_entity_to_dto(user)
        await self._cache.set_cached(cache_key, dto, UserDTO, ttl=3600)
        return dto

    async def get_user_by_email(self, email: str) -> UserDTO:
        async with self._uow as uow:
            user = await uow.user_repository.get_by_email(email)
            if not user:
                raise NotFoundError("User", email)
        return UserMapper.from_entity_to_dto(user)

    async def get_users(self, user_filter: UserFilter) -> tuple[list[UserDTO], int]:
        version = await self._cache.get_namespace_version("users")
        cache_key = f"users:list:v{version}:{hash(str(user_filter))}"
        
        cached_result = await self._cache.get_cached(cache_key, tuple[list[UserDTO], int])
        if cached_result:
            return cached_result

        async with self._uow as uow:
            users, total = await uow.user_repository.get_users(user_filter)
        
        result = [UserMapper.from_entity_to_dto(user) for user in users], total
        await self._cache.set_cached(cache_key, result, tuple[list[UserDTO], int], ttl=3600)
        return result

    async def update_user(
        self, user_id: UUID, update_dto: UserUpdateDTO, current_user_id: UUID | None = None
    ) -> UserDTO:
        logger.debug(f"Updating user with id: {user_id}, current_user_id: {current_user_id}")
        async with self._uow as uow:
            user = await uow.user_repository.get_by_id(user_id)
            if not user:
                logger.warning(f"User update failed: user not found with id: {user_id}")
                raise NotFoundError("User", str(user_id))

            if current_user_id and current_user_id != user_id:
                current_user = await uow.user_repository.get_by_id(current_user_id)
                if not current_user:
                    raise NotFoundError("User", str(current_user_id))
                if current_user.role not in (UserRole.ADMIN, UserRole.EMPLOYEE):
                    logger.warning(
                        f"User update failed: permission denied for user {current_user_id} to update {user_id}"
                    )
                    raise PermissionError("You can only update your own profile")

            if update_dto.email and update_dto.email != user.email:
                existing_user = await uow.user_repository.get_by_email(update_dto.email)
                if existing_user:
                    logger.warning(f"User update failed: email {update_dto.email} already exists")
                    raise BusinessError(f"User with email {update_dto.email} already exists")

            if update_dto.phone_number and update_dto.phone_number != user.phone_number:
                existing_user = await uow.user_repository.get_by_phone_number(update_dto.phone_number)
                if existing_user:
                    logger.warning(f"User update failed: phone number {update_dto.phone_number} already exists")
                    raise BusinessError(f"User with phone number {update_dto.phone_number} already exists")

            updated_user = UserMapper.from_update_dto_to_entity(user, update_dto)
            saved_user = await uow.user_repository.update(updated_user)
            logger.info(f"User updated successfully with id: {user_id}")

        dto = UserMapper.from_entity_to_dto(saved_user)
        await self._invalidate_user_caches(user_id)

        await self._pubsub.publish(
            settings.pubsub_settings.data_changes_channel, {"entity": "user", "action": "update", "id": str(user_id)}
        )

        return dto

    async def delete_user(self, user_id: UUID, current_user_id: UUID | None = None) -> bool:
        logger.debug(f"Deleting user with id: {user_id}, current_user_id: {current_user_id}")
        async with self._uow as uow:
            user = await uow.user_repository.get_by_id(user_id)
            if not user:
                logger.warning(f"User deletion failed: user not found with id: {user_id}")
                raise NotFoundError("User", str(user_id))

            if current_user_id and current_user_id != user_id:
                current_user = await uow.user_repository.get_by_id(current_user_id)
                if not current_user:
                    raise NotFoundError("User", str(current_user_id))
                if current_user.role != UserRole.ADMIN:
                    logger.warning(
                        f"User deletion failed: permission denied for user {current_user_id} to delete {user_id}"
                    )
                    raise PermissionError("Only admins can delete other users")

            result = await uow.user_repository.delete(user_id)
            logger.info(f"User deleted successfully with id: {user_id}")
        
        await self._invalidate_user_caches(user_id)

        await self._pubsub.publish(
            settings.pubsub_settings.data_changes_channel, {"entity": "user", "action": "delete", "id": str(user_id)}
        )

        return result
