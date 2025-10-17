from fastapi import status
from unittest.mock import MagicMock


class TestVideoList:
    def test_list_videos_success(self, client, mock_db, test_token, test_video):
        # Setup
        mock_query = MagicMock()
        mock_query.filter.return_value.order_by.return_value.all.return_value = [
            test_video
        ]
        mock_db.query.return_value = mock_query

        # Action
        response = client.get(
            "/api/videos",
            headers={"Authorization": f"Bearer {test_token}"},
        )

        # Expected
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.json(), list)

    def test_list_videos_unauthorized(self, client):
        # Action
        response = client.get("/api/videos")

        # Expected
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_list_videos_empty(self, client, mock_db, test_token):
        # Setup
        mock_query = MagicMock()
        mock_query.filter.return_value.order_by.return_value.all.return_value = []
        mock_db.query.return_value = mock_query

        # Action
        response = client.get(
            "/api/videos",
            headers={"Authorization": f"Bearer {test_token}"},
        )

        # Expected
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []


class TestVideoDetail:
    def test_get_video_detail_unauthorized(self, client, test_video):
        # Action
        response = client.get(f"/api/videos/{test_video.id}")

        # Expected
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_video_detail_not_found(self, client, mock_db, test_token):
        # Setup
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = None
        mock_db.query.return_value = mock_query

        # Action
        fake_id = 9999
        response = client.get(
            f"/api/videos/{fake_id}",
            headers={"Authorization": f"Bearer {test_token}"},
        )

        # Expected
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_video_detail_forbidden(
        self, client, mock_db, test_token_2, test_video
    ):
        # Setup
        mock_video = MagicMock()
        mock_video.id = test_video.id
        mock_video.owner_id = 999
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = mock_video
        mock_db.query.return_value = mock_query

        # Action
        response = client.get(
            f"/api/videos/{test_video.id}",
            headers={"Authorization": f"Bearer {test_token_2}"},
        )

        # Expected
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestVideoDelete:
    def test_delete_video_unauthorized(self, client, test_video):
        # Action
        response = client.delete(f"/api/videos/{test_video.id}")

        # Expected
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_video_not_found(self, client, mock_db, test_token):
        # Setup
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = None
        mock_db.query.return_value = mock_query

        # Action
        fake_id = 9999
        response = client.delete(
            f"/api/videos/{fake_id}",
            headers={"Authorization": f"Bearer {test_token}"},
        )

        # Expected
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_delete_video_forbidden(self, client, mock_db, test_token_2, test_video):
        # Setup
        mock_video = MagicMock()
        mock_video.id = test_video.id
        mock_video.owner_id = 999
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = mock_video
        mock_db.query.return_value = mock_query

        # Action
        response = client.delete(
            f"/api/videos/{test_video.id}",
            headers={"Authorization": f"Bearer {test_token_2}"},
        )

        # Expected
        assert response.status_code == status.HTTP_403_FORBIDDEN
