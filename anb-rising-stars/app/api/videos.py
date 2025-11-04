"""
Video management endpoints.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import os
import uuid
import re
from app.core.database import get_db
from app.core.config import settings
from app.models import User, Video, VideoStatus
from app.services.s3_storage import S3Storage

from app.schemas import (
    VideoResponse,
    VideoDetailResponse,
    VideoDeleteResponse,
    VideoUploadResponse,
    VideoUploadErrorResponse,
    VideoForbiddenResponse,
    VideoNotFoundResponse,
    VideoBadRequestResponse,
    UnauthorizedResponse,
)
from app.api.dependencies import get_current_user
from app.tasks.video_tasks import process_video_task

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    "/upload",
    status_code=status.HTTP_201_CREATED,
    response_model=VideoUploadResponse,
    responses={
        400: {
            "model": VideoUploadErrorResponse,
            "description": "Invalid file format or title",
        },
        401: {"model": UnauthorizedResponse, "description": "Credenciales inválidas"},
        413: {"model": VideoUploadErrorResponse, "description": "File too large"},
    },
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
        video_file: MP4 video file (max 100MB)
        title: Descriptive video title (1-255 characters)
        current_user: Current authenticated user
        db: Database session

    Returns:
        VideoUploadResponse: Success message and task ID

    Raises:
        HTTPException: If file format is invalid, title contains invalid characters, or file is too large
    """
    # Validate title (no special characters except spaces, hyphens, underscores)
    if not re.match(r"^[a-zA-Z0-9\s\-_áéíóúñ]+$", title):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El título contiene caracteres no permitidos. Solo se permiten letras, números, espacios, guiones y guiones bajos.",
        )

    # Validate file type
    if not video_file.filename.lower().endswith(".mp4"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se permiten archivos MP4.",
        )

    # Validate file size
    content = await video_file.read()
    file_size = len(content)

    if file_size > settings.max_file_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"El archivo excede el tamaño máximo de {settings.max_file_size / (1024 * 1024):.0f}MB.",
        )

    # Generate unique file ID
    file_id = str(uuid.uuid4())

    # Upload to S3 or local storage
    if settings.use_s3:
        try:
            s3_storage = S3Storage()
            s3_key = s3_storage.upload_video(
                content, file_id, prefix=settings.s3_original_prefix
            )
            file_path = s3_key
        except Exception as e:
            logger.error(f"S3 upload error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al guardar el video en S3.",
            )
    else:
        # Local storage fallback
        os.makedirs(settings.upload_dir, exist_ok=True)
        file_path = os.path.join(settings.upload_dir, f"{file_id}.mp4")
        with open(file_path, "wb") as f:
            f.write(content)
        os.chmod(file_path, 0o666)

    # Create video record
    video = Video(
        owner_id=current_user.id,
        title=title,
        status=VideoStatus.UPLOADED,
        original_filename=video_file.filename,
        original_path=file_path,
        task_id=file_id,
    )

    try:
        db.add(video)
        db.commit()
        db.refresh(video)
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error during video upload: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al guardar el video. Por favor intenta de nuevo.",
        )

    # Enqueue processing task to Celery
    task = process_video_task.delay(video.id)

    return {
        "message": "Video subido correctamente. Procesamiento en curso.",
        "task_id": task.id,
    }


@router.get(
    "",
    response_model=list[VideoResponse],
    responses={
        200: {"description": "Lista de videos obtenida"},
        401: {"model": UnauthorizedResponse, "description": "Falta de autenticación"},
    },
)
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
            processed_url = f"{settings.server_url}/processed/{filename}"

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


@router.get(
    "/{video_id}",
    response_model=VideoDetailResponse,
    responses={
        200: {"description": "Consulta exitosa. Se devuelve el detalle del video"},
        401: {
            "model": UnauthorizedResponse,
            "description": "El usuario no está autenticado o el token JWT es inválido o expirado",
        },
        403: {
            "model": VideoForbiddenResponse,
            "description": "El usuario autenticado no tiene permisos para acceder a este video",
        },
        404: {
            "model": VideoNotFoundResponse,
            "description": "El video no existe o no pertenece al usuario",
        },
    },
)
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

    # Convert paths to URLs
    original_url = None
    if video.original_path:
        if settings.use_s3:
            # Generate public URL for S3
            try:
                s3_storage = S3Storage()
                original_url = f"https://{s3_storage.bucket}.s3.amazonaws.com/{video.original_path}"
            except Exception as e:
                logger.error(f"Error generating S3 URL: {str(e)}")
                original_url = None
        else:
            # Local storage URL
            filename = os.path.basename(video.original_path)
            original_url = f"{settings.server_url}/uploads/{filename}"

    processed_url = None
    if video.status == VideoStatus.PROCESSED and video.processed_path:
        if settings.use_s3:
            # Generate public URL for S3
            try:
                s3_storage = S3Storage()
                processed_url = f"https://{s3_storage.bucket}.s3.amazonaws.com/{video.processed_path}"
            except Exception as e:
                logger.error(f"Error generating S3 URL: {str(e)}")
                processed_url = None
        else:
            # Local storage URL
            filename = os.path.basename(video.processed_path)
            processed_url = f"{settings.server_url}/processed/{filename}"

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


@router.delete(
    "/{video_id}",
    response_model=VideoDeleteResponse,
    responses={
        200: {"description": "El video ha sido eliminado correctamente"},
        400: {
            "model": VideoBadRequestResponse,
            "description": "El video no puede ser eliminado porque no cumple las condiciones",
        },
        401: {
            "model": UnauthorizedResponse,
            "description": "El usuario no está autenticado o el token JWT es inválido o expirado",
        },
        403: {
            "model": VideoForbiddenResponse,
            "description": "El usuario autenticado no tiene permisos para eliminar este video",
        },
        404: {
            "model": VideoNotFoundResponse,
            "description": "El video no existe o no pertenece al usuario autenticado",
        },
    },
)
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

    # Check if video is published for voting (has votes)
    if video.votes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes eliminar un video que ya está habilitado para votación.",
        )

    # Delete files
    if settings.use_s3:
        try:
            s3_storage = S3Storage()
            # Delete original video
            if video.original_path:
                s3_storage.delete_video(
                    str(video.id), prefix=settings.s3_original_prefix
                )
            # Delete processed video if exists
            if video.processed_path:
                s3_storage.delete_video(
                    str(video.id), prefix=settings.s3_processed_prefix
                )
        except Exception as e:
            logger.error(f"Error deleting videos from S3: {str(e)}")
            # Continue with database deletion even if S3 deletion fails
    else:
        # Local storage deletion
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
