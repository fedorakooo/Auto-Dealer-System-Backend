from datetime import datetime
from uuid import uuid4

from src.application.dtos.vehicle_dto import VehicleCreateDTO, VehicleDTO, VehicleUpdateDTO
from src.domain.entities.vehicle import Vehicle


class VehicleMapper:
    """Mapper for converting between Vehicle DTOs and Entities."""

    @staticmethod
    def from_entity_to_dto(vehicle: Vehicle, model_name: str | None = None) -> VehicleDTO:
        # Try to get model_name from vehicle attribute if not provided
        if model_name is None:
            model_name = getattr(vehicle, "model_name", None)
        return VehicleDTO(
            id=vehicle.id,
            model_id=vehicle.model_id,
            dealership_id=vehicle.dealership_id,
            vin=vehicle.vin,
            production_year=vehicle.production_year,
            exterior_color=vehicle.exterior_color,
            interior_color=vehicle.interior_color,
            price=vehicle.price,
            is_active=vehicle.is_active,
            created_at=vehicle.created_at,
            updated_at=vehicle.updated_at,
            model_name=model_name,
        )

    @staticmethod
    def from_create_dto_to_entity(create_dto: VehicleCreateDTO) -> Vehicle:
        now = datetime.utcnow()
        return Vehicle(
            id=uuid4(),
            model_id=create_dto.model_id,
            dealership_id=create_dto.dealership_id,
            vin=create_dto.vin,
            production_year=create_dto.production_year,
            exterior_color=create_dto.exterior_color,
            interior_color=create_dto.interior_color,
            price=create_dto.price,
            is_active=create_dto.is_active,
            created_at=now,
            updated_at=None,
        )

    @staticmethod
    def from_update_dto_to_entity(
        vehicle: Vehicle,
        update_dto: VehicleUpdateDTO,
    ) -> Vehicle:
        return Vehicle(
            id=vehicle.id,
            model_id=update_dto.model_id if update_dto.model_id is not None else vehicle.model_id,
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
            is_active=update_dto.is_active if update_dto.is_active is not None else vehicle.is_active,
            created_at=vehicle.created_at,
            updated_at=datetime.utcnow(),
        )
