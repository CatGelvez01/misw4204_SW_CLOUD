"""
Video processing service.
"""

import os
import logging
import subprocess
import tempfile
from pathlib import Path
from app.core.config import settings

logger = logging.getLogger(__name__)

# Path to pre-generated intro video
INTRO_VIDEO_PATH = Path(__file__).parent.parent.parent / "assets" / "anb_intro.mp4"


class VideoProcessor:
    """Service for processing videos."""

    def __init__(self):
        """Initialize video processor."""
        self.max_duration = settings.video_processed_max_duration
        self.output_resolution = settings.video_output_resolution
        self.aspect_ratio = settings.video_aspect_ratio
        self.intro_outro_duration = settings.video_intro_outro_duration
        self.temp_files = []  # Track temp files for cleanup

    def process_video(self, input_path: str, video_id) -> str:
        """
        Process a video: trim, adjust resolution, add intro with ANB logo, remove audio.

        Args:
            input_path: Path to the input video (local or S3)
            video_id: ID of the video being processed (UUID or int)

        Returns:
            str: Path to the processed video (local path)

        Raises:
            Exception: If processing fails
        """
        try:
            # Download from S3 if needed
            if settings.use_s3:
                from app.services.s3_storage import S3Storage

                s3_storage = S3Storage()
                video_content = s3_storage.download_video(
                    str(video_id), prefix=settings.s3_original_prefix
                )
                # Save to temp file
                with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
                    tmp.write(video_content)
                    input_path = tmp.name
                    self.temp_files.append(input_path)
                logger.info(f"Downloaded video from S3 to {input_path}")

            # Create output directory if it doesn't exist
            os.makedirs(settings.processed_dir, exist_ok=True)

            # Step 1: Use pre-generated intro clip
            logger.info(f"Using pre-generated intro clip for video {video_id}")
            intro_path = str(INTRO_VIDEO_PATH)

            if not os.path.exists(intro_path):
                raise Exception(
                    f"Intro video not found at {intro_path}. "
                    "Please run: python scripts/generate_assets.py"
                )

            # Step 2: Process main video (trim, scale, remove audio)
            logger.info(f"Processing main video content for video {video_id}")
            temp_video_path = os.path.join(
                settings.processed_dir, f"{video_id}_temp.mp4"
            )

            scale_filter = (
                f"scale={settings.video_output_width}:{settings.video_output_height}:"
                f"force_original_aspect_ratio=decrease,"
                f"pad={settings.video_output_width}:{settings.video_output_height}:"
                f"(ow-iw)/2:(oh-ih)/2"
            )
            cmd = [
                "/usr/bin/ffmpeg",
                "-i",
                input_path,
                "-t",
                str(self.max_duration),
                "-vf",
                scale_filter,
                "-an",
                "-c:v",
                "libx264",
                "-preset",
                settings.video_ffmpeg_preset,
                "-crf",
                str(settings.video_ffmpeg_crf),
                "-pix_fmt",
                settings.video_ffmpeg_pix_fmt,
                "-y",
                temp_video_path,
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)

            if result.returncode != 0:
                logger.error(f"FFmpeg error: {result.stderr}")
                raise Exception(f"FFmpeg processing failed: {result.stderr}")

            # Step 3: Concatenate intro + main video
            logger.info(f"Concatenating intro and main video for video {video_id}")

            output_path = os.path.join(settings.processed_dir, f"{video_id}.mp4")
            concat_list_path = os.path.join(
                settings.processed_dir, f"{video_id}_concat.txt"
            )

            # Create concat file
            with open(concat_list_path, "w") as f:
                f.write(f"file '{intro_path}'\n")
                f.write(f"file '{temp_video_path}'\n")

            # Concatenate using concat demuxer
            concat_cmd = [
                "/usr/bin/ffmpeg",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                concat_list_path,
                "-c",
                "copy",
                "-y",
                output_path,
            ]

            result = subprocess.run(
                concat_cmd, capture_output=True, text=True, timeout=1800
            )

            if result.returncode != 0:
                logger.error(f"FFmpeg concat error: {result.stderr}")
                raise Exception(f"FFmpeg concatenation failed: {result.stderr}")

            # Clean up concat file
            if os.path.exists(concat_list_path):
                os.remove(concat_list_path)

            # Clean up temporary files (but NOT the intro video - it's static)
            if os.path.exists(temp_video_path):
                os.remove(temp_video_path)

            # Clean up S3 downloaded temp files
            for temp_file in self.temp_files:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                    logger.info(f"Cleaned up temp file: {temp_file}")

            logger.info(f"Video {video_id} processed successfully: {output_path}")
            return output_path

        except subprocess.TimeoutExpired:
            logger.error(f"Video processing timeout for video {video_id}")
            self._cleanup_temp_files()
            raise RuntimeError("Video processing timeout")
        except (OSError, IOError) as e:
            logger.error(f"File system error processing video {video_id}: {str(e)}")
            self._cleanup_temp_files()
            raise
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg process error for video {video_id}: {str(e)}")
            self._cleanup_temp_files()
            raise

    def _cleanup_temp_files(self):
        """Clean up temporary files."""
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                    logger.info(f"Cleaned up temp file: {temp_file}")
            except Exception as e:
                logger.warning(f"Failed to clean up temp file {temp_file}: {str(e)}")
