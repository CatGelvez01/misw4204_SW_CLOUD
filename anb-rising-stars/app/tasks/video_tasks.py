"""
Video processing tasks for Celery.
"""

from celery import shared_task
from app.core.database import SessionLocal
from app.models import Video, VideoStatus
from app.services.video_processor import VideoProcessor
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def process_video_task(self, video_id):
    """
    Process a video: trim, adjust resolution, add watermark, remove audio.

    Args:
        video_id: ID of the video to process (UUID or int)

    Returns:
        dict: Processing result
    """
    db = SessionLocal()
    try:
        # Get video from database
        video = db.query(Video).filter(Video.id == video_id).first()
        if not video:
            logger.error(f"Video {video_id} not found")
            return {"status": "error", "message": "Video not found"}

        # Store task ID
        video.task_id = self.request.id

        # Update status to processing
        video.status = VideoStatus.PROCESSING
        db.commit()

        # Process video
        processor = VideoProcessor()
        processed_path = processor.process_video(video.original_path, video_id)

        # Update video record
        video.processed_path = processed_path
        video.status = VideoStatus.PROCESSED
        video.processed_at = datetime.now(timezone.utc)
        db.commit()

        logger.info(f"Video {video_id} processed successfully")
        return {"status": "success", "video_id": video_id}

    except Exception as exc:
        logger.error(f"Error processing video {video_id}: {str(exc)}")

        # Update video status to failed
        video = db.query(Video).filter(Video.id == video_id).first()
        if video:
            video.status = VideoStatus.FAILED
            db.commit()

        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2**self.request.retries))

    finally:
        db.close()
