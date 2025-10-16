"""
Video processing service.
"""

import os
import logging
import subprocess
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

    def process_video(self, input_path: str, video_id) -> str:
        """
        Process a video: trim, adjust resolution, add intro with ANB logo, remove audio.

        Args:
            input_path: Path to the input video
            video_id: ID of the video being processed (UUID or int)

        Returns:
            str: Path to the processed video

        Raises:
            Exception: If processing fails
        """
        try:
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

            cmd = [
                "ffmpeg",
                "-i",
                input_path,
                "-t",
                str(self.max_duration),  # Trim to max duration
                "-vf",
                "scale=854:480:force_original_aspect_ratio=decrease,pad=854:480:(ow-iw)/2:(oh-ih)/2",  # 16:9 480p (optimized)
                "-an",  # Remove audio
                "-c:v",
                "libx264",
                "-preset",
                "fast",
                "-crf",
                "23",
                "-y",  # Overwrite output file
                temp_video_path,
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

            if result.returncode != 0:
                logger.error(f"FFmpeg error: {result.stderr}")
                raise Exception(f"FFmpeg processing failed: {result.stderr}")

            # Step 3: Concatenate intro + main video
            logger.info(f"Concatenating intro and main video for video {video_id}")
            concat_list_path = os.path.join(
                settings.processed_dir, f"{video_id}_concat.txt"
            )

            # Use absolute paths in concat file
            intro_abs = os.path.abspath(intro_path)
            temp_abs = os.path.abspath(temp_video_path)

            with open(concat_list_path, "w") as f:
                f.write(f"file '{intro_abs}'\n")
                f.write(f"file '{temp_abs}'\n")

            output_path = os.path.join(settings.processed_dir, f"{video_id}.mp4")

            # Use copy codec since both files have same codec from encoding
            concat_cmd = [
                "ffmpeg",
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
                concat_cmd, capture_output=True, text=True, timeout=600
            )

            if result.returncode != 0:
                logger.error(f"FFmpeg concat error: {result.stderr}")
                raise Exception(f"FFmpeg concatenation failed: {result.stderr}")

            # Clean up temporary files (but NOT the intro video - it's static)
            for temp_file in [temp_video_path, concat_list_path]:
                if os.path.exists(temp_file):
                    os.remove(temp_file)

            logger.info(f"Video {video_id} processed successfully: {output_path}")
            return output_path

        except subprocess.TimeoutExpired:
            logger.error(f"Video processing timeout for video {video_id}")
            raise Exception("Video processing timeout")
        except Exception as e:
            logger.error(f"Error processing video {video_id}: {str(e)}")
            raise
