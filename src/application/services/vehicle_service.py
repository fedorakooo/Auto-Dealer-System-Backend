from uuid import UUID

from src.application.abstractions.model_media_service import IModelMediaService
from src.application.abstractions.vehicle_media_service import IVehicleMediaService
from src.application.abstractions.vehicle_service import IVehicleService
from src.application.dtos.vehicle_dto import VehicleCreateDTO, VehicleDTO, VehicleUpdateDTO
from src.application.exceptions.errors import BusinessError, NotFoundError, ValidationError
from src.application.mappers.vehicle_mapper import VehicleMapper
from src.config import settings
from src.domain.abstractions.database.uow import IUnitOfWork
from src.domain.abstractions.pubsub.manager import IPubSubManager
from src.domain.value_objects.filters import VehicleFilter
from src.domain.value_objects.media_type import MediaType
from src.logger import get_logger

logger = get_logger(__name__)


class VehicleService(IVehicleService):
    def __init__(
        self,
        uow: IUnitOfWork,
        pubsub: IPubSubManager,
        model_media_service: IModelMediaService | None = None,
        vehicle_media_service: IVehicleMediaService | None = None,
    ):
        self._uow = uow
        self._model_media_service = model_media_service
        self._vehicle_media_service = vehicle_media_service
        self._pubsub = pubsub

    async def _enrich(self, dtos: list[VehicleDTO]) -> None:
        """Attach model name plus both photo sets: the vehicle's own and its model's appearance."""
        if not dtos:
            return

        model_names: dict[UUID, str] = {}
        async with self._uow as uow:
            for model_id in {dto.model_id for dto in dtos if not dto.model_name}:
                model = await uow.model_repository.get_by_id(model_id)
                if model:
                    model_names[model_id] = model.name

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
            dto.model_images = model_images.get(dto.model_id)
            dto.images = await self._load_images(
                self._vehicle_media_service.get_media_by_vehicle if self._vehicle_media_service else None,
                dto.id,
                "vehicle-media",
            )

    @staticmethod
    async def _load_images(loader, owner_id: UUID, route: str) -> list[str] | None:
        """Return sorted image file URLs from a media loader, or None when there are none."""
        if loader is None:
            return None
        try:
            media_list = await loader(owner_id)
        except Exception as e:
            logger.warning(f"Failed to load {route} for {owner_id}: {e}")
            return None
        urls = [
            f"/api/v1/{route}/{media.id}/file"
            for media in sorted(media_list, key=lambda m: m.sort_order)
            if media.media_type == MediaType.IMAGE
        ]
        return urls or None

    async def create_vehicle(self, create_dto: VehicleCreateDTO) -> VehicleDTO:
        logger.debug(f"Creating vehicle with VIN: {create_dto.vin}, model_id: {create_dto.model_id}")
        async with self._uow as uow:
            model = await uow.model_repository.get_by_id(create_dto.model_id)
            if not model:
                logger.warning(f"Vehicle creation failed: model not found with id: {create_dto.model_id}")
                raise NotFoundError("Model", str(create_dto.model_id))

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

            vehicle = VehicleMapper.from_create_dto_to_entity(create_dto)
            created_vehicle = await uow.vehicle_repository.create(vehicle)
            logger.info(f"Vehicle created successfully with id: {created_vehicle.id}, VIN: {create_dto.vin}")

        await self._pubsub.publish(
            settings.pubsub_settings.data_changes_channel,
            {"entity": "vehicle", "action": "create", "id": str(created_vehicle.id)},
        )

        dto = VehicleMapper.from_entity_to_dto(created_vehicle)
        await self._enrich([dto])
        return dto

    async def get_vehicle(self, vehicle_id: UUID) -> VehicleDTO:
        async with self._uow as uow:
            vehicle = await uow.vehicle_repository.get_by_id(vehicle_id)
            if not vehicle:
                raise NotFoundError("Vehicle", str(vehicle_id))

        dto = VehicleMapper.from_entity_to_dto(vehicle)
        await self._enrich([dto])

        return dto

    async def get_vehicles(self, vehicle_filter: VehicleFilter) -> tuple[list[VehicleDTO], int]:
        async with self._uow as uow:
            vehicles, total = await uow.vehicle_repository.get_vehicles(vehicle_filter)

        dtos = [VehicleMapper.from_entity_to_dto(vehicle) for vehicle in vehicles]

        await self._enrich(dtos)

        return dtos, total

    async def search_vehicles(
        self,
        model_name: str | None = None,
        body_type: str | None = None,
        fuel_type: str | None = None,
        transmission_type: str | None = None,
        min_price: float = 0,
        max_price: float = 99999999,
        dealership_id: int | None = None,
    ) -> list[VehicleDTO]:
        async with self._uow as uow:
            vehicles = await uow.vehicle_repository.search_vehicles(
                model_name=model_name,
                body_type=body_type,
                fuel_type=fuel_type,
                transmission_type=transmission_type,
                min_price=min_price,
                max_price=max_price,
                dealership_id=dealership_id,
            )

        dtos = [VehicleMapper.from_entity_to_dto(vehicle) for vehicle in vehicles]

        await self._enrich(dtos)

        return dtos

    async def get_vehicles_by_dealership(self, dealership_id: int) -> list[VehicleDTO]:
        async with self._uow as uow:
            vehicles = await uow.vehicle_repository.get_by_dealership_id(dealership_id)

        dtos = [VehicleMapper.from_entity_to_dto(vehicle) for vehicle in vehicles]

        await self._enrich(dtos)

        return dtos

    async def update_vehicle(self, vehicle_id: UUID, update_dto: VehicleUpdateDTO) -> VehicleDTO:
        async with self._uow as uow:
            vehicle = await uow.vehicle_repository.get_by_id(vehicle_id)
            if not vehicle:
                raise NotFoundError("Vehicle", str(vehicle_id))

            if update_dto.model_id:
                model = await uow.model_repository.get_by_id(update_dto.model_id)
                if not model:
                    raise NotFoundError("Model", str(update_dto.model_id))

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

            updated_vehicle = VehicleMapper.from_update_dto_to_entity(vehicle, update_dto)
            saved_vehicle = await uow.vehicle_repository.update(updated_vehicle)

        await self._pubsub.publish(
            settings.pubsub_settings.data_changes_channel,
            {"entity": "vehicle", "action": "update", "id": str(vehicle_id)},
        )

        dto = VehicleMapper.from_entity_to_dto(saved_vehicle)
        await self._enrich([dto])

        return dto

    async def delete_vehicle(self, vehicle_id: UUID) -> bool:
        async with self._uow as uow:
            vehicle = await uow.vehicle_repository.get_by_id(vehicle_id)
            if not vehicle:
                raise NotFoundError("Vehicle", str(vehicle_id))

        if self._vehicle_media_service:
            await self._vehicle_media_service.delete_all_vehicle_media(vehicle_id)

        async with self._uow as uow:
            result = await uow.vehicle_repository.delete(vehicle_id)

        await self._pubsub.publish(
            settings.pubsub_settings.data_changes_channel,
            {"entity": "vehicle", "action": "delete", "id": str(vehicle_id)},
        )

        return result
