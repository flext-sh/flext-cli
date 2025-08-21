"""Tests for utils/auth.py to improve coverage.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

from flext_cli.cli_auth import (
    clear_auth_tokens,
    get_auth_token,
    get_refresh_token,
    get_refresh_token_path,
    get_token_path,
    is_authenticated,
    save_auth_token,
    save_refresh_token,
    should_auto_refresh,
)


class TestGetTokenPath:
    """Test get_token_path function."""

    @patch("flext_cli.utils.auth.get_config")
    def test_direct_token_file_path(self, mock_get_config: MagicMock) -> None:
        """Test when config has direct token_file Path."""
        mock_config = MagicMock()
        mock_config.token_file = Path("/custom/token/path")
        mock_get_config.return_value = mock_config

        result = get_token_path()
        assert result == Path("/custom/token/path")

    @patch("flext_cli.utils.auth.get_config")
    def test_auth_config_token_file_path(self, mock_get_config: MagicMock) -> None:
        """Test when config has auth.token_file Path."""
        mock_config = MagicMock()
        mock_config.token_file = None
        mock_auth_config = MagicMock()
        mock_auth_config.token_file = Path("/auth/token/path")
        mock_config.auth = mock_auth_config
        mock_get_config.return_value = mock_config

        result = get_token_path()
        assert result == Path("/auth/token/path")

    @patch("flext_cli.utils.auth.get_config")
    def test_default_token_path(self, mock_get_config: MagicMock) -> None:
        """Test default token path when no config paths."""
        mock_config = MagicMock()
        mock_config.token_file = None
        mock_config.auth = None
        mock_get_config.return_value = mock_config

        result = get_token_path()
        expected = Path.home() / ".flext" / "auth" / "token"
        assert result == expected

    @patch("flext_cli.utils.auth.get_config")
    def test_non_path_token_file(self, mock_get_config: MagicMock) -> None:
        """Test when token_file is not a Path object."""
        mock_config = MagicMock()
        mock_config.token_file = "/string/path"  # String, not Path
        mock_config.auth = None
        mock_get_config.return_value = mock_config

        result = get_token_path()
        expected = Path.home() / ".flext" / "auth" / "token"
        assert result == expected


class TestGetRefreshTokenPath:
    """Test get_refresh_token_path function."""

    @patch("flext_cli.utils.auth.get_config")
    def test_direct_refresh_token_file_path(self, mock_get_config: MagicMock) -> None:
        """Test when config has direct refresh_token_file Path."""
        mock_config = MagicMock()
        mock_config.refresh_token_file = Path("/custom/refresh/path")
        mock_get_config.return_value = mock_config

        result = get_refresh_token_path()
        assert result == Path("/custom/refresh/path")

    @patch("flext_cli.utils.auth.get_config")
    def test_auth_config_refresh_token_path(self, mock_get_config: MagicMock) -> None:
        """Test when config has auth.refresh_token_file Path."""
        mock_config = MagicMock()
        mock_config.refresh_token_file = None
        mock_auth_config = MagicMock()
        mock_auth_config.refresh_token_file = Path("/auth/refresh/path")
        mock_config.auth = mock_auth_config
        mock_get_config.return_value = mock_config

        result = get_refresh_token_path()
        assert result == Path("/auth/refresh/path")

    @patch("flext_cli.utils.auth.get_config")
    def test_default_refresh_token_path(self, mock_get_config: MagicMock) -> None:
        """Test default refresh token path."""
        mock_config = MagicMock()
        mock_config.refresh_token_file = None
        mock_config.auth = None
        mock_get_config.return_value = mock_config

        result = get_refresh_token_path()
        expected = Path.home() / ".flext" / "auth" / "refresh_token"
        assert result == expected


class TestSaveAuthToken:
    """Test save_auth_token function."""

    @patch("flext_cli.utils.auth.get_token_path")
    def test_save_auth_token_success(self, mock_get_token_path: MagicMock) -> None:
        """Test successful auth token saving."""
        with tempfile.TemporaryDirectory() as temp_dir:
            token_path = Path(temp_dir) / "token"
            mock_get_token_path.return_value = token_path

            result = save_auth_token("test_token_123")

            assert result.success
            assert token_path.exists()
            assert token_path.read_text(encoding="utf-8") == "test_token_123"
            # Check permissions (on Unix systems)
            if hasattr(Path, "stat"):
                stat = token_path.stat()
                assert oct(stat.st_mode)[-3:] == "600"

    @patch("flext_cli.utils.auth.get_token_path")
    def test_save_auth_token_creates_parent_dirs(
        self, mock_get_token_path: MagicMock
    ) -> None:
        """Test that parent directories are created."""
        with tempfile.TemporaryDirectory() as temp_dir:
            token_path = Path(temp_dir) / "nested" / "dirs" / "token"
            mock_get_token_path.return_value = token_path

            result = save_auth_token("test_token")

            assert result.success
            assert token_path.exists()
            assert token_path.parent.exists()

    @patch("flext_cli.utils.auth.get_token_path")
    def test_save_auth_token_permission_error(
        self, mock_get_token_path: MagicMock
    ) -> None:
        """Test handling of permission errors."""
        mock_path = MagicMock()
        mock_path.parent.mkdir.side_effect = PermissionError("Access denied")
        mock_get_token_path.return_value = mock_path

        result = save_auth_token("test_token")

        assert result.is_failure
        assert "Failed to save auth token" in result.error

    @patch("flext_cli.utils.auth.get_token_path")
    def test_save_auth_token_chmod_failure(
        self, mock_get_token_path: MagicMock
    ) -> None:
        """Test handling of chmod failures."""
        with tempfile.TemporaryDirectory() as temp_dir:
            token_path = Path(temp_dir) / "token"
            mock_get_token_path.return_value = token_path

            # Mock chmod to fail
            with patch.object(Path, "chmod", side_effect=OSError("chmod failed")):
                result = save_auth_token("test_token")

                assert result.is_failure
                assert "Failed to save auth token" in result.error


class TestSaveRefreshToken:
    """Test save_refresh_token function."""

    @patch("flext_cli.utils.auth.get_refresh_token_path")
    def test_save_refresh_token_success(
        self, mock_get_refresh_token_path: MagicMock
    ) -> None:
        """Test successful refresh token saving."""
        with tempfile.TemporaryDirectory() as temp_dir:
            token_path = Path(temp_dir) / "refresh_token"
            mock_get_refresh_token_path.return_value = token_path

            result = save_refresh_token("refresh_token_xyz")

            assert result.success
            assert token_path.exists()
            assert token_path.read_text(encoding="utf-8") == "refresh_token_xyz"

    @patch("flext_cli.utils.auth.get_refresh_token_path")
    def test_save_refresh_token_os_error(
        self, mock_get_refresh_token_path: MagicMock
    ) -> None:
        """Test handling of OS errors."""
        mock_path = MagicMock()
        mock_path.write_text.side_effect = OSError("Disk full")
        mock_get_refresh_token_path.return_value = mock_path

        result = save_refresh_token("refresh_token")

        assert result.is_failure
        assert "Failed to save refresh token" in result.error


class TestGetAuthToken:
    """Test get_auth_token function."""

    @patch("flext_cli.utils.auth.get_token_path")
    def test_get_auth_token_exists(self, mock_get_token_path: MagicMock) -> None:
        """Test getting auth token when file exists."""
        with tempfile.TemporaryDirectory() as temp_dir:
            token_path = Path(temp_dir) / "token"
            token_path.write_text("stored_token_123  \n", encoding="utf-8")
            mock_get_token_path.return_value = token_path

            result = get_auth_token()

            assert result == "stored_token_123"

    @patch("flext_cli.utils.auth.get_token_path")
    def test_get_auth_token_missing(self, mock_get_token_path: MagicMock) -> None:
        """Test getting auth token when file doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            token_path = Path(temp_dir) / "nonexistent_token"
            mock_get_token_path.return_value = token_path

            result = get_auth_token()

            assert result is None

    @patch("flext_cli.utils.auth.get_token_path")
    def test_get_auth_token_read_error(self, mock_get_token_path: MagicMock) -> None:
        """Test handling of read errors."""
        mock_path = MagicMock()
        mock_path.exists.return_value = True
        mock_path.read_text.side_effect = OSError("Read failed")
        mock_get_token_path.return_value = mock_path

        result = get_auth_token()

        assert result is None

    @patch("flext_cli.utils.auth.get_token_path")
    def test_get_auth_token_unicode_error(self, mock_get_token_path: MagicMock) -> None:
        """Test handling of unicode decode errors."""
        mock_path = MagicMock()
        mock_path.exists.return_value = True
        mock_path.read_text.side_effect = UnicodeDecodeError("utf-8", b"", 0, 1, "")
        mock_get_token_path.return_value = mock_path

        result = get_auth_token()

        assert result is None


class TestGetRefreshToken:
    """Test get_refresh_token function."""

    @patch("flext_cli.utils.auth.get_refresh_token_path")
    def test_get_refresh_token_exists(
        self, mock_get_refresh_token_path: MagicMock
    ) -> None:
        """Test getting refresh token when file exists."""
        with tempfile.TemporaryDirectory() as temp_dir:
            token_path = Path(temp_dir) / "refresh_token"
            token_path.write_text("refresh_xyz_789\n  ", encoding="utf-8")
            mock_get_refresh_token_path.return_value = token_path

            result = get_refresh_token()

            assert result == "refresh_xyz_789"

    @patch("flext_cli.utils.auth.get_refresh_token_path")
    def test_get_refresh_token_missing(
        self, mock_get_refresh_token_path: MagicMock
    ) -> None:
        """Test getting refresh token when file doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            token_path = Path(temp_dir) / "nonexistent"
            mock_get_refresh_token_path.return_value = token_path

            result = get_refresh_token()

            assert result is None


class TestClearAuthTokens:
    """Test clear_auth_tokens function."""

    @patch("flext_cli.utils.auth.get_token_path")
    @patch("flext_cli.utils.auth.get_refresh_token_path")
    def test_clear_both_tokens(
        self, mock_refresh_path: MagicMock, mock_token_path: MagicMock
    ) -> None:
        """Test clearing both token files when they exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            token_path = Path(temp_dir) / "token"
            refresh_path = Path(temp_dir) / "refresh"

            # Create both files
            token_path.write_text("token")
            refresh_path.write_text("refresh")

            mock_token_path.return_value = token_path
            mock_refresh_path.return_value = refresh_path

            result = clear_auth_tokens()

            assert result.success
            assert not token_path.exists()
            assert not refresh_path.exists()

    @patch("flext_cli.utils.auth.get_token_path")
    @patch("flext_cli.utils.auth.get_refresh_token_path")
    def test_clear_partial_tokens(
        self, mock_refresh_path: MagicMock, mock_token_path: MagicMock
    ) -> None:
        """Test clearing when only one token exists."""
        with tempfile.TemporaryDirectory() as temp_dir:
            token_path = Path(temp_dir) / "token"
            refresh_path = Path(temp_dir) / "refresh"

            # Only create token file
            token_path.write_text("token")

            mock_token_path.return_value = token_path
            mock_refresh_path.return_value = refresh_path

            result = clear_auth_tokens()

            assert result.success
            assert not token_path.exists()
            assert not refresh_path.exists()  # Was never created

    @patch("flext_cli.utils.auth.get_token_path")
    @patch("flext_cli.utils.auth.get_refresh_token_path")
    def test_clear_tokens_permission_error(
        self, mock_refresh_path: MagicMock, mock_token_path: MagicMock
    ) -> None:
        """Test handling of permission errors during clear."""
        mock_token_path_obj = MagicMock()
        mock_token_path_obj.exists.return_value = True
        mock_token_path_obj.unlink.side_effect = PermissionError("Access denied")
        mock_token_path.return_value = mock_token_path_obj

        mock_refresh_path_obj = MagicMock()
        mock_refresh_path_obj.exists.return_value = False
        mock_refresh_path.return_value = mock_refresh_path_obj

        result = clear_auth_tokens()

        assert result.is_failure
        assert "Failed to clear auth tokens" in result.error


class TestIsAuthenticated:
    """Test is_authenticated function."""

    @patch("flext_cli.utils.auth.get_auth_token")
    def test_is_authenticated_true(self, mock_get_auth_token: MagicMock) -> None:
        """Test authentication check when token exists."""
        mock_get_auth_token.return_value = "valid_token"

        result = is_authenticated()

        assert result is True

    @patch("flext_cli.utils.auth.get_auth_token")
    def test_is_authenticated_false(self, mock_get_auth_token: MagicMock) -> None:
        """Test authentication check when no token."""
        mock_get_auth_token.return_value = None

        result = is_authenticated()

        assert result is False

    @patch("flext_cli.utils.auth.get_auth_token")
    def test_is_authenticated_empty_token(self, mock_get_auth_token: MagicMock) -> None:
        """Test authentication check with empty token."""
        mock_get_auth_token.return_value = ""

        result = is_authenticated()

        # Empty string is still "authenticated" (token file exists)
        assert result is True


class TestShouldAutoRefresh:
    """Test should_auto_refresh function."""

    @patch("flext_cli.utils.auth.get_config")
    @patch("flext_cli.utils.auth.get_refresh_token")
    def test_direct_auto_refresh_true(
        self, mock_get_refresh_token: MagicMock, mock_get_config: MagicMock
    ) -> None:
        """Test auto refresh when config has direct auto_refresh=True."""
        mock_config = MagicMock()
        mock_config.auto_refresh = True
        mock_get_config.return_value = mock_config
        mock_get_refresh_token.return_value = "refresh_token"

        result = should_auto_refresh()

        assert result is True

    @patch("flext_cli.utils.auth.get_config")
    @patch("flext_cli.utils.auth.get_refresh_token")
    def test_direct_auto_refresh_false(
        self, mock_get_refresh_token: MagicMock, mock_get_config: MagicMock
    ) -> None:
        """Test auto refresh when config has direct auto_refresh=False."""
        mock_config = MagicMock()
        mock_config.auto_refresh = False
        mock_get_config.return_value = mock_config
        mock_get_refresh_token.return_value = "refresh_token"

        result = should_auto_refresh()

        assert result is False

    @patch("flext_cli.utils.auth.get_config")
    @patch("flext_cli.utils.auth.get_refresh_token")
    def test_auth_config_auto_refresh(
        self, mock_get_refresh_token: MagicMock, mock_get_config: MagicMock
    ) -> None:
        """Test auto refresh from auth config when no direct config."""
        mock_config = MagicMock()
        del mock_config.auto_refresh  # Simulate missing attribute
        mock_auth_config = MagicMock()
        mock_auth_config.auto_refresh = True
        mock_config.auth = mock_auth_config
        mock_get_config.return_value = mock_config
        mock_get_refresh_token.return_value = "refresh_token"

        result = should_auto_refresh()

        assert result is True

    @patch("flext_cli.utils.auth.get_config")
    @patch("flext_cli.utils.auth.get_refresh_token")
    def test_no_refresh_token(
        self, mock_get_refresh_token: MagicMock, mock_get_config: MagicMock
    ) -> None:
        """Test auto refresh when no refresh token available."""
        mock_config = MagicMock()
        mock_config.auto_refresh = True
        mock_get_config.return_value = mock_config
        mock_get_refresh_token.return_value = None

        result = should_auto_refresh()

        assert result is False

    @patch("flext_cli.utils.auth.get_config")
    @patch("flext_cli.utils.auth.get_refresh_token")
    def test_no_auth_config(
        self, mock_get_refresh_token: MagicMock, mock_get_config: MagicMock
    ) -> None:
        """Test auto refresh when no auth config available."""
        mock_config = MagicMock()
        del mock_config.auto_refresh
        mock_config.auth = None
        mock_get_config.return_value = mock_config
        mock_get_refresh_token.return_value = "refresh_token"

        result = should_auto_refresh()

        assert result is False
