"""
Pytest configuration and shared fixtures for all tests.
Uses mocking to avoid real database connections.
"""

import os
import pytest
from datetime import timedelta
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
import uuid

# Set testing environment BEFORE importing app
os.environ["TESTING"] = "true"

from app.core.security import hash_password, create_access_token
from app.models import User, Video, Vote, VideoStatus
from app.main import app


@pytest.fixture
def mock_db():
    """Create a mock database session."""
    db = MagicMock()
    db.query = MagicMock(return_value=MagicMock())
    db.add = MagicMock()
    db.commit = MagicMock()
    db.refresh = MagicMock()
    db.close = MagicMock()
    return db


@pytest.fixture
def client(mock_db):
    """Create a test client with mocked database dependency."""
    from app.core.database import get_db

    def override_get_db():
        yield mock_db

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)

    app.dependency_overrides.clear()


@pytest.fixture
def test_user():
    """Create a mock test user."""
    user = MagicMock(spec=User)
    user.id = 1
    user.first_name = "Test"
    user.last_name = "User"
    user.email = "test@example.com"
    user.hashed_password = hash_password("TestPassword123")
    user.city = "Bogotá"
    user.country = "Colombia"
    return user


@pytest.fixture
def test_user_2():
    """Create a mock second test user."""
    user = MagicMock(spec=User)
    user.id = 2
    user.first_name = "Another"
    user.last_name = "User"
    user.email = "another@example.com"
    user.hashed_password = hash_password("AnotherPass123")
    user.city = "Medellín"
    user.country = "Colombia"
    return user


@pytest.fixture
def test_token(test_user):
    """Create a valid JWT token for test user."""
    access_token_expires = timedelta(minutes=60)
    token = create_access_token(
        data={"sub": str(test_user.id), "email": test_user.email},
        expires_delta=access_token_expires,
    )
    return token


@pytest.fixture
def test_token_2(test_user_2):
    """Create a valid JWT token for second test user."""
    access_token_expires = timedelta(minutes=60)
    token = create_access_token(
        data={"sub": str(test_user_2.id), "email": test_user_2.email},
        expires_delta=access_token_expires,
    )
    return token


@pytest.fixture
def test_video(test_user):
    """Create a mock test video in PROCESSED status."""
    video = MagicMock(spec=Video)
    video.id = uuid.uuid4()
    video.owner_id = test_user.id
    video.title = "Test Video"
    video.status = VideoStatus.PROCESSED
    video.original_filename = "test.mp4"
    video.original_path = "/uploads/test.mp4"
    video.processed_path = "/processed/test.mp4"
    video.task_id = "test-task-id"
    return video


@pytest.fixture
def test_video_2(test_user_2):
    """Create a mock second test video in PROCESSED status."""
    video = MagicMock(spec=Video)
    video.id = uuid.uuid4()
    video.owner_id = test_user_2.id
    video.title = "Another Test Video"
    video.status = VideoStatus.PROCESSED
    video.original_filename = "another.mp4"
    video.original_path = "/uploads/another.mp4"
    video.processed_path = "/processed/another.mp4"
    video.task_id = "another-task-id"
    return video


@pytest.fixture
def test_vote(test_user, test_video_2):
    """Create a mock test vote."""
    vote = MagicMock(spec=Vote)
    vote.voter_id = test_user.id
    vote.video_id = test_video_2.id
    return vote
