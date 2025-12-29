from uuid import UUID

from src.application.abstractions.customer_service import ICustomerService
from src.application.dtos.customer_dto import CustomerCreateDTO, CustomerDTO, CustomerUpdateDTO
from src.application.dtos.user_dto import UserCreateDTO
from src.application.exceptions.errors import BusinessError, NotFoundError
from src.application.mappers.customer_mapper import CustomerMapper
from src.application.mappers.user_mapper import UserMapper
from src.domain.abstractions.auth.password_handler import IPasswordHandler
from src.domain.abstractions.database.uow import IUnitOfWork
from src.domain.value_objects.user_role import UserRole
from src.logger import get_logger

logger = get_logger(__name__)


class CustomerService(ICustomerService):
    def __init__(self, uow: IUnitOfWork, password_handler: IPasswordHandler):
        self._uow = uow
        self._password_handler = password_handler

    async def create_customer(self, create_dto: CustomerCreateDTO) -> CustomerDTO:
        logger.debug(f"Creating customer with email: {create_dto.email}")
        async with self._uow as uow:
            # Проверяем, не существует ли уже пользователь с таким email
            existing_user = await uow.user_repository.get_by_email(create_dto.email)
            if existing_user:
                logger.warning(f"Customer creation failed: email {create_dto.email} already exists")
                raise BusinessError(f"User with email {create_dto.email} already exists")

            # Проверяем, не существует ли уже пользователь с таким телефоном
            existing_user = await uow.user_repository.get_by_phone_number(create_dto.phone_number)
            if existing_user:
                logger.warning(f"Customer creation failed: phone number {create_dto.phone_number} already exists")
                raise BusinessError(f"User with phone number {create_dto.phone_number} already exists")

            # Создаем пользователя
            hashed_password = self._password_handler.hash_password(create_dto.password)
            user_create_dto = UserCreateDTO(
                first_name=create_dto.first_name,
                second_name=create_dto.second_name,
                phone_number=create_dto.phone_number,
                email=create_dto.email,
                password=create_dto.password,
                role=UserRole.CUSTOMER,
            )
            user = UserMapper.from_create_dto_to_entity(user_create_dto, hashed_password)
            created_user = await uow.user_repository.create(user)
            logger.info(f"User created successfully with id: {created_user.id}, email: {create_dto.email}")

            # Создаем customer с user_id созданного пользователя
            customer = CustomerMapper.from_create_dto_to_entity(create_dto, created_user.id)
            created_customer = await uow.customer_repository.create(customer)
            logger.info(f"Customer created successfully with id: {created_customer.id}, user_id: {created_user.id}")

        return CustomerMapper.from_entity_to_dto(created_customer)

    async def get_customer(self, customer_id: UUID) -> CustomerDTO:
        async with self._uow as uow:
            customer = await uow.customer_repository.get_by_id(customer_id)
            if not customer:
                raise NotFoundError("Customer", str(customer_id))
        return CustomerMapper.from_entity_to_dto(customer)

    async def get_customer_by_user_id(self, user_id: UUID) -> CustomerDTO:
        async with self._uow as uow:
            customer = await uow.customer_repository.get_by_user_id(user_id)
            if not customer:
                raise NotFoundError("Customer", str(user_id))
        return CustomerMapper.from_entity_to_dto(customer)

    async def update_customer(self, customer_id: UUID, update_dto: CustomerUpdateDTO) -> CustomerDTO:
        async with self._uow as uow:
            customer = await uow.customer_repository.get_by_id(customer_id)
            if not customer:
                raise NotFoundError("Customer", str(customer_id))

            updated_customer = CustomerMapper.from_update_dto_to_entity(customer, update_dto)
            saved_customer = await uow.customer_repository.update(updated_customer)

        return CustomerMapper.from_entity_to_dto(saved_customer)

    async def delete_customer(self, customer_id: UUID) -> bool:
        async with self._uow as uow:
            customer = await uow.customer_repository.get_by_id(customer_id)
            if not customer:
                raise NotFoundError("Customer", str(customer_id))

            result = await uow.customer_repository.delete(customer_id)
        return result
