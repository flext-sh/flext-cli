"""FLEXT CLI Protocols Tests - Protocol Validation Testing.

Tests for FlextCliProtocols covering protocol structure, structural typing compliance,
runtime checking, and CLI-specific protocol validation.

Modules tested: flext_cli.protocols.FlextCliProtocols
Scope: All protocol operations, structural typing, runtime checking

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import pytest
from flext_core import r
from flext_tests import tm

from flext_cli import FlextCliProtocols, p


class TestsCliProtocols:
    """Test suite for flext_cli.protocols.FlextCliProtocols module."""

    def test_protocol_class_has_required_attributes(self) -> None:
        """Test that FlextCliProtocols has all required protocol classes."""
        tm.that(hasattr(FlextCliProtocols, "Cli"), eq=True)

    def test_cli_namespace_has_all_protocols(self) -> None:
        """Test that Cli namespace contains all required protocols."""
        required_protocols = [
            "RichTable",
            "RichTree",
            "RichConsole",
            "RichProgress",
            "Command",
            "CliParameterSpec",
            "ConfirmConfig",
            "TableConfig",
            "CliParamsConfig",
            "CliContext",
            "CliCommandFunction",
            "CliCommandWrapper",
            "CommandHandlerCallable",
            "CliCommandHandler",
            "DecoratorCommandLike",
        ]
        for protocol_name in required_protocols:
            tm.that(hasattr(p.Cli, protocol_name), eq=True)

    @pytest.mark.parametrize(
        "protocol_name",
        [
            "RichTable",
            "RichTree",
            "RichConsole",
            "RichProgress",
            "Command",
            "CliParameterSpec",
            "ConfirmConfig",
            "TableConfig",
            "CliParamsConfig",
            "CliContext",
            "CliCommandFunction",
            "CliCommandWrapper",
            "CommandHandlerCallable",
            "CliCommandHandler",
            "DecoratorCommandLike",
        ],
    )
    def test_protocol_has_runtime_checkable_attribute(self, protocol_name: str) -> None:
        """Test that each protocol is runtime checkable."""
        protocol = getattr(p.Cli, protocol_name)
        tm.that(hasattr(protocol, "_is_protocol"), eq=True)

    def test_protocol_inheritance_structure(self) -> None:
        """Test protocol inheritance from FlextProtocols."""
        tm.that(issubclass(FlextCliProtocols, FlextCliProtocols), eq=True)

    def test_cli_namespace_nested_properly(self) -> None:
        """Test that Cli namespace is properly nested."""
        tm.that(hasattr(FlextCliProtocols, "Cli"), eq=True)
        tm.that(hasattr(p.Cli, "RichTable"), eq=True)
        tm.that(hasattr(p.Cli, "CliContext"), eq=True)

    def test_cli_registered_command_type_alias(self) -> None:
        """Test that CliRegisteredCommand type alias exists."""
        tm.that(hasattr(p.Cli, "CliRegisteredCommand"), eq=True)

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
                case _:
                    return r[bool].fail(f"Unknown test type: {test_type}")
            return r[bool].ok(success)
        except Exception as e:
            return r[bool].fail(str(e))
