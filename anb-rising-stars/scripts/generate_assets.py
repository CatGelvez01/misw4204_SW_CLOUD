#!/usr/bin/env python3
"""
Generate static ANB assets (logo and intro video).
Run this script once to create the assets that will be reused for all videos.
"""

import subprocess
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# Configuration
ASSETS_DIR = Path(__file__).parent.parent / "assets"
LOGO_PATH = ASSETS_DIR / "anb_logo.png"
INTRO_VIDEO_PATH = ASSETS_DIR / "anb_intro.mp4"

# Video settings
VIDEO_WIDTH = 1280
VIDEO_HEIGHT = 720
INTRO_DURATION = 5


def create_anb_logo(output_path: Path) -> Path:
    """Create ANB logo image."""
    print(f"Creating ANB logo: {output_path}")

    # Create image with ANB colors (dark blue background)
    img = Image.new("RGB", (VIDEO_WIDTH, VIDEO_HEIGHT), color=(15, 35, 80))
    draw = ImageDraw.Draw(img)

    # Try to use a nice font, fallback to default
    try:
        font_size = int(VIDEO_HEIGHT * 0.15)
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

    x = (VIDEO_WIDTH - text_width) // 2
    y = (VIDEO_HEIGHT - text_height) // 2

    # Draw text with white color
    draw.text((x, y), text, fill=(255, 255, 255), font=font)

    # Draw subtitle
    try:
        subtitle_font_size = int(VIDEO_HEIGHT * 0.08)
        subtitle_font = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", subtitle_font_size
        )
    except (FileNotFoundError, OSError):
        subtitle_font = ImageFont.load_default()

    subtitle = "Rising Stars Showcase"
    subtitle_bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
    subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]

    subtitle_x = (VIDEO_WIDTH - subtitle_width) // 2
    subtitle_y = y + text_height + int(VIDEO_HEIGHT * 0.05)

    draw.text(
        (subtitle_x, subtitle_y), subtitle, fill=(200, 200, 200), font=subtitle_font
    )

    # Save logo
    img.save(output_path)
    print(f"ANB logo created: {output_path}")
    return output_path


def create_intro_video(logo_path: Path, output_path: Path) -> Path:
    """Create intro video from logo image."""
    print(f"Creating intro video: {output_path}")

    cmd = [
        "ffmpeg",
        "-loop",
        "1",
        "-i",
        str(logo_path),
        "-c:v",
        "libx264",
        "-t",
        str(INTRO_DURATION),
        "-pix_fmt",
        "yuv420p",
        "-vf",
        f"scale={VIDEO_WIDTH}:{VIDEO_HEIGHT}",
        "-y",
        str(output_path),
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode != 0:
            print(f"FFmpeg error: {result.stderr}")
            raise Exception(f"Failed to create intro video: {result.stderr}")

        print(f"Intro video created: {output_path}")
        return output_path

    except subprocess.TimeoutExpired:
        print("Timeout creating intro video")
        raise Exception("Timeout creating intro video")


def main():
    """Generate all static assets."""
    print("=" * 60)
    print("ANB Rising Stars - Asset Generator")
    print("=" * 60)

    # Create assets directory
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Assets directory: {ASSETS_DIR}\n")

    # Generate logo
    create_anb_logo(LOGO_PATH)
    print()

    # Generate intro video
    create_intro_video(LOGO_PATH, INTRO_VIDEO_PATH)
    print()

    print("=" * 60)
    print("All assets generated successfully!")
    print("=" * 60)
    print("\nAssets created:")
    print(f"  - Logo: {LOGO_PATH}")
    print(f"  - Intro video: {INTRO_VIDEO_PATH}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)
