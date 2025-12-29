from src.application.abstractions.dealership_service import IDealershipService
from src.application.dtos.dealership_dto import (
    DealershipCreateDTO,
    DealershipDTO,
    DealershipUpdateDTO,
)
from src.application.exceptions.errors import NotFoundError
from src.application.mappers.dealership_mapper import DealershipMapper
from src.domain.abstractions.database.uow import IUnitOfWork


class DealershipService(IDealershipService):
    def __init__(self, uow: IUnitOfWork):
        self._uow = uow

    async def create_dealership(self, create_dto: DealershipCreateDTO) -> DealershipDTO:
        async with self._uow as uow:
            city = await uow.city_repository.get_by_id(create_dto.city_id)
            if not city:
                raise NotFoundError("City", str(create_dto.city_id))

            all_dealerships, _ = await uow.dealership_repository.get_all()
            next_id = max([d.id for d in all_dealerships], default=0) + 1

            dealership = DealershipMapper.from_create_dto_to_entity(create_dto, next_id)
            created_dealership = await uow.dealership_repository.create(dealership)

        return DealershipMapper.from_entity_to_dto(created_dealership)

    async def get_dealership(self, dealership_id: int) -> DealershipDTO:
        async with self._uow as uow:
            dealership = await uow.dealership_repository.get_by_id(dealership_id)
            if not dealership:
                raise NotFoundError("Dealership", str(dealership_id))
        return DealershipMapper.from_entity_to_dto(dealership)

    async def get_all_dealerships(self, page: int = 1, limit: int = 20) -> tuple[list[DealershipDTO], int]:
        async with self._uow as uow:
            dealerships, total = await uow.dealership_repository.get_all(page=page, limit=limit)
        return [DealershipMapper.from_entity_to_dto(d) for d in dealerships], total

    async def get_active_dealerships(self) -> list[DealershipDTO]:
        async with self._uow as uow:
            dealerships = await uow.dealership_repository.get_active()
        return [DealershipMapper.from_entity_to_dto(d) for d in dealerships]

    async def get_dealerships_by_city(self, city_id: int) -> list[DealershipDTO]:
        async with self._uow as uow:
            dealerships = await uow.dealership_repository.get_by_city_id(city_id)
        return [DealershipMapper.from_entity_to_dto(d) for d in dealerships]

    async def get_dealerships_by_country(self, country: str) -> list[DealershipDTO]:
        async with self._uow as uow:
            dealerships = await uow.dealership_repository.get_by_country(country)
        return [DealershipMapper.from_entity_to_dto(d) for d in dealerships]

    async def update_dealership(self, dealership_id: int, update_dto: DealershipUpdateDTO) -> DealershipDTO:
        async with self._uow as uow:
            dealership = await uow.dealership_repository.get_by_id(dealership_id)
            if not dealership:
                raise NotFoundError("Dealership", str(dealership_id))

            if update_dto.city_id:
                city = await uow.city_repository.get_by_id(update_dto.city_id)
                if not city:
                    raise NotFoundError("City", str(update_dto.city_id))

            updated_dealership = DealershipMapper.from_update_dto_to_entity(dealership, update_dto)
            saved_dealership = await uow.dealership_repository.update(updated_dealership)

        return DealershipMapper.from_entity_to_dto(saved_dealership)

    async def delete_dealership(self, dealership_id: int) -> bool:
        async with self._uow as uow:
            dealership = await uow.dealership_repository.get_by_id(dealership_id)
            if not dealership:
                raise NotFoundError("Dealership", str(dealership_id))

            result = await uow.dealership_repository.delete(dealership_id)
        return result
