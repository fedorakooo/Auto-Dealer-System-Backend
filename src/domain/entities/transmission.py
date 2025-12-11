from dataclasses import dataclass

from src.domain.value_objects.transmission_type import TransmissionType


@dataclass
class Transmission:
    id: int
    name: str
    type: TransmissionType
    number_of_gears: int
    description: str | None = None
