from abc import ABC, abstractmethod

from src.application.dtos.lookup_dto import LookupsDTO


class ILookupService(ABC):
    """Interface for catalog reference data (body types, engines, enum codes)."""

    @abstractmethod
    async def get_lookups(self) -> LookupsDTO:
        """Returns all catalog lookups in one payload."""
