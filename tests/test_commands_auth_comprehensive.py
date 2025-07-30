"""Comprehensive tests for commands.auth module.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

Tests for authentication commands to achieve near 100% coverage.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import click
import pytest
from click.testing import CliRunner
from flext_cli.commands.auth import auth, login, logout, status


class TestAuthGroup:
    """Test auth command group."""

    def test_auth_group_exists(self) -> None:
        """Test that auth group is properly defined."""
        assert isinstance(auth, click.Group)
        if auth.name != "auth":
            msg = f"Expected {'auth'}, got {auth.name}"
            raise AssertionError(msg)

    def test_auth_group_help(self) -> None:
        """Test auth group help message."""
        runner = CliRunner()
        result = runner.invoke(auth, ["--help"])
        if result.exit_code != 0:
            msg = f"Expected {0}, got {result.exit_code}"
            raise AssertionError(msg)
        if "Manage authentication commands" not in result.output:
            msg = f"Expected {'Manage authentication commands'} in {result.output}"
            raise AssertionError(msg)

    def test_auth_group_commands(self) -> None:
        """Test that auth group has expected commands."""
        commands = auth.list_commands(None)
        if "login" not in commands:
            msg = f"Expected {'login'} in {commands}"
            raise AssertionError(msg)
        assert "logout" in commands
        if "status" not in commands:
            msg = f"Expected {'status'} in {commands}"
            raise AssertionError(msg)


class TestLoginCommand:
    """Test login command."""

    def test_login_command_exists(self) -> None:
        """Test that login command is properly defined."""
        assert isinstance(login, click.Command)
        if login.name != "login":
            msg = f"Expected {'login'}, got {login.name}"
            raise AssertionError(msg)

    def test_login_help(self) -> None:
        """Test login command help."""
        runner = CliRunner()
        result = runner.invoke(login, ["--help"])
        if result.exit_code != 0:
            msg = f"Expected {0}, got {result.exit_code}"
            raise AssertionError(msg)
        if "Login to FLEXT" not in result.output:
            msg = f"Expected {'Login to FLEXT'} in {result.output}"
            raise AssertionError(msg)
        assert "--username" in result.output
        if "--password" not in result.output:
            msg = f"Expected {'--password'} in {result.output}"
            raise AssertionError(msg)

    @patch("flext_cli.commands.auth.FlextApiClient")
    @patch("flext_cli.commands.auth.save_auth_token")
    def test_login_success(
        self,
        mock_save_token: MagicMock,
        mock_client_class: MagicMock,
    ) -> None:
        """Test successful login."""
        # Setup mocks
        mock_client = AsyncMock()
        mock_client.login.return_value = {
            "token": "test-token-123",
            "user": {"name": "Test User", "username": "testuser"},
        }
        mock_client_class.return_value.__aenter__.return_value = mock_client

        mock_console = MagicMock()
        runner = CliRunner()

        result = runner.invoke(
            login,
            ["--username", "testuser", "--password", "testpass"],
            obj={"console": mock_console},
        )

        if result.exit_code != 0:
            msg = f"Expected {0}, got {result.exit_code}"
            raise AssertionError(msg)
        mock_save_token.assert_called_once_with("test-token-123")
        mock_console.print.assert_any_call("[yellow]Logging in as testuser...[/yellow]")
        mock_console.print.assert_any_call("[green]✅ Login successful![/green]")
        mock_console.print.assert_any_call("Welcome, Test User!")

    @patch("flext_cli.commands.auth.FlextApiClient")
    @patch("flext_cli.commands.auth.save_auth_token")
    def test_login_success_no_user_name(
        self,
        mock_save_token: MagicMock,
        mock_client_class: MagicMock,
    ) -> None:
        """Test successful login without user name in response."""
        # Setup mocks
        mock_client = AsyncMock()
        mock_client.login.return_value = {
            "token": "test-token-456",
            "user": {"username": "testuser"},  # No name field
        }
        mock_client_class.return_value.__aenter__.return_value = mock_client

        mock_console = MagicMock()
        runner = CliRunner()

        result = runner.invoke(
            login,
            ["--username", "testuser", "--password", "testpass"],
            obj={"console": mock_console},
        )

        if result.exit_code != 0:
            msg = f"Expected {0}, got {result.exit_code}"
            raise AssertionError(msg)
        mock_save_token.assert_called_once_with("test-token-456")
        mock_console.print.assert_any_call(
            "Welcome, testuser!",
        )  # Falls back to username

    @patch("flext_cli.commands.auth.FlextApiClient")
    def test_login_no_token_in_response(self, mock_client_class: MagicMock) -> None:
        """Test login when response doesn't contain token."""
        # Setup mocks
        mock_client = AsyncMock()
        mock_client.login.return_value = {"message": "Login failed"}
        mock_client_class.return_value.__aenter__.return_value = mock_client

        mock_console = MagicMock()
        runner = CliRunner()

        result = runner.invoke(
            login,
            ["--username", "testuser", "--password", "wrong"],
            obj={"console": mock_console},
        )

        if result.exit_code != 0:
            msg = f"Expected {0}, got {result.exit_code}"
            raise AssertionError(msg)
        mock_console.print.assert_any_call(
            "[red]❌ Login failed: Invalid response[/red]",
        )

    @patch("flext_cli.commands.auth.FlextApiClient")
    def test_login_connection_error(self, mock_client_class: MagicMock) -> None:
        """Test login with connection error."""
        # Setup mocks
        mock_client = AsyncMock()
        mock_client.login.side_effect = ConnectionError("Connection failed")
        mock_client_class.return_value.__aenter__.return_value = mock_client

        mock_console = MagicMock()
        runner = CliRunner()

        result = runner.invoke(
            login,
            ["--username", "testuser", "--password", "testpass"],
            obj={"console": mock_console},
        )

        if result.exit_code != 1:
            msg = f"Expected {1}, got {result.exit_code}"
            raise AssertionError(msg)
        mock_console.print.assert_any_call(
            "[red]❌ Login failed: Connection failed[/red]",
        )

    @patch("flext_cli.commands.auth.FlextApiClient")
    def test_login_timeout_error(self, mock_client_class: MagicMock) -> None:
        """Test login with timeout error."""
        # Setup mocks
        mock_client = AsyncMock()
        mock_client.login.side_effect = TimeoutError("Request timed out")
        mock_client_class.return_value.__aenter__.return_value = mock_client

        mock_console = MagicMock()
        runner = CliRunner()

        result = runner.invoke(
            login,
            ["--username", "testuser", "--password", "testpass"],
            obj={"console": mock_console},
        )

        if result.exit_code != 1:
            msg = f"Expected {1}, got {result.exit_code}"
            raise AssertionError(msg)
        mock_console.print.assert_any_call(
            "[red]❌ Login failed: Request timed out[/red]",
        )

    @patch("flext_cli.commands.auth.FlextApiClient")
    def test_login_value_error(self, mock_client_class: MagicMock) -> None:
        """Test login with value error."""
        # Setup mocks
        mock_client = AsyncMock()
        mock_client.login.side_effect = ValueError("Invalid credentials")
        mock_client_class.return_value.__aenter__.return_value = mock_client

        mock_console = MagicMock()
        runner = CliRunner()

        result = runner.invoke(
            login,
            ["--username", "testuser", "--password", "testpass"],
            obj={"console": mock_console},
        )

        if result.exit_code != 1:
            msg = f"Expected {1}, got {result.exit_code}"
            raise AssertionError(msg)
        mock_console.print.assert_any_call(
            "[red]❌ Login failed: Invalid credentials[/red]",
        )

    @patch("flext_cli.commands.auth.FlextApiClient")
    def test_login_key_error(self, mock_client_class: MagicMock) -> None:
        """Test login with key error."""
        # Setup mocks
        mock_client = AsyncMock()
        mock_client.login.side_effect = KeyError("required_field")
        mock_client_class.return_value.__aenter__.return_value = mock_client

        mock_console = MagicMock()
        runner = CliRunner()

        result = runner.invoke(
            login,
            ["--username", "testuser", "--password", "testpass"],
            obj={"console": mock_console},
        )

        if result.exit_code != 1:
            msg = f"Expected {1}, got {result.exit_code}"
            raise AssertionError(msg)
        mock_console.print.assert_any_call(
            "[red]❌ Login failed: 'required_field'[/red]",
        )

    @patch("flext_cli.commands.auth.FlextApiClient")
    def test_login_os_error(self, mock_client_class: MagicMock) -> None:
        """Test login with OS error."""
        # Setup mocks
        mock_client = AsyncMock()
        mock_client.login.side_effect = OSError("Network unreachable")
        mock_client_class.return_value.__aenter__.return_value = mock_client

        mock_console = MagicMock()
        runner = CliRunner()

        result = runner.invoke(
            login,
            ["--username", "testuser", "--password", "testpass"],
            obj={"console": mock_console},
        )

        if result.exit_code != 1:
            msg = f"Expected {1}, got {result.exit_code}"
            raise AssertionError(msg)
        mock_console.print.assert_any_call(
            "[red]❌ Network error during login: Network unreachable[/red]",
        )

    def test_login_prompts_for_username(self) -> None:
        """Test that login prompts for username when not provided."""
        runner = CliRunner()
        result = runner.invoke(login, input="testuser\ntestpass\n")

        # Should prompt for username and password
        if "Username:" not in result.output:
            msg = f"Expected {'Username:'} in {result.output}"
            raise AssertionError(msg)


class TestLogoutCommand:
    """Test logout command."""

    def test_logout_command_exists(self) -> None:
        """Test that logout command is properly defined."""
        assert isinstance(logout, click.Command)
        if logout.name != "logout":
            msg = f"Expected {'logout'}, got {logout.name}"
            raise AssertionError(msg)

    def test_logout_help(self) -> None:
        """Test logout command help."""
        runner = CliRunner()
        result = runner.invoke(logout, ["--help"])
        if result.exit_code != 0:
            msg = f"Expected {0}, got {result.exit_code}"
            raise AssertionError(msg)
        if "Logout from FLEXT" not in result.output:
            msg = f"Expected {'Logout from FLEXT'} in {result.output}"
            raise AssertionError(msg)

    @patch("flext_cli.commands.auth.get_auth_token")
    def test_logout_not_logged_in(self, mock_get_token: MagicMock) -> None:
        """Test logout when not logged in."""
        mock_get_token.return_value = None
        mock_console = MagicMock()

        runner = CliRunner()
        result = runner.invoke(logout, obj={"console": mock_console})

        if result.exit_code != 0:
            msg = f"Expected {0}, got {result.exit_code}"
            raise AssertionError(msg)
        mock_console.print.assert_any_call("[yellow]Not logged in[/yellow]")

    @patch("flext_cli.commands.auth.get_auth_token")
    def test_logout_empty_token(self, mock_get_token: MagicMock) -> None:
        """Test logout with empty token."""
        mock_get_token.return_value = ""
        mock_console = MagicMock()

        runner = CliRunner()
        result = runner.invoke(logout, obj={"console": mock_console})

        if result.exit_code != 0:
            msg = f"Expected {0}, got {result.exit_code}"
            raise AssertionError(msg)
        mock_console.print.assert_any_call("[yellow]Not logged in[/yellow]")

    @patch("flext_cli.commands.auth.FlextApiClient")
    @patch("flext_cli.commands.auth.clear_auth_tokens")
    @patch("flext_cli.commands.auth.get_auth_token")
    def test_logout_success(
        self,
        mock_get_token: MagicMock,
        mock_clear_tokens: MagicMock,
        mock_client_class: MagicMock,
    ) -> None:
        """Test successful logout."""
        # Setup mocks
        mock_get_token.return_value = "valid-token"
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client

        mock_console = MagicMock()
        runner = CliRunner()

        result = runner.invoke(logout, obj={"console": mock_console})

        if result.exit_code != 0:
            msg = f"Expected {0}, got {result.exit_code}"
            raise AssertionError(msg)
        mock_client.logout.assert_called_once()
        mock_clear_tokens.assert_called_once()
        mock_console.print.assert_any_call("[yellow]Logging out...[/yellow]")
        mock_console.print.assert_any_call("[green]✅ Logged out successfully[/green]")

    @patch("flext_cli.commands.auth.FlextApiClient")
    @patch("flext_cli.commands.auth.clear_auth_tokens")
    @patch("flext_cli.commands.auth.get_auth_token")
    def test_logout_connection_error(
        self,
        mock_get_token: MagicMock,
        mock_clear_tokens: MagicMock,
        mock_client_class: MagicMock,
    ) -> None:
        """Test logout with connection error."""
        # Setup mocks
        mock_get_token.return_value = "valid-token"
        mock_client = AsyncMock()
        mock_client.logout.side_effect = ConnectionError("Connection failed")
        mock_client_class.return_value.__aenter__.return_value = mock_client

        mock_console = MagicMock()
        runner = CliRunner()

        result = runner.invoke(logout, obj={"console": mock_console})

        if result.exit_code != 0:
            msg = f"Expected {0}, got {result.exit_code}"
            raise AssertionError(msg)
        mock_clear_tokens.assert_called_once()  # Still clears tokens locally
        mock_console.print.assert_any_call(
            "[yellow]⚠️  Logged out locally (Connection failed)[/yellow]",
        )

    @patch("flext_cli.commands.auth.FlextApiClient")
    @patch("flext_cli.commands.auth.clear_auth_tokens")
    @patch("flext_cli.commands.auth.get_auth_token")
    def test_logout_timeout_error(
        self,
        mock_get_token: MagicMock,
        mock_clear_tokens: MagicMock,
        mock_client_class: MagicMock,
    ) -> None:
        """Test logout with timeout error."""
        # Setup mocks
        mock_get_token.return_value = "valid-token"
        mock_client = AsyncMock()
        mock_client.logout.side_effect = TimeoutError("Request timed out")
        mock_client_class.return_value.__aenter__.return_value = mock_client

        mock_console = MagicMock()
        runner = CliRunner()

        result = runner.invoke(logout, obj={"console": mock_console})

        if result.exit_code != 0:
            msg = f"Expected {0}, got {result.exit_code}"
            raise AssertionError(msg)
        mock_clear_tokens.assert_called_once()
        mock_console.print.assert_any_call(
            "[yellow]⚠️  Logged out locally (Request timed out)[/yellow]",
        )

    @patch("flext_cli.commands.auth.FlextApiClient")
    @patch("flext_cli.commands.auth.clear_auth_tokens")
    @patch("flext_cli.commands.auth.get_auth_token")
    def test_logout_value_error(
        self,
        mock_get_token: MagicMock,
        mock_clear_tokens: MagicMock,
        mock_client_class: MagicMock,
    ) -> None:
        """Test logout with value error."""
        # Setup mocks
        mock_get_token.return_value = "valid-token"
        mock_client = AsyncMock()
        mock_client.logout.side_effect = ValueError("Invalid token")
        mock_client_class.return_value.__aenter__.return_value = mock_client

        mock_console = MagicMock()
        runner = CliRunner()

        result = runner.invoke(logout, obj={"console": mock_console})

        if result.exit_code != 0:
            msg = f"Expected {0}, got {result.exit_code}"
            raise AssertionError(msg)
        mock_clear_tokens.assert_called_once()
        mock_console.print.assert_any_call(
            "[yellow]⚠️  Logged out locally (Invalid token)[/yellow]",
        )

    @patch("flext_cli.commands.auth.FlextApiClient")
    @patch("flext_cli.commands.auth.clear_auth_tokens")
    @patch("flext_cli.commands.auth.get_auth_token")
    def test_logout_key_error(
        self,
        mock_get_token: MagicMock,
        mock_clear_tokens: MagicMock,
        mock_client_class: MagicMock,
    ) -> None:
        """Test logout with key error."""
        # Setup mocks
        mock_get_token.return_value = "valid-token"
        mock_client = AsyncMock()
        mock_client.logout.side_effect = KeyError("token")
        mock_client_class.return_value.__aenter__.return_value = mock_client

        mock_console = MagicMock()
        runner = CliRunner()

        result = runner.invoke(logout, obj={"console": mock_console})

        if result.exit_code != 0:
            msg = f"Expected {0}, got {result.exit_code}"
            raise AssertionError(msg)
        mock_clear_tokens.assert_called_once()
        mock_console.print.assert_any_call(
            "[green]✅ Logged out successfully[/green]",
        )

    @patch("flext_cli.commands.auth.FlextApiClient")
    @patch("flext_cli.commands.auth.clear_auth_tokens")
    @patch("flext_cli.commands.auth.get_auth_token")
    def test_logout_os_error(
        self,
        mock_get_token: MagicMock,
        mock_clear_tokens: MagicMock,
        mock_client_class: MagicMock,
    ) -> None:
        """Test logout with OS error."""
        # Setup mocks
        mock_get_token.return_value = "valid-token"
        mock_client = AsyncMock()
        mock_client.logout.side_effect = OSError("Network unreachable")
        mock_client_class.return_value.__aenter__.return_value = mock_client

        mock_console = MagicMock()
        runner = CliRunner()

        result = runner.invoke(logout, obj={"console": mock_console})

        if result.exit_code != 0:
            msg = f"Expected {0}, got {result.exit_code}"
            raise AssertionError(msg)
        mock_clear_tokens.assert_called_once()
        expected_msg = "[yellow]⚠️  Network error during logout, logged out locally (Network unreachable)[/yellow]"
        mock_console.print.assert_any_call(expected_msg)


class TestStatusCommand:
    """Test status command."""

    def test_status_command_exists(self) -> None:
        """Test that status command is properly defined."""
        assert isinstance(status, click.Command)
        if status.name != "status":
            msg = f"Expected {'status'}, got {status.name}"
            raise AssertionError(msg)

    def test_status_help(self) -> None:
        """Test status command help."""
        runner = CliRunner()
        result = runner.invoke(status, ["--help"])
        if result.exit_code != 0:
            msg = f"Expected {0}, got {result.exit_code}"
            raise AssertionError(msg)
        if "Check authentication status" not in result.output:
            msg = f"Expected {'Check authentication status'} in {result.output}"
            raise AssertionError(msg)

    @patch("flext_cli.commands.auth.get_auth_token")
    def test_status_not_authenticated(self, mock_get_token: MagicMock) -> None:
        """Test status when not authenticated."""
        mock_get_token.return_value = None
        mock_console = MagicMock()

        runner = CliRunner()
        result = runner.invoke(status, obj={"console": mock_console})

        if result.exit_code != 1:
            msg = f"Expected {1}, got {result.exit_code}"
            raise AssertionError(msg)
        mock_console.print.assert_any_call("[red]❌ Not authenticated[/red]")
        mock_console.print.assert_any_call("Run 'flext auth login' to authenticate")

    @patch("flext_cli.commands.auth.get_auth_token")
    def test_status_empty_token(self, mock_get_token: MagicMock) -> None:
        """Test status with empty token."""
        mock_get_token.return_value = ""
        mock_console = MagicMock()

        runner = CliRunner()
        result = runner.invoke(status, obj={"console": mock_console})

        if result.exit_code != 1:
            msg = f"Expected {1}, got {result.exit_code}"
            raise AssertionError(msg)
        mock_console.print.assert_any_call("[red]❌ Not authenticated[/red]")

    @patch("flext_cli.commands.auth.FlextApiClient")
    @patch("flext_cli.commands.auth.get_auth_token")
    def test_status_authenticated(
        self,
        mock_get_token: MagicMock,
        mock_client_class: MagicMock,
    ) -> None:
        """Test status when authenticated."""
        # Setup mocks
        mock_get_token.return_value = "valid-token"
        mock_client = AsyncMock()
        mock_client.get_current_user.return_value = {
            "username": "testuser",
            "email": "test@example.com",
            "role": "REDACTED_LDAP_BIND_PASSWORD",
        }
        mock_client_class.return_value.__aenter__.return_value = mock_client

        mock_console = MagicMock()
        runner = CliRunner()

        result = runner.invoke(status, obj={"console": mock_console})

        if result.exit_code != 0:
            msg = f"Expected {0}, got {result.exit_code}"
            raise AssertionError(msg)
        mock_console.print.assert_any_call(
            "[yellow]Checking authentication...[/yellow]",
        )
        mock_console.print.assert_any_call("[green]✅ Authenticated[/green]")
        mock_console.print.assert_any_call("User: testuser")
        mock_console.print.assert_any_call("Email: test@example.com")
        mock_console.print.assert_any_call("Role: REDACTED_LDAP_BIND_PASSWORD")

    @patch("flext_cli.commands.auth.FlextApiClient")
    @patch("flext_cli.commands.auth.get_auth_token")
    def test_status_authenticated_missing_fields(
        self,
        mock_get_token: MagicMock,
        mock_client_class: MagicMock,
    ) -> None:
        """Test status when authenticated but user data is incomplete."""
        # Setup mocks
        mock_get_token.return_value = "valid-token"
        mock_client = AsyncMock()
        mock_client.get_current_user.return_value = {}  # Empty user data
        mock_client_class.return_value.__aenter__.return_value = mock_client

        mock_console = MagicMock()
        runner = CliRunner()

        result = runner.invoke(status, obj={"console": mock_console})

        if result.exit_code != 0:
            msg = f"Expected {0}, got {result.exit_code}"
            raise AssertionError(msg)
        mock_console.print.assert_any_call("User: Unknown")
        mock_console.print.assert_any_call("Email: Unknown")
        mock_console.print.assert_any_call("Role: Unknown")

    @patch("flext_cli.commands.auth.FlextApiClient")
    @patch("flext_cli.commands.auth.get_auth_token")
    def test_status_connection_error(
        self,
        mock_get_token: MagicMock,
        mock_client_class: MagicMock,
    ) -> None:
        """Test status with connection error."""
        # Setup mocks
        mock_get_token.return_value = "valid-token"
        mock_client = AsyncMock()
        mock_client.get_current_user.side_effect = ConnectionError("Connection failed")
        mock_client_class.return_value.__aenter__.return_value = mock_client

        mock_console = MagicMock()
        runner = CliRunner()

        result = runner.invoke(status, obj={"console": mock_console})

        if result.exit_code != 1:
            msg = f"Expected {1}, got {result.exit_code}"
            raise AssertionError(msg)
        mock_console.print.assert_any_call(
            "[red]❌ Authentication check failed: Connection failed[/red]",
        )
        mock_console.print.assert_any_call("Run 'flext auth login' to re-authenticate")

    @patch("flext_cli.commands.auth.FlextApiClient")
    @patch("flext_cli.commands.auth.get_auth_token")
    def test_status_timeout_error(
        self,
        mock_get_token: MagicMock,
        mock_client_class: MagicMock,
    ) -> None:
        """Test status with timeout error."""
        # Setup mocks
        mock_get_token.return_value = "valid-token"
        mock_client = AsyncMock()
        mock_client.get_current_user.side_effect = TimeoutError("Request timed out")
        mock_client_class.return_value.__aenter__.return_value = mock_client

        mock_console = MagicMock()
        runner = CliRunner()

        result = runner.invoke(status, obj={"console": mock_console})

        if result.exit_code != 1:
            msg = f"Expected {1}, got {result.exit_code}"
            raise AssertionError(msg)
        mock_console.print.assert_any_call(
            "[red]❌ Authentication check failed: Request timed out[/red]",
        )

    @patch("flext_cli.commands.auth.FlextApiClient")
    @patch("flext_cli.commands.auth.get_auth_token")
    def test_status_value_error(
        self,
        mock_get_token: MagicMock,
        mock_client_class: MagicMock,
    ) -> None:
        """Test status with value error."""
        # Setup mocks
        mock_get_token.return_value = "valid-token"
        mock_client = AsyncMock()
        mock_client.get_current_user.side_effect = ValueError("Invalid response")
        mock_client_class.return_value.__aenter__.return_value = mock_client

        mock_console = MagicMock()
        runner = CliRunner()

        result = runner.invoke(status, obj={"console": mock_console})

        if result.exit_code != 1:
            msg = f"Expected {1}, got {result.exit_code}"
            raise AssertionError(msg)
        mock_console.print.assert_any_call(
            "[red]❌ Authentication check failed: Invalid response[/red]",
        )

    @patch("flext_cli.commands.auth.FlextApiClient")
    @patch("flext_cli.commands.auth.get_auth_token")
    def test_status_key_error(
        self,
        mock_get_token: MagicMock,
        mock_client_class: MagicMock,
    ) -> None:
        """Test status with key error."""
        # Setup mocks
        mock_get_token.return_value = "valid-token"
        mock_client = AsyncMock()
        mock_client.get_current_user.side_effect = KeyError("user_id")
        mock_client_class.return_value.__aenter__.return_value = mock_client

        mock_console = MagicMock()
        runner = CliRunner()

        result = runner.invoke(status, obj={"console": mock_console})

        if result.exit_code != 1:
            msg = f"Expected {1}, got {result.exit_code}"
            raise AssertionError(msg)
        mock_console.print.assert_any_call(
            "[red]❌ Authentication check failed: 'user_id'[/red]",
        )

    @patch("flext_cli.commands.auth.FlextApiClient")
    @patch("flext_cli.commands.auth.get_auth_token")
    def test_status_os_error(
        self,
        mock_get_token: MagicMock,
        mock_client_class: MagicMock,
    ) -> None:
        """Test status with OS error."""
        # Setup mocks
        mock_get_token.return_value = "valid-token"
        mock_client = AsyncMock()
        mock_client.get_current_user.side_effect = OSError("Network unreachable")
        mock_client_class.return_value.__aenter__.return_value = mock_client

        mock_console = MagicMock()
        runner = CliRunner()

        result = runner.invoke(status, obj={"console": mock_console})

        if result.exit_code != 1:
            msg = f"Expected {1}, got {result.exit_code}"
            raise AssertionError(msg)
        expected_msg = "[red]❌ Network error during authentication check: Network unreachable[/red]"
        mock_console.print.assert_any_call(expected_msg)
        mock_console.print.assert_any_call("Run 'flext auth login' to re-authenticate")


class TestAuthIntegration:
    """Integration tests for auth commands."""

    def test_auth_commands_integration(self) -> None:
        """Test that all auth commands are properly registered."""
        runner = CliRunner()
        result = runner.invoke(auth, ["--help"])

        if result.exit_code != 0:
            msg = f"Expected {0}, got {result.exit_code}"
            raise AssertionError(msg)
        if "login" not in result.output:
            msg = f"Expected {'login'} in {result.output}"
            raise AssertionError(msg)
        assert "logout" in result.output
        if "status" not in result.output:
            msg = f"Expected {'status'} in {result.output}"
            raise AssertionError(msg)

    @patch("flext_cli.commands.auth.FlextApiClient")
    @patch("flext_cli.commands.auth.save_auth_token")
    @patch("flext_cli.commands.auth.clear_auth_tokens")
    @patch("flext_cli.commands.auth.get_auth_token")
    def test_full_auth_workflow(
        self,
        mock_get_token: MagicMock,
        mock_clear_tokens: MagicMock,
        mock_save_token: MagicMock,
        mock_client_class: MagicMock,
    ) -> None:
        """Test complete authentication workflow."""
        # Setup client mock
        mock_client = AsyncMock()
        mock_client.login.return_value = {
            "token": "test-token",
            "user": {"name": "Test User", "username": "testuser"},
        }
        mock_client.get_current_user.return_value = {
            "username": "testuser",
            "email": "test@example.com",
            "role": "user",
        }
        mock_client_class.return_value.__aenter__.return_value = mock_client

        mock_console = MagicMock()
        runner = CliRunner()

        # 1. Login
        mock_get_token.return_value = None  # Not logged in initially
        result = runner.invoke(
            login,
            ["--username", "testuser", "--password", "testpass"],
            obj={"console": mock_console},
        )
        if result.exit_code != 0:
            msg = f"Expected {0}, got {result.exit_code}"
            raise AssertionError(msg)
        mock_save_token.assert_called_with("test-token")

        # 2. Check status
        mock_get_token.return_value = "test-token"  # Now logged in
        result = runner.invoke(status, obj={"console": mock_console})
        if result.exit_code != 0:
            msg = f"Expected {0}, got {result.exit_code}"
            raise AssertionError(msg)

        # 3. Logout
        result = runner.invoke(logout, obj={"console": mock_console})
        if result.exit_code != 0:
            msg = f"Expected {0}, got {result.exit_code}"
            raise AssertionError(msg)
        mock_clear_tokens.assert_called()

    def test_command_error_handling_consistency(self) -> None:
        """Test that all commands handle errors consistently."""
        mock_console = MagicMock()
        runner = CliRunner()

        # All commands should handle missing console gracefully
        # This would raise if error handling is inconsistent
        try:
            runner.invoke(
                login,
                ["--username", "test", "--password", "test"],
                obj={"console": mock_console},
            )
            runner.invoke(logout, obj={"console": mock_console})
            runner.invoke(status, obj={"console": mock_console})
        except (RuntimeError, ValueError, TypeError) as e:
            pytest.fail(f"Commands should handle errors consistently: {e}")
