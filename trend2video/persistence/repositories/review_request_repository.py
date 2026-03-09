from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from trend2video.domain.entities.review_request import ReviewRequest, ReviewRequestStatus
from trend2video.persistence.models.review_request import ReviewRequestORM


class ReviewRequestRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _to_entity(self, orm: ReviewRequestORM) -> ReviewRequest:
        return ReviewRequest(
            id=orm.id,
            render_job_id=orm.render_job_id,
            channel_type=orm.channel_type,
            status=orm.status,
            reviewer=orm.reviewer,
            review_comment=orm.review_comment,
            created_at=orm.created_at,
            reviewed_at=orm.reviewed_at,
        )

    async def create(self, request: ReviewRequest) -> ReviewRequest:
        orm = ReviewRequestORM(
            render_job_id=request.render_job_id,
            channel_type=request.channel_type,
            status=request.status.value if hasattr(request.status, "value") else str(request.status),
            reviewer=request.reviewer,
            review_comment=request.review_comment,
        )
        self._session.add(orm)
        await self._session.commit()
        await self._session.refresh(orm)
        return self._to_entity(orm)

    async def update_status(
        self,
        request_id: int,
        *,
        status: ReviewRequestStatus | str,
        reviewer: str | None = None,
        review_comment: str | None = None,
    ) -> ReviewRequest | None:
        orm = await self._session.get(ReviewRequestORM, request_id)
        if orm is None:
            return None
        orm.status = status.value if hasattr(status, "value") else str(status)
        orm.reviewer = reviewer
        orm.review_comment = review_comment
        orm.reviewed_at = datetime.now(timezone.utc)
        await self._session.commit()
        await self._session.refresh(orm)
        return self._to_entity(orm)
