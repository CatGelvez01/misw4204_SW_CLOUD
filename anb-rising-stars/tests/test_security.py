from datetime import timedelta
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_token,
)


class TestPasswordHashing:
    def test_hash_password_creates_hash(self):
        # Action
        password = "TestPassword123"
        hashed = hash_password(password)
        # Expected
        assert hashed is not None
        assert hashed != password

    def test_hash_password_different_each_time(self):
        # Action
        password = "TestPassword123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        # Expected
        assert hash1 != hash2

    def test_verify_password_correct(self):
        # Setup
        password = "TestPassword123"
        hashed = hash_password(password)
        # Action
        result = verify_password(password, hashed)
        # Expected
        assert result is True

    def test_verify_password_incorrect(self):
        # Setup
        password = "TestPassword123"
        wrong_password = "WrongPassword456"
        hashed = hash_password(password)
        # Action
        result = verify_password(wrong_password, hashed)
        # Expected
        assert result is False

    def test_verify_password_empty_string(self):
        # Setup
        password = "TestPassword123"
        hashed = hash_password(password)
        # Action
        result = verify_password("", hashed)
        # Expected
        assert result is False

    def test_hash_password_long_password(self):
        # Setup
        password = "A" * 255
        # Action
        hashed = hash_password(password)
        result = verify_password(password, hashed)
        # Expected
        assert result is True

    def test_hash_password_special_characters(self):
        # Setup
        password = "P@ssw0rd!#$%^&*()"
        # Action
        hashed = hash_password(password)
        result = verify_password(password, hashed)
        # Expected
        assert result is True


class TestJWTTokens:
    def test_create_access_token_returns_string(self):
        # Setup
        data = {"sub": "1", "email": "test@example.com"}
        # Action
        token = create_access_token(data)
        # Expected
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_access_token_with_custom_expiry(self):
        # Setup
        data = {"sub": "1", "email": "test@example.com"}
        expires_delta = timedelta(hours=2)
        # Action
        token = create_access_token(data, expires_delta)
        decoded = decode_token(token)
        # Expected
        assert decoded is not None
        assert "exp" in decoded

    def test_decode_token_valid(self):
        # Setup
        data = {"sub": "1", "email": "test@example.com"}
        token = create_access_token(data)
        # Action
        decoded = decode_token(token)
        # Expected
        assert decoded is not None
        assert decoded["sub"] == "1"
        assert decoded["email"] == "test@example.com"

    def test_decode_token_invalid(self):
        # Setup
        invalid_token = "invalid.token.here"
        # Action
        decoded = decode_token(invalid_token)
        # Expected
        assert decoded is None

    def test_decode_token_empty_string(self):
        # Action
        decoded = decode_token("")
        # Expected
        assert decoded is None

    def test_decode_token_malformed(self):
        # Setup
        malformed_token = "not.a.valid.jwt"
        # Action
        decoded = decode_token(malformed_token)
        # Expected
        assert decoded is None

    def test_create_access_token_contains_exp(self):
        # Setup
        data = {"sub": "1"}
        # Action
        token = create_access_token(data)
        decoded = decode_token(token)
        # Expected
        assert "exp" in decoded

    def test_create_access_token_preserves_data(self):
        # Setup
        data = {"sub": "123", "email": "user@example.com", "role": "admin"}
        # Action
        token = create_access_token(data)
        decoded = decode_token(token)
        # Expected
        assert decoded["sub"] == "123"
        assert decoded["email"] == "user@example.com"
        assert decoded["role"] == "admin"

    def test_decode_token_with_tampered_payload(self):
        # Setup
        data = {"sub": "1", "email": "test@example.com"}
        token = create_access_token(data)
        tampered_token = token[:-10] + "0000000000"
        # Action
        decoded = decode_token(tampered_token)
        # Expected
        assert decoded is None
