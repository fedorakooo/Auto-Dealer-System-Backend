from uuid import UUID

from src.application.abstractions.model_media_service import IModelMediaService
from src.application.abstractions.model_service import IModelService
from src.application.dtos.model_dto import ModelCreateDTO, ModelDTO, ModelUpdateDTO
from src.application.exceptions.errors import NotFoundError, ValidationError
from src.application.mappers.model_mapper import ModelMapper
from src.domain.abstractions.database.uow import IUnitOfWork
from src.domain.value_objects.filters import ModelFilter
from src.domain.value_objects.media_type import MediaType
from src.logger import get_logger

logger = get_logger(__name__)


class ModelService(IModelService):
    """Service for vehicle model operations."""

    def __init__(self, uow: IUnitOfWork, model_media_service: IModelMediaService | None = None) -> None:
        self._uow = uow
        self._model_media_service = model_media_service

    async def create_model(self, create_dto: ModelCreateDTO) -> ModelDTO:
        """Create a new model."""
        async with self._uow as uow:
            if create_dto.production_year_end and create_dto.production_year_start > create_dto.production_year_end:
                raise ValidationError("Production year start must be before or equal to production year end")

            model = ModelMapper.from_create_dto_to_entity(create_dto)
            created_model = await uow.model_repository.create(model)

        return ModelMapper.from_entity_to_dto(created_model)

    async def get_model(self, model_id: UUID) -> ModelDTO:
        """Get model by ID."""
        async with self._uow as uow:
            model = await uow.model_repository.get_by_id(model_id)
            if not model:
                raise NotFoundError("Model", str(model_id))
        dto = ModelMapper.from_entity_to_dto(model)
        await self._attach_stock_stats([dto])
        await self._attach_images([dto])
        return dto

    async def get_models(self, model_filter: ModelFilter) -> tuple[list[ModelDTO], int]:
        """Get models with filtering and pagination."""
        async with self._uow as uow:
            models, total = await uow.model_repository.get_models(model_filter)
        dtos = [ModelMapper.from_entity_to_dto(model) for model in models]
        await self._attach_stock_stats(dtos)
        await self._attach_images(dtos)
        return dtos, total

    async def _attach_stock_stats(self, dtos: list[ModelDTO]) -> None:
        """Fill how many vehicles of each model are in stock and the lowest in-stock price."""
        async with self._uow as uow:
            stats = await uow.vehicle_repository.get_model_stock_stats([dto.id for dto in dtos])
        for dto in dtos:
            dto.vehicles_in_stock, dto.min_price = stats.get(dto.id, (0, None))

    async def _attach_images(self, dtos: list[ModelDTO]) -> None:
        """Fill `images` with the model's appearance photos (sorted, images only)."""
        if not self._model_media_service:
            return
        for dto in dtos:
            try:
                media_list = await self._model_media_service.get_media_by_model(dto.id)
            except Exception as e:
                logger.warning(f"Failed to load media for model {dto.id}: {e}")
                continue
            urls = [
                f"/api/v1/model-media/{media.id}/file"
                for media in sorted(media_list, key=lambda m: m.sort_order)
                if media.media_type == MediaType.IMAGE
            ]
            dto.images = urls or None

    async def update_model(self, model_id: UUID, update_dto: ModelUpdateDTO) -> ModelDTO:
        """Update model."""
        async with self._uow as uow:
            model = await uow.model_repository.get_by_id(model_id)
            if not model:
                raise NotFoundError("Model", str(model_id))

            production_year_start = (
                update_dto.production_year_start
                if update_dto.production_year_start is not None
                else model.production_year_start
            )
            production_year_end = (
                update_dto.production_year_end
                if update_dto.production_year_end is not None
                else model.production_year_end
            )
            if production_year_end and production_year_start > production_year_end:
                raise ValidationError("Production year start must be before or equal to production year end")

            updated_model = ModelMapper.from_update_dto_to_entity(model, update_dto)
            saved_model = await uow.model_repository.update(updated_model)

        return ModelMapper.from_entity_to_dto(saved_model)

    async def delete_model(self, model_id: UUID) -> bool:
        """Delete model."""
        async with self._uow as uow:
            model = await uow.model_repository.get_by_id(model_id)
            if not model:
                raise NotFoundError("Model", str(model_id))

        if self._model_media_service:
            await self._model_media_service.delete_all_model_media(model_id)

        async with self._uow as uow:
            result = await uow.model_repository.delete(model_id)
        return result
