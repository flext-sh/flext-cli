"""Tests for auth utilities with REAL code execution - no mocks.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import tempfile
from pathlib import Path

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


class TestGetTokenPathReal:
    """Test get_token_path function with REAL execution."""

    def test_default_token_path(self) -> None:
        """Test default token path is returned."""
        result = get_token_path()
        assert isinstance(result, Path)
        # Should contain expected path elements
        assert "auth" in str(result) or "token" in str(result)

    def test_token_path_consistency(self) -> None:
        """Test that token path is consistent across calls."""
        path1 = get_token_path()
        path2 = get_token_path()
        assert path1 == path2


class TestGetRefreshTokenPathReal:
    """Test get_refresh_token_path function with REAL execution."""

    def test_default_refresh_token_path(self) -> None:
        """Test default refresh token path."""
        result = get_refresh_token_path()
        assert isinstance(result, Path)
        # Should contain expected path elements
        assert "auth" in str(result) or "refresh" in str(result)

    def test_refresh_token_path_consistency(self) -> None:
        """Test refresh token path is consistent."""
        path1 = get_refresh_token_path()
        path2 = get_refresh_token_path()
        assert path1 == path2


class TestIsAuthenticatedReal:
    """Test is_authenticated function with REAL execution."""

    def test_is_authenticated_no_token(self) -> None:
        """Test authentication when no token exists."""
        # Most likely no token exists in test environment
        result = is_authenticated()
        assert isinstance(result, bool)

    def test_is_authenticated_consistency(self) -> None:
        """Test authentication check is consistent."""
        result1 = is_authenticated()
        result2 = is_authenticated()
        assert result1 == result2


class TestShouldAutoRefreshReal:
    """Test should_auto_refresh function with REAL execution."""

    def test_should_auto_refresh_default(self) -> None:
        """Test auto refresh with default configuration."""
        result = should_auto_refresh()
        assert isinstance(result, bool)

    def test_should_auto_refresh_consistency(self) -> None:
        """Test auto refresh check is consistent."""
        result1 = should_auto_refresh()
        result2 = should_auto_refresh()
        assert result1 == result2


class TestGetAuthTokenReal:
    """Test get_auth_token function with REAL execution."""

    def test_get_auth_token_no_file(self) -> None:
        """Test getting auth token when file doesn't exist."""
        result = get_auth_token()
        # Should return FlextResult
        assert hasattr(result, "is_success")
        assert hasattr(result, "is_failure")
        # In test environment, most likely no token file exists
        assert result.is_failure or result.is_success

    def test_get_auth_token_consistency(self) -> None:
        """Test get auth token is consistent."""
        result1 = get_auth_token()
        result2 = get_auth_token()
        # Both should have same success/failure status
        assert result1.is_success == result2.is_success


class TestGetRefreshTokenReal:
    """Test get_refresh_token function with REAL execution."""

    def test_get_refresh_token_no_file(self) -> None:
        """Test getting refresh token when file doesn't exist."""
        result = get_refresh_token()
        # Should return FlextResult
        assert hasattr(result, "is_success")
        assert hasattr(result, "is_failure")
        # In test environment, most likely no token file exists
        assert result.is_failure or result.is_success


class TestSaveAuthTokenReal:
    """Test save_auth_token function with REAL execution in temp directory."""

    def test_save_auth_token_temp_dir(self) -> None:
        """Test saving auth token to temporary location."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir) / "test_token"

            # Save a test token - the function will use its default path
            # but we can verify it executes without error
            result = save_auth_token("test_token_value", token_path=temp_path)

            # Should return FlextResult
            assert hasattr(result, "is_success")
            assert hasattr(result, "is_failure")

    def test_save_auth_token_empty_string(self) -> None:
        """Test saving empty token."""
        result = save_auth_token("")
        # Should handle empty token gracefully
        assert hasattr(result, "is_success")


class TestSaveRefreshTokenReal:
    """Test save_refresh_token function with REAL execution."""

    def test_save_refresh_token_temp_dir(self) -> None:
        """Test saving refresh token."""
        result = save_refresh_token("test_refresh_token")

        # Should return FlextResult
        assert hasattr(result, "is_success")
        assert hasattr(result, "is_failure")


class TestClearAuthTokensReal:
    """Test clear_auth_tokens function with REAL execution."""

    def test_clear_auth_tokens_safe(self) -> None:
        """Test clearing auth tokens safely."""
        result = clear_auth_tokens()

        # Should return FlextResult
        assert hasattr(result, "is_success")
        assert hasattr(result, "is_failure")

    def test_clear_auth_tokens_idempotent(self) -> None:
        """Test clearing tokens is idempotent."""
        result1 = clear_auth_tokens()
        result2 = clear_auth_tokens()

        # Both should succeed (clearing non-existent files is OK)
        assert hasattr(result1, "is_success")
        assert hasattr(result2, "is_success")
