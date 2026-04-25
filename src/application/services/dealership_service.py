from src.application.abstractions.dealership_service import IDealershipService
from src.application.dtos.dealership_dto import (
    DealershipCreateDTO,
    DealershipDTO,
    DealershipUpdateDTO,
)
from src.application.exceptions.errors import NotFoundError
from src.application.mappers.dealership_mapper import DealershipMapper
from src.application.utils.cache_manager import CacheManager
from src.domain.abstractions.database.uow import IUnitOfWork
from src.domain.abstractions.redis.redis_client import IRedisClient


class DealershipService(IDealershipService):
    def __init__(self, uow: IUnitOfWork, redis_client: IRedisClient):
        self._uow = uow
        self._cache = CacheManager(redis_client)

    async def _invalidate_cache(self, dealership_id: int | None = None) -> None:
        await self._cache.invalidate_namespace("catalog:dealerships")
        if dealership_id:
            await self._cache.delete_cached(f"catalog:dealerships:{dealership_id}")

    async def create_dealership(self, create_dto: DealershipCreateDTO) -> DealershipDTO:
        async with self._uow as uow:
            city = await uow.city_repository.get_by_id(create_dto.city_id)
            if not city:
                raise NotFoundError("City", str(create_dto.city_id))

            all_dealerships, _ = await uow.dealership_repository.get_all()
            next_id = max([d.id for d in all_dealerships], default=0) + 1

            dealership = DealershipMapper.from_create_dto_to_entity(create_dto, next_id)
            created_dealership = await uow.dealership_repository.create(dealership)

        dto = DealershipMapper.from_entity_to_dto(created_dealership)
        await self._invalidate_cache(created_dealership.id)
        return dto

    async def get_dealership(self, dealership_id: int) -> DealershipDTO:
        cache_key = f"catalog:dealerships:{dealership_id}"
        cached_dealership = await self._cache.get_cached(cache_key, DealershipDTO)
        if cached_dealership:
            return cached_dealership

        async with self._uow as uow:
            dealership = await uow.dealership_repository.get_by_id(dealership_id)
            if not dealership:
                raise NotFoundError("Dealership", str(dealership_id))
        
        dto = DealershipMapper.from_entity_to_dto(dealership)
        await self._cache.set_cached(cache_key, dto, DealershipDTO, ttl=86400)
        return dto

    async def get_all_dealerships(self, page: int = 1, limit: int = 20) -> tuple[list[DealershipDTO], int]:
        version = await self._cache.get_namespace_version("catalog:dealerships")
        cache_key = f"catalog:dealerships:v{version}:all:{page}:{limit}"
        
        cached_res = await self._cache.get_cached(cache_key, tuple[list[DealershipDTO], int])
        if cached_res:
            return cached_res

        async with self._uow as uow:
            dealerships, total = await uow.dealership_repository.get_all(page=page, limit=limit)
        
        result = [DealershipMapper.from_entity_to_dto(d) for d in dealerships], total
        await self._cache.set_cached(cache_key, result, tuple[list[DealershipDTO], int], ttl=86400)
        return result

    async def get_active_dealerships(self) -> list[DealershipDTO]:
        version = await self._cache.get_namespace_version("catalog:dealerships")
        cache_key = f"catalog:dealerships:v{version}:active"
        
        cached_res = await self._cache.get_cached(cache_key, list[DealershipDTO])
        if cached_res:
            return cached_res

        async with self._uow as uow:
            dealerships = await uow.dealership_repository.get_active()
        
        result = [DealershipMapper.from_entity_to_dto(d) for d in dealerships]
        await self._cache.set_cached(cache_key, result, list[DealershipDTO], ttl=86400)
        return result

    async def get_dealerships_by_city(self, city_id: int) -> list[DealershipDTO]:
        version = await self._cache.get_namespace_version("catalog:dealerships")
        cache_key = f"catalog:dealerships:v{version}:city:{city_id}"
        
        cached_res = await self._cache.get_cached(cache_key, list[DealershipDTO])
        if cached_res:
            return cached_res

        async with self._uow as uow:
            dealerships = await uow.dealership_repository.get_by_city_id(city_id)
        
        result = [DealershipMapper.from_entity_to_dto(d) for d in dealerships]
        await self._cache.set_cached(cache_key, result, list[DealershipDTO], ttl=86400)
        return result

    async def get_dealerships_by_country(self, country: str) -> list[DealershipDTO]:
        version = await self._cache.get_namespace_version("catalog:dealerships")
        cache_key = f"catalog:dealerships:v{version}:country:{country}"
        
        cached_res = await self._cache.get_cached(cache_key, list[DealershipDTO])
        if cached_res:
            return cached_res

        async with self._uow as uow:
            dealerships = await uow.dealership_repository.get_by_country(country)
        
        result = [DealershipMapper.from_entity_to_dto(d) for d in dealerships]
        await self._cache.set_cached(cache_key, result, list[DealershipDTO], ttl=86400)
        return result

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

        dto = DealershipMapper.from_entity_to_dto(saved_dealership)
        await self._invalidate_cache(dealership_id)
        return dto

    async def delete_dealership(self, dealership_id: int) -> bool:
        async with self._uow as uow:
            dealership = await uow.dealership_repository.get_by_id(dealership_id)
            if not dealership:
                raise NotFoundError("Dealership", str(dealership_id))

            result = await uow.dealership_repository.delete(dealership_id)
        
        await self._invalidate_cache(dealership_id)
        return result
