"""
Video processing service.
"""

import os
import logging
import subprocess
from app.core.config import settings
from app.services.watermark_generator import create_intro_outro_clip

logger = logging.getLogger(__name__)


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
        Process a video: trim, adjust resolution, add intro/outro with ANB logo, remove audio.

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

            # Step 1: Create intro/outro clips with ANB logo
            logger.info(f"Creating intro/outro clips for video {video_id}")
            intro_path = os.path.join(settings.processed_dir, f"{video_id}_intro.mp4")
            outro_path = os.path.join(settings.processed_dir, f"{video_id}_outro.mp4")

            create_intro_outro_clip(
                duration=self.intro_outro_duration,
                width=1280,
                height=720,
                output_path=intro_path,
            )
            create_intro_outro_clip(
                duration=self.intro_outro_duration,
                width=1280,
                height=720,
                output_path=outro_path,
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
                "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2",  # 16:9 720p
                "-an",  # Remove audio
                "-c:v",
                "libx264",
                "-preset",
                "medium",
                "-crf",
                "23",
                "-y",  # Overwrite output file
                temp_video_path,
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

            if result.returncode != 0:
                logger.error(f"FFmpeg error: {result.stderr}")
                raise Exception(f"FFmpeg processing failed: {result.stderr}")

            # Step 3: Concatenate intro + main video + outro
            logger.info(
                f"Concatenating intro, main video, and outro for video {video_id}"
            )
            concat_list_path = os.path.join(
                settings.processed_dir, f"{video_id}_concat.txt"
            )

            # Use absolute paths in concat file
            intro_abs = os.path.abspath(intro_path)
            temp_abs = os.path.abspath(temp_video_path)
            outro_abs = os.path.abspath(outro_path)

            with open(concat_list_path, "w") as f:
                f.write(f"file '{intro_abs}'\n")
                f.write(f"file '{temp_abs}'\n")
                f.write(f"file '{outro_abs}'\n")

            output_path = os.path.join(settings.processed_dir, f"{video_id}.mp4")

            # Use re-encoding instead of copy to handle different codecs
            concat_cmd = [
                "ffmpeg",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                concat_list_path,
                "-c:v",
                "libx264",
                "-preset",
                "fast",
                "-crf",
                "23",
                "-c:a",
                "aac",
                "-y",
                output_path,
            ]

            result = subprocess.run(
                concat_cmd, capture_output=True, text=True, timeout=600
            )

            if result.returncode != 0:
                logger.error(f"FFmpeg concat error: {result.stderr}")
                raise Exception(f"FFmpeg concatenation failed: {result.stderr}")

            # Clean up temporary files
            for temp_file in [
                intro_path,
                outro_path,
                temp_video_path,
                concat_list_path,
            ]:
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
