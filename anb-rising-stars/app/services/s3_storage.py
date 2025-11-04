"""
S3 storage service for video uploads and downloads.
"""

import logging
import boto3
from botocore.exceptions import ClientError
from app.core.config import settings

logger = logging.getLogger(__name__)


class S3Storage:
    """Service for managing files in AWS S3."""

    def __init__(self):
        """Initialize S3 client."""
        # Use explicit credentials if provided, otherwise use IAM role
        if settings.aws_access_key_id and settings.aws_secret_access_key:
            self.s3_client = boto3.client(
                "s3",
                region_name=settings.aws_region,
                aws_access_key_id=settings.aws_access_key_id,
                aws_secret_access_key=settings.aws_secret_access_key,
            )
        else:
            self.s3_client = boto3.client("s3", region_name=settings.aws_region)
        self.bucket = settings.s3_bucket

    def upload_video(self, file_path: str, video_id: str, prefix: str = None) -> str:
        """
        Upload video to S3.

        Args:
            file_path: Local path to video file or bytes content
            video_id: Unique video identifier
            prefix: Optional S3 prefix (folder). Defaults to s3_original_prefix

        Returns:
            str: S3 object key

        Raises:
            Exception: If upload fails
        """
        if prefix is None:
            prefix = settings.s3_original_prefix

        key = f"{prefix}/{video_id}.mp4"
        try:
            if isinstance(file_path, bytes):
                # Upload from bytes
                self.s3_client.put_object(
                    Bucket=self.bucket,
                    Key=key,
                    Body=file_path,
                    ContentType="video/mp4",
                )
            else:
                # Upload from file path
                self.s3_client.upload_file(
                    file_path, self.bucket, key, ExtraArgs={"ContentType": "video/mp4"}
                )
            logger.info(f"Uploaded video to S3: {key}")
            return key
        except ClientError as e:
            logger.error(f"Error uploading video to S3: {str(e)}")
            raise

    def download_video(self, video_id: str, prefix: str = None) -> bytes:
        """
        Download video from S3.

        Args:
            video_id: Unique video identifier
            prefix: Optional S3 prefix (folder). Defaults to s3_original_prefix

        Returns:
            bytes: Video file content

        Raises:
            Exception: If download fails
        """
        if prefix is None:
            prefix = settings.s3_original_prefix

        key = f"{prefix}/{video_id}.mp4"
        try:
            response = self.s3_client.get_object(Bucket=self.bucket, Key=key)
            return response["Body"].read()
        except ClientError as e:
            logger.error(f"Error downloading from S3: {str(e)}")
            raise

    def get_presigned_url(self, video_id: str, prefix: str = None) -> str:
        """
        Generate public URL for video access (requires bucket to have public read access).

        Args:
            video_id: Unique video identifier
            prefix: Optional S3 prefix (folder). Defaults to s3_original_prefix

        Returns:
            str: Public S3 URL

        Raises:
            Exception: If URL generation fails
        """
        if prefix is None:
            prefix = settings.s3_original_prefix

        key = f"{prefix}/{video_id}.mp4"
        try:
            url = f"https://{self.bucket}.s3.amazonaws.com/{key}"
            logger.info(f"Generated public URL: {url}")
            return url
        except Exception as e:
            logger.error(f"Error generating public URL: {str(e)}")
            raise

    def delete_video(self, video_id: str, prefix: str = None) -> None:
        """
        Delete video from S3.

        Args:
            video_id: Unique video identifier
            prefix: Optional S3 prefix (folder). Defaults to s3_original_prefix

        Raises:
            Exception: If deletion fails
        """
        if prefix is None:
            prefix = settings.s3_original_prefix

        key = f"{prefix}/{video_id}.mp4"
        try:
            self.s3_client.delete_object(Bucket=self.bucket, Key=key)
            logger.info(f"Deleted video from S3: {key}")
        except ClientError as e:
            logger.error(f"Error deleting from S3: {str(e)}")
            raise
