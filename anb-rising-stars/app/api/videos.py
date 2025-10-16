"""
Video management endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
import os
import uuid
from app.core.database import get_db
from app.core.config import settings
from app.models import User, Video, VideoStatus
from app.schemas import (
    VideoResponse,
    VideoDetailResponse,
    VideoDeleteResponse,
    VideoUploadResponse,
)
from app.api.dependencies import get_current_user
from app.tasks.video_tasks import process_video_task

router = APIRouter()


@router.post(
    "/upload", status_code=status.HTTP_201_CREATED, response_model=VideoUploadResponse
)
async def upload_video(
    video_file: UploadFile = File(...),
    title: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Upload a video for processing.

    Args:
        video_file: Video file to upload
        title: Video title
        current_user: Current authenticated user
        db: Database session

    Returns:
        dict: Success message and task ID

    Raises:
        HTTPException: If file is invalid or too large
    """
    # Validate file type
    if not video_file.filename.lower().endswith(".mp4"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se permiten archivos MP4.",
        )

    # Validate file size
    file_size = 0
    content = await video_file.read()
    file_size = len(content)

    if file_size > settings.max_file_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El archivo excede el tamaño máximo de {settings.max_file_size / (1024 * 1024):.0f}MB.",
        )

    # Create upload directory if it doesn't exist
    os.makedirs(settings.upload_dir, exist_ok=True)

    # Generate unique filename
    file_id = str(uuid.uuid4())
    file_path = os.path.join(settings.upload_dir, f"{file_id}.mp4")

    # Save file
    with open(file_path, "wb") as f:
        f.write(content)

    # Create video record
    video = Video(
        owner_id=current_user.id,
        title=title,
        status=VideoStatus.UPLOADED,
        original_filename=video_file.filename,
        original_path=file_path,
        task_id=file_id,
    )

    db.add(video)
    db.commit()
    db.refresh(video)

    # Enqueue processing task to Celery
    task = process_video_task.delay(video.id)

    return {
        "message": "Video subido correctamente. Procesamiento en curso.",
        "task_id": task.id,
    }


@router.get("", response_model=list[VideoResponse])
async def list_my_videos(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    List all videos uploaded by the current user.

    Args:
        current_user: Current authenticated user
        db: Database session

    Returns:
        list: List of user's videos ordered by upload date (newest first)
    """
    videos = (
        db.query(Video)
        .filter(Video.owner_id == current_user.id)
        .order_by(Video.uploaded_at.desc())
        .all()
    )

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


@router.get("/{video_id}", response_model=VideoDetailResponse)
async def get_video_detail(
    video_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get details of a specific video.

    Args:
        video_id: Video ID
        current_user: Current authenticated user
        db: Database session

    Returns:
        VideoDetailResponse: Video details

    Raises:
        HTTPException: If video not found or user doesn't have permission
    """
    video = db.query(Video).filter(Video.id == video_id).first()

    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El video no existe.",
        )

    if video.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para acceder a este video.",
        )

    # Convert filesystem paths to HTTP URLs
    original_url = None
    if video.original_path:
        filename = os.path.basename(video.original_path)
        original_url = f"http://localhost:8080/uploads/{filename}"

    processed_url = None
    if video.status == VideoStatus.PROCESSED and video.processed_path:
        filename = os.path.basename(video.processed_path)
        processed_url = f"http://localhost:8080/processed/{filename}"

    return {
        "video_id": str(video.id),
        "title": video.title,
        "status": video.status,
        "uploaded_at": video.uploaded_at,
        "processed_at": video.processed_at,
        "original_url": original_url,
        "processed_url": processed_url,
        "votes": len(video.votes),
    }


@router.delete("/{video_id}", response_model=VideoDeleteResponse)
async def delete_video(
    video_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Delete a video uploaded by the current user.

    Args:
        video_id: Video ID
        current_user: Current authenticated user
        db: Database session

    Returns:
        VideoDeleteResponse: Deletion confirmation

    Raises:
        HTTPException: If video not found, user doesn't have permission, or video is published
    """
    video = db.query(Video).filter(Video.id == video_id).first()

    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El video no existe.",
        )

    if video.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para eliminar este video.",
        )

    # TODO: Check if video is published for voting

    # Delete files
    if os.path.exists(video.original_path):
        os.remove(video.original_path)

    if video.processed_path and os.path.exists(video.processed_path):
        os.remove(video.processed_path)

    # Delete from database
    db.delete(video)
    db.commit()

    return {
        "message": "El video ha sido eliminado exitosamente.",
        "video_id": video_id,
    }
