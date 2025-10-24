from fastapi import status


class TestHealthCheck:
    def test_root_endpoint_success(self, client):
        # Action
        response = client.get("/")

        # Expected
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "message": "ANB Rising Stars Showcase API",
            "version": "1.0.0",
            "status": "running",
        }

    def test_root_endpoint_has_version(self, client):
        # Action
        response = client.get("/")

        # Expected
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data == {
            "message": "ANB Rising Stars Showcase API",
            "version": "1.0.0",
            "status": "running",
        }

    def test_root_endpoint_no_authentication_required(self, client):
        # Action
        response = client.get("/")

        # Expected
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "message": "ANB Rising Stars Showcase API",
            "version": "1.0.0",
            "status": "running",
        }
