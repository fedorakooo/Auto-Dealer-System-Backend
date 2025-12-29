from datetime import datetime
from uuid import uuid4

from src.application.dtos.model_dto import ModelCreateDTO, ModelDTO, ModelUpdateDTO
from src.domain.entities.model import Model


class ModelMapper:
    """Mapper for converting between Model DTOs and Entities."""

    @staticmethod
    def from_entity_to_dto(model: Model) -> ModelDTO:
        return ModelDTO(
            id=model.id,
            body_type_id=model.body_type_id,
            engine_id=model.engine_id,
            transmission_id=model.transmission_id,
            name=model.name,
            model_code=model.model_code,
            is_in_production=model.is_in_production,
            production_year_start=model.production_year_start,
            production_year_end=model.production_year_end,
            description=model.description,
            drive_type=model.drive_type,
            max_speed_kmh=model.max_speed_kmh,
            acceleration_0_100_sec=model.acceleration_0_100_sec,
            fuel_tank_capacity_l=model.fuel_tank_capacity_l,
            number_of_seats=model.number_of_seats,
            number_of_doors=model.number_of_doors,
            length_mm=model.length_mm,
            width_mm=model.width_mm,
            height_mm=model.height_mm,
            curb_weight_kg=model.curb_weight_kg,
            gross_weight_kg=model.gross_weight_kg,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def from_create_dto_to_entity(create_dto: ModelCreateDTO) -> Model:
        now = datetime.utcnow()
        return Model(
            id=uuid4(),
            body_type_id=create_dto.body_type_id,
            engine_id=create_dto.engine_id,
            transmission_id=create_dto.transmission_id,
            name=create_dto.name,
            model_code=create_dto.model_code,
            is_in_production=create_dto.is_in_production,
            production_year_start=create_dto.production_year_start,
            production_year_end=create_dto.production_year_end,
            description=create_dto.description,
            drive_type=create_dto.drive_type,
            max_speed_kmh=create_dto.max_speed_kmh,
            acceleration_0_100_sec=create_dto.acceleration_0_100_sec,
            fuel_tank_capacity_l=create_dto.fuel_tank_capacity_l,
            number_of_seats=create_dto.number_of_seats,
            number_of_doors=create_dto.number_of_doors,
            length_mm=create_dto.length_mm,
            width_mm=create_dto.width_mm,
            height_mm=create_dto.height_mm,
            curb_weight_kg=create_dto.curb_weight_kg,
            gross_weight_kg=create_dto.gross_weight_kg,
            created_at=now,
            updated_at=None,
        )

    @staticmethod
    def from_update_dto_to_entity(
        model: Model,
        update_dto: ModelUpdateDTO,
    ) -> Model:
        return Model(
            id=model.id,
            body_type_id=update_dto.body_type_id if update_dto.body_type_id is not None else model.body_type_id,
            engine_id=update_dto.engine_id if update_dto.engine_id is not None else model.engine_id,
            transmission_id=(
                update_dto.transmission_id if update_dto.transmission_id is not None else model.transmission_id
            ),
            name=update_dto.name if update_dto.name is not None else model.name,
            model_code=update_dto.model_code if update_dto.model_code is not None else model.model_code,
            is_in_production=(
                update_dto.is_in_production if update_dto.is_in_production is not None else model.is_in_production
            ),
            production_year_start=(
                update_dto.production_year_start
                if update_dto.production_year_start is not None
                else model.production_year_start
            ),
            production_year_end=(
                update_dto.production_year_end
                if update_dto.production_year_end is not None
                else model.production_year_end
            ),
            description=update_dto.description if update_dto.description is not None else model.description,
            drive_type=update_dto.drive_type if update_dto.drive_type is not None else model.drive_type,
            max_speed_kmh=update_dto.max_speed_kmh if update_dto.max_speed_kmh is not None else model.max_speed_kmh,
            acceleration_0_100_sec=(
                update_dto.acceleration_0_100_sec
                if update_dto.acceleration_0_100_sec is not None
                else model.acceleration_0_100_sec
            ),
            fuel_tank_capacity_l=(
                update_dto.fuel_tank_capacity_l
                if update_dto.fuel_tank_capacity_l is not None
                else model.fuel_tank_capacity_l
            ),
            number_of_seats=(
                update_dto.number_of_seats if update_dto.number_of_seats is not None else model.number_of_seats
            ),
            number_of_doors=(
                update_dto.number_of_doors if update_dto.number_of_doors is not None else model.number_of_doors
            ),
            length_mm=update_dto.length_mm if update_dto.length_mm is not None else model.length_mm,
            width_mm=update_dto.width_mm if update_dto.width_mm is not None else model.width_mm,
            height_mm=update_dto.height_mm if update_dto.height_mm is not None else model.height_mm,
            curb_weight_kg=update_dto.curb_weight_kg if update_dto.curb_weight_kg is not None else model.curb_weight_kg,
            gross_weight_kg=(
                update_dto.gross_weight_kg if update_dto.gross_weight_kg is not None else model.gross_weight_kg
            ),
            created_at=model.created_at,
            updated_at=datetime.utcnow(),
        )
