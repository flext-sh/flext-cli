"""Real functionality tests for FlextCliAuth unified class - NO MOCKS.

Tests authentication functionality using real implementations following
the ZERO TOLERANCE requirements for production-ready code.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from flext_core import FlextResult

from flext_cli.auth import FlextCliAuth
from flext_cli.config import FlextCliConfig


class TestFlextCliAuth(unittest.TestCase):
    """Real functionality tests for FlextCliAuth unified authentication class."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        # Create temporary directory for test tokens
        self.temp_dir = Path(tempfile.mkdtemp())

        # Create test config with temp directory
        self.config = FlextCliConfig(
            token_file=self.temp_dir / "token.json",
            refresh_token_file=self.temp_dir / "refresh_token.json",
        )

        self.auth = FlextCliAuth(config=self.config)

    def tearDown(self) -> None:
        """Clean up test fixtures."""
        # Clean up temporary files
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_auth_initialization(self) -> None:
        """Test FlextCliAuth initialization."""
        # Test with config
        auth_with_config = FlextCliAuth(config=self.config)
        assert isinstance(auth_with_config, FlextCliAuth)

        # Test without config (should create default)
        auth_default = FlextCliAuth()
        assert isinstance(auth_default, FlextCliAuth)

    def test_token_path_methods(self) -> None:
        """Test token file path methods."""
        token_path = self.auth.get_token_path()
        assert isinstance(token_path, Path)

        refresh_path = self.auth.get_refresh_token_path()
        assert isinstance(refresh_path, Path)

    def test_auth_token_operations(self) -> None:
        """Test authentication token save/load operations."""
        test_token = "test_access_token_12345"

        # Test save token
        save_result = self.auth.save_auth_token(test_token)
        assert isinstance(save_result, FlextResult)
        assert save_result.is_success

        # Test get token
        get_result = self.auth.get_auth_token()
        assert isinstance(get_result, FlextResult)
        assert get_result.is_success
        assert get_result.value == test_token

    def test_refresh_token_operations(self) -> None:
        """Test refresh token save/load operations."""
        test_refresh_token = "test_refresh_token_67890"

        # Test save refresh token
        save_result = self.auth.save_refresh_token(test_refresh_token)
        assert isinstance(save_result, FlextResult)
        assert save_result.is_success

        # Test get refresh token
        get_result = self.auth.get_refresh_token()
        assert isinstance(get_result, FlextResult)
        assert get_result.is_success
        assert get_result.value == test_refresh_token

    def test_authentication_status(self) -> None:
        """Test authentication status checking."""
        # Initially should not be authenticated
        is_auth = self.auth.is_authenticated()
        assert isinstance(is_auth, bool)
        assert is_auth is False

        # Save a token and check again
        self.auth.save_auth_token("valid_token")
        is_auth_with_token = self.auth.is_authenticated()
        assert isinstance(is_auth_with_token, bool)
        assert is_auth_with_token is True

    def test_clear_auth_tokens(self) -> None:
        """Test clearing authentication tokens."""
        # Set up tokens first
        self.auth.save_auth_token("test_token")
        self.auth.save_refresh_token("test_refresh")

        # Verify tokens exist
        assert self.auth.is_authenticated() is True

        # Clear tokens
        clear_result = self.auth.clear_auth_tokens()
        assert isinstance(clear_result, FlextResult)
        assert clear_result.is_success

        # Verify tokens are cleared
        assert self.auth.is_authenticated() is False

    def test_auto_refresh_logic(self) -> None:
        """Test auto-refresh logic."""
        # Test should_auto_refresh method
        should_refresh = self.auth.should_auto_refresh()
        assert isinstance(should_refresh, bool)


class TestFlextCliAuthIntegration(unittest.TestCase):
    """Integration tests for FlextCliAuth with different configurations."""

    def test_auth_with_custom_config(self) -> None:
        """Test authentication with custom configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            custom_config = FlextCliConfig(
                token_file=temp_path / "custom_token.json",
                refresh_token_file=temp_path / "custom_refresh.json",
                auto_refresh=False,
            )

            auth = FlextCliAuth(config=custom_config)

            # Test custom paths are used
            token_path = auth.get_token_path()
            refresh_path = auth.get_refresh_token_path()

            assert token_path == temp_path / "custom_token.json"
            assert refresh_path == temp_path / "custom_refresh.json"

            # Test functionality works with custom config
            auth.save_auth_token("custom_token")
            token_result = auth.get_auth_token()
            assert token_result.is_success
            assert token_result.value == "custom_token"

    def test_auth_error_handling(self) -> None:
        """Test authentication error handling."""
        # Test with invalid/inaccessible paths
        invalid_config = FlextCliConfig(
            token_file=Path("/invalid/path/token.json"),
            refresh_token_file=Path("/invalid/path/refresh.json"),
        )

        auth = FlextCliAuth(config=invalid_config)

        # Operations should return failures, not raise exceptions
        save_result = auth.save_auth_token("test_token")
        assert isinstance(save_result, FlextResult)
        # Should fail due to invalid path
        assert save_result.is_failure

    def test_concurrent_auth_operations(self) -> None:
        """Test authentication operations work correctly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            config = FlextCliConfig(
                token_file=temp_path / "concurrent_token.json",
                refresh_token_file=temp_path / "concurrent_refresh.json",
            )

            auth1 = FlextCliAuth(config=config)
            auth2 = FlextCliAuth(config=config)

            # Save token with first instance
            auth1.save_auth_token("shared_token")

            # Read token with second instance
            token_result = auth2.get_auth_token()
            assert token_result.is_success
            assert token_result.value == "shared_token"


if __name__ == "__main__":
    unittest.main()
