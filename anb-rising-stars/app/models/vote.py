"""
Vote model for database.
"""

from sqlalchemy import Column, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.database import Base


class Vote(Base):
    __tablename__ = "votes"

    id = Column(Integer, primary_key=True, index=True)
    voter_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    video_id = Column(Integer, ForeignKey("videos.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)

    # Unique constraint to ensure one vote per user per video
    __table_args__ = (UniqueConstraint("voter_id", "video_id", name="uq_voter_video"),)

    # Relationships
    voter = relationship("User", back_populates="votes")
    video = relationship("Video", back_populates="votes")

    def __repr__(self) -> str:
        return (
            f"<Vote(id={self.id}, voter_id={self.voter_id}, video_id={self.video_id})>"
        )
