from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from trend2video.apps.api.deps import get_render_job_repository, get_review_request_repository
from trend2video.domain.entities.review_request import ReviewRequest, ReviewRequestStatus
from trend2video.persistence.repositories.render_job_repository import RenderJobRepository
from trend2video.persistence.repositories.review_request_repository import ReviewRequestRepository


router = APIRouter(tags=["review-requests"])


class ReviewRequestCreatePayload(BaseModel):
    channel_type: str
    reviewer: str | None = None


class ReviewDecisionPayload(BaseModel):
    reviewer: str | None = None
    review_comment: str | None = None


@router.post("/renders/{render_job_id}/review-request")
async def create_review_request(
    render_job_id: int,
    payload: ReviewRequestCreatePayload,
    render_repo: RenderJobRepository = Depends(get_render_job_repository),
    review_repo: ReviewRequestRepository = Depends(get_review_request_repository),
) -> dict[str, Any]:
    render_job = await render_repo.get_by_id(render_job_id)
    if render_job is None:
        raise HTTPException(status_code=404, detail="render not found")
    request = await review_repo.create(
        ReviewRequest(
            render_job_id=render_job_id,
            channel_type=payload.channel_type,
            reviewer=payload.reviewer,
        )
    )
    return request.model_dump(mode="json")


@router.post("/review-requests/{request_id}/approve")
async def approve_review_request(
    request_id: int,
    payload: ReviewDecisionPayload,
    review_repo: ReviewRequestRepository = Depends(get_review_request_repository),
) -> dict[str, Any]:
    request = await review_repo.update_status(
        request_id,
        status=ReviewRequestStatus.APPROVED,
        reviewer=payload.reviewer,
        review_comment=payload.review_comment,
    )
    if request is None:
        raise HTTPException(status_code=404, detail="review request not found")
    return request.model_dump(mode="json")


@router.post("/review-requests/{request_id}/reject")
async def reject_review_request(
    request_id: int,
    payload: ReviewDecisionPayload,
    review_repo: ReviewRequestRepository = Depends(get_review_request_repository),
) -> dict[str, Any]:
    request = await review_repo.update_status(
        request_id,
        status=ReviewRequestStatus.REJECTED,
        reviewer=payload.reviewer,
        review_comment=payload.review_comment,
    )
    if request is None:
        raise HTTPException(status_code=404, detail="review request not found")
    return request.model_dump(mode="json")
