"""
Tests for authentication endpoints.
"""

from fastapi import status
from unittest.mock import MagicMock


class TestSignup:
    def test_signup_success(self, client, mock_db):
        # Setup
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = None
        mock_db.query.return_value = mock_query
        mock_db.add = MagicMock()
        mock_db.commit = MagicMock()
        mock_db.refresh = MagicMock(side_effect=lambda x: setattr(x, "id", 1))

        # Action
        response = client.post(
            "/api/auth/signup",
            json={
                "first_name": "John",
                "last_name": "Doe",
                "email": "john@example.com",
                "password1": "SecurePass123",
                "password2": "SecurePass123",
                "city": "Bogotá",
                "country": "Colombia",
            },
        )

        # Expected
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() == {
            "message": "Usuario creado exitosamente.",
            "user_id": 1,
        }

    def test_signup_duplicate_email(self, client, mock_db, test_user):
        # Setup
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = test_user
        mock_db.query.return_value = mock_query

        # Action
        response = client.post(
            "/api/auth/signup",
            json={
                "first_name": "Jane",
                "last_name": "Doe",
                "email": test_user.email,
                "password1": "SecurePass123",
                "password2": "SecurePass123",
                "city": "Medellín",
                "country": "Colombia",
            },
        )

        # Expected
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {
            "detail": "El correo electrónico ya está registrado."
        }

    def test_signup_invalid_email(self, client):
        # Action
        response = client.post(
            "/api/auth/signup",
            json={
                "first_name": "John",
                "last_name": "Doe",
                "email": "invalid-email",
                "password1": "SecurePass123",
                "password2": "SecurePass123",
                "city": "Bogotá",
                "country": "Colombia",
            },
        )

        # Expected
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_signup_short_password(self, client):
        # Action
        response = client.post(
            "/api/auth/signup",
            json={
                "first_name": "John",
                "last_name": "Doe",
                "email": "john@example.com",
                "password1": "short",
                "password2": "short",
                "city": "Bogotá",
                "country": "Colombia",
            },
        )

        # Expected
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_signup_missing_fields(self, client):
        # Action
        response = client.post(
            "/api/auth/signup",
            json={
                "first_name": "John",
                "email": "john@example.com",
                "password1": "SecurePass123",
                "password2": "SecurePass123",
            },
        )

        # Expected
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestLogin:
    def test_login_success(self, client, mock_db, test_user):
        # Setup
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = test_user
        mock_db.query.return_value = mock_query

        # Action
        response = client.post(
            "/api/auth/login",
            json={
                "email": test_user.email,
                "password": "TestPassword123",
            },
        )

        # Expected
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "Bearer"
        assert "expires_in" in data

    def test_login_invalid_email(self, client, mock_db):
        # Setup
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = None
        mock_db.query.return_value = mock_query

        # Action
        response = client.post(
            "/api/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "SomePassword123",
            },
        )

        # Expected
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": "Credenciales inválidas."}

    def test_login_invalid_password(self, client, mock_db, test_user):
        # Setup
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = test_user
        mock_db.query.return_value = mock_query

        # Action
        response = client.post(
            "/api/auth/login",
            json={
                "email": test_user.email,
                "password": "WrongPassword123",
            },
        )

        # Expected
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": "Credenciales inválidas."}

    def test_login_missing_fields(self, client):
        # Action
        response = client.post(
            "/api/auth/login",
            json={
                "email": "test@example.com",
            },
        )

        # Expected
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
