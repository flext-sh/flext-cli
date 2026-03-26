"""FLEXT CLI Protocols Tests - Protocol Validation Testing.

Tests for FlextCliProtocols covering protocol structure and CLI-specific protocol validation.

Modules tested: flext_cli.protocols.FlextCliProtocols
Scope: All remaining protocol operations

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_tests import tm

from flext_cli import FlextCliProtocols, p


class TestsCliProtocols:
    """Test suite for flext_cli.protocols.FlextCliProtocols module."""

    def test_protocol_class_has_required_attributes(self) -> None:
        """Test that FlextCliProtocols has all required protocol classes."""
        tm.that(hasattr(FlextCliProtocols, "Cli"), eq=True)

    def test_cli_namespace_has_remaining_protocols(self) -> None:
        """Test that Cli namespace contains remaining protocols."""
        tm.that(hasattr(p.Cli, "CliCommandWrapper"), eq=True)
        tm.that(hasattr(p.Cli, "CliParamsConfig"), eq=True)

    def test_cli_command_wrapper_protocol(self) -> None:
        """Test CliCommandWrapper protocol exists and is a class."""
        wrapper = p.Cli.CliCommandWrapper
        tm.that(wrapper, none=False)
        tm.that(hasattr(wrapper, "__mro__"), eq=True)

    def test_cli_params_config_protocol(self) -> None:
        """Test CliParamsConfig protocol exists and is a class."""
        config = p.Cli.CliParamsConfig
        tm.that(config, none=False)
        tm.that(hasattr(config, "__mro__"), eq=True)
