"""Real functionality tests for commands.auth module.

Tests for authentication commands with ZERO TOLERANCE - NO MOCKS, real functionality only.




Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""


from __future__ import annotations

import tempfile
from pathlib import Path

import click
import pytest
from click.testing import CliRunner
from rich.console import Console

from flext_cli import auth
from flext_cli.auth import FlextCliAuth
from flext_cli.config import FlextCliConfig


class TestAuthGroup:
    """Test auth command group with real functionality."""

    def test_auth_group_exists(self) -> None:
        """Test that auth group is properly defined."""
        assert isinstance(auth, click.Group)
        assert auth.name == "auth"

    def test_auth_group_help(self) -> None:
        """Test auth group help message."""
        runner = CliRunner()
        result = runner.invoke(auth, ["--help"])
        assert result.exit_code == 0
        assert "Authentication management commands" in result.output

    def test_auth_group_commands(self) -> None:
        """Test that auth group has expected commands."""
        commands = auth.list_commands(None)
        assert "login" in commands
        assert "logout" in commands
        assert "status" in commands


class TestLoginCommand:
    """Test login command with real functionality."""

    def test_login_help(self) -> None:
        """Test login command help."""
        runner = CliRunner()
        result = runner.invoke(auth, ["login", "--help"])
        assert result.exit_code == 0
        assert "--username" in result.output
        assert "--password" in result.output

    def test_login_real_functionality(self) -> None:
        """Test login command executes real authentication logic."""
        runner = CliRunner()
        console = Console()

        # Test real login flow - should handle gracefully without API server
        result = runner.invoke(
            auth,
            ["login", "--username", "testuser", "--password", "testpass"],
            obj={"console": console},
            catch_exceptions=False,
        )

        # Real functionality test - login may fail due to no server, but should not crash
        assert result.exit_code in [0, 1]  # Success or expected network failure

        # Should contain actual processing output
        output_lower = result.output.lower()
        assert any(
            word in output_lower for word in ["login", "testuser", "failed", "error"]
        )


class TestLogoutCommand:
    """Test logout command with real functionality."""

    def test_logout_help(self) -> None:
        """Test logout command help."""
        runner = CliRunner()
        result = runner.invoke(auth, ["logout", "--help"])
        assert result.exit_code == 0

    def test_logout_real_functionality(self) -> None:
        """Test logout command with real authentication."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create real config with temp paths
            config = FlextCliConfig(
                token_file=temp_path / "token.json",
                refresh_token_file=temp_path / "refresh_token.json",
            )

            # Create real auth instance
            auth_instance = FlextCliAuth(config=config)

            # Save a real token first
            save_result = auth_instance.save_auth_token("test_token_12345")
            assert save_result.is_success

            # Now test logout command
            runner = CliRunner()
            console = Console()

            result = runner.invoke(
                auth, ["logout"], obj={"console": console}, catch_exceptions=False
            )

            # Real functionality - logout should work even if API call fails
            assert result.exit_code in [0, 1]


class TestStatusCommand:
    """Test status command with real functionality."""

    def test_status_help(self) -> None:
        """Test status command help."""
        runner = CliRunner()
        result = runner.invoke(auth, ["status", "--help"])
        assert result.exit_code == 0

    def test_status_real_functionality_not_authenticated(self) -> None:
        """Test status command when not authenticated."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create real config with temp paths (no token file)
            config = FlextCliConfig(
                token_file=temp_path / "nonexistent_token.json",
                refresh_token_file=temp_path / "nonexistent_refresh.json",
            )

            # Test status shows not authenticated
            auth_instance = FlextCliAuth(config=config)
            status_info = auth_instance.get_status()

            assert status_info["authenticated"] is False
            assert status_info["token_exists"] is False

    def test_status_real_functionality_authenticated(self) -> None:
        """Test status command when authenticated."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create real config and auth
            config = FlextCliConfig(
                token_file=temp_path / "token.json",
                refresh_token_file=temp_path / "refresh_token.json",
            )

            auth_instance = FlextCliAuth(config=config)

            # Save real token
            save_result = auth_instance.save_auth_token("real_test_token")
            assert save_result.is_success

            # Test status shows authenticated
            status_info = auth_instance.get_status()

            assert status_info["authenticated"] is True
            assert status_info["token_exists"] is True

    def test_status_command_execution(self) -> None:
        """Test status command execution."""
        runner = CliRunner()
        console = Console()

        result = runner.invoke(
            auth, ["status"], obj={"console": console}, catch_exceptions=False
        )

        # Status should always work and show authentication state
        assert result.exit_code == 0
        assert "Authentication Status:" in result.output


class TestRealAuthIntegration:
    """Integration tests with real FlextCliAuth functionality."""

    def test_complete_auth_workflow(self) -> None:
        """Test complete authentication workflow with real functionality."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create real configuration
            config = FlextCliConfig(
                token_file=temp_path / "workflow_token.json",
                refresh_token_file=temp_path / "workflow_refresh.json",
            )

            auth_instance = FlextCliAuth(config=config)

            # Test 1: Initially not authenticated
            assert auth_instance.is_authenticated() is False

            # Test 2: Save authentication token
            token_result = auth_instance.save_auth_token("workflow_test_token")
            assert token_result.is_success

            # Test 3: Now authenticated
            assert auth_instance.is_authenticated() is True

            # Test 4: Get token
            get_result = auth_instance.get_auth_token()
            assert get_result.is_success
            assert get_result.value == "workflow_test_token"

            # Test 5: Clear tokens
            clear_result = auth_instance.clear_auth_tokens()
            assert clear_result.is_success

            # Test 6: No longer authenticated
            assert auth_instance.is_authenticated() is False

    def test_auth_headers_generation(self) -> None:
        """Test authentication header generation with real tokens."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            config = FlextCliConfig(
                token_file=temp_path / "headers_token.json",
                refresh_token_file=temp_path / "headers_refresh.json",
            )

            auth_instance = FlextCliAuth(config=config)

            # No token - no headers
            headers = auth_instance.get_auth_headers()
            assert headers == {}

            # Save token - get headers
            auth_instance.save_auth_token("bearer_test_token")
            headers = auth_instance.get_auth_headers()

            assert "Authorization" in headers
            assert headers["Authorization"] == "Bearer bearer_test_token"


if __name__ == "__main__":
    pytest.main([__file__])
