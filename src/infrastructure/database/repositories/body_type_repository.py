from src.domain.abstractions.database.connection import IDatabaseConnection
from src.domain.abstractions.database.repositories.body_type_repository import IBodyTypeRepository
from src.domain.entities.body_type import BodyType


class BodyTypeRepository(IBodyTypeRepository):
    """PostgreSQL repository for body types."""

    def __init__(self, db_connection: IDatabaseConnection) -> None:
        self._db = db_connection

    async def get_all(self) -> list[BodyType]:
        """Returns all body types ordered by name."""
        rows = await self._db.fetch("SELECT id, name FROM body_types ORDER BY name")
        return [BodyType(id=row["id"], name=row["name"]) for row in rows]
