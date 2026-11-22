from uuid import UUID

import asyncpg

from src.domain.abstractions.database.connection import IDatabaseConnection
from src.domain.abstractions.database.repositories.dealership_review_repository import IDealershipReviewRepository
from src.domain.entities.dealership_review import (
    DealershipRatingSummary,
    DealershipReview,
    DealershipReviewComment,
)
from src.domain.utils.uuid_helpers import parse_uuid
from src.infrastructure.database.exceptions import DatabaseNotFoundError


class DealershipReviewRepository(IDealershipReviewRepository):
    """PostgreSQL repository for dealership reviews and comments."""

    def __init__(self, db_connection: IDatabaseConnection) -> None:
        self._db = db_connection

    async def get_by_id(self, review_id: UUID) -> DealershipReview | None:
        """Returns one review (without author details and comments) or None."""
        row = await self._db.fetchrow("SELECT * FROM dealership_reviews WHERE id = $1", str(review_id))
        return self._row_to_review(row) if row else None

    async def get_by_dealership_and_customer(self, dealership_id: int, customer_id: UUID) -> DealershipReview | None:
        """Returns the review a customer left for a dealership or None."""
        query = "SELECT * FROM dealership_reviews WHERE dealership_id = $1 AND customer_id = $2"
        row = await self._db.fetchrow(query, dealership_id, str(customer_id))
        return self._row_to_review(row) if row else None

    async def get_page(
        self,
        dealership_id: int,
        include_hidden: bool,
        viewer_customer_id: UUID | None,
        offset: int,
        limit: int,
    ) -> tuple[list[DealershipReview], int]:
        """Returns a page of reviews with author details and comments, and the total count."""
        viewer = str(viewer_customer_id) if viewer_customer_id else None
        rows = await self._db.fetch(
            "SELECT * FROM get_dealership_reviews($1, $2, $3::UUID, $4, $5)",
            dealership_id,
            include_hidden,
            viewer,
            offset,
            limit,
        )
        total = await self._db.fetchval(
            "SELECT count_dealership_reviews($1, $2, $3::UUID)", dealership_id, include_hidden, viewer
        )
        reviews = [self._row_to_review(row) for row in rows]
        if reviews:
            comment_rows = await self._db.fetch(
                "SELECT * FROM get_dealership_review_comments($1::UUID[])", [str(r.id) for r in reviews]
            )
            by_review = {review.id: review for review in reviews}
            for comment_row in comment_rows:
                comment = self._row_to_comment(comment_row)
                by_review[comment.review_id].comments.append(comment)
        return reviews, total or 0

    async def get_rating_summaries(self, dealership_ids: list[int]) -> dict[int, DealershipRatingSummary]:
        """Returns the rating of visible reviews keyed by dealership ID; dealerships without reviews are absent."""
        if not dealership_ids:
            return {}
        rows = await self._db.fetch("SELECT * FROM get_dealership_rating_stats($1::INTEGER[])", dealership_ids)
        return {
            row["dealership_id"]: DealershipRatingSummary(
                dealership_id=row["dealership_id"],
                reviews_count=row["reviews_count"],
                average_rating=row["average_rating"],
                distribution={star: row[f"rating_{star}"] for star in range(1, 6)},
            )
            for row in rows
        }

    async def create(self, review: DealershipReview) -> DealershipReview:
        """Creates a review."""
        query = """
            INSERT INTO dealership_reviews (id, dealership_id, customer_id, rating, title, comment)
            VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING *
        """
        row = await self._db.fetchrow(
            query,
            str(review.id),
            review.dealership_id,
            str(review.customer_id),
            review.rating,
            review.title,
            review.comment,
        )
        return self._row_to_review(row)

    async def update(self, review: DealershipReview) -> DealershipReview:
        """Updates rating, title, comment and visibility of a review."""
        query = """
            UPDATE dealership_reviews
            SET rating = $2, title = $3, comment = $4, is_hidden = $5
            WHERE id = $1
            RETURNING *
        """
        row = await self._db.fetchrow(
            query, str(review.id), review.rating, review.title, review.comment, review.is_hidden
        )
        if not row:
            raise DatabaseNotFoundError(f"DealershipReview with id {review.id} not found")
        return self._row_to_review(row)

    async def delete(self, review_id: UUID) -> bool:
        """Deletes a review with its comments."""
        result = await self._db.execute("DELETE FROM dealership_reviews WHERE id = $1", str(review_id))
        return result == "DELETE 1"

    async def get_comment(self, comment_id: UUID) -> DealershipReviewComment | None:
        """Returns one comment or None."""
        row = await self._db.fetchrow("SELECT * FROM dealership_review_comments WHERE id = $1", str(comment_id))
        return self._row_to_comment(row) if row else None

    async def create_comment(self, comment: DealershipReviewComment) -> DealershipReviewComment:
        """Creates a comment and returns it with the author name."""
        query = """
            WITH inserted AS (
                INSERT INTO dealership_review_comments (id, review_id, author_user_id, body, is_official)
                VALUES ($1, $2, $3, $4, $5)
                RETURNING *
            )
            SELECT i.*, (u.first_name || ' ' || left(u.second_name, 1) || '.') AS author_name
            FROM inserted i
            JOIN users u ON u.id = i.author_user_id
        """
        row = await self._db.fetchrow(
            query,
            str(comment.id),
            str(comment.review_id),
            str(comment.author_user_id),
            comment.body,
            comment.is_official,
        )
        return self._row_to_comment(row)

    async def delete_comment(self, comment_id: UUID) -> bool:
        """Deletes a comment by its ID."""
        result = await self._db.execute("DELETE FROM dealership_review_comments WHERE id = $1", str(comment_id))
        return result == "DELETE 1"

    def _row_to_review(self, row: asyncpg.Record) -> DealershipReview:
        return DealershipReview(
            id=parse_uuid(row["id"]),
            dealership_id=row["dealership_id"],
            customer_id=parse_uuid(row["customer_id"]),
            rating=row["rating"],
            title=row.get("title"),
            comment=row.get("comment"),
            is_hidden=row["is_hidden"],
            author_name=row.get("author_name"),
            is_verified_customer=bool(row.get("is_verified_customer")),
            created_at=row.get("created_at"),
            updated_at=row.get("updated_at"),
        )

    def _row_to_comment(self, row: asyncpg.Record) -> DealershipReviewComment:
        return DealershipReviewComment(
            id=parse_uuid(row["id"]),
            review_id=parse_uuid(row["review_id"]),
            author_user_id=parse_uuid(row["author_user_id"]),
            body=row["body"],
            is_official=row["is_official"],
            author_name=row.get("author_name"),
            created_at=row.get("created_at"),
            updated_at=row.get("updated_at"),
        )
