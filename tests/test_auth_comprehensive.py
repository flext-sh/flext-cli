"""Comprehensive auth tests using FlextTests* utilities and real functionality.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import pytest
from flext_core import FlextResult
from flext_tests import FlextTestsBuilders, FlextTestsDomains, FlextTestsMatchers

from flext_cli import FlextCliApi, FlextCliAuth, FlextCliMain
from flext_cli.models import FlextCliModels


@pytest.mark.auth
@pytest.mark.real
class TestAuthCore:
    """Core auth functionality tests using FlextTests* utilities."""

    def test_auth_instance_creation(self, cli_auth: FlextCliAuth) -> None:
        """Test FlextCliAuth instance creation."""
        assert isinstance(cli_auth, FlextCliAuth)
        assert hasattr(cli_auth, "save_auth_token")
        assert hasattr(cli_auth, "get_auth_token")
        assert hasattr(cli_auth, "clear_auth_tokens")
        assert hasattr(cli_auth, "get_status")

    def test_auth_token_operations(
        self,
        cli_auth: FlextCliAuth,
        auth_tokens: dict[str, str],
        flext_matchers: FlextTestsMatchers,
    ) -> None:
        """Test auth token save/load operations using FlextTests* utilities."""
        test_token = auth_tokens["valid"]

        # Test save operation
        save_result = cli_auth.save_auth_token(test_token)
        flext_matchers.assert_result_success(save_result)

        # Test load operation
        load_result = cli_auth.get_auth_token()
        flext_matchers.assert_result_success(load_result)
        assert load_result.value == test_token

        # Test clear operation
        clear_result = cli_auth.clear_auth_tokens()
        flext_matchers.assert_result_success(clear_result)

        # Verify token was cleared
        cleared_result = cli_auth.get_auth_token()
        flext_matchers.assert_result_failure(cleared_result)

    def test_auth_status_functionality(
        self,
        cli_auth: FlextCliAuth,
    ) -> None:
        """Test auth status functionality."""
        status_result = cli_auth.get_status()
        assert isinstance(status_result, FlextResult)
        # Status can be success or failure - both are valid states

    def test_auth_token_edge_cases(
        self,
        cli_auth: FlextCliAuth,
        auth_tokens: dict[str, str],
        flext_matchers: FlextTestsMatchers,
    ) -> None:
        """Test auth token edge cases using test data constants."""
        # Test empty token validation
        empty_result = cli_auth.save_auth_token(auth_tokens["empty"])
        flext_matchers.assert_result_failure(empty_result)
        assert "cannot be empty" in str(empty_result.error or "").lower()

        # Test special characters token
        special_result = cli_auth.save_auth_token(auth_tokens["special_chars"])
        flext_matchers.assert_result_success(special_result)

        special_load = cli_auth.get_auth_token()
        flext_matchers.assert_result_success(special_load)
        assert special_load.value == auth_tokens["special_chars"]

        # Test very long token
        long_result = cli_auth.save_auth_token(auth_tokens["long"])
        flext_matchers.assert_result_success(long_result)

        long_load = cli_auth.get_auth_token()
        flext_matchers.assert_result_success(long_load)
        assert long_load.value == auth_tokens["long"]


@pytest.mark.auth
@pytest.mark.cli
class TestAuthCommands:
    """Test auth commands using FlextTests* utilities."""

    def test_auth_group_registration(
        self,
        cli_main: FlextCliMain,
        auth_commands: dict[str, FlextCliModels.CliCommand],
        flext_matchers: FlextTestsMatchers,
    ) -> None:
        """Test auth command group registration."""
        register_result = cli_main.register_command_group(
            "auth",
            auth_commands,
            "Authentication commands",
        )
        flext_matchers.assert_result_success(register_result)

    def test_login_command_functionality(
        self,
        cli_api: FlextCliApi,
        cli_auth: FlextCliAuth,
        auth_tokens: dict[str, str],
        flext_matchers: FlextTestsMatchers,
        flext_builders: FlextTestsBuilders,
    ) -> None:
        """Test login command functionality."""
        test_token = auth_tokens["valid"]

        # Test login data formatting
        login_data = flext_builders.success_result(
            {
                "username": "testuser",
                "authentication_method": "password",
                "status": "success",
            }
        ).value

        format_result = cli_api.format_output(login_data, format_type="json")
        flext_matchers.assert_result_success(format_result)

        # Test token storage
        save_result = cli_auth.save_auth_token(test_token)
        flext_matchers.assert_result_success(save_result)

        get_result = cli_auth.get_auth_token()
        flext_matchers.assert_result_success(get_result)
        assert get_result.value == test_token

    def test_logout_command_functionality(
        self,
        cli_api: FlextCliApi,
        cli_auth: FlextCliAuth,
        auth_tokens: dict[str, str],
        test_messages: dict[str, str],
        flext_matchers: FlextTestsMatchers,
    ) -> None:
        """Test logout command functionality."""
        # Set up token first
        test_token = auth_tokens["valid"]
        cli_auth.save_auth_token(test_token)

        # Test logout functionality
        logout_result = cli_auth.clear_auth_tokens()
        flext_matchers.assert_result_success(logout_result)

        # Verify token cleared
        get_result = cli_auth.get_auth_token()
        flext_matchers.assert_result_failure(get_result)

        # Test success message display
        message_result = cli_api.display_message(
            test_messages["logout_success"], "success"
        )
        flext_matchers.assert_result_success(message_result)

    def test_status_command_functionality(
        self,
        cli_api: FlextCliApi,
        cli_auth: FlextCliAuth,
        auth_tokens: dict[str, str],
        test_messages: dict[str, str],
        flext_matchers: FlextTestsMatchers,
    ) -> None:
        """Test status command functionality."""
        # Test status with token
        test_token = auth_tokens["valid"]
        cli_auth.save_auth_token(test_token)

        status_result = cli_auth.get_status()
        assert isinstance(status_result, FlextResult)

        if status_result.is_success:
            format_result = cli_api.format_output(
                status_result.value,
                format_type="table",
            )
            flext_matchers.assert_result_success(format_result)

        # Clean up
        cli_auth.clear_auth_tokens()

        # Test status without token
        no_auth_message = cli_api.display_message(
            test_messages["not_authenticated"],
            "warning",
        )
        flext_matchers.assert_result_success(no_auth_message)


@pytest.mark.auth
@pytest.mark.integration
class TestAuthIntegration:
    """Integration tests for auth workflow using FlextTests* utilities."""

    def test_complete_auth_workflow(
        self,
        cli_api: FlextCliApi,
        cli_main: FlextCliMain,
        cli_auth: FlextCliAuth,
        auth_commands: dict[str, FlextCliModels.CliCommand],
        auth_tokens: dict[str, str],
        test_messages: dict[str, str],
        flext_matchers: FlextTestsMatchers,
        flext_domains: FlextTestsDomains,
    ) -> None:
        """Test complete auth workflow integration."""
        # Step 1: Register auth commands
        register_result = cli_main.register_command_group(
            "auth",
            auth_commands,
            "Authentication commands",
        )
        flext_matchers.assert_result_success(register_result)

        # Step 2: Create test user data using FlextTestsDomains
        user_data = flext_domains.create_user(
            name="Test User",
            email="test@example.com",
            age=25,
        )

        # Step 3: Format login data
        login_data = {"username": user_data["name"], "status": "success"}
        login_format = cli_api.format_output(login_data, format_type="json")
        flext_matchers.assert_result_success(login_format)

        # Step 4: Token management workflow
        test_token = auth_tokens["workflow"]
        save_result = cli_auth.save_auth_token(test_token)
        flext_matchers.assert_result_success(save_result)

        # Step 5: Status check
        status_result = cli_auth.get_status()
        assert isinstance(status_result, FlextResult)

        # Step 6: Logout
        logout_result = cli_auth.clear_auth_tokens()
        flext_matchers.assert_result_success(logout_result)

        # Step 7: Verify logout success message
        success_msg = cli_api.display_message(test_messages["auth_success"], "success")
        flext_matchers.assert_result_success(success_msg)

    def test_auth_error_scenarios(
        self,
        cli_api: FlextCliApi,
        test_messages: dict[str, str],
        flext_matchers: FlextTestsMatchers,
    ) -> None:
        """Test auth error scenarios."""
        # Test authentication failure message
        error_result = cli_api.display_message(test_messages["auth_failure"], "error")
        flext_matchers.assert_result_success(error_result)

        # Test token expired warning
        warning_result = cli_api.display_message(
            test_messages["token_expired"], "warning"
        )
        flext_matchers.assert_result_success(warning_result)

    def test_auth_output_formatting(
        self,
        cli_api: FlextCliApi,
        cli_auth: FlextCliAuth,
        auth_tokens: dict[str, str],
        flext_matchers: FlextTestsMatchers,
    ) -> None:
        """Test auth output formatting through CLI API."""
        # Set up auth status
        test_token = auth_tokens["integration"]
        cli_auth.save_auth_token(test_token)

        status_result = cli_auth.get_status()

        if status_result.is_success:
            # Test multiple output formats
            for format_type in ["json", "yaml", "table"]:
                format_result = cli_api.format_output(
                    status_result.value,
                    format_type=format_type,
                )
                flext_matchers.assert_result_success(format_result)
                assert isinstance(format_result.value, str)
                assert len(format_result.value) > 0

    @pytest.mark.performance
    def test_auth_concurrent_operations(
        self,
        cli_auth: FlextCliAuth,
        auth_tokens: dict[str, str],
        flext_matchers: FlextTestsMatchers,
    ) -> None:
        """Test sequential auth token operations."""
        tokens = [
            auth_tokens["valid"],
            auth_tokens["integration"],
            auth_tokens["workflow"],
        ]

        for token in tokens:
            save_result = cli_auth.save_auth_token(token)
            flext_matchers.assert_result_success(save_result)

            # Verify each token save
            load_result = cli_auth.get_auth_token()
            flext_matchers.assert_result_success(load_result)
            assert load_result.value == token


@pytest.mark.auth
@pytest.mark.unit
class TestAuthValidation:
    """Auth validation tests using Pydantic models and FlextTests*."""

    def test_auth_result_patterns(
        self,
        cli_auth: FlextCliAuth,
        auth_tokens: dict[str, str],
        flext_matchers: FlextTestsMatchers,
    ) -> None:
        """Test FlextResult patterns in auth operations."""
        test_token = auth_tokens["valid"]

        # Test success pattern
        save_result = cli_auth.save_auth_token(test_token)
        assert isinstance(save_result, FlextResult)
        flext_matchers.assert_result_success(save_result)
        assert save_result.error is None

        # Test load pattern
        load_result = cli_auth.get_auth_token()
        assert isinstance(load_result, FlextResult)
        flext_matchers.assert_result_success(load_result)
        assert load_result.value == test_token

        # Test clear pattern
        clear_result = cli_auth.clear_auth_tokens()
        assert isinstance(clear_result, FlextResult)
        flext_matchers.assert_result_success(clear_result)

        # Test failure pattern
        no_token_result = cli_auth.get_auth_token()
        flext_matchers.assert_result_failure(no_token_result)
        assert (
            "not found" in str(no_token_result.error or "").lower()
            or "does not exist" in str(no_token_result.error or "").lower()
        )

    def test_auth_model_validation(
        self,
        auth_commands: dict[str, FlextCliModels.CliCommand],
        flext_domains: FlextTestsDomains,
    ) -> None:
        """Test auth model validation using Pydantic."""
        # Test command model validation
        for cmd_name, cmd_model in auth_commands.items():
            assert isinstance(cmd_model, FlextCliModels.CliCommand)
            assert cmd_model.name == cmd_name
            assert cmd_model.entry_point is not None
            assert cmd_model.entry_point.startswith("auth.")
            assert cmd_model.command_line is not None
            assert cmd_model.command_line.startswith("auth ")

        # Test user data validation
        user_data = flext_domains.create_user(
            name="Auth Test User",
            email="auth@test.com",
            age=30,
        )
        assert user_data["name"] == "Auth Test User"
        assert user_data["email"] == "auth@test.com"
        assert user_data["age"] == 30
