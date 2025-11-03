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

    def upload_video(self, file_path: str, video_id: str) -> str:
        """
        Upload video to S3.

        Args:
            file_path: Local path to video file or bytes content
            video_id: Unique video identifier

        Returns:
            str: S3 object key

        Raises:
            Exception: If upload fails
        """
        key = f"{video_id}.mp4"
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
                self.s3_client.upload_file(file_path, self.bucket, key)
            logger.info(f"Uploaded video to S3: {key}")
            return key
        except ClientError as e:
            logger.error(f"Error uploading video to S3: {str(e)}")
            raise

    def download_video(self, video_id: str) -> bytes:
        """
        Download video from S3.

        Args:
            video_id: Unique video identifier

        Returns:
            bytes: Video file content

        Raises:
            Exception: If download fails
        """
        key = f"{video_id}.mp4"
        try:
            response = self.s3_client.get_object(Bucket=self.bucket, Key=key)
            return response["Body"].read()
        except ClientError as e:
            logger.error(f"Error downloading from S3: {str(e)}")
            raise

    def get_presigned_url(self, video_id: str) -> str:
        """
        Generate presigned URL for video access.

        Args:
            video_id: Unique video identifier

        Returns:
            str: Presigned URL valid for 1 hour

        Raises:
            Exception: If URL generation fails
        """
        key = f"{video_id}.mp4"
        try:
            url = self.s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket, "Key": key},
                ExpiresIn=3600,  # 1 hour
            )
            return url
        except ClientError as e:
            logger.error(f"Error generating presigned URL: {str(e)}")
            raise

    def delete_video(self, video_id: str) -> None:
        """
        Delete video from S3.

        Args:
            video_id: Unique video identifier

        Raises:
            Exception: If deletion fails
        """
        key = f"{video_id}.mp4"
        try:
            self.s3_client.delete_object(Bucket=self.bucket, Key=key)
            logger.info(f"Deleted video from S3: {key}")
        except ClientError as e:
            logger.error(f"Error deleting from S3: {str(e)}")
            raise
