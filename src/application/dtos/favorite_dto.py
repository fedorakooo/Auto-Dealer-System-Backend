from dataclasses import dataclass
from uuid import UUID


@dataclass
class FavoriteAddDTO:
    customer_id: UUID
    vehicle_id: UUID


@dataclass
class FavoriteRemoveDTO:
    customer_id: UUID
    vehicle_id: UUID
