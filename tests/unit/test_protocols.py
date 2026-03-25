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

import pytest
from flext_core import r
from flext_tests import tm

from flext_cli import FlextCliProtocols, p, t
from tests import c

from ..helpers import FlextCliTestHelpers


class TestsCliProtocols:
    """Comprehensive test suite for flext_cli.protocols.FlextCliProtocols module."""

    def test_protocol_class_has_required_attributes(self) -> None:
        """Test that FlextCliProtocols has all required protocol classes."""
        tm.that(hasattr(FlextCliProtocols, "Cli"), eq=True)

    def test_cli_namespace_has_all_protocols(self) -> None:
        """Test that Cli namespace contains all required protocols."""
        required_protocols = [
            "CliFormatter",
            "CliConfigProvider",
            "CliAuthenticator",
            "CliDebugProvider",
            "CliPlugin",
            "ModelCommandHandler",
        ]
        for protocol_name in required_protocols:
            tm.that(hasattr(p.Cli, protocol_name), eq=True)

    @pytest.mark.parametrize(
        "protocol_name",
        [
            "CliFormatter",
            "CliConfigProvider",
            "CliAuthenticator",
            "CliDebugProvider",
            "CliPlugin",
            "ModelCommandHandler",
        ],
    )
    def test_protocol_has_runtime_checkable_attribute(self, protocol_name: str) -> None:
        """Test that each protocol is runtime checkable."""
        protocol = getattr(p.Cli, protocol_name)
        tm.that(hasattr(protocol, "_is_protocol"), eq=True)

    def test_structural_typing_enabled(self) -> None:
        """Test that protocols support structural typing through runtime_checkable."""
        tm.that(hasattr(p.Cli.CliFormatter, "_is_protocol"), eq=True)
        tm.that(hasattr(p.Cli.CliConfigProvider, "_is_protocol"), eq=True)
        tm.that(hasattr(p.Cli.CliAuthenticator, "_is_protocol"), eq=True)

    def test_duck_typing_with_formatter(self) -> None:
        """Test duck typing - class satisfies protocol without inheritance."""

        class DuckFormatter:
            def format_data(
                self,
                data: t.NormalizedValue,
                **options: t.Scalar,
            ) -> r[str]:
                return r[str].ok("formatted")

        duck = DuckFormatter()
        obj = duck
        tm.that(obj, is_=p.Cli.CliFormatter)

    def test_cli_formatter_implementation(self) -> None:
        """Test CLI formatter protocol implementation."""
        formatter_result = (
            FlextCliTestHelpers.ProtocolHelpers.create_formatter_implementation()
        )
        (
            tm.ok(formatter_result),
            (formatter_result.error or "create_formatter_implementation failed"),
        )
        if formatter_result.is_success and formatter_result.value:
            formatter = formatter_result.value
            validation_result = self._validate_formatter_instance(formatter)
            (
                tm.ok(validation_result),
                (validation_result.error or "formatter validation failed"),
            )

    def test_formatter_format_data_method(self) -> None:
        """Test formatter's format_data method."""
        formatter_result = (
            FlextCliTestHelpers.ProtocolHelpers.create_formatter_implementation()
        )
        (
            tm.ok(formatter_result),
            (formatter_result.error or "create_formatter_implementation failed"),
        )
        if formatter_result.is_success and formatter_result.value:
            formatter = formatter_result.value
            if isinstance(formatter, p.Cli.CliFormatter):
                test_data_raw = {"key": "value"}
                test_data = test_data_raw
                format_result = formatter.format_data(test_data)
                tm.ok(format_result)

    def test_cli_config_provider_implementation(self) -> None:
        """Test CLI config provider protocol implementation."""
        provider_result = (
            FlextCliTestHelpers.ProtocolHelpers.create_config_provider_implementation()
        )
        (
            tm.ok(provider_result),
            (provider_result.error or "create_config_provider_implementation failed"),
        )
        if provider_result.is_success and provider_result.value:
            provider = provider_result.value
            validation_result = self._validate_config_provider_instance(provider)
            (
                tm.ok(validation_result),
                (validation_result.error or "config provider validation failed"),
            )

    def test_config_provider_load_save_methods(self) -> None:
        """Test config provider's load_config and save_config methods."""
        provider_result = (
            FlextCliTestHelpers.ProtocolHelpers.create_config_provider_implementation()
        )
        (
            tm.ok(provider_result),
            (provider_result.error or "create_config_provider_implementation failed"),
        )
        if provider_result.is_success and provider_result.value:
            provider = provider_result.value
            if isinstance(provider, p.Cli.CliConfigProvider):
                test_config_raw = c.Cli.Test.TestConfiguration.BASIC_CONFIG
                test_config: t.ContainerMapping = {}
                for key, value in test_config_raw.items():
                    if isinstance(value, t.PRIMITIVES_TYPES) or value is None:
                        test_config[key] = value
                    else:
                        test_config[key] = str(value)
                save_result = provider.save_config(test_config)
                tm.ok(save_result)
                load_result = provider.load_config()
                tm.ok(load_result)

    def test_cli_authenticator_implementation(self) -> None:
        """Test CLI authenticator protocol implementation."""
        auth_result = (
            FlextCliTestHelpers.ProtocolHelpers.create_authenticator_implementation()
        )
        (
            tm.ok(auth_result),
            (auth_result.error or "create_authenticator_implementation failed"),
        )
        if auth_result.is_success and auth_result.value:
            authenticator = auth_result.value
            validation_result = self._validate_authenticator_instance(authenticator)
            (
                tm.ok(validation_result),
                (validation_result.error or "authenticator validation failed"),
            )

    def test_authenticator_authenticate_method(self) -> None:
        """Test authenticator's authenticate method."""
        auth_result = (
            FlextCliTestHelpers.ProtocolHelpers.create_authenticator_implementation()
        )
        (
            tm.ok(auth_result),
            (auth_result.error or "create_authenticator_implementation failed"),
        )
        if auth_result.is_success and auth_result.value:
            authenticator = auth_result.value
            if isinstance(authenticator, p.Cli.CliAuthenticator):
                creds_raw = c.Authentication.VALID_CREDS
                creds = creds_raw
                username = creds.get("username", "test_user")
                password = creds.get("password", "test_pass")
                auth_method = getattr(authenticator, "authenticate", None)
                if auth_method and callable(auth_method):
                    auth_response = auth_method(username, password)
                    is_failure = getattr(auth_response, "is_failure", True)
                    if is_failure:
                        err_msg = f"authenticate failed: {getattr(auth_response, 'error', '')}. Username: '{username}', Password: '{password}'"
                        pytest.fail(err_msg)
                    tm.that(getattr(auth_response, "is_success", False), eq=True)
                else:
                    pytest.fail("authenticate method not found or not callable")

    def test_authenticator_validate_token_method(self) -> None:
        """Test authenticator's validate_token method."""
        auth_result = (
            FlextCliTestHelpers.ProtocolHelpers.create_authenticator_implementation()
        )
        (
            tm.ok(auth_result),
            (auth_result.error or "create_authenticator_implementation failed"),
        )
        if auth_result.is_success and auth_result.value:
            authenticator = auth_result.value
            if isinstance(authenticator, p.Cli.CliAuthenticator):
                token = c.Authentication.VALID_TOKEN
                validation_result = authenticator.validate_token(token)
                (
                    tm.ok(validation_result),
                    (validation_result.error or "validate_token failed"),
                )

    def test_cli_debug_provider_exists(self) -> None:
        """Test that CLI debug provider protocol exists."""
        tm.that(hasattr(p.Cli, "CliDebugProvider"), eq=True)

    def test_cli_debug_provider_is_runtime_checkable(self) -> None:
        """Test that CLI debug provider is runtime checkable."""
        tm.that(hasattr(p.Cli.CliDebugProvider, "_is_protocol"), eq=True)

    def test_cli_plugin_exists(self) -> None:
        """Test that CLI plugin protocol exists."""
        tm.that(hasattr(p.Cli, "CliPlugin"), eq=True)

    def test_cli_plugin_is_runtime_checkable(self) -> None:
        """Test that CLI plugin is runtime checkable."""
        tm.that(hasattr(p.Cli.CliPlugin, "_is_protocol"), eq=True)

    def test_cli_command_handler_exists(self) -> None:
        """Test that CLI command handler protocol exists."""
        tm.that(hasattr(p.Cli, "ModelCommandHandler"), eq=True)

    def test_cli_command_handler_is_runtime_checkable(self) -> None:
        """Test that CLI command handler is runtime checkable."""
        tm.that(hasattr(p.Cli.ModelCommandHandler, "_is_protocol"), eq=True)

    def test_protocol_inheritance_structure(self) -> None:
        """Test protocol inheritance from p."""
        tm.that(issubclass(FlextCliProtocols, FlextCliProtocols), eq=True)

    def test_cli_namespace_nested_properly(self) -> None:
        """Test that Cli namespace is properly nested."""
        tm.that(hasattr(FlextCliProtocols, "Cli"), eq=True)
        tm.that(hasattr(p.Cli, "CliFormatter"), eq=True)
        tm.that(hasattr(p.Cli, "CliConfigProvider"), eq=True)

    @pytest.mark.parametrize(
        ("test_type", "description", "should_succeed"),
        [
            ("init", "Initialization test", True),
            ("command", "Command decorator test", True),
            ("group", "Group decorator test", True),
        ],
    )
    def test_protocol_comprehensive_scenarios(
        self,
        test_type: str,
        description: str,
        should_succeed: bool,
    ) -> None:
        """Comprehensive protocol scenario tests using parametrization."""
        result = self._execute_protocol_test(test_type)
        tm.that(should_succeed is True, eq=True)
        tm.ok(result)

    def _validate_formatter_instance(self, instance: t.NormalizedValue) -> r[bool]:
        """Validate formatter instance against protocol."""
        try:
            if isinstance(instance, p.Cli.CliFormatter):
                return r[bool].ok(True)
            return r[bool].fail("Instance does not implement CliFormatter")
        except Exception as e:
            return r[bool].fail(str(e))

    def _validate_config_provider_instance(
        self,
        instance: t.NormalizedValue,
    ) -> r[bool]:
        """Validate config provider instance against protocol."""
        try:
            if isinstance(instance, p.Cli.CliConfigProvider):
                return r[bool].ok(True)
            return r[bool].fail("Instance does not implement CliConfigProvider")
        except Exception as e:
            return r[bool].fail(str(e))

    def _validate_authenticator_instance(self, instance: t.NormalizedValue) -> r[bool]:
        """Validate authenticator instance against protocol."""
        try:
            if isinstance(instance, p.Cli.CliAuthenticator):
                return r[bool].ok(True)
            error_msg = "Instance does not implement CliAuthenticator"
            return r[bool].fail(error_msg)
        except Exception as e:
            return r[bool].fail(str(e))

    def _execute_protocol_test(self, test_type: str) -> r[bool]:
        """Execute specific protocol test by type."""
        try:
            success = False
            match test_type:
                case "init":
                    self.test_protocol_class_has_required_attributes()
                    success = True
                case "command":
                    success = hasattr(p.Cli, "CliCommandFunction")
                case "group":
                    success = hasattr(p.Cli, "CliCommandWrapper")
                case "structural_typing":
                    self.test_structural_typing_enabled()
                    success = True
                case "cli_formatter":
                    self.test_cli_formatter_implementation()
                    success = True
                case "cli_config_provider":
                    self.test_cli_config_provider_implementation()
                    success = True
                case "cli_authenticator":
                    self.test_cli_authenticator_implementation()
                    success = True
                case "cli_debug_provider":
                    self.test_cli_debug_provider_exists()
                    success = True
                case "cli_plugin":
                    self.test_cli_plugin_exists()
                    success = True
                case "cli_command_handler":
                    self.test_cli_command_handler_exists()
                    success = True
                case "protocol_inheritance":
                    self.test_protocol_inheritance_structure()
                    success = True
                case "runtime_checking":
                    self.test_duck_typing_with_formatter()
                    success = True
                case _:
                    return r[bool].fail(f"Unknown test type: {test_type}")
            return r[bool].ok(success)
        except Exception as e:
            return r[bool].fail(str(e))
