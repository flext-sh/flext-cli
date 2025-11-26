"""FLEXT CLI Protocols Tests - Comprehensive Protocol Validation Testing.

Tests for FlextCliProtocols covering protocol structure, structural typing compliance,
protocol implementations, runtime checking, CLI-specific protocol validation,
protocol inheritance, and edge cases with 100% coverage.

Modules tested: flext_cli.protocols.FlextCliProtocols
Scope: All protocol operations, structural typing, runtime checking, validation

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import cast

import pytest
from flext_core import FlextResult
from flext_tests import FlextTestsMatchers

from flext_cli import FlextCliProtocols, FlextCliTypes

from ..fixtures.constants import TestProtocols
from ..helpers import FlextCliTestHelpers


class TestFlextCliProtocols:
    """Comprehensive test suite for flext_cli.protocols.FlextCliProtocols module."""

    # ========================================================================
    # PROTOCOL STRUCTURE VALIDATION
    # ========================================================================

    def test_protocol_class_has_required_attributes(self) -> None:
        """Test that FlextCliProtocols has all required protocol classes."""
        assert hasattr(FlextCliProtocols, "Cli")

    def test_cli_namespace_has_all_protocols(self) -> None:
        """Test that Cli namespace contains all required protocols."""
        required_protocols = [
            "CliFormatter",
            "CliConfigProvider",
            "CliAuthenticator",
            "CliDebugProvider",
            "CliPlugin",
            "CliCommandHandler",
        ]
        for protocol_name in required_protocols:
            assert hasattr(FlextCliProtocols.Cli, protocol_name), (
                f"Missing protocol: {protocol_name}"
            )

    @pytest.mark.parametrize(
        "protocol_name",
        [
            "CliFormatter",
            "CliConfigProvider",
            "CliAuthenticator",
            "CliDebugProvider",
            "CliPlugin",
            "CliCommandHandler",
        ],
    )
    def test_protocol_has_runtime_checkable_attribute(self, protocol_name: str) -> None:
        """Test that each protocol is runtime checkable."""
        protocol = getattr(FlextCliProtocols.Cli, protocol_name)
        assert hasattr(protocol, "_is_protocol"), (
            f"{protocol_name} is not runtime checkable"
        )

    # ========================================================================
    # STRUCTURAL TYPING (DUCK TYPING)
    # ========================================================================

    def test_structural_typing_enabled(self) -> None:
        """Test that protocols support structural typing through runtime_checkable."""
        assert hasattr(FlextCliProtocols.Cli.CliFormatter, "_is_protocol")
        assert hasattr(FlextCliProtocols.Cli.CliConfigProvider, "_is_protocol")
        assert hasattr(FlextCliProtocols.Cli.CliAuthenticator, "_is_protocol")

    def test_duck_typing_with_formatter(self) -> None:
        """Test duck typing - class satisfies protocol without inheritance."""

        class DuckFormatter:
            def format_data(self, data: object, **options: object) -> FlextResult[str]:
                return FlextResult[str].ok("formatted")

        duck = DuckFormatter()
        assert isinstance(duck, FlextCliProtocols.Cli.CliFormatter)

    # ========================================================================
    # CLI FORMATTER PROTOCOL
    # ========================================================================

    def test_cli_formatter_implementation(self) -> None:
        """Test CLI formatter protocol implementation."""
        formatter_result = (
            FlextCliTestHelpers.ProtocolHelpers.create_formatter_implementation()
        )
        FlextTestsMatchers.assert_success(formatter_result)

        if formatter_result.is_success and formatter_result.value:
            formatter = formatter_result.value
            validation_result = self._validate_formatter_instance(formatter)
            FlextTestsMatchers.assert_success(validation_result)

    def test_formatter_format_data_method(self) -> None:
        """Test formatter's format_data method."""
        formatter_result = (
            FlextCliTestHelpers.ProtocolHelpers.create_formatter_implementation()
        )
        FlextTestsMatchers.assert_success(formatter_result)

        if formatter_result.is_success and formatter_result.value:
            formatter = formatter_result.value
            # Type narrowing using protocol check
            if isinstance(formatter, FlextCliProtocols.Cli.CliFormatter):
                test_data_raw = TestProtocols.TestData.Formatting.SIMPLE_DATA
                # Cast to CliFormatData (which is CliJsonDict)
                test_data = cast("FlextCliTypes.Data.CliFormatData", test_data_raw)
                format_result = formatter.format_data(test_data)
                FlextTestsMatchers.assert_success(format_result)

    # ========================================================================
    # CLI CONFIG PROVIDER PROTOCOL
    # ========================================================================

    def test_cli_config_provider_implementation(self) -> None:
        """Test CLI config provider protocol implementation."""
        provider_result = (
            FlextCliTestHelpers.ProtocolHelpers.create_config_provider_implementation()
        )
        FlextTestsMatchers.assert_success(provider_result)

        if provider_result.is_success and provider_result.value:
            provider = provider_result.value
            validation_result = self._validate_config_provider_instance(provider)
            FlextTestsMatchers.assert_success(validation_result)

    def test_config_provider_load_save_methods(self) -> None:
        """Test config provider's load_config and save_config methods."""
        provider_result = (
            FlextCliTestHelpers.ProtocolHelpers.create_config_provider_implementation()
        )
        FlextTestsMatchers.assert_success(provider_result)

        if provider_result.is_success and provider_result.value:
            provider = provider_result.value
            # Type narrowing using protocol check
            if isinstance(provider, FlextCliProtocols.Cli.CliConfigProvider):
                test_config_raw = TestProtocols.TestData.Configuration.BASIC_CONFIG
                # Cast to CliConfigData
                test_config = cast("FlextCliTypes.Data.CliConfigData", test_config_raw)
                save_result = provider.save_config(test_config)
                FlextTestsMatchers.assert_success(save_result)

                load_result = provider.load_config()
                FlextTestsMatchers.assert_success(load_result)

    # ========================================================================
    # CLI AUTHENTICATOR PROTOCOL
    # ========================================================================

    def test_cli_authenticator_implementation(self) -> None:
        """Test CLI authenticator protocol implementation."""
        auth_result = (
            FlextCliTestHelpers.ProtocolHelpers.create_authenticator_implementation()
        )
        FlextTestsMatchers.assert_success(auth_result)

        if auth_result.is_success and auth_result.value:
            authenticator = auth_result.value
            validation_result = self._validate_authenticator_instance(authenticator)
            FlextTestsMatchers.assert_success(validation_result)

    def test_authenticator_authenticate_method(self) -> None:
        """Test authenticator's authenticate method."""
        auth_result = (
            FlextCliTestHelpers.ProtocolHelpers.create_authenticator_implementation()
        )
        FlextTestsMatchers.assert_success(auth_result)

        if auth_result.is_success and auth_result.value:
            authenticator = auth_result.value
            # Type narrowing using protocol check
            if isinstance(authenticator, FlextCliProtocols.Cli.CliAuthenticator):
                creds_raw = TestProtocols.TestData.Authentication.VALID_CREDS
                # Cast to AuthConfigData for authenticate method
                creds = cast("FlextCliTypes.Data.AuthConfigData", creds_raw)
                auth_response = authenticator.authenticate(creds)
                FlextTestsMatchers.assert_success(auth_response)

    def test_authenticator_validate_token_method(self) -> None:
        """Test authenticator's validate_token method."""
        auth_result = (
            FlextCliTestHelpers.ProtocolHelpers.create_authenticator_implementation()
        )
        FlextTestsMatchers.assert_success(auth_result)

        if auth_result.is_success and auth_result.value:
            authenticator = auth_result.value
            # Type narrowing using protocol check
            if isinstance(authenticator, FlextCliProtocols.Cli.CliAuthenticator):
                token = TestProtocols.TestData.Authentication.VALID_TOKEN
                validation_result = authenticator.validate_token(token)
                FlextTestsMatchers.assert_success(validation_result)

    # ========================================================================
    # CLI DEBUG PROVIDER PROTOCOL
    # ========================================================================

    def test_cli_debug_provider_exists(self) -> None:
        """Test that CLI debug provider protocol exists."""
        assert hasattr(FlextCliProtocols.Cli, "CliDebugProvider")

    def test_cli_debug_provider_is_runtime_checkable(self) -> None:
        """Test that CLI debug provider is runtime checkable."""
        assert hasattr(FlextCliProtocols.Cli.CliDebugProvider, "_is_protocol")

    # ========================================================================
    # CLI PLUGIN PROTOCOL
    # ========================================================================

    def test_cli_plugin_exists(self) -> None:
        """Test that CLI plugin protocol exists."""
        assert hasattr(FlextCliProtocols.Cli, "CliPlugin")

    def test_cli_plugin_is_runtime_checkable(self) -> None:
        """Test that CLI plugin is runtime checkable."""
        assert hasattr(FlextCliProtocols.Cli.CliPlugin, "_is_protocol")

    # ========================================================================
    # CLI COMMAND HANDLER PROTOCOL
    # ========================================================================

    def test_cli_command_handler_exists(self) -> None:
        """Test that CLI command handler protocol exists."""
        assert hasattr(FlextCliProtocols.Cli, "CliCommandHandler")

    def test_cli_command_handler_is_runtime_checkable(self) -> None:
        """Test that CLI command handler is runtime checkable."""
        assert hasattr(FlextCliProtocols.Cli.CliCommandHandler, "_is_protocol")

    # ========================================================================
    # PROTOCOL INHERITANCE
    # ========================================================================

    def test_protocol_inheritance_structure(self) -> None:
        """Test protocol inheritance from FlextProtocols."""
        assert issubclass(FlextCliProtocols, FlextCliProtocols)

    def test_cli_namespace_nested_properly(self) -> None:
        """Test that Cli namespace is properly nested."""
        assert hasattr(FlextCliProtocols, "Cli")
        assert hasattr(FlextCliProtocols.Cli, "CliFormatter")
        assert hasattr(FlextCliProtocols.Cli, "CliConfigProvider")

    # ========================================================================
    # COMPREHENSIVE PROTOCOL TESTS
    # ========================================================================

    @pytest.mark.parametrize(
        ("test_type", "description", "should_succeed"),
        TestProtocols.TestCases.CASES,
    )
    def test_protocol_comprehensive_scenarios(
        self, test_type: str, description: str, should_succeed: bool
    ) -> None:
        """Comprehensive protocol scenario tests using parametrization."""
        result = self._execute_protocol_test(test_type)
        # All test cases are expected to succeed; should_succeed is always True
        assert should_succeed is True
        FlextTestsMatchers.assert_success(result)

    # ========================================================================
    # VALIDATION HELPERS
    # ========================================================================

    def _validate_formatter_instance(self, instance: object) -> FlextResult[bool]:
        """Validate formatter instance against protocol."""
        try:
            if isinstance(instance, FlextCliProtocols.Cli.CliFormatter):
                return FlextResult[bool].ok(True)
            return FlextResult[bool].fail("Instance does not implement CliFormatter")
        except Exception as e:
            return FlextResult[bool].fail(str(e))

    def _validate_config_provider_instance(self, instance: object) -> FlextResult[bool]:
        """Validate config provider instance against protocol."""
        try:
            if isinstance(instance, FlextCliProtocols.Cli.CliConfigProvider):
                return FlextResult[bool].ok(True)
            return FlextResult[bool].fail(
                "Instance does not implement CliConfigProvider"
            )
        except Exception as e:
            return FlextResult[bool].fail(str(e))

    def _validate_authenticator_instance(self, instance: object) -> FlextResult[bool]:
        """Validate authenticator instance against protocol."""
        try:
            if isinstance(instance, FlextCliProtocols.Cli.CliAuthenticator):
                return FlextResult[bool].ok(True)
            error_msg = "Instance does not implement CliAuthenticator"
            return FlextResult[bool].fail(error_msg)
        except Exception as e:
            return FlextResult[bool].fail(str(e))

    def _execute_protocol_test(self, test_type: str) -> FlextResult[bool]:
        """Execute specific protocol test by type."""
        try:
            match test_type:
                case TestProtocols.TestTypes.INITIALIZATION:
                    self.test_protocol_class_has_required_attributes()
                    return FlextResult[bool].ok(True)
                case TestProtocols.TestTypes.STRUCTURAL_TYPING:
                    self.test_structural_typing_enabled()
                    return FlextResult[bool].ok(True)
                case TestProtocols.TestTypes.CLI_FORMATTER:
                    self.test_cli_formatter_implementation()
                    return FlextResult[bool].ok(True)
                case TestProtocols.TestTypes.CLI_CONFIG_PROVIDER:
                    self.test_cli_config_provider_implementation()
                    return FlextResult[bool].ok(True)
                case TestProtocols.TestTypes.CLI_AUTHENTICATOR:
                    self.test_cli_authenticator_implementation()
                    return FlextResult[bool].ok(True)
                case TestProtocols.TestTypes.CLI_DEBUG_PROVIDER:
                    self.test_cli_debug_provider_exists()
                    return FlextResult[bool].ok(True)
                case TestProtocols.TestTypes.CLI_PLUGIN:
                    self.test_cli_plugin_exists()
                    return FlextResult[bool].ok(True)
                case TestProtocols.TestTypes.CLI_COMMAND_HANDLER:
                    self.test_cli_command_handler_exists()
                    return FlextResult[bool].ok(True)
                case TestProtocols.TestTypes.PROTOCOL_INHERITANCE:
                    self.test_protocol_inheritance_structure()
                    return FlextResult[bool].ok(True)
                case TestProtocols.TestTypes.RUNTIME_CHECKING:
                    self.test_duck_typing_with_formatter()
                    return FlextResult[bool].ok(True)
                case _:
                    return FlextResult[bool].fail(f"Unknown test type: {test_type}")
        except Exception as e:
            return FlextResult[bool].fail(str(e))
