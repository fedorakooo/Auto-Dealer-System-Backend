from uuid import UUID

from src.application.abstractions.favorite_service import IFavoriteService
from src.application.dtos.favorite_dto import FavoriteAddDTO, FavoriteRemoveDTO
from src.application.dtos.vehicle_dto import VehicleDTO
from src.application.exceptions.errors import BusinessError, NotFoundError
from src.application.mappers.vehicle_mapper import VehicleMapper
from src.domain.abstractions.database.uow import IUnitOfWork


class FavoriteService(IFavoriteService):
    def __init__(self, uow: IUnitOfWork):
        self._uow = uow

    async def add_favorite(self, favorite_dto: FavoriteAddDTO) -> bool:
        async with self._uow as uow:
            customer = await uow.customer_repository.get_by_id(favorite_dto.customer_id)
            if not customer:
                raise NotFoundError("Customer", str(favorite_dto.customer_id))

            vehicle = await uow.vehicle_repository.get_by_id(favorite_dto.vehicle_id)
            if not vehicle:
                raise NotFoundError("Vehicle", str(favorite_dto.vehicle_id))

            exists = await uow.favorite_repository.exists(favorite_dto.customer_id, favorite_dto.vehicle_id)
            if exists:
                raise BusinessError("Vehicle is already in favorites")

            result = await uow.favorite_repository.add(favorite_dto.customer_id, favorite_dto.vehicle_id)
        return result

    async def remove_favorite(self, favorite_dto: FavoriteRemoveDTO) -> bool:
        async with self._uow as uow:
            customer = await uow.customer_repository.get_by_id(favorite_dto.customer_id)
            if not customer:
                raise NotFoundError("Customer", str(favorite_dto.customer_id))

            vehicle = await uow.vehicle_repository.get_by_id(favorite_dto.vehicle_id)
            if not vehicle:
                raise NotFoundError("Vehicle", str(favorite_dto.vehicle_id))

            exists = await uow.favorite_repository.exists(favorite_dto.customer_id, favorite_dto.vehicle_id)
            if not exists:
                raise BusinessError("Vehicle is not in favorites")

            result = await uow.favorite_repository.remove(favorite_dto.customer_id, favorite_dto.vehicle_id)
        return result

    async def get_favorites(self, customer_id: UUID) -> list[VehicleDTO]:
        async with self._uow as uow:
            customer = await uow.customer_repository.get_by_id(customer_id)
            if not customer:
                raise NotFoundError("Customer", str(customer_id))

            vehicles = await uow.favorite_repository.get_by_customer_id(customer_id)
        return [VehicleMapper.from_entity_to_dto(vehicle) for vehicle in vehicles]
