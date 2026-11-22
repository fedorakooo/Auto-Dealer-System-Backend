from datetime import datetime
from uuid import UUID, uuid4

from src.application.dtos.vehicle_dto import VehicleCreateDTO, VehicleDTO, VehicleUpdateDTO
from src.domain.entities.vehicle import Vehicle


class VehicleMapper:
    """Mapper for converting between Vehicle DTOs and Entities."""

    @staticmethod
    def from_entity_to_dto(vehicle: Vehicle, model_name: str | None = None) -> VehicleDTO:
        """Maps a vehicle entity to a DTO."""
        if model_name is None:
            model_name = getattr(vehicle, "model_name", None)
        return VehicleDTO(
            id=vehicle.id,
            model_id=vehicle.model_id,
            trim_id=vehicle.trim_id,
            dealership_id=vehicle.dealership_id,
            vin=vehicle.vin,
            production_year=vehicle.production_year,
            exterior_color=vehicle.exterior_color,
            interior_color=vehicle.interior_color,
            price=vehicle.price,
            status=vehicle.status,
            created_at=vehicle.created_at,
            updated_at=vehicle.updated_at,
            model_name=model_name,
        )

    @staticmethod
    def from_create_dto_to_entity(create_dto: VehicleCreateDTO, model_id: UUID) -> Vehicle:
        """Builds a new vehicle entity from a create DTO."""
        now = datetime.utcnow()
        return Vehicle(
            id=uuid4(),
            model_id=model_id,
            trim_id=create_dto.trim_id,
            dealership_id=create_dto.dealership_id,
            vin=create_dto.vin,
            production_year=create_dto.production_year,
            exterior_color=create_dto.exterior_color,
            interior_color=create_dto.interior_color,
            price=create_dto.price,
            status=create_dto.status,
            created_at=now,
            updated_at=None,
        )

    @staticmethod
    def from_update_dto_to_entity(vehicle: Vehicle, update_dto: VehicleUpdateDTO) -> Vehicle:
        """Applies an update DTO to a vehicle entity."""
        return Vehicle(
            id=vehicle.id,
            model_id=vehicle.model_id,
            trim_id=update_dto.trim_id if update_dto.trim_id is not None else vehicle.trim_id,
            dealership_id=update_dto.dealership_id if update_dto.dealership_id is not None else vehicle.dealership_id,
            vin=update_dto.vin if update_dto.vin is not None else vehicle.vin,
            production_year=(
                update_dto.production_year if update_dto.production_year is not None else vehicle.production_year
            ),
            exterior_color=(
                update_dto.exterior_color if update_dto.exterior_color is not None else vehicle.exterior_color
            ),
            interior_color=(
                update_dto.interior_color if update_dto.interior_color is not None else vehicle.interior_color
            ),
            price=update_dto.price if update_dto.price is not None else vehicle.price,
            status=vehicle.status,
            created_at=vehicle.created_at,
            updated_at=datetime.utcnow(),
        )
