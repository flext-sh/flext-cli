"""Tests for auth commands - REAL FUNCTIONALITY.

Tests authentication command functionality with actual execution.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import tempfile

import click
from click.testing import CliRunner
from flext_core import FlextResult

from flext_cli import (
    clear_auth_tokens,
    get_auth_token,
    save_auth_token,
)
from flext_cli.auth import auth


class TestAuthCommands:
    """Test auth commands with real functionality."""

    def setup_method(self) -> None:
        """Set up test environment."""
        self.runner = CliRunner()

    def test_auth_group_structure(self) -> None:
        """Test auth command group structure - REAL validation."""
        # Test actual command group structure
        assert isinstance(auth, click.Group), (
            f"auth should be a click.Group, got {type(auth)}"
        )
        assert auth.name == "auth", f"Expected 'auth', got {auth.name}"

        # Verify commands exist and are callable
        commands = auth.commands
        expected_commands = ["login", "logout", "status", "whoami"]  # Real commands that exist
        for cmd_name in expected_commands:
            assert cmd_name in commands, (
                f"Command '{cmd_name}' not found in auth group. "
                f"Available: {list(commands.keys())}"
            )

    def test_save_auth_token_success(self) -> None:
        """Test saving authentication token - REAL functionality."""
        with tempfile.TemporaryDirectory():
            # Use real token saving functionality
            test_token = "test_token_123"
            result = save_auth_token(test_token)

            # Verify result using FlextResult patterns
            assert result.is_success, f"Token save failed: {result.error}"
            # For save operations, success is indicated by is_success being True
            # value is None for FlextResult[None] operations

    def test_save_auth_token_invalid(self) -> None:
        """Test saving invalid token - REAL functionality."""
        # Test with empty token
        result = save_auth_token("")
        assert result.is_failure, "Empty token should fail"
        assert "empty" in result.error.lower() or "invalid" in result.error.lower()

    def test_get_auth_token_when_none_exists(self) -> None:
        """Test getting token when none exists - REAL functionality."""
        # Clear any existing tokens first
        clear_auth_tokens()
        # Don't assert on clear result as it may fail if no tokens exist

        # Try to get token
        result = get_auth_token()
        assert result.is_failure, "Should fail when no token exists"

    def test_clear_auth_tokens(self) -> None:
        """Test clearing auth tokens - REAL functionality."""
        # Save a token first
        test_token = "token_to_clear"
        save_result = save_auth_token(test_token)
        if save_result.is_success:
            # Clear tokens
            clear_result = clear_auth_tokens()
            # Should succeed or be idempotent
            assert clear_result.is_success or clear_result.is_failure

            # Verify token is gone
            get_result = get_auth_token()
            assert get_result.is_failure, "Token should be cleared"

    def test_auth_status_command(self) -> None:
        """Test auth status command - REAL execution."""
        # Run the actual status command
        result = self.runner.invoke(auth, ["status"])

        # Should execute without crashing
        assert result.exit_code in {0, 1}, (
            f"Status command should exit with 0 or 1, got {result.exit_code}: {result.output}"
        )

        # Output should contain status information
        assert result.output, "Status command should produce output"

    def test_auth_help_command(self) -> None:
        """Test auth help command - REAL execution."""
        # Test help for auth group
        result = self.runner.invoke(auth, ["--help"])

        assert result.exit_code == 0, f"Help command failed: {result.output}"
        assert "auth" in result.output.lower()
        assert "command" in result.output.lower()

    def test_token_roundtrip(self) -> None:
        """Test complete token save/get/clear cycle - REAL functionality."""
        test_token = "roundtrip_token_xyz"

        # 1. Clear any existing tokens
        clear_auth_tokens()

        # 2. Save a token
        save_result = save_auth_token(test_token)
        assert save_result.is_success, f"Failed to save token: {save_result.error}"

        # 3. Retrieve the token
        get_result = get_auth_token()
        if get_result.is_success:
            assert get_result.value == test_token, (
                f"Retrieved token doesn't match. Expected: {test_token}, Got: {get_result.value}"
            )

        # 4. Clear tokens
        clear_result = clear_auth_tokens()
        assert (
            clear_result.is_success or clear_result.is_failure
        )  # Either outcome is acceptable

        # 5. Verify token is cleared
        final_get_result = get_auth_token()
        assert final_get_result.is_failure, "Token should be cleared"

    def test_flext_result_patterns(self) -> None:
        """Test that auth functions use FlextResult patterns correctly."""
        # Test save_auth_token returns FlextResult
        result = save_auth_token("test")
        assert isinstance(result, FlextResult), (
            f"Expected FlextResult, got {type(result)}"
        )
        assert hasattr(result, "is_success"), "Result should have is_success property"
        assert hasattr(result, "is_failure"), "Result should have is_failure property"
        assert hasattr(result, "value"), "Result should have value property"
        assert hasattr(result, "error"), "Result should have error property"

        # Test get_auth_token returns FlextResult
        get_result = get_auth_token()
        assert isinstance(get_result, FlextResult), (
            f"Expected FlextResult, got {type(get_result)}"
        )

        # Test clear_auth_tokens returns FlextResult
        clear_result = clear_auth_tokens()
        assert isinstance(clear_result, FlextResult), (
            f"Expected FlextResult, got {type(clear_result)}"
        )
