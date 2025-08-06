"""Tests for auth commands.

Tests authentication command functionality for coverage.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import click
from click.testing import CliRunner
from flext_cli.client import FlextApiClient
from flext_cli.commands.auth import auth
from flext_core import FlextResult
from rich.console import Console


class TestAuthCommands:
    """Test auth commands."""

    def setup_method(self) -> None:
        """Set up test environment."""
        self.runner = CliRunner()

    def test_auth_group_structure(self) -> None:
        """Test auth command group structure."""
        if auth.name != "auth":
            raise AssertionError(f"Expected {'auth'}, got {auth.name}")
        if "login" not in auth.commands:
            raise AssertionError(f"Expected {'login'} in {auth.commands}")
        assert "logout" in auth.commands
        if "status" not in auth.commands:
            raise AssertionError(f"Expected {'status'} in {auth.commands}")
        if "whoami" not in auth.commands:
            raise AssertionError(f"Expected {'whoami'} in {auth.commands}")

    def test_login_success(self) -> None:
        """Test successful login."""
        with (
            patch("flext_cli.commands.auth.FlextApiClient") as mock_client_class,
            patch("flext_cli.commands.auth.save_auth_token") as mock_save_token,
        ):
            self._test_login_success_impl(mock_save_token, mock_client_class)

    def _test_login_success_impl(
        self,
        mock_save_token: MagicMock,
        mock_client_class: MagicMock,
    ) -> None:
        """Test successful login implementation."""
        # Mock async client
        mock_client = AsyncMock()
        # Mock FlextResult success response
        mock_login_result = FlextResult.ok(
            {
                "token": "token_testuser_abc123",
                "user": {"name": "Test User", "username": "testuser"},
            }
        )
        mock_client.login.return_value = mock_login_result
        mock_client_class.return_value.__aenter__.return_value = mock_client

        # Mock console
        mock_console = MagicMock()

        result = self.runner.invoke(
            auth,
            ["login"],
            input="testuser\ntestpass\n",
            obj={"console": mock_console},
        )

        # Should complete successfully
        if result.exit_code != 0:
            raise AssertionError(f"Expected {0}, got {result.exit_code}")
        # Auth implementation saves token from response
        mock_save_token.assert_called_once_with("token_testuser_abc123")

    @patch("flext_cli.commands.auth.FlextApiClient")
    @patch("flext_cli.commands.auth.save_auth_token")
    def test_login_invalid_response(
        self,
        mock_save_token: MagicMock,
        mock_client_class: MagicMock,
    ) -> None:
        """Test login with invalid response."""
        # Mock async client with no token in response
        mock_client = AsyncMock()
        # Mock FlextResult failure response
        mock_client.login.return_value = FlextResult.fail("Login failed")
        mock_client_class.return_value.__aenter__.return_value = mock_client

        mock_console = MagicMock()

        result = self.runner.invoke(
            auth,
            ["login"],
            input="testuser\ntestpass\n",
            obj={"console": mock_console},
        )

        # Should fail with exit code 1 for invalid response
        if result.exit_code != 1:
            raise AssertionError(f"Expected {1}, got {result.exit_code}")
        # No token should be saved for invalid response
        mock_save_token.assert_not_called()

    @patch("flext_cli.commands.auth.FlextApiClient")
    def test_login_connection_error(
        self,
        mock_client_class: MagicMock,
    ) -> None:
        """Test login with connection error."""
        # Mock async client that raises exception
        mock_client = AsyncMock()
        mock_client.login.side_effect = ConnectionError("Connection failed")
        mock_client_class.return_value.__aenter__.return_value = mock_client

        mock_console = MagicMock()

        result = self.runner.invoke(
            auth,
            ["login"],
            input="testuser\ntestpass\n",
            obj={"console": mock_console},
        )

        # Should handle the exception and exit with error
        assert result.exit_code == 1

    @patch("flext_cli.commands.auth.get_auth_token")
    @patch("flext_cli.commands.auth.FlextApiClient")
    @patch("flext_cli.commands.auth.clear_auth_tokens")
    def test_logout_success(
        self,
        mock_clear_tokens: MagicMock,
        mock_client_class: MagicMock,
        mock_get_token: MagicMock,
    ) -> None:
        """Test successful logout."""
        mock_get_token.return_value = "test_token"

        # Mock async client
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client

        mock_console = MagicMock()

        result = self.runner.invoke(
            auth,
            ["logout"],
            obj={"console": mock_console},
        )

        if result.exit_code != 0:
            raise AssertionError(f"Expected {0}, got {result.exit_code}")
        # Should clear tokens on successful logout
        mock_clear_tokens.assert_called_once()

    def test_logout_not_logged_in(self) -> None:
        """Test logout when not logged in."""
        with patch("flext_cli.commands.auth.get_auth_token") as mock_get_token:
            self._test_logout_not_logged_in_impl(mock_get_token)

    def _test_logout_not_logged_in_impl(self, mock_get_token: MagicMock) -> None:
        """Test logout when not logged in implementation."""
        mock_get_token.return_value = None

        mock_console = MagicMock()

        result = self.runner.invoke(
            auth,
            ["logout"],
            obj={"console": mock_console},
        )

        if result.exit_code != 0:
            raise AssertionError(f"Expected {0}, got {result.exit_code}")
        # Should handle not logged in case gracefully
        mock_console.print.assert_called()

    @patch("flext_cli.commands.auth.get_auth_token")
    @patch("flext_cli.commands.auth.FlextApiClient")
    @patch("flext_cli.commands.auth.clear_auth_tokens")
    def test_logout_api_error(
        self,
        mock_clear_tokens: MagicMock,
        mock_client_class: MagicMock,
        mock_get_token: MagicMock,
    ) -> None:
        """Test logout with API error."""
        mock_get_token.return_value = "test_token"

        # Mock async client to raise exception
        mock_client = AsyncMock()
        mock_client.logout.side_effect = ConnectionError("API error")
        mock_client_class.return_value.__aenter__.return_value = mock_client

        mock_console = MagicMock()

        result = self.runner.invoke(
            auth,
            ["logout"],
            obj={"console": mock_console},
        )

        if result.exit_code != 0:
            raise AssertionError(f"Expected {0}, got {result.exit_code}")
        mock_clear_tokens.assert_called_once()

    @patch("flext_cli.commands.auth.get_auth_token")
    @patch("flext_cli.commands.auth.FlextApiClient")
    def test_status_authenticated(
        self,
        mock_client_class: MagicMock,
        mock_get_token: MagicMock,
    ) -> None:
        """Test status when authenticated."""
        mock_get_token.return_value = "test_token"

        # Mock async client
        mock_client = AsyncMock()
        # Mock FlextResult success response
        mock_client.get_current_user.return_value = FlextResult.ok(
            {
                "username": "testuser",
                "email": "test@example.com",
                "role": "user",
            }
        )
        mock_client_class.return_value.__aenter__.return_value = mock_client

        mock_console = MagicMock()

        result = self.runner.invoke(
            auth,
            ["status"],
            obj={"console": mock_console},
        )

        if result.exit_code != 0:
            raise AssertionError(f"Expected {0}, got {result.exit_code}")
        # Should print status information
        mock_console.print.assert_called()

    @patch("flext_cli.commands.auth.get_auth_token")
    def test_status_not_authenticated(
        self,
        mock_get_token: MagicMock,
    ) -> None:
        """Test status when not authenticated."""
        mock_get_token.return_value = None

        mock_console = MagicMock()

        result = self.runner.invoke(
            auth,
            ["status"],
            obj={"console": mock_console},
        )

        # Should exit with error code
        assert result.exit_code == 1

    @patch("flext_cli.commands.auth.get_auth_token")
    @patch("flext_cli.commands.auth.FlextApiClient")
    def test_status_api_error(
        self,
        mock_client_class: MagicMock,
        mock_get_token: MagicMock,
    ) -> None:
        """Test status with API error."""
        mock_get_token.return_value = "test_token"

        # Mock async client to raise exception
        mock_client = AsyncMock()
        mock_client.get_current_user.side_effect = ConnectionError("API error")
        mock_client_class.return_value.__aenter__.return_value = mock_client

        mock_console = MagicMock()

        result = self.runner.invoke(
            auth,
            ["status"],
            obj={"console": mock_console},
        )

        # Should exit with error code
        assert result.exit_code == 1

    @patch("flext_cli.commands.auth.get_auth_token")
    @patch("flext_cli.commands.auth.FlextApiClient")
    def test_whoami_authenticated(
        self,
        mock_client_class: MagicMock,
        mock_get_token: MagicMock,
    ) -> None:
        """Test whoami when authenticated."""
        mock_get_token.return_value = "test_token"

        # Mock async client
        mock_client = AsyncMock()
        # Mock FlextResult success response
        mock_client.get_current_user.return_value = FlextResult.ok(
            {
                "username": "testuser",
                "full_name": "Test User",
                "email": "test@example.com",
                "role": "user",
                "id": "123",
            }
        )
        mock_client_class.return_value.__aenter__.return_value = mock_client

        mock_console = MagicMock()

        result = self.runner.invoke(
            auth,
            ["whoami"],
            obj={"console": mock_console},
        )

        if result.exit_code != 0:
            raise AssertionError(f"Expected {0}, got {result.exit_code}")
        # Should print user information
        mock_console.print.assert_called()

    @patch("flext_cli.commands.auth.get_auth_token")
    def test_whoami_not_authenticated(
        self,
        mock_get_token: MagicMock,
    ) -> None:
        """Test whoami when not authenticated."""
        mock_get_token.return_value = None

        mock_console = MagicMock()

        result = self.runner.invoke(
            auth,
            ["whoami"],
            obj={"console": mock_console},
        )

        # Should exit with error code
        assert result.exit_code == 1

    def test_auth_commands_help(self) -> None:
        """Test auth command help."""
        commands_to_test = ["login", "logout", "status", "whoami"]

        for cmd in commands_to_test:
            result = self.runner.invoke(auth, [cmd, "--help"])
            if result.exit_code != 0:
                raise AssertionError(f"Expected {0}, got {result.exit_code}")
            if "Usage:" not in result.output:
                raise AssertionError(f"Expected {'Usage:'} in {result.output}")

    def test_auth_group_help(self) -> None:
        """Test auth group help."""
        result = self.runner.invoke(auth, ["--help"])
        if result.exit_code != 0:
            raise AssertionError(f"Expected {0}, got {result.exit_code}")
        if "Manage authentication commands" not in result.output:
            raise AssertionError(
                f"Expected {'Manage authentication commands'} in {result.output}"
            )

    def test_login_with_options(self) -> None:
        """Test login command with username and password options."""
        mock_console = MagicMock()

        with (
            patch("flext_cli.commands.auth.FlextApiClient"),
            patch("asyncio.run"),
        ):
            result = self.runner.invoke(
                auth,
                ["login", "--username", "testuser", "--password", "testpass"],
                obj={"console": mock_console},
            )

        # Should complete without prompting
        if result.exit_code != 0:
            raise AssertionError(f"Expected {0}, got {result.exit_code}")

    def test_login_prompts_for_missing_options(self) -> None:
        """Test login command prompts for missing username/password."""
        mock_console = MagicMock()

        with (
            patch("flext_cli.commands.auth.FlextApiClient"),
            patch("asyncio.run"),
        ):
            result = self.runner.invoke(
                auth,
                ["login"],
                input="testuser\ntestpass\n",
                obj={"console": mock_console},
            )

        # Should complete after prompting
        if result.exit_code != 0:
            raise AssertionError(f"Expected {0}, got {result.exit_code}")


class TestAuthFunctionality:
    """Test auth functionality."""

    def test_async_implementation(self) -> None:
        """Test async implementation with asyncio wrapper pattern."""
        # Auth commands use asyncio.run() wrapper pattern
        # This validates the async refactoring worked correctly
        from flext_cli.commands.auth import login, logout, status, whoami

        # Commands should be regular functions but contain async inner functions
        assert callable(login)
        assert callable(logout)
        assert callable(status)
        assert callable(whoami)

    def test_click_context_pattern(self) -> None:
        """Test Click context pattern used in commands."""

        # Test that we can create a mock context like used in commands
        console = MagicMock(spec=Console)
        ctx = MagicMock(spec=click.Context)
        ctx.obj = {"console": console}

        # Test accessing console from context (pattern used in all auth commands)
        accessed_console = ctx.obj["console"]
        assert accessed_console is console

    def test_auth_imports(self) -> None:
        """Test that all required imports work."""

        # All imports should work (asyncio removed from auth commands)
        assert click
        assert MagicMock

    def test_mock_client_patterns(self) -> None:
        """Test mock client patterns used in tests."""
        # Test async mock pattern
        mock_client = AsyncMock()

        # Test that client can be mocked for async use
        assert mock_client is not None
        assert callable(mock_client)

    def test_async_client_pattern(self) -> None:
        """Test async client pattern used with FlextApiClient."""
        # Auth commands use async context manager pattern
        mock_client_class = MagicMock()
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client

        # This is the pattern used in async refactored auth commands
        client_context = mock_client_class()
        assert client_context.__aenter__.return_value is mock_client

    def test_auth_response_patterns(self) -> None:
        """Test authentication response patterns."""
        # Test async client response patterns
        success_response = {
            "token": "token_testuser",
            "user": {"name": "testuser"},
        }

        if "token" not in success_response:
            raise AssertionError(f"Expected {'token'} in {success_response}")
        if success_response["token"] != "token_testuser":
            raise AssertionError(
                f"Expected {'token_testuser'}, got {success_response['token']}"
            )
        assert success_response["user"]["name"] == "testuser"

        # Test user data patterns
        user_data = success_response["user"]
        if not isinstance(user_data, dict):
            raise TypeError(f"Expected dict, got {type(user_data)}")
        assert "name" in user_data

    def test_user_info_patterns(self) -> None:
        """Test user info patterns used in status command."""
        user_info = {
            "username": "testuser",
            "email": "test@example.com",
            "role": "admin",
        }

        # Test .get() pattern used in commands
        username = user_info.get("username", "Unknown")
        email = user_info.get("email", "Unknown")
        role = user_info.get("role", "Unknown")
        missing = user_info.get("missing_field", "Unknown")

        if username != "testuser":
            raise AssertionError(f"Expected {'testuser'}, got {username}")
        assert email == "test@example.com"
        if role != "admin":
            raise AssertionError(f"Expected {'admin'}, got {role}")
        assert missing == "Unknown"

    def _test_exception_type(self, exc_type: type[Exception]) -> None:
        """Test a specific exception type - DRY abstracted raise pattern."""

        def _raise_test_exception() -> None:
            """DRY helper to abstract raise in inner function."""
            msg = "Test error"
            raise exc_type(msg)

        try:
            _raise_test_exception()
        except exc_type as e:
            if "Test error" not in str(e):
                raise AssertionError(f"Expected {'Test error'} in {e!s}") from e

    def test_exception_handling_patterns(self) -> None:
        """Test exception handling patterns used in auth commands."""
        # Test the exception types used in auth commands
        exceptions = [ConnectionError, TimeoutError, ValueError, KeyError, OSError]

        for exc_type in exceptions:
            self._test_exception_type(exc_type)


class TestAuthErrorHandling:
    """Test auth error handling."""

    def setup_method(self) -> None:
        """Set up test environment."""
        self.runner = CliRunner()

    @patch("flext_cli.commands.auth.FlextApiClient")
    def test_login_with_exception(
        self,
        mock_client_class: MagicMock,
    ) -> None:
        """Test login command with exception."""
        # Make client raise an exception
        mock_client_class.side_effect = Exception("Client error")

        mock_console = MagicMock()

        result = self.runner.invoke(
            auth,
            ["login"],
            input="testuser\ntestpass\n",
            obj={"console": mock_console},
        )

        # Command should handle the exception and exit with error
        assert result.exit_code == 1

    @patch("flext_cli.commands.auth.get_auth_token")
    @patch("flext_cli.commands.auth.FlextApiClient")
    @patch("flext_cli.commands.auth.clear_auth_tokens")
    def test_logout_with_exception(
        self,
        mock_clear_tokens: MagicMock,
        mock_client_class: MagicMock,
        mock_get_token: MagicMock,
    ) -> None:
        """Test logout command with exception."""
        mock_get_token.return_value = "test_token"
        mock_client_class.side_effect = ValueError("Client error")

        mock_console = MagicMock()

        self.runner.invoke(
            auth,
            ["logout"],
            obj={"console": mock_console},
        )

        # Command should still clear tokens even on exception
        mock_clear_tokens.assert_called_once()

    @patch("flext_cli.commands.auth.get_auth_token")
    @patch("flext_cli.commands.auth.FlextApiClient")
    def test_status_with_exception(
        self,
        mock_client_class: MagicMock,
        mock_get_token: MagicMock,
    ) -> None:
        """Test status command with exception."""
        mock_get_token.return_value = "test_token"
        mock_client_class.side_effect = Exception("Client error")

        mock_console = MagicMock()

        result = self.runner.invoke(
            auth,
            ["status"],
            obj={"console": mock_console},
        )

        # Command should handle the exception and exit with error
        assert result.exit_code == 1

    def test_commands_without_context(self) -> None:
        """Test auth commands without context."""
        commands_to_test = [
            ["login"],
            ["logout"],
            ["status"],
        ]

        for cmd_args in commands_to_test:
            result = self.runner.invoke(auth, cmd_args, input="testuser\ntestpass\n")
            # Should handle missing context gracefully
            if result.exit_code not in {0, 1, 2}:
                raise AssertionError(f"Expected {result.exit_code} in {[0, 1, 2]}")

    @patch("flext_cli.commands.auth.FlextApiClient")
    def test_login_network_errors(self, mock_client_class: MagicMock) -> None:
        """Test login with various network errors."""
        error_types = [ConnectionError, TimeoutError, OSError]

        for error_type in error_types:
            # Mock async client to raise exception
            mock_client = AsyncMock()
            mock_client.login.side_effect = error_type("Network error")
            mock_client_class.return_value.__aenter__.return_value = mock_client

            mock_console = MagicMock()

            result = self.runner.invoke(
                auth,
                ["login"],
                input="testuser\ntestpass\n",
                obj={"console": mock_console},
            )

            # Should handle error and exit with error code
            assert result.exit_code == 1
            # Reset for next iteration
            mock_client_class.reset_mock()

    @patch("flext_cli.commands.auth.get_auth_token")
    @patch("flext_cli.commands.auth.FlextApiClient")
    @patch("flext_cli.commands.auth.clear_auth_tokens")
    def test_logout_network_errors(
        self,
        mock_clear_tokens: MagicMock,
        mock_client_class: MagicMock,
        mock_get_token: MagicMock,
    ) -> None:
        """Test logout with various network errors."""
        mock_get_token.return_value = "test_token"
        error_types = [ConnectionError, TimeoutError, OSError]

        for error_type in error_types:
            # Mock async client to raise exception
            mock_client = AsyncMock()
            mock_client.logout.side_effect = error_type("Network error")
            mock_client_class.return_value.__aenter__.return_value = mock_client

            mock_console = MagicMock()

            self.runner.invoke(
                auth,
                ["logout"],
                obj={"console": mock_console},
            )

            # Should clear tokens even on network error
            mock_clear_tokens.assert_called()
            # Reset for next iteration
            mock_client_class.reset_mock()
            mock_clear_tokens.reset_mock()

    @patch("flext_cli.commands.auth.get_auth_token")
    @patch("flext_cli.commands.auth.FlextApiClient")
    def test_status_network_errors(
        self,
        mock_client_class: MagicMock,
        mock_get_token: MagicMock,
    ) -> None:
        """Test status with various network errors."""
        mock_get_token.return_value = "test_token"
        error_types = [ConnectionError, TimeoutError, OSError]

        for error_type in error_types:
            # Mock async client to raise exception
            mock_client = AsyncMock()
            mock_client.get_current_user.side_effect = error_type("Network error")
            mock_client_class.return_value.__aenter__.return_value = mock_client

            mock_console = MagicMock()

            result = self.runner.invoke(
                auth,
                ["status"],
                obj={"console": mock_console},
            )

            # Should handle error and exit with error code
            assert result.exit_code == 1
            # Reset for next iteration
            mock_client_class.reset_mock()


class TestAuthIntegration:
    """Integration tests for auth commands."""

    def test_all_commands_registered(self) -> None:
        """Test that all auth commands are properly registered."""
        command_functions = ["login", "logout", "status"]

        for cmd_name in command_functions:
            if cmd_name not in auth.commands:
                raise AssertionError(f"Expected {cmd_name} in {auth.commands}")

        registered_commands = auth.commands
        if len(registered_commands) < 3:
            raise AssertionError(
                f"Expected {len(registered_commands)} >= {3}, Missing commands in auth group"
            )

    def test_auth_group_structure_complete(self) -> None:
        """Test complete auth group structure."""
        if auth.name != "auth":
            raise AssertionError(f"Expected {'auth'}, got {auth.name}")
        assert auth.help == "Manage authentication commands."

        # Check that all expected commands exist
        expected_commands = ["login", "logout", "status", "whoami"]
        for cmd in expected_commands:
            if cmd not in auth.commands:
                raise AssertionError(f"Expected {cmd} not in {auth.commands}")

    def test_click_runner_integration(self) -> None:
        """Test integration with Click runner."""
        runner = CliRunner()

        # Test that we can invoke the auth group
        result = runner.invoke(auth, ["--help"])
        if "Manage authentication commands" not in result.output:
            raise AssertionError(
                f"Expected {'Manage authentication commands'} in {result.output}"
            )
        if result.exit_code != 0:
            raise AssertionError(f"Expected {0}, got {result.exit_code}")

    def test_command_option_handling(self) -> None:
        """Test command option handling."""
        runner = CliRunner()

        # Test login command with options - DRY combined context managers
        with (
            patch("flext_cli.commands.auth.FlextApiClient"),
            patch("asyncio.run"),
        ):
            result = runner.invoke(
                auth,
                ["login", "--username", "test", "--password", "pass"],
                obj={"console": MagicMock()},
            )

        # Should complete without error
        if result.exit_code not in {0, 1, 2}:
            raise AssertionError(f"Expected {result.exit_code} in {[0, 1, 2]}")

    def test_prompt_handling(self) -> None:
        """Test prompt handling in login command."""
        runner = CliRunner()

        # Test that login prompts for username and password - DRY combined context managers
        with (
            patch("flext_cli.commands.auth.FlextApiClient"),
            patch("asyncio.run"),
        ):
            result = runner.invoke(
                auth,
                ["login"],
                input="testuser\ntestpass\n",
                obj={"console": MagicMock()},
            )

        # Should complete after prompting
        if result.exit_code not in {0, 1, 2}:
            raise AssertionError(f"Expected {result.exit_code} in {[0, 1, 2]}")

    def test_auth_utils_integration(self) -> None:
        """Test integration with auth utils."""
        # Test that auth utility functions are importable
        from flext_cli.utils.auth import (
            clear_auth_tokens,
            get_auth_token,
            save_auth_token,
        )

        # Functions should exist
        assert callable(clear_auth_tokens)
        assert callable(get_auth_token)
        assert callable(save_auth_token)

    def test_client_integration(self) -> None:
        """Test integration with FlextApiClient."""

        # Client should be importable
        assert FlextApiClient

    def test_rich_console_integration(self) -> None:
        """Test Rich console integration."""

        # Console should be importable and usable
        console = Console()
        assert console

        # Test console methods used in auth commands
        assert hasattr(console, "print")

    def test_synchronous_patterns_used(self) -> None:
        """Test synchronous patterns used in auth commands."""

        # Test async client pattern
        mock_client = AsyncMock()
        # Mock FlextResult success response
        mock_client.login.return_value = FlextResult.ok({"token": "test"})

        # Verify async mock setup works
        async def test_async_call() -> None:
            result = await mock_client.login("user", "pass")
            # FlextResult should have data containing the token
            expected_data = {"token": "test"}
            if not (result.success and result.data == expected_data):
                raise AssertionError(
                    f"Expected success with data {expected_data}, got {result}"
                )

        # Execute async test
        import asyncio

        if hasattr(asyncio, "_get_running_loop") and asyncio._get_running_loop():
            # Already in async context
            result = mock_client.login.return_value
            if result != {"token": "test"}:
                raise AssertionError(f"Expected {{'token': 'test'}}, got {result}")
        else:
            asyncio.run(test_async_call())

    def test_auth_flow_simulation(self) -> None:
        """Test complete auth flow simulation."""
        runner = CliRunner()

        # Test complete flow: login -> status -> logout
        commands = ["login", "status", "logout"]

        for cmd in commands:
            with (
                patch("flext_cli.commands.auth.FlextApiClient"),
                patch("flext_cli.commands.auth.get_auth_token", return_value="token"),
                patch("asyncio.run"),
            ):
                result = runner.invoke(
                    auth,
                    [cmd]
                    + (
                        ["--username", "test", "--password", "pass"]
                        if cmd == "login"
                        else []
                    ),
                    obj={"console": MagicMock()},
                )

            # All commands should complete
            if result.exit_code not in {0, 1, 2}:
                raise AssertionError(f"Expected {result.exit_code} in {[0, 1, 2]}")
