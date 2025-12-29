"""Pydantic models for city API."""

from pydantic import BaseModel

from src.application.dtos.city_dto import CityCreateDTO, CityDTO, CityUpdateDTO


class CityCreateRequest(BaseModel):
    name: str
    country: str

    def to_dto(self) -> CityCreateDTO:
        return CityCreateDTO(name=self.name, country=self.country)


class CityUpdateRequest(BaseModel):
    name: str | None = None
    country: str | None = None

    def to_dto(self) -> CityUpdateDTO:
        return CityUpdateDTO(name=self.name, country=self.country)


class CityResponse(BaseModel):
    id: int
    name: str
    country: str

    @classmethod
    def from_dto(cls, city: CityDTO) -> "CityResponse":
        return cls(id=city.id, name=city.name, country=city.country)


class CitiesResponse(BaseModel):
    cities: list[CityResponse]
