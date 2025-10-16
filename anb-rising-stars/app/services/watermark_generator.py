"""
Watermark and logo generation for videos.
"""

import os
from PIL import Image, ImageDraw, ImageFont
import logging

logger = logging.getLogger(__name__)


def create_anb_logo(
    width: int = 1280, height: int = 720, output_path: str = None
) -> str:
    """
    Create ANB logo image.

    Args:
        width: Image width
        height: Image height
        output_path: Path to save the logo

    Returns:
        str: Path to the created logo
    """
    if output_path is None:
        output_path = "/tmp/anb_logo.png"

    # Create image with ANB colors (dark blue background)
    img = Image.new("RGB", (width, height), color=(15, 35, 80))  # Dark blue
    draw = ImageDraw.Draw(img)

    # Try to use a nice font, fallback to default
    try:
        font_size = int(height * 0.15)
        font = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size
        )
    except (FileNotFoundError, OSError):
        font = ImageFont.load_default()

    # Draw ANB text
    text = "ANB"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    x = (width - text_width) // 2
    y = (height - text_height) // 2

    # Draw text with white color
    draw.text((x, y), text, fill=(255, 255, 255), font=font)

    # Draw subtitle
    try:
        subtitle_font_size = int(height * 0.08)
        subtitle_font = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", subtitle_font_size
        )
    except (FileNotFoundError, OSError):
        subtitle_font = ImageFont.load_default()

    subtitle = "Rising Stars Showcase"
    subtitle_bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
    subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]

    subtitle_x = (width - subtitle_width) // 2
    subtitle_y = y + text_height + int(height * 0.05)

    draw.text(
        (subtitle_x, subtitle_y), subtitle, fill=(200, 200, 200), font=subtitle_font
    )

    # Save logo
    img.save(output_path)
    logger.info(f"ANB logo created: {output_path}")

    return output_path


def create_intro_outro_clip(
    duration: int = 5, width: int = 1280, height: int = 720, output_path: str = None
) -> str:
    """
    Create intro/outro video clip with ANB logo.

    Args:
        duration: Duration in seconds
        width: Video width
        height: Video height
        output_path: Path to save the video

    Returns:
        str: Path to the created video
    """
    import subprocess
    from app.core.config import settings

    if output_path is None:
        output_path = os.path.join(settings.processed_dir, "anb_intro.mp4")

    # Create logo image
    logo_path = create_anb_logo(width, height)

    # Use ffmpeg to create video from image
    cmd = [
        "ffmpeg",
        "-loop",
        "1",
        "-i",
        logo_path,
        "-c:v",
        "libx264",
        "-t",
        str(duration),
        "-pix_fmt",
        "yuv420p",
        "-vf",
        f"scale={width}:{height}",
        "-y",
        output_path,
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode != 0:
            logger.error(f"FFmpeg error creating intro: {result.stderr}")
            raise Exception(f"Failed to create intro clip: {result.stderr}")

        logger.info(f"Intro/outro clip created: {output_path}")
        return output_path

    except subprocess.TimeoutExpired:
        logger.error("Timeout creating intro clip")
        raise Exception("Timeout creating intro clip")
    finally:
        # Clean up logo image
        if os.path.exists(logo_path):
            os.remove(logo_path)
