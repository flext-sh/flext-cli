"""Real validation tests for FlextCliAuth - testing actual functionality."""

from pathlib import Path

from flext_cli.flext_cli_auth import FlextCliAuth
from flext_cli.models import FlextCliModels
from flext_core import FlextResult


class TestFlextCliAuthRealValidation:
    """Real validation tests for FlextCliAuth functionality."""

    def test_auth_service_initialization(self) -> None:
        """Test that auth service initializes correctly."""
        auth = FlextCliAuth()

        # Test basic initialization
        assert auth is not None
        assert hasattr(auth, "execute")
        assert hasattr(auth, "_config")

        # Test execute method returns success
        result: FlextResult[str] = auth.execute()
        assert result.is_success
        assert "FlextCliAuth service operational" in result.value

    def test_config_retrieval(self) -> None:
        """Test that config is retrieved correctly."""
        auth = FlextCliAuth()

        # Test config attribute (it's a private attribute, not a property)
        config: FlextCliModels.FlextCliConfig = auth._config
        assert isinstance(config, FlextCliModels.FlextCliConfig)
        assert config.profile == "default"

    def test_credentials_validation(self) -> None:
        """Test credentials validation with real data."""
        auth = FlextCliAuth()

        # Test valid credentials
        result: FlextResult[None] = auth.validate_credentials("testuser", "testpass123")
        assert result.is_success

        # Test invalid credentials (empty username)
        result = auth.validate_credentials("", "testpass123")
        assert result.is_failure
        assert result.error is not None
        assert "username" in result.error.lower()

        # Test invalid credentials (empty password)
        result = auth.validate_credentials("testuser", "")
        assert result.is_failure
        assert result.error is not None
        assert "password" in result.error.lower()

    def test_auth_token_save_and_retrieve(self) -> None:
        """Test saving and retrieving auth tokens."""
        auth = FlextCliAuth()

        # Test saving token
        token: str = "test_access_token_123"
        result: FlextResult[None] = auth.save_auth_token(token)
        assert result.is_success

        # Test retrieving token
        token_result: FlextResult[str] = auth.get_auth_token()
        assert token_result.is_success
        assert token_result.value == token

    def test_authentication_status_check(self) -> None:
        """Test authentication status checking."""
        auth = FlextCliAuth()

        # Test is_authenticated method
        is_auth: bool = auth.is_authenticated()
        assert isinstance(is_auth, bool)

        # Test when no token exists initially
        assert not is_auth

        # Save a token and test again
        auth.save_auth_token("test_token")
        is_auth = auth.is_authenticated()
        assert is_auth

    def test_auth_status_retrieval(self) -> None:
        """Test auth status retrieval."""
        auth = FlextCliAuth()

        result: FlextResult[dict[str, object]] = auth.get_auth_status()
        assert result.is_success

        status: dict[str, object] = result.value
        assert "authenticated" in status
        assert "token_file" in status
        assert "token_exists" in status
        assert isinstance(status["authenticated"], bool)
        assert isinstance(status["token_exists"], bool)

    def test_token_clearing(self) -> None:
        """Test token clearing functionality."""
        auth = FlextCliAuth()

        # Save a token first
        token: str = "test_token_to_clear"
        auth.save_auth_token(token)

        # Verify token exists
        result: FlextResult[str] = auth.get_auth_token()
        assert result.is_success
        assert result.value == token

        # Clear tokens
        clear_result: FlextResult[None] = auth.clear_auth_tokens()
        assert clear_result.is_success

        # Verify token is cleared
        result = auth.get_auth_token()
        assert result.is_failure

    def test_authenticate_method(self) -> None:
        """Test authenticate method with different credential types."""
        auth = FlextCliAuth()

        # Test token-based authentication
        credentials: dict[str, object] = {"token": "test_token_123"}
        result: FlextResult[str] = auth.authenticate(credentials)
        assert result.is_success
        assert result.value == "test_token_123"

        # Test username/password authentication
        credentials = {"username": "testuser", "password": "testpass"}
        result = auth.authenticate(credentials)
        assert result.is_success
        assert "auth_token_testuser" in result.value

        # Test invalid credentials
        credentials = {"invalid": "data"}
        result: FlextResult[str] = auth.authenticate(credentials)
        assert result.is_failure
        assert result.error is not None
        assert "Invalid credentials" in result.error

    def test_logout_flow(self) -> None:
        """Test logout flow using clear_auth_tokens method."""
        auth = FlextCliAuth()

        # Save a token first
        auth.save_auth_token("test_token")

        # Test logout by clearing tokens
        result: FlextResult[None] = auth.clear_auth_tokens()
        assert result.is_success

        # Verify token is cleared
        token_result: FlextResult[str] = auth.get_auth_token()
        assert token_result.is_failure

    def test_auth_config_model(self) -> None:
        """Test AuthConfig model from FlextCliModels."""
        # Test AuthConfig model creation
        auth_config = FlextCliModels.AuthConfig(
            api_url="https://api.example.com",
            token_file=Path("/path/to/token"),
            refresh_token_file=Path("/path/to/refresh_token"),
        )
        assert auth_config.api_url == "https://api.example.com"
        assert str(auth_config.token_file) == "/path/to/token"
        assert str(auth_config.refresh_token_file) == "/path/to/refresh_token"
        assert auth_config.auto_refresh is True

        # Test validation
        validation_result: FlextResult[None] = auth_config.validate_business_rules()
        assert validation_result.is_success

    def test_error_handling(self) -> None:
        """Test error handling in various scenarios."""
        auth = FlextCliAuth()

        # Test invalid credentials validation
        result: FlextResult[None] = auth.validate_credentials("", "")
        assert result.is_failure
        assert result.error is not None
        assert "username" in result.error.lower()

        # Test getting token when none exists
        auth.clear_auth_tokens()
        token_result: FlextResult[str] = auth.get_auth_token()
        assert token_result.is_failure

        # Test saving empty token
        result: FlextResult[None] = auth.save_auth_token("")
        assert result.is_failure
        assert result.error is not None
        assert "Token cannot be empty" in result.error

        # Test authenticate with empty credentials
        auth_result: FlextResult[str] = auth.authenticate({})
        assert auth_result.is_failure
        assert auth_result.error is not None
        assert "Invalid credentials" in auth_result.error

    def test_auth_helper_methods(self) -> None:
        """Test authentication helper methods."""
        auth = FlextCliAuth()

        # Test credential validation with various inputs
        result: FlextResult[None] = auth.validate_credentials("user", "pass")
        assert result.is_success

        result = auth.validate_credentials("  user  ", "  pass  ")
        assert result.is_success

        result = auth.validate_credentials("", "pass")
        assert result.is_failure

        result = auth.validate_credentials("user", "")
        assert result.is_failure

        result = auth.validate_credentials(" ", " ")
        assert result.is_failure

    def test_auth_status_comprehensive(self) -> None:
        """Test comprehensive authentication status."""
        auth = FlextCliAuth()

        # Clear any existing tokens
        auth.clear_auth_tokens()

        # Test status when not authenticated
        result: FlextResult[dict[str, object]] = auth.get_auth_status()
        assert result.is_success
        status: dict[str, object] = result.value
        assert status["authenticated"] is False
        assert status["token_exists"] is False

        # Save a token and test status again
        auth.save_auth_token("test_token_123")
        result = auth.get_auth_status()
        assert result.is_success
        status = result.value
        assert status["authenticated"] is True
        assert status["token_exists"] is True
        assert "timestamp" in status
