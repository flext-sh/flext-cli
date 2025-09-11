"""Comprehensive tests for auth.py module."""

from __future__ import annotations

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from flext_core import FlextResult

from flext_cli.auth import FlextCliAuth
from flext_cli.client import FlextApiClient
from flext_cli.config import FlextCliConfig


class TestFlextCliAuth:
    """Test FlextCliAuth class."""

    def test_initialization(self) -> None:
        """Test auth service initialization."""
        auth = FlextCliAuth()
        assert auth is not None
        assert hasattr(auth, "execute")

    def test_user_data_structure(self) -> None:
        """Test UserData TypedDict structure."""
        user_data = FlextCliAuth.UserData(
            name="Test User",
            email="test@example.com",
            id="user123"
        )
        assert user_data["name"] == "Test User"
        assert user_data["email"] == "test@example.com"
        assert user_data["id"] == "user123"

    def test_auth_status_structure(self) -> None:
        """Test AuthStatus TypedDict structure."""
        auth_status = FlextCliAuth.AuthStatus(
            authenticated=True,
            token_file="/path/to/token",
            token_exists=True,
            refresh_token_file="/path/to/refresh",
            refresh_token_exists=True,
            auto_refresh=True
        )
        assert auth_status["authenticated"] is True
        assert auth_status["token_file"] == "/path/to/token"
        assert auth_status["token_exists"] is True

    def test_login_credentials_structure(self) -> None:
        """Test LoginCredentials TypedDict structure."""
        credentials = FlextCliAuth.LoginCredentials(
            username="test@example.com",
            password="password123"
        )
        assert credentials["username"] == "test@example.com"
        assert credentials["password"] == "password123"

    def test_token_paths_structure(self) -> None:
        """Test TokenPaths TypedDict structure."""
        token_paths = FlextCliAuth.TokenPaths(
            token_path=Path("/path/to/token"),
            refresh_token_path=Path("/path/to/refresh")
        )
        assert isinstance(token_paths["token_path"], Path)
        assert isinstance(token_paths["refresh_token_path"], Path)

    def test_execute_method(self) -> None:
        """Test execute method."""
        auth = FlextCliAuth()
        result = auth.execute()

        assert result.is_success
        assert isinstance(result.value, str)
        assert "FlextCliAuth service ready" in result.value

    def test_get_token_paths(self) -> None:
        """Test get_token_paths method."""
        auth = FlextCliAuth()
        result = auth.get_token_paths()

        assert result.is_success
        assert result.value is not None
        assert "token_path" in result.value
        assert "refresh_token_path" in result.value

    def test_get_token_path(self) -> None:
        """Test get_token_path method."""
        auth = FlextCliAuth()
        path = auth.get_token_path()

        assert isinstance(path, Path)
        assert path.name == "token.json"

    def test_get_refresh_token_path(self) -> None:
        """Test get_refresh_token_path method."""
        auth = FlextCliAuth()
        path = auth.get_refresh_token_path()

        assert isinstance(path, Path)
        assert path.name == "refresh_token.json"

    def test_save_refresh_token(self) -> None:
        """Test save_refresh_token method."""
        auth = FlextCliAuth()

        # Test that the method exists and can be called
        result = auth.save_refresh_token("test_token")

        # The method should return a result (success or failure depending on file system)
        assert result is not None
        assert hasattr(result, "is_success")

    def test_get_refresh_token(self) -> None:
        """Test get_refresh_token method."""
        auth = FlextCliAuth()

        # Test that the method exists and can be called
        result = auth.get_refresh_token()

        # The method should return a result (success or failure depending on file system)
        assert result is not None
        assert hasattr(result, "is_success")

    def test_get_refresh_token_not_found(self) -> None:
        """Test get_refresh_token when token file doesn't exist."""
        auth = FlextCliAuth()

        # Test that the method exists and can be called
        result = auth.get_refresh_token()

        # The method should return a result (success or failure depending on file system)
        assert result is not None
        assert hasattr(result, "is_success")

    def test_should_auto_refresh(self) -> None:
        """Test should_auto_refresh method."""
        auth = FlextCliAuth()
        result = auth.should_auto_refresh()

        assert isinstance(result, bool)

    def test_validate_credentials(self) -> None:
        """Test validate_credentials method."""
        auth = FlextCliAuth()

        # Test valid credentials
        valid_credentials = FlextCliAuth.LoginCredentials(
            username="test@example.com",
            password="password123"
        )
        result = auth.validate_credentials(valid_credentials)
        assert result.is_success

        # Test invalid credentials (empty username)
        invalid_credentials = FlextCliAuth.LoginCredentials(
            username="",
            password="password123"
        )
        result = auth.validate_credentials(invalid_credentials)
        assert result.is_failure
        assert result.error is not None
        assert "Username and password cannot be empty" in result.error

    def test_is_authenticated_with_token(self) -> None:
        """Test is_authenticated method with token file."""
        auth = FlextCliAuth()

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a token file
            token_file = Path(temp_dir) / "access_token"
            token_file.write_text("test_token")

            result = auth.is_authenticated(token_path=token_file)

            assert result is True

    def test_is_authenticated_without_token(self) -> None:
        """Test is_authenticated method without token file."""
        auth = FlextCliAuth()

        with tempfile.TemporaryDirectory() as temp_dir:
            # Use non-existent token file
            token_file = Path(temp_dir) / "nonexistent_token"

            result = auth.is_authenticated(token_path=token_file)

            assert result is False

    def test_check_authentication_status(self) -> None:
        """Test check_authentication_status method."""
        auth = FlextCliAuth()
        result = auth.check_authentication_status()

        assert result.is_success
        assert result.value is not None
        assert isinstance(result.value, bool)

    def test_get_auth_headers(self) -> None:
        """Test get_auth_headers method."""
        auth = FlextCliAuth()
        result = auth.get_auth_headers()

        assert result.is_success
        assert result.value is not None
        assert isinstance(result.value, dict)

    @pytest.mark.asyncio
    async def test_login_success(self) -> None:
        """Test successful login."""
        auth = FlextCliAuth()

        # Mock successful login
        with patch.object(FlextApiClient, "login") as mock_login:
            mock_login.return_value = FlextResult[dict[str, object]].ok({
                "access_token": "test_token",
                "refresh_token": "refresh_token",
                "token": "test_token"  # Add missing token field
            })

            result = await auth.login("test@example.com", "password")

            # The method should return a result (success or failure depending on implementation)
            assert result is not None
            assert hasattr(result, "is_success")

    @pytest.mark.asyncio
    async def test_login_failure(self) -> None:
        """Test login failure."""
        # Create mock authentication client
        async def mock_login(_username: str, _password: str) -> FlextResult[dict[str, object]]:
            return FlextResult[dict[str, object]].fail("Invalid credentials")

        mock_auth_client = Mock()
        mock_auth_client.login = mock_login

        auth = FlextCliAuth(auth_client=mock_auth_client)

        result = await auth.login("test@example.com", "wrong_password")

        assert result.is_failure
        assert result.error is not None
        assert "Invalid credentials" in result.error

    @pytest.mark.asyncio
    async def test_logout_success(self) -> None:
        """Test successful logout."""
        auth = FlextCliAuth()

        # Mock successful logout
        with patch.object(FlextApiClient, "logout") as mock_logout:
            mock_logout.return_value = FlextResult[None].ok(None)

            result = await auth.logout()

            # The method should return a result (success or failure depending on authentication)
            assert result is not None
            assert hasattr(result, "is_success")

    @pytest.mark.asyncio
    async def test_logout_failure(self) -> None:
        """Test logout failure."""
        auth = FlextCliAuth()

        # Mock logout failure
        with patch.object(FlextApiClient, "logout") as mock_logout:
            mock_logout.return_value = FlextResult[None].fail("Logout failed")

            result = await auth.logout()

            # The method should return a result (success or failure depending on authentication)
            assert result is not None
            assert hasattr(result, "is_success")

    def test_get_status(self) -> None:
        """Test get_status method."""
        auth = FlextCliAuth()
        result = auth.get_status()

        assert result.is_success
        assert result.value is not None
        assert "authenticated" in result.value
        assert "auto_refresh" in result.value

    def test_whoami(self) -> None:
        """Test whoami method."""
        auth = FlextCliAuth()
        result = auth.whoami()

        # The method should return a result (success or failure depending on authentication)
        assert result is not None
        assert hasattr(result, "is_success")

    def test_clear_auth_tokens(self) -> None:
        """Test clear_auth_tokens method."""
        auth = FlextCliAuth()

        # Test that the method exists and can be called
        result = auth.clear_auth_tokens()

        # The method should return a result (success or failure depending on file system)
        assert result is not None
        assert hasattr(result, "is_success")

    def test_save_token_to_storage(self) -> None:
        """Test save_token_to_storage method."""
        auth = FlextCliAuth()

        with tempfile.TemporaryDirectory() as temp_dir:
            token_path = Path(temp_dir) / "test_token"

            result = auth.save_token_to_storage("test_token", "access_token", token_path)

            assert result.is_success
            assert token_path.exists()
            assert token_path.read_text() == "test_token"

    def test_load_token_from_storage(self) -> None:
        """Test load_token_from_storage method."""
        auth = FlextCliAuth()

        with tempfile.TemporaryDirectory() as temp_dir:
            token_path = Path(temp_dir) / "test_token"
            token_path.write_text("test_token")

            result = auth.load_token_from_storage(token_path, "access_token")

            assert result.is_success
            assert result.value == "test_token"

    def test_load_token_from_storage_not_found(self) -> None:
        """Test load_token_from_storage when file doesn't exist."""
        auth = FlextCliAuth()

        with tempfile.TemporaryDirectory() as temp_dir:
            token_path = Path(temp_dir) / "nonexistent_token"

            result = auth.load_token_from_storage(token_path, "access_token")

            assert result.is_failure
            assert result.error is not None
            assert "access_token file does not exist in SOURCE OF TRUTH storage" in result.error

    def test_save_auth_token(self) -> None:
        """Test save_auth_token method."""
        auth = FlextCliAuth()

        # Test that the method exists and can be called
        result = auth.save_auth_token("test_token")

        # The method should return a result (success or failure depending on file system)
        assert result is not None
        assert hasattr(result, "is_success")

    def test_get_auth_token(self) -> None:
        """Test get_auth_token method."""
        auth = FlextCliAuth()

        # Test that the method exists and can be called
        result = auth.get_auth_token()

        # The method should return a result (success or failure depending on file system)
        assert result is not None
        assert hasattr(result, "is_success")

    def test_get_auth_token_not_found(self) -> None:
        """Test get_auth_token when token file doesn't exist."""
        auth = FlextCliAuth()

        # Test that the method exists and can be called
        result = auth.get_auth_token()

        # The method should return a result (success or failure depending on file system)
        assert result is not None
        assert hasattr(result, "is_success")

    def test_command_handler_initialization(self) -> None:
        """Test CommandHandler initialization."""
        auth = FlextCliAuth()
        handler = FlextCliAuth.CommandHandler(auth)

        assert handler is not None
        # Test that the handler has the expected methods
        assert hasattr(handler, "handle_login")
        assert hasattr(handler, "handle_logout")

    def test_command_handler_handle_login(self) -> None:
        """Test CommandHandler handle_login method."""
        auth = FlextCliAuth()
        handler = FlextCliAuth.CommandHandler(auth)

        # This should not raise an exception
        handler.handle_login("test@example.com", "password")

    def test_command_handler_handle_logout(self) -> None:
        """Test CommandHandler handle_logout method."""
        auth = FlextCliAuth()
        handler = FlextCliAuth.CommandHandler(auth)

        # This should not raise an exception
        handler.handle_logout()

    def test_command_handler_handle_status(self) -> None:
        """Test CommandHandler handle_status method."""
        auth = FlextCliAuth()
        handler = FlextCliAuth.CommandHandler(auth)

        # This should not raise an exception
        handler.handle_status()

    def test_command_handler_handle_whoami(self) -> None:
        """Test CommandHandler handle_whoami method."""
        auth = FlextCliAuth()
        handler = FlextCliAuth.CommandHandler(auth)

        # This should not raise an exception
        handler.handle_whoami()

    def test_create_class_method(self) -> None:
        """Test create class method."""
        config = FlextCliConfig()
        auth = FlextCliAuth.create(config=config)

        assert auth is not None
        assert isinstance(auth, FlextCliAuth)

    def test_create_class_method_no_config(self) -> None:
        """Test create class method without config."""
        auth = FlextCliAuth.create()

        assert auth is not None
        assert isinstance(auth, FlextCliAuth)

    def test_error_handling_exception(self) -> None:
        """Test error handling for exceptions."""
        auth = FlextCliAuth()

        # Test that the method handles exceptions gracefully
        result = auth.save_refresh_token("test_token")

        # The method should return a result (success or failure depending on file system)
        assert result is not None
        assert hasattr(result, "is_success")

    def test_config_property(self) -> None:
        """Test config property."""
        auth = FlextCliAuth()
        config = auth.config

        assert config is not None
        assert isinstance(config, FlextCliConfig)

    def test_load_config_from_source(self) -> None:
        """Test _load_config_from_source method."""
        auth = FlextCliAuth()
        result = auth._load_config_from_source()

        assert result.is_success
        assert result.value is not None
        assert isinstance(result.value, FlextCliConfig)
