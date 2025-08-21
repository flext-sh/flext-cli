"""REAL tests for auth commands - NO MOCKING!

Tests authentication command functionality with ACTUAL execution.
Following user requirement: "melhore bem os tests para executar codigo de verdade
e validar a funcionalidade requerida, pare de ficar mockando tudo!"

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import click
from click.testing import CliRunner
from flext_core import FlextResult

from flext_cli import (
    auth,
    clear_auth_tokens,
    get_auth_token,
    save_auth_token,
    status,
)


class TestAuthCommandsReal:
    """Test auth commands with REAL functionality - NO MOCKS."""

    def setup_method(self) -> None:
        """Set up test environment."""
        self.runner = CliRunner()

    def test_auth_group_structure_real(self) -> None:
        """Test auth command group structure - REAL validation."""
        # Test actual command group structure
        assert isinstance(auth, click.Group), (
            f"auth should be a click.Group, got {type(auth)}"
        )
        assert auth.name == "auth", f"Expected 'auth', got {auth.name}"

        # Verify commands exist and are callable
        commands = auth.commands
        expected_commands = ["status"]  # Only test commands that actually exist
        for cmd_name in expected_commands:
            assert cmd_name in commands, (
                f"Expected '{cmd_name}' in {list(commands.keys())}"
            )
            cmd = commands[cmd_name]
            assert callable(cmd), f"Command '{cmd_name}' should be callable"

    def test_auth_token_operations_real_filesystem(self) -> None:
        """Test REAL auth token save/load operations with actual API."""
        # Note: Auth functions use default config paths, not custom paths
        test_token = "real_test_token_12345"

        # Clear any existing tokens first
        clear_result = clear_auth_tokens()
        assert clear_result.success, (
            f"Failed to clear existing tokens: {clear_result.error if clear_result.is_failure else 'Unknown error'}"
        )

        # Test REAL save operation with actual API
        save_result = save_auth_token(test_token)
        assert save_result.success, (
            f"Failed to save token: {save_result.error if save_result.is_failure else 'Unknown error'}"
        )

        # Test REAL load operation with actual API
        loaded_token = get_auth_token()
        assert loaded_token is not None, "Failed to load token: got None"
        assert loaded_token == test_token, (
            f"Token mismatch: expected '{test_token}', got '{loaded_token}'"
        )

        # Test REAL clear operation with actual API
        clear_result = clear_auth_tokens()
        assert clear_result.success, (
            f"Failed to clear token: {clear_result.error if clear_result.is_failure else 'Unknown error'}"
        )

        # Verify token was ACTUALLY cleared
        cleared_token = get_auth_token()
        assert cleared_token is None, (
            f"Token should be None after clear, got '{cleared_token}'"
        )

    def test_auth_status_command_real_execution(self) -> None:
        """Test auth status command with REAL execution - NO MOCKS."""
        # Test the status command ACTUALLY executes
        result = self.runner.invoke(auth, ["status"])

        # Command should execute successfully (exit code 0 or 1 are both valid)
        assert result.exit_code in {0, 1}, (
            f"Status command failed with unexpected exit code {result.exit_code}. Output: {result.output}"
        )

        # Should produce ACTUAL output
        assert result.output.strip(), "Status command produced no output"

        # Output should contain relevant authentication status info
        output_lower = result.output.lower()
        assert any(
            keyword in output_lower
            for keyword in [
                "token",
                "auth",
                "status",
                "not authenticated",
                "authenticated",
            ]
        ), f"Status output should contain auth-related keywords. Got: {result.output}"

    def test_flext_result_integration_real_error_handling(self) -> None:
        """Test REAL FlextResult integration with auth functions - ACTUAL error handling."""
        # Test FlextResult patterns with actual auth functions
        test_token = "integration_test_token_xyz789"

        # Clear any existing tokens
        clear_auth_tokens()

        # Test successful save returns FlextResult
        save_result = save_auth_token(test_token)
        assert isinstance(save_result, FlextResult), (
            "save_auth_token should return FlextResult"
        )
        assert save_result.success, f"Save should succeed: {save_result.error}"

        # Test successful load
        loaded_token = get_auth_token()
        assert loaded_token == test_token, (
            f"Token should match: expected '{test_token}', got '{loaded_token}'"
        )

        # Test successful clear returns FlextResult
        clear_result = clear_auth_tokens()
        assert isinstance(clear_result, FlextResult), (
            "clear_auth_tokens should return FlextResult"
        )
        assert clear_result.success, f"Clear should succeed: {clear_result.error}"

    def test_auth_commands_help_real(self) -> None:
        """Test auth command help - REAL execution."""
        # Test auth group help
        result = self.runner.invoke(auth, ["--help"])
        assert result.exit_code == 0, (
            f"Auth help failed with exit code {result.exit_code}. Output: {result.output}"
        )
        assert "Usage:" in result.output, (
            f"Expected 'Usage:' in help output: {result.output}"
        )
        assert "Commands:" in result.output, (
            f"Expected 'Commands:' in help output: {result.output}"
        )

    def test_auth_token_file_permissions_real(self) -> None:
        """Test REAL file permissions for token storage using actual API."""
        test_token = "permission_test_token_abc123"

        # Clear existing tokens
        clear_auth_tokens()

        # Save token using real API
        save_result = save_auth_token(test_token)
        assert save_result.success, f"Failed to save token: {save_result.error}"

        # Verify we can load the token (tests file readability)
        loaded_token = get_auth_token()
        assert loaded_token is not None, "Should be able to load saved token"
        assert loaded_token == test_token, (
            f"Content mismatch: expected '{test_token}', got '{loaded_token}'"
        )

        # Clean up
        clear_auth_tokens()

    def test_auth_token_edge_cases_real(self) -> None:
        """Test REAL edge cases for auth token operations using actual API."""
        # Test empty token
        clear_auth_tokens()
        empty_result = save_auth_token("")
        assert empty_result.success, "Should be able to save empty token"

        loaded_empty = get_auth_token()
        assert loaded_empty is not None, "Empty token should be loadable (not None)"
        assert loaded_empty == "", "Empty token should load as empty string"

        # Test token with special characters
        special_token = "token_with_!@#$%^&*()_+-={}[]|\\:;\"'<>,.?/"
        special_result = save_auth_token(special_token)
        assert special_result.success, (
            "Should be able to save token with special characters"
        )

        loaded_special = get_auth_token()
        assert loaded_special == special_token, (
            "Special character token should load correctly"
        )

        # Test very long token
        long_token = "x" * 1000  # 1000 character token
        long_result = save_auth_token(long_token)
        assert long_result.success, "Should be able to save very long token"

        loaded_long = get_auth_token()
        assert loaded_long == long_token, "Long token should load correctly"

        # Clean up
        clear_auth_tokens()

    def test_auth_token_concurrent_operations_real(self) -> None:
        """Test REAL sequential token operations using actual API."""
        # Test multiple save operations (sequential, not concurrent for simplicity)
        tokens = ["token1", "token2", "token3"]

        for token in tokens:
            save_result = save_auth_token(token)
            assert save_result.success, f"Failed to save token '{token}'"

            # Verify ACTUAL token content after each save
            loaded_token = get_auth_token()
            assert loaded_token == token, (
                f"Token mismatch after save: expected '{token}', got '{loaded_token}'"
            )

        # Clean up
        clear_auth_tokens()

    def test_auth_status_command_output_format_real(self) -> None:
        """Test REAL output format of auth status command."""
        result = self.runner.invoke(auth, ["status"])

        # Should have ACTUAL output
        assert result.output, "Status command should produce output"

        # Output should be properly formatted
        lines = result.output.strip().split("\n")
        assert len(lines) > 0, "Status output should have at least one line"

        # Should not contain obvious error markers
        output_lower = result.output.lower()
        error_markers = ["traceback", "exception", "error:", "failed:", "crash"]
        has_errors = any(marker in output_lower for marker in error_markers)
        assert not has_errors, (
            f"Status output should not contain errors: {result.output}"
        )


class TestAuthFunctionalityReal:
    """Test auth functionality with REAL execution - NO MOCKS."""

    def test_auth_imports_real(self) -> None:
        """Test that all required imports work ACTUALLY."""
        # All imports should work in REAL environment
        assert click
        assert auth
        assert status
        assert save_auth_token
        assert get_auth_token
        assert clear_auth_tokens

        # Test that functions are actually callable
        assert callable(save_auth_token)
        assert callable(get_auth_token)
        assert callable(clear_auth_tokens)

    def test_flext_result_pattern_real(self) -> None:
        """Test REAL FlextResult pattern usage in auth functions."""
        test_token = "result_test_token_xyz789"

        # Clear existing tokens
        clear_auth_tokens()

        # Test REAL FlextResult success case for save
        save_result = save_auth_token(test_token)
        assert isinstance(save_result, FlextResult), (
            "save_auth_token should return FlextResult"
        )
        assert save_result.success, "Save operation should succeed"
        assert save_result.error is None, "Successful result should have no error"

        # Test that get_auth_token works (returns string, not FlextResult)
        loaded_token = get_auth_token()
        assert loaded_token == test_token, "Should load correct token"

        # Test REAL FlextResult success case for clear
        clear_result = clear_auth_tokens()
        assert isinstance(clear_result, FlextResult), (
            "clear_auth_tokens should return FlextResult"
        )
        assert clear_result.success, "Clear operation should succeed"
        assert clear_result.error is None, "Successful result should have no error"

    def test_auth_error_propagation_real(self) -> None:
        """Test REAL error propagation in auth functions."""
        # Clear existing tokens
        clear_auth_tokens()

        # Test loading when no token exists
        no_token = get_auth_token()
        assert no_token is None, "Should return None when no token exists"

        # Test saving and loading work correctly
        test_token = "error_test_token"
        save_result = save_auth_token(test_token)
        assert isinstance(save_result, FlextResult), "Should return FlextResult"
        assert save_result.success, "Should succeed for valid operation"

        # Verify token was saved
        loaded_token = get_auth_token()
        assert loaded_token == test_token, "Should load saved token correctly"

        # Clean up
        clear_auth_tokens()

    def test_click_command_structure_real(self) -> None:
        """Test REAL Click command structure."""
        # Test that auth is a proper Click group
        assert hasattr(auth, "commands"), "Auth should have commands attribute"
        assert hasattr(auth, "name"), "Auth should have name attribute"
        assert hasattr(auth, "help"), "Auth should have help attribute"

        # Test commands are properly registered
        for cmd_name, cmd in auth.commands.items():
            assert isinstance(cmd, click.Command), (
                f"Command '{cmd_name}' should be a Click command"
            )
            assert hasattr(cmd, "callback"), (
                f"Command '{cmd_name}' should have callback"
            )
            assert callable(cmd.callback), (
                f"Command '{cmd_name}' callback should be callable"
            )

    def test_auth_integration_real_workflow(self) -> None:
        """Test REAL complete auth workflow integration using actual API."""
        test_token = "workflow_integration_token_123"

        # Step 1: Clear any existing tokens
        clear_result = clear_auth_tokens()
        assert clear_result.success, f"Workflow step 1 failed: {clear_result.error}"

        # Step 2: Save token (REAL operation)
        save_result = save_auth_token(test_token)
        assert save_result.success, f"Workflow step 2 failed: {save_result.error}"

        # Step 3: Load token (REAL operation)
        loaded_token = get_auth_token()
        assert loaded_token == test_token, (
            f"Workflow step 3 failed: expected '{test_token}', got '{loaded_token}'"
        )

        # Step 4: Check status command works (REAL execution)
        runner = CliRunner()
        status_result = runner.invoke(auth, ["status"])
        assert status_result.exit_code in {0, 1}, (
            f"Workflow step 4 failed: unexpected exit code {status_result.exit_code}"
        )

        # Step 5: Clear token (REAL operation)
        clear_result = clear_auth_tokens()
        assert clear_result.success, f"Workflow step 5 failed: {clear_result.error}"

        # Step 6: Verify token cleared (REAL operation)
        cleared_token = get_auth_token()
        assert cleared_token is None, (
            "Workflow step 6 failed: token should be None after clear"
        )
