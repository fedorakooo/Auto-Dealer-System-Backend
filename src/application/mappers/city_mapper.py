from src.application.dtos.city_dto import CityCreateDTO, CityDTO, CityUpdateDTO
from src.domain.entities.city import City


class CityMapper:
    """Mapper for converting between City DTOs and Entities."""

    @staticmethod
    def from_entity_to_dto(city: City) -> CityDTO:
        return CityDTO(
            id=city.id,
            name=city.name,
            country=city.country,
        )

    @staticmethod
    def from_create_dto_to_entity(create_dto: CityCreateDTO, city_id: int) -> City:
        return City(
            id=city_id,
            name=create_dto.name,
            country=create_dto.country,
        )

    @staticmethod
    def from_update_dto_to_entity(
        city: City,
        update_dto: CityUpdateDTO,
    ) -> City:
        return City(
            id=city.id,
            name=update_dto.name if update_dto.name is not None else city.name,
            country=update_dto.country if update_dto.country is not None else city.country,
        )
