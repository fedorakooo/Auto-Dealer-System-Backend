from abc import ABC, abstractmethod

from src.domain.entities.body_type import BodyType


class IBodyTypeRepository(ABC):
    """Interface for body type repository operations."""

    @abstractmethod
    async def get_all(self) -> list[BodyType]:
        """Returns all body types ordered by name."""
