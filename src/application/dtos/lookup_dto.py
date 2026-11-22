from dataclasses import dataclass


@dataclass
class BodyTypeDTO:
    """Body type option."""

    id: int
    name: str


@dataclass
class EngineLookupDTO:
    """Engine option for catalog filters and forms."""

    id: int
    name: str
    fuel_type: str
    horsepower: int | None


@dataclass
class TransmissionLookupDTO:
    """Transmission option for catalog filters and forms."""

    id: int
    name: str
    type: str
    number_of_gears: int


@dataclass
class LookupsDTO:
    """All catalog lookups and enum codes."""

    body_types: list[BodyTypeDTO]
    engines: list[EngineLookupDTO]
    transmissions: list[TransmissionLookupDTO]
    fuel_types: list[str]
    transmission_types: list[str]
    drive_types: list[str]
