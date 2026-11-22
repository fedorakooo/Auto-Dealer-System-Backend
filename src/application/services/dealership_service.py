from collections.abc import Awaitable, Callable
from dataclasses import replace

from src.application.abstractions.dealership_service import IDealershipService
from src.application.dtos.dealership_dto import (
    DealershipCreateDTO,
    DealershipDTO,
    DealershipUpdateDTO,
)
from src.application.exceptions.errors import NotFoundError
from src.application.mappers.dealership_mapper import DealershipMapper
from src.application.services.dealership_access import ensure_can_manage_dealership, get_managed_dealership_id
from src.application.utils.cache_manager import CacheManager
from src.domain.abstractions.database.uow import IUnitOfWork
from src.domain.abstractions.redis.redis_client import IRedisClient
from src.domain.entities.dealership import Dealership
from src.domain.entities.user import User
from src.domain.value_objects.user_role import UserRole

MAX_MANAGED_DEALERSHIPS = 1000


class DealershipService(IDealershipService):
    """Service for dealership operations."""

    def __init__(self, uow: IUnitOfWork, redis_client: IRedisClient) -> None:
        self._uow = uow
        self._cache = CacheManager(redis_client)

    async def _invalidate_cache(self, dealership_id: int | None = None) -> None:
        await self._cache.invalidate_namespace("catalog:dealerships")
        if dealership_id:
            await self._cache.delete_cached(f"catalog:dealerships:{dealership_id}")

    async def _with_stats(self, dealerships: list[DealershipDTO]) -> list[DealershipDTO]:
        """Adds rating and gallery cover; read live because reviews and photos change outside this cache."""
        if not dealerships:
            return dealerships
        ids = [d.id for d in dealerships]
        async with self._uow as uow:
            ratings = await uow.dealership_review_repository.get_rating_summaries(ids)
            covers = await uow.dealership_media_repository.get_cover_ids(ids)
        result = []
        for dealership in dealerships:
            rating = ratings.get(dealership.id)
            result.append(
                replace(
                    dealership,
                    rating_average=rating.average_rating if rating else None,
                    reviews_count=rating.reviews_count if rating else 0,
                    cover_media_id=covers.get(dealership.id),
                )
            )
        return result

    async def create_dealership(self, create_dto: DealershipCreateDTO) -> DealershipDTO:
        """Create a new dealership."""
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
        """Get dealership by ID."""
        cache_key = f"catalog:dealerships:{dealership_id}"
        dto = await self._cache.get_cached(cache_key, DealershipDTO)
        if not dto:
            async with self._uow as uow:
                dealership = await uow.dealership_repository.get_by_id(dealership_id)
                if not dealership:
                    raise NotFoundError("Dealership", str(dealership_id))

            dto = DealershipMapper.from_entity_to_dto(dealership)
            await self._cache.set_cached(cache_key, dto, DealershipDTO, ttl=86400)
        return (await self._with_stats([dto]))[0]

    async def get_all_dealerships(self, page: int = 1, limit: int = 20) -> tuple[list[DealershipDTO], int]:
        """Get all dealerships with pagination."""
        version = await self._cache.get_namespace_version("catalog:dealerships")
        cache_key = f"catalog:dealerships:v{version}:all:{page}:{limit}"

        cached_res = await self._cache.get_cached(cache_key, tuple[list[DealershipDTO], int])
        if cached_res:
            dealerships, total = cached_res
        else:
            async with self._uow as uow:
                entities, total = await uow.dealership_repository.get_all(page=page, limit=limit)
            dealerships = [DealershipMapper.from_entity_to_dto(d) for d in entities]
            await self._cache.set_cached(cache_key, (dealerships, total), tuple[list[DealershipDTO], int], ttl=86400)
        return await self._with_stats(dealerships), total

    async def _get_cached_list(
        self, suffix: str, loader: Callable[[IUnitOfWork], Awaitable[list[Dealership]]]
    ) -> list[DealershipDTO]:
        version = await self._cache.get_namespace_version("catalog:dealerships")
        cache_key = f"catalog:dealerships:v{version}:{suffix}"

        cached_res = await self._cache.get_cached(cache_key, list[DealershipDTO])
        if cached_res is None:
            async with self._uow as uow:
                entities = await loader(uow)
            cached_res = [DealershipMapper.from_entity_to_dto(d) for d in entities]
            await self._cache.set_cached(cache_key, cached_res, list[DealershipDTO], ttl=86400)
        return await self._with_stats(cached_res)

    async def get_active_dealerships(self) -> list[DealershipDTO]:
        """Get active dealerships."""
        return await self._get_cached_list("active", lambda uow: uow.dealership_repository.get_active())

    async def get_dealerships_by_city(self, city_id: int) -> list[DealershipDTO]:
        """Get dealerships by city ID."""
        return await self._get_cached_list(
            f"city:{city_id}", lambda uow: uow.dealership_repository.get_by_city_id(city_id)
        )

    async def get_dealerships_by_country(self, country: str) -> list[DealershipDTO]:
        """Get dealerships by country."""
        return await self._get_cached_list(
            f"country:{country}", lambda uow: uow.dealership_repository.get_by_country(country)
        )

    async def get_managed_dealerships(self, requesting_user: User) -> list[DealershipDTO]:
        """Get dealerships the user may manage: all for an admin, the own one for an employee."""
        async with self._uow as uow:
            if requesting_user.role == UserRole.ADMIN:
                entities, _ = await uow.dealership_repository.get_all(page=1, limit=MAX_MANAGED_DEALERSHIPS)
            else:
                own_id = await get_managed_dealership_id(uow, requesting_user)
                own = await uow.dealership_repository.get_by_id(own_id) if own_id is not None else None
                entities = [own] if own else []
        return await self._with_stats([DealershipMapper.from_entity_to_dto(d) for d in entities])

    async def update_dealership(
        self, dealership_id: int, update_dto: DealershipUpdateDTO, requesting_user: User
    ) -> DealershipDTO:
        """Update dealership; only an admin or an employee of this dealership may do it."""
        async with self._uow as uow:
            dealership = await uow.dealership_repository.get_by_id(dealership_id)
            if not dealership:
                raise NotFoundError("Dealership", str(dealership_id))
            await ensure_can_manage_dealership(uow, requesting_user, dealership_id)

            if update_dto.city_id:
                city = await uow.city_repository.get_by_id(update_dto.city_id)
                if not city:
                    raise NotFoundError("City", str(update_dto.city_id))

            updated_dealership = DealershipMapper.from_update_dto_to_entity(dealership, update_dto)
            saved_dealership = await uow.dealership_repository.update(updated_dealership)

        dto = DealershipMapper.from_entity_to_dto(saved_dealership)
        await self._invalidate_cache(dealership_id)
        return (await self._with_stats([dto]))[0]

    async def delete_dealership(self, dealership_id: int) -> bool:
        """Delete dealership."""
        async with self._uow as uow:
            dealership = await uow.dealership_repository.get_by_id(dealership_id)
            if not dealership:
                raise NotFoundError("Dealership", str(dealership_id))

            result = await uow.dealership_repository.delete(dealership_id)

        await self._invalidate_cache(dealership_id)
        return result
