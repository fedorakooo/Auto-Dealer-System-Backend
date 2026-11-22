from collections.abc import Awaitable, Callable, Sequence
from uuid import UUID

from src.application.abstractions.model_media_service import IModelMediaService
from src.application.abstractions.vehicle_media_service import IVehicleMediaService
from src.application.abstractions.vehicle_service import IVehicleService
from src.application.dtos.model_media_dto import ModelMediaDTO
from src.application.dtos.vehicle_dto import VehicleCreateDTO, VehicleDTO, VehicleUpdateDTO
from src.application.dtos.vehicle_media_dto import VehicleMediaDTO
from src.application.exceptions.errors import BusinessError, NotFoundError, ValidationError
from src.application.mappers.vehicle_mapper import VehicleMapper
from src.config import settings
from src.domain.abstractions.database.uow import IUnitOfWork
from src.domain.abstractions.pubsub.manager import IPubSubManager
from src.domain.entities.vehicle import Vehicle
from src.domain.value_objects.filters import VehicleFilter
from src.domain.value_objects.media_type import MediaType
from src.domain.value_objects.vehicle_status import MANUAL_VEHICLE_STATUSES
from src.logger import get_logger

logger = get_logger(__name__)

MediaLoader = Callable[[UUID], Awaitable[Sequence[ModelMediaDTO | VehicleMediaDTO]]]


class VehicleService(IVehicleService):
    """Service for vehicle operations."""

    def __init__(
        self,
        uow: IUnitOfWork,
        pubsub: IPubSubManager,
        model_media_service: IModelMediaService | None = None,
        vehicle_media_service: IVehicleMediaService | None = None,
    ) -> None:
        self._uow = uow
        self._model_media_service = model_media_service
        self._vehicle_media_service = vehicle_media_service
        self._pubsub = pubsub

    async def _enrich(self, dtos: list[VehicleDTO]) -> None:
        """Attach model name plus both photo sets: the vehicle's own and its model's appearance."""
        if not dtos:
            return

        model_names: dict[UUID, str] = {}
        trim_names: dict[UUID, str] = {}
        async with self._uow as uow:
            for model_id in {dto.model_id for dto in dtos if not dto.model_name}:
                model = await uow.model_repository.get_by_id(model_id)
                if model:
                    model_names[model_id] = model.name
            for trim_id in {dto.trim_id for dto in dtos if not dto.trim_name}:
                trim = await uow.trim_repository.get_by_id(trim_id)
                if trim:
                    trim_names[trim_id] = trim.name

        model_images: dict[UUID, list[str] | None] = {}
        for model_id in {dto.model_id for dto in dtos}:
            model_images[model_id] = await self._load_images(
                self._model_media_service.get_media_by_model if self._model_media_service else None,
                model_id,
                "model-media",
            )

        for dto in dtos:
            if not dto.model_name:
                dto.model_name = model_names.get(dto.model_id)
            if not dto.trim_name:
                dto.trim_name = trim_names.get(dto.trim_id)
            dto.model_images = model_images.get(dto.model_id)
            dto.images = await self._load_images(
                self._vehicle_media_service.get_media_by_vehicle if self._vehicle_media_service else None,
                dto.id,
                f"models/{dto.model_id}/vehicles/{dto.id}/media",
            )

    @staticmethod
    async def _load_images(loader: MediaLoader | None, owner_id: UUID, route: str) -> list[str] | None:
        """Return sorted image file URLs from a media loader, or None when there are none."""
        if loader is None:
            return None
        try:
            media_list = await loader(owner_id)
        except Exception as e:
            # Missing photos must not break vehicle listings.
            logger.warning(f"Failed to load {route} for {owner_id}: {e}")
            return None
        urls = [
            f"/api/v1/{route}/{media.id}/file"
            for media in sorted(media_list, key=lambda m: m.sort_order)
            if media.media_type == MediaType.IMAGE
        ]
        return urls or None

    async def create_vehicle(self, model_id: UUID, create_dto: VehicleCreateDTO) -> VehicleDTO:
        """Create a vehicle of the model; its trim must belong to that model."""
        logger.debug(f"Creating vehicle with VIN: {create_dto.vin}, model_id: {model_id}")
        async with self._uow as uow:
            if not await uow.model_repository.get_by_id(model_id):
                raise NotFoundError("Model", str(model_id))
            await self._require_trim_of_model(uow, model_id, create_dto.trim_id)

            dealership = await uow.dealership_repository.get_by_id(create_dto.dealership_id)
            if not dealership:
                logger.warning(f"Vehicle creation failed: dealership not found with id: {create_dto.dealership_id}")
                raise NotFoundError("Dealership", str(create_dto.dealership_id))

            existing_vehicle = await uow.vehicle_repository.get_by_vin(create_dto.vin)
            if existing_vehicle:
                logger.warning(f"Vehicle creation failed: VIN {create_dto.vin} already exists")
                raise BusinessError(f"Vehicle with VIN {create_dto.vin} already exists")

            if create_dto.price < 0:
                logger.warning(f"Vehicle creation failed: negative price: {create_dto.price}")
                raise ValidationError("Price cannot be negative")

            if create_dto.status not in MANUAL_VEHICLE_STATUSES:
                raise BusinessError(f"Vehicle status '{create_dto.status.value}' is managed by orders")

            vehicle = VehicleMapper.from_create_dto_to_entity(create_dto, model_id)
            created_vehicle = await uow.vehicle_repository.create(vehicle)
            logger.info(f"Vehicle created successfully with id: {created_vehicle.id}, VIN: {create_dto.vin}")

        await self._pubsub.publish(
            settings.pubsub_settings.data_changes_channel,
            {"entity": "vehicle", "action": "create", "id": str(created_vehicle.id)},
        )

        dto = VehicleMapper.from_entity_to_dto(created_vehicle)
        await self._enrich([dto])
        return dto

    @staticmethod
    async def _require_trim_of_model(uow: IUnitOfWork, model_id: UUID, trim_id: UUID) -> None:
        trim = await uow.trim_repository.get_by_id(trim_id)
        if not trim:
            raise NotFoundError("Trim", str(trim_id))
        if trim.model_id != model_id:
            raise ValidationError(f"Trim {trim_id} does not belong to model {model_id}")

    @staticmethod
    async def _require_vehicle_of_model(uow: IUnitOfWork, model_id: UUID, vehicle_id: UUID) -> Vehicle:
        vehicle = await uow.vehicle_repository.get_by_id(vehicle_id)
        if not vehicle or vehicle.model_id != model_id:
            raise NotFoundError("Vehicle", str(vehicle_id))
        return vehicle

    async def ensure_vehicle_in_model(self, model_id: UUID, vehicle_id: UUID) -> None:
        """Raise NotFoundError unless the vehicle exists and belongs to the model."""
        async with self._uow as uow:
            await self._require_vehicle_of_model(uow, model_id, vehicle_id)

    async def get_vehicle(self, model_id: UUID, vehicle_id: UUID) -> VehicleDTO:
        """Get a vehicle of the model."""
        async with self._uow as uow:
            vehicle = await self._require_vehicle_of_model(uow, model_id, vehicle_id)

        dto = VehicleMapper.from_entity_to_dto(vehicle)
        await self._enrich([dto])

        return dto

    async def get_vehicles(self, vehicle_filter: VehicleFilter) -> tuple[list[VehicleDTO], int]:
        """Get vehicles with filtering and pagination, within one model or across models."""
        async with self._uow as uow:
            vehicles, total = await uow.vehicle_repository.get_vehicles(vehicle_filter)

        dtos = [VehicleMapper.from_entity_to_dto(vehicle) for vehicle in vehicles]

        await self._enrich(dtos)

        return dtos, total

    async def update_vehicle(
        self, model_id: UUID, vehicle_id: UUID, update_dto: VehicleUpdateDTO, current_user_id: UUID | None = None
    ) -> VehicleDTO:
        """Update a vehicle of the model; its trim can only change within the model."""
        async with self._uow as uow:
            vehicle = await self._require_vehicle_of_model(uow, model_id, vehicle_id)
            if update_dto.trim_id:
                await self._require_trim_of_model(uow, model_id, update_dto.trim_id)

            if update_dto.dealership_id:
                dealership = await uow.dealership_repository.get_by_id(update_dto.dealership_id)
                if not dealership:
                    raise NotFoundError("Dealership", str(update_dto.dealership_id))

            if update_dto.vin and update_dto.vin != vehicle.vin:
                existing_vehicle = await uow.vehicle_repository.get_by_vin(update_dto.vin)
                if existing_vehicle:
                    raise BusinessError(f"Vehicle with VIN {update_dto.vin} already exists")

            if update_dto.price is not None and update_dto.price < 0:
                raise ValidationError("Price cannot be negative")

            if update_dto.status is not None and update_dto.status != vehicle.status:
                if update_dto.status not in MANUAL_VEHICLE_STATUSES or vehicle.status not in MANUAL_VEHICLE_STATUSES:
                    raise BusinessError("Statuses 'reserved' and 'sold' are managed by orders")
                await uow.vehicle_repository.update_status(vehicle_id, update_dto.status, current_user_id)

            updated_vehicle = VehicleMapper.from_update_dto_to_entity(vehicle, update_dto)
            saved_vehicle = await uow.vehicle_repository.update(updated_vehicle)

        await self._pubsub.publish(
            settings.pubsub_settings.data_changes_channel,
            {"entity": "vehicle", "action": "update", "id": str(vehicle_id)},
        )

        dto = VehicleMapper.from_entity_to_dto(saved_vehicle)
        await self._enrich([dto])

        return dto

    async def delete_vehicle(self, model_id: UUID, vehicle_id: UUID) -> bool:
        """Delete a vehicle of the model."""
        async with self._uow as uow:
            await self._require_vehicle_of_model(uow, model_id, vehicle_id)

        if self._vehicle_media_service:
            await self._vehicle_media_service.delete_all_vehicle_media(vehicle_id)

        async with self._uow as uow:
            result = await uow.vehicle_repository.delete(vehicle_id)

        await self._pubsub.publish(
            settings.pubsub_settings.data_changes_channel,
            {"entity": "vehicle", "action": "delete", "id": str(vehicle_id)},
        )

        return result
