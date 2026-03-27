from src.application.abstractions.city_service import ICityService
from src.application.dtos.city_dto import CityCreateDTO, CityDTO, CityUpdateDTO
from src.application.exceptions.errors import BusinessError, NotFoundError
from src.application.mappers.city_mapper import CityMapper
from src.application.utils.cache_manager import CacheManager
from src.domain.abstractions.database.uow import IUnitOfWork
from src.domain.abstractions.redis.redis_client import IRedisClient


class CityService(ICityService):
    def __init__(self, uow: IUnitOfWork, redis_client: IRedisClient):
        self._uow = uow
        self._cache = CacheManager(redis_client)

    async def _invalidate_cache(self, city_id: int | None = None) -> None:
        await self._cache.delete_cached("catalog:cities:all")
        if city_id:
            await self._cache.delete_cached(f"catalog:cities:{city_id}")

    async def create_city(self, create_dto: CityCreateDTO) -> CityDTO:
        async with self._uow as uow:
            existing_city = await uow.city_repository.get_by_name_and_country(create_dto.name, create_dto.country)
            if existing_city:
                raise BusinessError(f"City {create_dto.name} in {create_dto.country} already exists")

            all_cities = await uow.city_repository.get_all()
            next_id = max([c.id for c in all_cities], default=0) + 1

            city = CityMapper.from_create_dto_to_entity(create_dto, next_id)
            created_city = await uow.city_repository.create(city)

        dto = CityMapper.from_entity_to_dto(created_city)
        await self._invalidate_cache(created_city.id)
        return dto

    async def get_city(self, city_id: int) -> CityDTO:
        cache_key = f"catalog:cities:{city_id}"
        cached_city = await self._cache.get_cached(cache_key, CityDTO)
        if cached_city:
            return cached_city

        async with self._uow as uow:
            city = await uow.city_repository.get_by_id(city_id)
            if not city:
                raise NotFoundError("City", str(city_id))
        
        dto = CityMapper.from_entity_to_dto(city)
        await self._cache.set_cached(cache_key, dto, CityDTO, ttl=86400)
        return dto

    async def get_all_cities(self) -> list[CityDTO]:
        cache_key = "catalog:cities:all"
        cached_cities = await self._cache.get_cached(cache_key, list[CityDTO])
        if cached_cities:
            return cached_cities

        async with self._uow as uow:
            cities = await uow.city_repository.get_all()
        
        result = [CityMapper.from_entity_to_dto(city) for city in cities]
        await self._cache.set_cached(cache_key, result, list[CityDTO], ttl=86400)
        return result

    async def update_city(self, city_id: int, update_dto: CityUpdateDTO) -> CityDTO:
        async with self._uow as uow:
            city = await uow.city_repository.get_by_id(city_id)
            if not city:
                raise NotFoundError("City", str(city_id))

            new_name = update_dto.name if update_dto.name is not None else city.name
            new_country = update_dto.country if update_dto.country is not None else city.country
            if new_name != city.name or new_country != city.country:
                existing_city = await uow.city_repository.get_by_name_and_country(new_name, new_country)
                if existing_city and existing_city.id != city_id:
                    raise BusinessError(f"City {new_name} in {new_country} already exists")

            updated_city = CityMapper.from_update_dto_to_entity(city, update_dto)
            saved_city = await uow.city_repository.update(updated_city)

        dto = CityMapper.from_entity_to_dto(saved_city)
        await self._invalidate_cache(city_id)
        return dto

    async def delete_city(self, city_id: int) -> bool:
        async with self._uow as uow:
            city = await uow.city_repository.get_by_id(city_id)
            if not city:
                raise NotFoundError("City", str(city_id))

            result = await uow.city_repository.delete(city_id)
        
        await self._invalidate_cache(city_id)
        return result
