"""
Video model for database.
"""

from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Enum, Uuid
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum
from app.core.database import Base
from datetime import timezone
import uuid


class VideoStatus(str, PyEnum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"


class Video(Base):
    __tablename__ = "videos"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    status = Column(Enum(VideoStatus), default=VideoStatus.UPLOADED, nullable=False)
    original_filename = Column(String(255), nullable=False)
    original_path = Column(String(500), nullable=False)
    processed_path = Column(String(500), nullable=True)
    task_id = Column(String(255), nullable=True, index=True)
    uploaded_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    processed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )

    # Relationships
    owner = relationship("User", back_populates="videos")
    votes = relationship("Vote", back_populates="video", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Video(id={self.id}, title={self.title}, status={self.status})>"
