from pydantic import BaseModel

from src.application.dtos.lookup_dto import LookupsDTO


class BodyTypeResponse(BaseModel):
    """Body type option."""

    id: int
    name: str


class EngineLookupResponse(BaseModel):
    """Engine option for catalog filters and forms."""

    id: int
    name: str
    fuel_type: str
    horsepower: int | None


class TransmissionLookupResponse(BaseModel):
    """Transmission option for catalog filters and forms."""

    id: int
    name: str
    type: str
    number_of_gears: int


class LookupsResponse(BaseModel):
    """Catalog reference data; enum lists hold stable codes, labels are a UI concern."""

    body_types: list[BodyTypeResponse]
    engines: list[EngineLookupResponse]
    transmissions: list[TransmissionLookupResponse]
    fuel_types: list[str]
    transmission_types: list[str]
    drive_types: list[str]

    @classmethod
    def from_dto(cls, dto: LookupsDTO) -> "LookupsResponse":
        """Builds the response from a lookups DTO."""
        return cls.model_validate(dto, from_attributes=True)
