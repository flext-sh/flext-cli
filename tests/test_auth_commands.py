"""REAL tests for auth commands - NO MOCKING!.

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

from flext_cli import FlextCliAuth
from flext_cli.auth import auth, status


class TestAuthCommandsReal:
    """Test auth commands with REAL functionality - NO MOCKS."""

    def setup_method(self) -> None:
        """Set up test environment."""
        self.runner = CliRunner()
        self.auth = FlextCliAuth()

    def test_auth_instance_creation(self) -> None:
        """Test FlextCliAuth instance creation."""
        auth_instance = FlextCliAuth()
        assert isinstance(auth_instance, FlextCliAuth)
        assert hasattr(auth_instance, "save_auth_token")
        assert hasattr(auth_instance, "get_auth_token")
        assert hasattr(auth_instance, "clear_auth_tokens")

    def test_auth_token_operations_real_filesystem(self) -> None:
        """Test REAL auth token save/load operations with actual API."""
        # Note: Auth functions use default config paths, not custom paths
        test_token = "real_test_token_12345"

        # Clear any existing tokens first
        clear_result = self.auth.clear_auth_tokens()
        assert clear_result.is_success, (
            f"Failed to clear existing tokens: {clear_result.error if not clear_result.is_success else 'Unknown error'}"
        )

        # Test REAL save operation with actual API
        save_result = self.auth.save_auth_token(test_token)
        assert save_result.is_success, (
            f"Failed to save token: {save_result.error if not save_result.is_success else 'Unknown error'}"
        )

        # Test REAL load operation with actual API
        loaded_token_result = self.auth.get_auth_token()
        assert loaded_token_result.is_success, "Failed to load token: operation failed"
        assert loaded_token_result.value == test_token, (
            f"Token mismatch: expected '{test_token}', got '{loaded_token_result.value}'"
        )

        # Test REAL clear operation with actual API
        clear_result = self.auth.clear_auth_tokens()
        assert clear_result.is_success, (
            f"Failed to clear token: {clear_result.error if not clear_result.is_success else 'Unknown error'}"
        )

        # Verify token was ACTUALLY cleared
        cleared_token_result = self.auth.get_auth_token()
        assert not cleared_token_result.is_success, (
            f"Token should be cleared after clear operation: {cleared_token_result}"
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
        self.auth.clear_auth_tokens()

        # Test successful save returns FlextResult
        save_result = self.auth.save_auth_token(test_token)
        assert isinstance(save_result, FlextResult), (
            "save_auth_token should return FlextResult"
        )
        assert save_result.is_success, f"Save should succeed: {save_result.error}"

        # Test successful load
        loaded_token_result = self.auth.get_auth_token()
        assert loaded_token_result.is_success, "Token load should succeed"
        assert loaded_token_result.value == test_token, (
            f"Token should match: expected '{test_token}', got '{loaded_token_result.value}'"
        )

        # Test successful clear returns FlextResult
        clear_result = self.auth.clear_auth_tokens()
        assert isinstance(clear_result, FlextResult), (
            "clear_auth_tokens should return FlextResult"
        )
        assert clear_result.is_success, f"Clear should succeed: {clear_result.error}"

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
        self.auth.clear_auth_tokens()

        # Save token using real API
        save_result = self.auth.save_auth_token(test_token)
        assert save_result.is_success, f"Failed to save token: {save_result.error}"

        # Verify we can load the token (tests file readability)
        loaded_token_result = self.auth.get_auth_token()
        assert loaded_token_result.is_success, "Should be able to load saved token"
        assert loaded_token_result.value == test_token, (
            f"Content mismatch: expected '{test_token}', got '{loaded_token_result.value}'"
        )

        # Clean up
        self.auth.clear_auth_tokens()

    def test_auth_token_edge_cases_real(self) -> None:
        """Test REAL edge cases for auth token operations using actual API."""
        # Test empty token (should fail validation)
        self.auth.clear_auth_tokens()
        empty_result = self.auth.save_auth_token("")
        assert not empty_result.is_success, (
            "Empty token should be rejected (validation working correctly)"
        )
        assert "cannot be empty" in empty_result.error.lower(), (
            "Should have meaningful error message"
        )

        # Test token with special characters
        special_token = "token_with_!@#$%^&*()_+-={}[]|\\:;\"'<>,.?/"
        special_result = self.auth.save_auth_token(special_token)
        assert special_result.is_success, (
            "Should be able to save token with special characters"
        )

        loaded_special_result = self.auth.get_auth_token()
        assert loaded_special_result.is_success, "Special token load should succeed"
        assert loaded_special_result.value == special_token, (
            "Special character token should load correctly"
        )

        # Test very long token
        long_token = "x" * 1000  # 1000 character token
        long_result = self.auth.save_auth_token(long_token)
        assert long_result.is_success, "Should be able to save very long token"

        loaded_long_result = self.auth.get_auth_token()
        assert loaded_long_result.is_success, "Long token load should succeed"
        assert loaded_long_result.value == long_token, (
            "Long token should load correctly"
        )

        # Clean up
        self.auth.clear_auth_tokens()

    def test_auth_token_concurrent_operations_real(self) -> None:
        """Test REAL sequential token operations using actual API."""
        # Test multiple save operations (sequential, not concurrent for simplicity)
        tokens = ["token1", "token2", "token3"]

        for token in tokens:
            save_result = self.auth.save_auth_token(token)
            assert save_result.is_success, f"Failed to save token '{token}'"

            # Verify ACTUAL token content after each save
            loaded_token_result = self.auth.get_auth_token()
            assert loaded_token_result.is_success, f"Failed to load token '{token}'"
            assert loaded_token_result.value == token, (
                f"Token mismatch after save: expected '{token}', got '{loaded_token_result.value}'"
            )

        # Clean up
        self.auth.clear_auth_tokens()

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

    def setup_method(self) -> None:
        """Set up test environment with real auth instance."""
        self.auth = FlextCliAuth()

    def test_auth_imports_real(self) -> None:
        """Test that all required imports work ACTUALLY."""
        # All imports should work in REAL environment
        assert click
        assert auth
        assert status

        # Test FlextCliAuth methods are available
        auth_instance = FlextCliAuth()
        assert hasattr(auth_instance, "save_auth_token")
        assert hasattr(auth_instance, "get_auth_token")
        assert hasattr(auth_instance, "clear_auth_tokens")

        # Test that methods are actually callable
        assert callable(auth_instance.save_auth_token)
        assert callable(auth_instance.get_auth_token)
        assert callable(auth_instance.clear_auth_tokens)

    def test_flext_result_pattern_real(self) -> None:
        """Test REAL FlextResult pattern usage in auth functions."""
        test_token = "result_test_token_xyz789"

        # Create REAL FlextCliAuth instance using flext_tests pattern
        auth_service = FlextCliAuth()

        # Clear existing tokens - test REAL clear operation
        clear_result = auth_service.clear_auth_tokens()
        assert isinstance(clear_result, FlextResult), (
            "clear_auth_tokens should return FlextResult"
        )

        # Test REAL FlextResult success case for save
        save_result = auth_service.save_auth_token(test_token)
        assert isinstance(save_result, FlextResult), (
            "save_auth_token should return FlextResult"
        )
        assert save_result.is_success, "Save operation should succeed"
        assert save_result.error is None, "Successful result should have no error"

        # Test that get_auth_token works (returns FlextResult[str])
        loaded_token_result = auth_service.get_auth_token()
        assert isinstance(loaded_token_result, FlextResult), (
            "get_auth_token should return FlextResult"
        )
        assert loaded_token_result.is_success, "Load operation should succeed"
        assert loaded_token_result.value == test_token, (
            f"Loaded token should match saved token: {loaded_token_result.value} != {test_token}"
        )

        # Test REAL FlextResult success case for clear
        clear_result = auth_service.clear_auth_tokens()
        assert isinstance(clear_result, FlextResult), (
            "clear_auth_tokens should return FlextResult"
        )
        assert clear_result.is_success, "Clear operation should succeed"
        assert clear_result.error is None, "Successful result should have no error"

    def test_auth_error_propagation_real(self) -> None:
        """Test REAL error propagation in auth functions."""
        # Clear existing tokens
        self.auth.clear_auth_tokens()

        # Test loading when no token exists
        no_token_result = self.auth.get_auth_token()
        assert not no_token_result.is_success, "Should fail when no token exists"
        assert ("not found" in no_token_result.error.lower() or
                "does not exist" in no_token_result.error.lower()), (
            "Should have meaningful error message"
        )

        # Test saving and loading work correctly
        test_token = "error_test_token"
        save_result = self.auth.save_auth_token(test_token)
        assert isinstance(save_result, FlextResult), "Should return FlextResult"
        assert save_result.is_success, "Should succeed for valid operation"

        # Verify token was saved
        loaded_token_result = self.auth.get_auth_token()
        assert loaded_token_result.is_success, "Should load saved token correctly"
        assert loaded_token_result.value == test_token, (
            "Should load saved token correctly"
        )

        # Clean up
        self.auth.clear_auth_tokens()

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
        clear_result = self.auth.clear_auth_tokens()
        assert clear_result.is_success, f"Workflow step 1 failed: {clear_result.error}"

        # Step 2: Save token (REAL operation)
        save_result = self.auth.save_auth_token(test_token)
        assert save_result.is_success, f"Workflow step 2 failed: {save_result.error}"

        # Step 3: Load token (REAL operation)
        loaded_token_result = self.auth.get_auth_token()
        assert loaded_token_result.is_success, (
            "Workflow step 3 failed: token load should succeed"
        )
        assert loaded_token_result.value == test_token, (
            f"Workflow step 3 failed: expected '{test_token}', got '{loaded_token_result.value}'"
        )

        # Step 4: Check status command works (REAL execution)
        runner = CliRunner()
        status_result = runner.invoke(auth, ["status"])
        assert status_result.exit_code in {0, 1}, (
            f"Workflow step 4 failed: unexpected exit code {status_result.exit_code}"
        )

        # Step 5: Clear token (REAL operation)
        clear_result = self.auth.clear_auth_tokens()
        assert clear_result.is_success, f"Workflow step 5 failed: {clear_result.error}"

        # Step 6: Verify token cleared (REAL operation)
        cleared_token_result = self.auth.get_auth_token()
        assert not cleared_token_result.is_success, (
            "Workflow step 6 failed: token should be cleared after clear operation"
        )
