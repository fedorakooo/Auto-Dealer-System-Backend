from dataclasses import dataclass


@dataclass
class CityCreateDTO:
    name: str
    country: str


@dataclass
class CityUpdateDTO:
    name: str | None = None
    country: str | None = None


@dataclass
class CityDTO:
    id: int
    name: str
    country: str
