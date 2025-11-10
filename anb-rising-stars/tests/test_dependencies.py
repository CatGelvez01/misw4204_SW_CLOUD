from fastapi import status
from unittest.mock import MagicMock


class TestGetCurrentUser:
    def test_get_current_user_valid_token(self, client, test_token, test_user, mock_db):
        # Setup
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = test_user
        mock_db.query.return_value = mock_query
        # Action
        response = client.get(
            "/api/videos", headers={"Authorization": f"Bearer {test_token}"}
        )
        # Expected
        assert response.status_code == status.HTTP_200_OK

    def test_get_current_user_invalid_token(self, client):
        # Action
        response = client.get(
            "/api/videos", headers={"Authorization": "Bearer invalid.token.here"}
        )
        # Expected
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_current_user_missing_token(self, client):
        # Action
        response = client.get("/api/videos")
        # Expected
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_current_user_expired_token(self, client, mock_db):
        # Setup
        from datetime import timedelta
        from app.core.security import create_access_token

        expired_token = create_access_token({"sub": "1"}, timedelta(seconds=-1))
        # Action
        response = client.get(
            "/api/videos", headers={"Authorization": f"Bearer {expired_token}"}
        )
        # Expected
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_current_user_user_not_found(self, client, test_token, mock_db):
        # Setup
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = None
        mock_db.query.return_value = mock_query
        # Action
        response = client.get(
            "/api/videos", headers={"Authorization": f"Bearer {test_token}"}
        )
        # Expected
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
