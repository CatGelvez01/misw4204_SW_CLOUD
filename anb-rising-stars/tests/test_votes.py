from fastapi import status
from unittest.mock import MagicMock


class TestPublicVideos:
    def test_list_public_videos_success(self, client, mock_db, test_video):
        # Setup
        mock_query = MagicMock()
        mock_query.filter.return_value.all.return_value = [test_video]
        mock_db.query.return_value = mock_query

        # Action
        response = client.get("/api/public/videos")

        # Expected
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.json(), list)

    def test_list_public_videos_empty(self, client, mock_db):
        # Setup
        mock_query = MagicMock()
        mock_query.filter.return_value.all.return_value = []
        mock_db.query.return_value = mock_query

        # Action
        response = client.get("/api/public/videos")

        # Expected
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []


class TestVoting:
    def test_vote_unauthorized(self, client, test_video):
        # Action
        response = client.post(f"/api/public/videos/{test_video.id}/vote")

        # Expected
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_vote_video_not_found(self, client, mock_db, test_token):
        # Setup
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = None
        mock_db.query.return_value = mock_query

        # Action
        import uuid

        fake_id = str(uuid.uuid4())
        response = client.post(
            f"/api/public/videos/{fake_id}/vote",
            headers={"Authorization": f"Bearer {test_token}"},
        )

        # Expected
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_vote_duplicate(self, client, mock_db, test_token, test_video):
        # Setup
        mock_video = MagicMock()
        mock_video.id = test_video.id
        mock_existing_vote = MagicMock()

        mock_query_video = MagicMock()
        mock_query_video.filter.return_value.first.return_value = mock_video

        mock_query_vote = MagicMock()
        mock_query_vote.filter.return_value.first.return_value = mock_existing_vote

        def query_side_effect(model):
            if hasattr(model, "__tablename__") and model.__tablename__ == "votes":
                return mock_query_vote
            return mock_query_video

        mock_db.query.side_effect = query_side_effect

        # Action
        response = client.post(
            f"/api/public/videos/{test_video.id}/vote",
            headers={"Authorization": f"Bearer {test_token}"},
        )

        # Expected
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {"detail": "Ya has votado por este video."}


class TestRanking:
    def test_ranking_success(self, client, mock_db, test_user):
        # Setup
        mock_query = MagicMock()
        mock_query.offset.return_value.limit.return_value.all.return_value = [
            (
                test_user.id,
                test_user.first_name,
                test_user.last_name,
                test_user.city,
                100,
            )
        ]
        mock_db.query.return_value = mock_query

        # Action
        response = client.get("/api/public/rankings")

        # Expected
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.json(), list)

    def test_ranking_empty(self, client, mock_db):
        # Setup
        mock_query = MagicMock()
        mock_query.offset.return_value.limit.return_value.all.return_value = []
        mock_db.query.return_value = mock_query

        # Action
        response = client.get("/api/public/rankings")

        # Expected
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_ranking_with_city_filter(self, client, mock_db, test_user):
        # Setup
        mock_query = MagicMock()
        mock_query.filter.return_value.offset.return_value.limit.return_value.all.return_value = [
            (
                test_user.id,
                test_user.first_name,
                test_user.last_name,
                test_user.city,
                100,
            )
        ]
        mock_db.query.return_value = mock_query

        # Action
        response = client.get(f"/api/public/rankings?city={test_user.city}")

        # Expected
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.json(), list)
