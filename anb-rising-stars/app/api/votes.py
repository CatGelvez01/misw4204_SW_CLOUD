"""
Voting and ranking endpoints.
"""

import os
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.core.database import get_db
from app.models import User, Video, Vote, VideoStatus
from app.schemas import (
    VoteResponse,
    RankingEntry,
    VoteDuplicateResponse,
    VoteNotFoundResponse,
    RankingBadRequestResponse,
    VideoResponse,
    UnauthorizedResponse,
)
from app.api.dependencies import get_current_user

router = APIRouter()


@router.get(
    "/videos",
    response_model=list[VideoResponse],
    responses={
        200: {"description": "Lista de videos obtenida"},
    },
)
async def list_public_videos(
    db: Session = Depends(get_db),
):
    """
    List all videos available for voting.

    Args:
        db: Database session

    Returns:
        list: List of public videos
    """
    videos = db.query(Video).filter(Video.status == VideoStatus.PROCESSED).all()

    # Build response with proper field names
    result = []
    for video in videos:
        # Convert filesystem path to HTTP URL
        processed_url = None
        if video.status == VideoStatus.PROCESSED and video.processed_path:
            filename = os.path.basename(video.processed_path)
            processed_url = f"http://localhost:8080/processed/{filename}"

        video_dict = {
            "video_id": str(video.id),
            "title": video.title,
            "status": video.status,
            "uploaded_at": video.uploaded_at,
            "processed_at": video.processed_at,
            "processed_url": processed_url,
            "votes": len(video.votes),
        }
        result.append(video_dict)

    return result


@router.post(
    "/videos/{video_id}/vote",
    response_model=VoteResponse,
    responses={
        200: {
            "model": VoteResponse,
            "description": "Voto exitoso.",
        },
        400: {
            "model": VoteDuplicateResponse,
            "description": "Ya has votado por este video.",
        },
        404: {
            "model": VoteNotFoundResponse,
            "description": "Video no encontrado.",
        },
        401: {
            "model": UnauthorizedResponse,
            "description": "Falta de autenticación.",
        },
    },
)
async def vote_video(
    video_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Vote for a video.

    Args:
        video_id: Video ID to vote for
        current_user: Current authenticated user
        db: Database session

    Returns:
        VoteResponse: Vote confirmation

    Raises:
        HTTPException: If video not found, already voted, or user not authenticated
    """
    # Check if video exists
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El video no existe.",
        )

    # Check if user already voted for this video
    existing_vote = (
        db.query(Vote)
        .filter(
            Vote.voter_id == current_user.id,
            Vote.video_id == video_id,
        )
        .first()
    )

    if existing_vote:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya has votado por este video.",
        )

    # Create vote
    vote = Vote(
        voter_id=current_user.id,
        video_id=video_id,
    )

    db.add(vote)
    db.commit()

    return VoteResponse(message="Voto registrado exitosamente.")


@router.get(
    "/rankings",
    response_model=list[RankingEntry],
    responses={
        200: {
            "description": "Lista de rankings obtenida.",
        },
        400: {
            "model": RankingBadRequestResponse,
            "description": "Parámetro inválido en la consulta.",
        },
    },
)
async def get_rankings(
    city: str = Query(None, description="Filter by city"),
    limit: int = Query(100, ge=1, le=1000, description="Number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    db: Session = Depends(get_db),
):
    """
    Get ranking of players by votes.

    Args:
        city: Optional city filter
        limit: Number of results to return
        offset: Offset for pagination
        db: Database session

    Returns:
        list: Ranking entries

    Raises:
        HTTPException: If invalid parameters
    """
    # Build query
    query = (
        db.query(
            User.id,
            User.first_name,
            User.last_name,
            User.city,
            func.count(Vote.id).label("vote_count"),
        )
        .outerjoin(Video, User.id == Video.owner_id)
        .outerjoin(Vote, Video.id == Vote.video_id)
        .filter(Video.status == VideoStatus.PROCESSED)
        .group_by(
            User.id,
            User.first_name,
            User.last_name,
            User.city,
        )
        .order_by(desc("vote_count"))
    )

    # Apply city filter if provided
    if city:
        query = query.filter(User.city == city)

    # Apply pagination
    results = query.offset(offset).limit(limit).all()

    # Format response
    ranking = []
    for position, (_, first_name, last_name, user_city, vote_count) in enumerate(
        results, start=offset + 1
    ):
        ranking.append(
            RankingEntry(
                position=position,
                username=f"{first_name} {last_name}",
                city=user_city,
                votes=vote_count or 0,
            )
        )

    return ranking
