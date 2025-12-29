"""Pydantic models for favorite API."""

from uuid import UUID

from pydantic import BaseModel

from src.api.v1.models.vehicle_models import VehicleResponse
from src.application.dtos.favorite_dto import FavoriteAddDTO, FavoriteRemoveDTO
from src.application.dtos.vehicle_dto import VehicleDTO


class FavoriteAddRequest(BaseModel):
    """Request body for adding a vehicle to favorites."""

    customer_id: UUID
    vehicle_id: UUID

    def to_dto(self) -> FavoriteAddDTO:
        return FavoriteAddDTO(
            customer_id=self.customer_id,
            vehicle_id=self.vehicle_id,
        )


class FavoriteRemoveRequest(BaseModel):
    """Request body for removing a vehicle from favorites."""

    customer_id: UUID
    vehicle_id: UUID

    def to_dto(self) -> FavoriteRemoveDTO:
        return FavoriteRemoveDTO(
            customer_id=self.customer_id,
            vehicle_id=self.vehicle_id,
        )


class FavoritesResponse(BaseModel):
    """List of favorite vehicles response."""

    vehicles: list[VehicleResponse]

    @classmethod
    def from_dtos(cls, vehicles: list[VehicleDTO]) -> "FavoritesResponse":
        return cls(vehicles=[VehicleResponse.from_dto(v) for v in vehicles])
