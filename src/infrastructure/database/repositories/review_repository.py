from datetime import datetime
from uuid import UUID

import asyncpg

from src.domain.abstractions.database.connection import IDatabaseConnection
from src.domain.abstractions.database.repositories.review_repository import IReviewRepository
from src.domain.entities.review import Review
from src.domain.utils.uuid_helpers import parse_uuid
from src.infrastructure.database.exceptions import DatabaseNotFoundError


class ReviewRepository(IReviewRepository):
    def __init__(self, db_connection: IDatabaseConnection):
        self._db = db_connection

    async def get_by_id(self, review_id: UUID) -> Review | None:
        query = "SELECT * FROM reviews WHERE id = $1"
        row = await self._db.fetchrow(query, str(review_id))
        if not row:
            return None
        return self._row_to_review(row)

    async def get_by_model_id(self, model_id: UUID) -> list[Review]:
        query = "SELECT * FROM reviews WHERE model_id = $1 ORDER BY created_at DESC"
        rows = await self._db.fetch(query, str(model_id))
        return [self._row_to_review(row) for row in rows]

    async def get_by_customer_id(self, customer_id: UUID) -> list[Review]:
        query = "SELECT * FROM reviews WHERE customer_id = $1 ORDER BY created_at DESC"
        rows = await self._db.fetch(query, str(customer_id))
        return [self._row_to_review(row) for row in rows]

    async def create(self, review: Review) -> Review:
        query = """
            INSERT INTO reviews (id, customer_id, model_id, rating, title, comment, created_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            RETURNING *
        """
        row = await self._db.fetchrow(
            query,
            str(review.id),
            str(review.customer_id),
            str(review.model_id),
            review.rating,
            review.title,
            review.comment,
            review.created_at or datetime.utcnow(),
        )
        return self._row_to_review(row)

    async def update(self, review: Review) -> Review:
        query = """
            UPDATE reviews
            SET rating = $2, title = $3, comment = $4, updated_at = $5
            WHERE id = $1
            RETURNING *
        """
        row = await self._db.fetchrow(
            query,
            str(review.id),
            review.rating,
            review.title,
            review.comment,
            datetime.utcnow(),
        )
        if not row:
            raise DatabaseNotFoundError(f"Review with id {review.id} not found")
        return self._row_to_review(row)

    async def delete(self, review_id: UUID) -> bool:
        query = "DELETE FROM reviews WHERE id = $1"
        result = await self._db.execute(query, str(review_id))
        return result == "DELETE 1"

    def _row_to_review(self, row: asyncpg.Record) -> Review:
        return Review(
            id=parse_uuid(row["id"]),
            customer_id=parse_uuid(row["customer_id"]),
            model_id=parse_uuid(row["model_id"]),
            rating=row["rating"],
            title=row.get("title"),
            comment=row.get("comment"),
            created_at=row.get("created_at"),
            updated_at=row.get("updated_at"),
        )
