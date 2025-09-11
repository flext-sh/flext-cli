"""Real validation tests for FlextCliAuth - testing actual functionality."""

import tempfile
from datetime import UTC, datetime
from pathlib import Path

from flext_core import FlextResult

from flext_cli.auth import FlextCliAuth
from flext_cli.config import FlextCliConfig


class TestFlextCliAuthRealValidation:
    """Real validation tests for FlextCliAuth functionality."""

    def test_auth_service_initialization(self) -> None:
        """Test that auth service initializes correctly."""
        auth = FlextCliAuth()

        # Test basic initialization
        assert auth is not None
        assert hasattr(auth, "execute")
        assert hasattr(auth, "config")

        # Test execute method returns success
        result = auth.execute()
        assert result.is_success
        assert "FlextCliAuth service ready" in result.value

    def test_config_retrieval(self) -> None:
        """Test that config is retrieved correctly."""
        auth = FlextCliAuth()

        # Test config property (it's a property, not a method)
        config = auth.config
        assert isinstance(config, FlextCliConfig)
        assert config.app_name == "flext-app"

    def test_token_paths_retrieval(self) -> None:
        """Test that token paths are retrieved correctly."""
        auth = FlextCliAuth()

        result = auth.get_token_paths()
        assert result.is_success

        token_paths = result.value
        assert "token_path" in token_paths
        assert "refresh_token_path" in token_paths

        # Test that paths are Path objects
        assert isinstance(token_paths["token_path"], Path)
        assert isinstance(token_paths["refresh_token_path"], Path)

    def test_credentials_validation(self) -> None:
        """Test credentials validation with real data."""
        auth = FlextCliAuth()

        # Test valid credentials
        valid_credentials = auth.LoginCredentials(
            username="testuser",
            password="testpass123"
        )

        result = auth.validate_credentials(valid_credentials)
        assert result.is_success

        # Test invalid credentials (empty username)
        invalid_credentials = auth.LoginCredentials(
            username="",
            password="testpass123"
        )

        result = auth.validate_credentials(invalid_credentials)
        assert result.is_failure
        assert result.error is not None
        assert "username" in result.error.lower()

    def test_auth_token_save_and_retrieve(self) -> None:
        """Test saving and retrieving auth tokens."""
        auth = FlextCliAuth()

        # Test saving token
        token = "test_access_token_123"
        result = auth.save_auth_token(token)
        assert result.is_success

        # Test retrieving token
        token_result: FlextResult[str] = auth.get_auth_token()
        assert token_result.is_success
        assert token_result.value == token

    def test_authentication_status_check(self) -> None:
        """Test authentication status checking."""
        auth = FlextCliAuth()

        # Test when no token exists
        result = auth.check_authentication_status()
        assert result.is_success
        assert isinstance(result.value, bool)

        # Test is_authenticated method
        is_auth = auth.is_authenticated()
        assert isinstance(is_auth, bool)

    def test_auth_headers_generation(self) -> None:
        """Test auth headers generation."""
        auth = FlextCliAuth()

        # Save a token first
        token = "test_token_123"
        auth.save_auth_token(token)

        # Test headers generation
        result = auth.get_auth_headers()
        assert result.is_success

        headers = result.value
        assert "Authorization" in headers
        assert headers["Authorization"] == f"Bearer {token}"

    def test_auth_status_retrieval(self) -> None:
        """Test auth status retrieval."""
        auth = FlextCliAuth()

        result = auth.get_status()
        assert result.is_success

        status = result.value
        assert "authenticated" in status
        assert "token_file" in status
        assert "token_exists" in status
        assert isinstance(status["authenticated"], bool)
        assert isinstance(status["token_exists"], bool)

    def test_user_info_retrieval(self) -> None:
        """Test user info retrieval."""
        auth = FlextCliAuth()

        result = auth.whoami()
        # The method should return a result (success or failure depending on authentication)
        assert result is not None
        assert hasattr(result, "is_success")

    def test_token_clearing(self) -> None:
        """Test token clearing functionality."""
        auth = FlextCliAuth()

        # Save a token first
        token = "test_token_to_clear"
        auth.save_auth_token(token)

        # Verify token exists
        result = auth.get_auth_token()
        assert result.is_success
        assert result.value == token

        # Clear tokens
        clear_result: FlextResult[None] = auth.clear_auth_tokens()
        assert clear_result.is_success

        # Verify token is cleared
        result = auth.get_auth_token()
        assert result.is_failure

    def test_refresh_token_operations(self) -> None:
        """Test refresh token operations."""
        auth = FlextCliAuth()

        # Test saving refresh token
        refresh_token = "test_refresh_token_123"
        result = auth.save_refresh_token(refresh_token)
        assert result.is_success

        # Test retrieving refresh token
        refresh_result: FlextResult[str] = auth.get_refresh_token()
        assert refresh_result.is_success
        assert refresh_result.value == refresh_token

    def test_auto_refresh_configuration(self) -> None:
        """Test auto refresh configuration."""
        auth = FlextCliAuth()

        # Test auto refresh check
        should_refresh = auth.should_auto_refresh()
        assert isinstance(should_refresh, bool)

    def test_login_flow(self) -> None:
        """Test login flow using authenticate_user method."""
        auth = FlextCliAuth()

        # Test authenticate_user method (synchronous)
        result = auth.authenticate_user("testuser", "testpass")

        assert result.is_success
        assert result.value == "access_token_123"

    def test_logout_flow(self) -> None:
        """Test logout flow using clear_auth_tokens method."""
        auth = FlextCliAuth()

        # Save a token first
        auth.save_auth_token("test_token")

        # Test logout by clearing tokens
        result = auth.clear_auth_tokens()

        assert result.is_success

        # Verify token is cleared
        token_result = auth.get_auth_token()
        assert token_result.is_failure

    def test_typed_dict_structures(self) -> None:
        """Test TypedDict structures."""
        auth = FlextCliAuth()

        # Test UserData
        user_data = auth.UserData(
            name="Test User",
            email="test@example.com",
            id="user123"
        )
        assert user_data["name"] == "Test User"
        assert user_data["email"] == "test@example.com"

        # Test AuthStatus
        auth_status = auth.AuthStatus(
            authenticated=True,
            token_file="/path/to/token",
            token_exists=True,
            refresh_token_file="/path/to/refresh_token",
            refresh_token_exists=True,
            auto_refresh=True
        )
        assert auth_status["authenticated"] is True
        assert auth_status["token_exists"] is True

        # Test LoginCredentials
        credentials = auth.LoginCredentials(
            username="testuser",
            password="testpass"
        )
        assert credentials["username"] == "testuser"
        assert credentials["password"] == "testpass"

        # Test AuthConfig
        auth_config = auth.AuthConfig(
            api_key="test_key",
            base_url="https://api.example.com",
            timeout=30
        )
        assert auth_config["api_key"] == "test_key"
        assert auth_config["base_url"] == "https://api.example.com"

        # Test TokenData
        token_data = auth.TokenData(
            access_token="access123",
            refresh_token="refresh123",
            expires_at=datetime.now(UTC),
            token_type="Bearer"
        )
        assert token_data["access_token"] == "access123"
        assert token_data["token_type"] == "Bearer"

    def test_error_handling(self) -> None:
        """Test error handling in various scenarios."""
        auth = FlextCliAuth()

        # Test invalid credentials validation
        invalid_credentials = auth.LoginCredentials(
            username="",
            password=""
        )

        result = auth.validate_credentials(invalid_credentials)
        assert result.is_failure
        assert result.error is not None
        assert "username" in result.error.lower()

        # Test getting token when none exists
        auth.clear_auth_tokens()
        token_result = auth.get_auth_token()
        assert token_result.is_failure

    def test_file_operations(self) -> None:
        """Test file operations for config and tokens."""
        auth = FlextCliAuth()

        with tempfile.NamedTemporaryFile(mode="w", delete=False) as tmp_file:
            config_data = {
                "api_key": "test_key",
                "base_url": "https://api.example.com",
                "timeout": 30
            }

            # Test saving config
            result = auth.save_auth_config(config_data, tmp_file.name)
            assert result.is_success

            # Test loading config
            config_result = auth.load_auth_config(tmp_file.name)
            assert config_result.is_success
            assert isinstance(config_result.value, dict)
            assert config_result.value["api_key"] == "test_key"

            # Test clearing auth data
            result = auth.clear_auth_data(tmp_file.name)
            assert result.is_success

            # Verify file is deleted
            assert not Path(tmp_file.name).exists()

    def test_validation_methods(self) -> None:
        """Test validation methods."""
        auth = FlextCliAuth()

        # Test user data validation
        valid_user: dict[str, object] = {
            "name": "Test User",
            "email": "test@example.com"
        }

        result = auth._validate_user_data(valid_user)
        assert result.is_success

        # Test invalid user data
        invalid_user: dict[str, object] = {
            "name": "",
            "email": "test@example.com"
        }

        result = auth._validate_user_data(invalid_user)
        assert result.is_failure

        # Test auth config validation
        valid_config: dict[str, object] = {
            "api_key": "test_key",
            "base_url": "https://api.example.com"
        }

        result = auth._validate_auth_config(valid_config)
        assert result.is_success

        # Test invalid auth config
        invalid_config: dict[str, object] = {
            "api_key": "",
            "base_url": "https://api.example.com"
        }

        result = auth._validate_auth_config(invalid_config)
        assert result.is_failure

    def test_token_expiration_check(self) -> None:
        """Test token expiration checking."""
        auth = FlextCliAuth()

        # Test with expired timestamp
        expired_time = datetime.now(UTC).replace(year=2020)
        is_expired = auth._is_token_expired(expired_time)
        assert is_expired is True

        # Test with future timestamp
        future_time = datetime.now(UTC).replace(year=2030)
        is_expired = auth._is_token_expired(future_time)
        assert is_expired is False
