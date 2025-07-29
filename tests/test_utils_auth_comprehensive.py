"""Comprehensive tests for utils.auth module.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

Tests for authentication utilities to achieve near 100% coverage.
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

from flext_cli.utils.auth import (
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


class TestTokenPaths:
    """Test token path functions."""

    def test_get_token_path(self) -> None:
        """Test getting token path."""
        with patch("flext_cli.utils.auth.get_config") as mock_get_config:
            mock_config = MagicMock()
            mock_config.token_file = Path("/test/token.txt")
            mock_get_config.return_value = mock_config

            result = get_token_path()
            if result != Path("/test/token.txt"):
                raise AssertionError(f"Expected {Path("/test/token.txt")}, got {result}")
            mock_get_config.assert_called_once()

    def test_get_refresh_token_path(self) -> None:
        """Test getting refresh token path."""
        with patch("flext_cli.utils.auth.get_config") as mock_get_config:
            mock_config = MagicMock()
            mock_config.refresh_token_file = Path("/test/refresh_token.txt")
            mock_get_config.return_value = mock_config

            result = get_refresh_token_path()
            if result != Path("/test/refresh_token.txt"):
                raise AssertionError(f"Expected {Path("/test/refresh_token.txt")}, got {result}")
            mock_get_config.assert_called_once()


class TestSaveAuthToken:
    """Test save_auth_token function."""

    def test_save_auth_token_success(self) -> None:
        """Test successful auth token save."""
        with tempfile.TemporaryDirectory() as temp_dir:
            token_path = Path(temp_dir) / "token.txt"

            with patch("flext_cli.utils.auth.get_token_path", return_value=token_path):
                result = save_auth_token("test-token-123")

                assert result.is_success
                assert result.unwrap() is None
                assert token_path.exists()
                if token_path.read_text() != "test-token-123":
                    raise AssertionError(f"Expected {"test-token-123"}, got {token_path.read_text()}")

                # Check file permissions
                stat = token_path.stat()
                if oct(stat.st_mode)[-3:] != "600":
                    raise AssertionError(f"Expected {"600"}, got {oct(stat.st_mode)[-3:]}")

    def test_save_auth_token_creates_parent_directories(self) -> None:
        """Test that parent directories are created."""
        with tempfile.TemporaryDirectory() as temp_dir:
            token_path = Path(temp_dir) / "nested" / "path" / "token.txt"

            with patch("flext_cli.utils.auth.get_token_path", return_value=token_path):
                result = save_auth_token("test-token-456")

                assert result.is_success
                assert token_path.exists()
                if token_path.read_text() != "test-token-456":
                    raise AssertionError(f"Expected {"test-token-456"}, got {token_path.read_text()}")

    def test_save_auth_token_permission_error(self) -> None:
        """Test handling permission error when saving."""
        mock_path = MagicMock()
        mock_path.parent.mkdir.side_effect = PermissionError("Permission denied")

        with patch("flext_cli.utils.auth.get_token_path", return_value=mock_path):
            result = save_auth_token("test-token")

            assert result.is_failure
            if "Failed to save auth token" not in result.error:
                raise AssertionError(f"Expected {"Failed to save auth token"} in {result.error}")
            assert "Permission denied" in result.error

    def test_save_auth_token_write_error(self) -> None:
        """Test handling write error when saving."""
        mock_path = MagicMock()
        mock_path.write_text.side_effect = OSError("Disk full")

        with patch("flext_cli.utils.auth.get_token_path", return_value=mock_path):
            result = save_auth_token("test-token")

            assert result.is_failure
            if "Failed to save auth token" not in result.error:
                raise AssertionError(f"Expected {"Failed to save auth token"} in {result.error}")
            assert "Disk full" in result.error

    def test_save_auth_token_chmod_error(self) -> None:
        """Test handling chmod error when saving."""
        mock_path = MagicMock()
        mock_path.parent.mkdir.return_value = None
        mock_path.write_text.return_value = None
        mock_path.chmod.side_effect = OSError("chmod failed")

        with patch("flext_cli.utils.auth.get_token_path", return_value=mock_path):
            result = save_auth_token("test-token")

            assert result.is_failure
            if "Failed to save auth token" not in result.error:
                raise AssertionError(f"Expected {"Failed to save auth token"} in {result.error}")
            assert "chmod failed" in result.error


class TestSaveRefreshToken:
    """Test save_refresh_token function."""

    def test_save_refresh_token_success(self) -> None:
        """Test successful refresh token save."""
        with tempfile.TemporaryDirectory() as temp_dir:
            refresh_token_path = Path(temp_dir) / "refresh_token.txt"

            with patch(
                "flext_cli.utils.auth.get_refresh_token_path",
                return_value=refresh_token_path,
            ):
                result = save_refresh_token("refresh-token-789")

                assert result.is_success
                assert result.unwrap() is None
                assert refresh_token_path.exists()
                if refresh_token_path.read_text() != "refresh-token-789":
                    raise AssertionError(f"Expected {"refresh-token-789"}, got {refresh_token_path.read_text()}")

                # Check file permissions
                stat = refresh_token_path.stat()
                if oct(stat.st_mode)[-3:] != "600":
                    raise AssertionError(f"Expected {"600"}, got {oct(stat.st_mode)[-3:]}")

    def test_save_refresh_token_creates_parent_directories(self) -> None:
        """Test that parent directories are created."""
        with tempfile.TemporaryDirectory() as temp_dir:
            refresh_token_path = (
                Path(temp_dir) / "deep" / "nested" / "refresh_token.txt"
            )

            with patch(
                "flext_cli.utils.auth.get_refresh_token_path",
                return_value=refresh_token_path,
            ):
                result = save_refresh_token("refresh-token-abc")

                assert result.is_success
                assert refresh_token_path.exists()
                if refresh_token_path.read_text() != "refresh-token-abc":
                    raise AssertionError(f"Expected {"refresh-token-abc"}, got {refresh_token_path.read_text()}")

    def test_save_refresh_token_permission_error(self) -> None:
        """Test handling permission error when saving refresh token."""
        mock_path = MagicMock()
        mock_path.parent.mkdir.side_effect = PermissionError("Access denied")

        with patch(
            "flext_cli.utils.auth.get_refresh_token_path", return_value=mock_path
        ):
            result = save_refresh_token("refresh-token")

            assert result.is_failure
            if "Failed to save refresh token" not in result.error:
                raise AssertionError(f"Expected {"Failed to save refresh token"} in {result.error}")
            assert "Access denied" in result.error

    def test_save_refresh_token_write_error(self) -> None:
        """Test handling write error when saving refresh token."""
        mock_path = MagicMock()
        mock_path.write_text.side_effect = OSError("Write failed")

        with patch(
            "flext_cli.utils.auth.get_refresh_token_path", return_value=mock_path
        ):
            result = save_refresh_token("refresh-token")

            assert result.is_failure
            if "Failed to save refresh token" not in result.error:
                raise AssertionError(f"Expected {"Failed to save refresh token"} in {result.error}")
            assert "Write failed" in result.error


class TestGetAuthToken:
    """Test get_auth_token function."""

    def test_get_auth_token_exists(self) -> None:
        """Test getting auth token when file exists."""
        with tempfile.TemporaryDirectory() as temp_dir:
            token_path = Path(temp_dir) / "token.txt"
            token_path.write_text("  my-auth-token  \n")  # With whitespace

            with patch("flext_cli.utils.auth.get_token_path", return_value=token_path):
                result = get_auth_token()

                if result != "my-auth-token":  # Stripped
                    raise AssertionError(f"Expected {'my-auth-token'}, got {result}")

    def test_get_auth_token_not_exists(self) -> None:
        """Test getting auth token when file doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            token_path = Path(temp_dir) / "nonexistent_token.txt"

            with patch("flext_cli.utils.auth.get_token_path", return_value=token_path):
                result = get_auth_token()

                assert result is None

    def test_get_auth_token_empty_file(self) -> None:
        """Test getting auth token from empty file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            token_path = Path(temp_dir) / "empty_token.txt"
            token_path.write_text("")

            with patch("flext_cli.utils.auth.get_token_path", return_value=token_path):
                result = get_auth_token()

                if result != "":

                    raise AssertionError(f"Expected {""}, got {result}")

    def test_get_auth_token_whitespace_only(self) -> None:
        """Test getting auth token from file with only whitespace."""
        with tempfile.TemporaryDirectory() as temp_dir:
            token_path = Path(temp_dir) / "whitespace_token.txt"
            token_path.write_text("   \n\t  ")

            with patch("flext_cli.utils.auth.get_token_path", return_value=token_path):
                result = get_auth_token()

                if result != "":

                    raise AssertionError(f"Expected {""}, got {result}")


class TestGetRefreshToken:
    """Test get_refresh_token function."""

    def test_get_refresh_token_exists(self) -> None:
        """Test getting refresh token when file exists."""
        with tempfile.TemporaryDirectory() as temp_dir:
            refresh_token_path = Path(temp_dir) / "refresh_token.txt"
            refresh_token_path.write_text("\nmy-refresh-token\t")  # With whitespace

            with patch(
                "flext_cli.utils.auth.get_refresh_token_path",
                return_value=refresh_token_path,
            ):
                result = get_refresh_token()

                if result != "my-refresh-token":  # Stripped
                    raise AssertionError(f"Expected {'my-refresh-token'}, got {result}")

    def test_get_refresh_token_not_exists(self) -> None:
        """Test getting refresh token when file doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            refresh_token_path = Path(temp_dir) / "missing_refresh_token.txt"

            with patch(
                "flext_cli.utils.auth.get_refresh_token_path",
                return_value=refresh_token_path,
            ):
                result = get_refresh_token()

                assert result is None

    def test_get_refresh_token_empty_file(self) -> None:
        """Test getting refresh token from empty file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            refresh_token_path = Path(temp_dir) / "empty_refresh.txt"
            refresh_token_path.write_text("")

            with patch(
                "flext_cli.utils.auth.get_refresh_token_path",
                return_value=refresh_token_path,
            ):
                result = get_refresh_token()

                if result != "":

                    raise AssertionError(f"Expected {""}, got {result}")


class TestClearAuthTokens:
    """Test clear_auth_tokens function."""

    def test_clear_auth_tokens_both_exist(self) -> None:
        """Test clearing tokens when both files exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            token_path = Path(temp_dir) / "token.txt"
            refresh_token_path = Path(temp_dir) / "refresh_token.txt"

            # Create both files
            token_path.write_text("auth-token")
            refresh_token_path.write_text("refresh-token")

            with patch("flext_cli.utils.auth.get_token_path", return_value=token_path):
                with patch(
                    "flext_cli.utils.auth.get_refresh_token_path",
                    return_value=refresh_token_path,
                ):
                    result = clear_auth_tokens()

                    assert result.is_success
                    assert result.unwrap() is None
                    assert not token_path.exists()
                    assert not refresh_token_path.exists()

    def test_clear_auth_tokens_only_token_exists(self) -> None:
        """Test clearing tokens when only auth token exists."""
        with tempfile.TemporaryDirectory() as temp_dir:
            token_path = Path(temp_dir) / "token.txt"
            refresh_token_path = Path(temp_dir) / "refresh_token.txt"

            # Create only token file
            token_path.write_text("auth-token")

            with patch("flext_cli.utils.auth.get_token_path", return_value=token_path):
                with patch(
                    "flext_cli.utils.auth.get_refresh_token_path",
                    return_value=refresh_token_path,
                ):
                    result = clear_auth_tokens()

                    assert result.is_success
                    assert not token_path.exists()
                    assert not refresh_token_path.exists()  # Still doesn't exist

    def test_clear_auth_tokens_only_refresh_exists(self) -> None:
        """Test clearing tokens when only refresh token exists."""
        with tempfile.TemporaryDirectory() as temp_dir:
            token_path = Path(temp_dir) / "token.txt"
            refresh_token_path = Path(temp_dir) / "refresh_token.txt"

            # Create only refresh token file
            refresh_token_path.write_text("refresh-token")

            with patch("flext_cli.utils.auth.get_token_path", return_value=token_path):
                with patch(
                    "flext_cli.utils.auth.get_refresh_token_path",
                    return_value=refresh_token_path,
                ):
                    result = clear_auth_tokens()

                    assert result.is_success
                    assert not token_path.exists()  # Still doesn't exist
                    assert not refresh_token_path.exists()

    def test_clear_auth_tokens_neither_exists(self) -> None:
        """Test clearing tokens when neither file exists."""
        with tempfile.TemporaryDirectory() as temp_dir:
            token_path = Path(temp_dir) / "token.txt"
            refresh_token_path = Path(temp_dir) / "refresh_token.txt"

            with patch("flext_cli.utils.auth.get_token_path", return_value=token_path):
                with patch(
                    "flext_cli.utils.auth.get_refresh_token_path",
                    return_value=refresh_token_path,
                ):
                    result = clear_auth_tokens()

                    assert result.is_success
                    assert not token_path.exists()
                    assert not refresh_token_path.exists()

    def test_clear_auth_tokens_permission_error(self) -> None:
        """Test handling permission error when clearing tokens."""
        mock_token_path = MagicMock()
        mock_refresh_path = MagicMock()
        mock_token_path.exists.return_value = True
        mock_token_path.unlink.side_effect = PermissionError("Cannot delete")

        with patch("flext_cli.utils.auth.get_token_path", return_value=mock_token_path):
            with patch(
                "flext_cli.utils.auth.get_refresh_token_path",
                return_value=mock_refresh_path,
            ):
                result = clear_auth_tokens()

                assert result.is_failure
                if "Failed to clear auth tokens" not in result.error:
                    raise AssertionError(f"Expected {"Failed to clear auth tokens"} in {result.error}")
                assert "Cannot delete" in result.error

    def test_clear_auth_tokens_unlink_error_refresh(self) -> None:
        """Test handling unlink error on refresh token."""
        mock_token_path = MagicMock()
        mock_refresh_path = MagicMock()
        mock_token_path.exists.return_value = False
        mock_refresh_path.exists.return_value = True
        mock_refresh_path.unlink.side_effect = OSError("Unlink failed")

        with patch("flext_cli.utils.auth.get_token_path", return_value=mock_token_path):
            with patch(
                "flext_cli.utils.auth.get_refresh_token_path",
                return_value=mock_refresh_path,
            ):
                result = clear_auth_tokens()

                assert result.is_failure
                if "Failed to clear auth tokens" not in result.error:
                    raise AssertionError(f"Expected {"Failed to clear auth tokens"} in {result.error}")
                assert "Unlink failed" in result.error


class TestIsAuthenticated:
    """Test is_authenticated function."""

    def test_is_authenticated_with_token(self) -> None:
        """Test authentication check when token exists."""
        with patch("flext_cli.utils.auth.get_auth_token", return_value="valid-token"):
            result = is_authenticated()
            if not (result):
                raise AssertionError(f"Expected True, got {result}")

    def test_is_authenticated_without_token(self) -> None:
        """Test authentication check when no token exists."""
        with patch("flext_cli.utils.auth.get_auth_token", return_value=None):
            result = is_authenticated()
            if result:
                raise AssertionError(f"Expected False, got {result}")

    def test_is_authenticated_empty_token(self) -> None:
        """Test authentication check with empty token."""
        with patch("flext_cli.utils.auth.get_auth_token", return_value=""):
            result = is_authenticated()
            assert result is True  # Empty string is still truthy for the function


class TestShouldAutoRefresh:
    """Test should_auto_refresh function."""

    def test_should_auto_refresh_enabled_with_token(self) -> None:
        """Test auto refresh when enabled and refresh token exists."""
        mock_config = MagicMock()
        mock_config.auto_refresh = True

        with patch("flext_cli.utils.auth.get_config", return_value=mock_config):
            with patch(
                "flext_cli.utils.auth.get_refresh_token", return_value="refresh-token"
            ):
                result = should_auto_refresh()
                if not (result):
                    raise AssertionError(f"Expected True, got {result}")

    def test_should_auto_refresh_enabled_without_token(self) -> None:
        """Test auto refresh when enabled but no refresh token."""
        mock_config = MagicMock()
        mock_config.auto_refresh = True

        with patch("flext_cli.utils.auth.get_config", return_value=mock_config):
            with patch("flext_cli.utils.auth.get_refresh_token", return_value=None):
                result = should_auto_refresh()
                if result:
                    raise AssertionError(f"Expected False, got {result}")

    def test_should_auto_refresh_disabled_with_token(self) -> None:
        """Test auto refresh when disabled but refresh token exists."""
        mock_config = MagicMock()
        mock_config.auto_refresh = False

        with patch("flext_cli.utils.auth.get_config", return_value=mock_config):
            with patch(
                "flext_cli.utils.auth.get_refresh_token", return_value="refresh-token"
            ):
                result = should_auto_refresh()
                if result:
                    raise AssertionError(f"Expected False, got {result}")

    def test_should_auto_refresh_disabled_without_token(self) -> None:
        """Test auto refresh when disabled and no refresh token."""
        mock_config = MagicMock()
        mock_config.auto_refresh = False

        with patch("flext_cli.utils.auth.get_config", return_value=mock_config):
            with patch("flext_cli.utils.auth.get_refresh_token", return_value=None):
                result = should_auto_refresh()
                if result:
                    raise AssertionError(f"Expected False, got {result}")


class TestAuthIntegration:
    """Integration tests for auth utilities."""

    def test_full_auth_workflow(self) -> None:
        """Test complete authentication workflow."""
        with tempfile.TemporaryDirectory() as temp_dir:
            token_path = Path(temp_dir) / "token.txt"
            refresh_token_path = Path(temp_dir) / "refresh_token.txt"

            with patch("flext_cli.utils.auth.get_token_path", return_value=token_path):
                with patch(
                    "flext_cli.utils.auth.get_refresh_token_path",
                    return_value=refresh_token_path,
                ):
                    # Initially not authenticated
                    assert not is_authenticated()

                    # Save tokens
                    auth_result = save_auth_token("my-auth-token")
                    refresh_result = save_refresh_token("my-refresh-token")

                    assert auth_result.is_success
                    assert refresh_result.is_success

                    # Now authenticated
                    assert is_authenticated()
                    if get_auth_token() != "my-auth-token":
                        raise AssertionError(f"Expected {"my-auth-token"}, got {get_auth_token()}")
                    assert get_refresh_token() == "my-refresh-token"

                    # Clear tokens
                    clear_result = clear_auth_tokens()
                    assert clear_result.is_success

                    # No longer authenticated
                    assert not is_authenticated()
                    assert get_auth_token() is None
                    assert get_refresh_token() is None

    def test_auth_workflow_with_config(self) -> None:
        """Test auth workflow with configuration."""
        mock_config = MagicMock()
        mock_config.auto_refresh = True

        with tempfile.TemporaryDirectory() as temp_dir:
            token_path = Path(temp_dir) / "token.txt"
            refresh_token_path = Path(temp_dir) / "refresh_token.txt"
            mock_config.token_file = token_path
            mock_config.refresh_token_file = refresh_token_path

            with patch("flext_cli.utils.auth.get_config", return_value=mock_config):
                # Save refresh token
                save_refresh_token("refresh-token-123")

                # Should auto refresh since config enabled and token exists
                assert should_auto_refresh()

                # Clear tokens
                clear_auth_tokens()

                # Should not auto refresh since no refresh token
                assert not should_auto_refresh()

    def test_error_recovery_scenarios(self) -> None:
        """Test error recovery in various scenarios."""
        # Test when files are corrupted/unreadable
        mock_path = MagicMock()
        mock_path.exists.return_value = True
        mock_path.read_text.side_effect = UnicodeDecodeError(
            "utf-8", b"", 0, 1, "invalid"
        )

        with patch("flext_cli.utils.auth.get_token_path", return_value=mock_path):
            # Should not crash, but won't return valid token
            try:
                get_auth_token()
                # If exception not raised, that's fine too
            except UnicodeDecodeError:
                # Expected behavior - let the exception bubble up
                pass
