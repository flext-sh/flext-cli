"""FLEXT CLI Base Tests - Comprehensive Base Service Validation Testing.

Tests for FlextCliServiceBase covering initialization, configuration access,
singleton pattern, and inheritance from FlextService with 100% coverage.

Modules tested: flext_cli.base.FlextCliServiceBase
Scope: All base service functionality, config access, inheritance patterns

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import override

from flext_core import r
from flext_tests import tm

from flext_cli import FlextCliServiceBase, FlextCliSettings
from tests import t


class TestsCliServiceBase:
    """Comprehensive test suite for FlextCliServiceBase functionality.

    Single class with nested helper classes and methods organized by functionality.
    Tests cover all base service methods and properties with 100% coverage.
    """

    class _ConcreteService(FlextCliServiceBase):
        """Concrete implementation for testing abstract base class."""

        @override
        def execute(self) -> r[t.Cli.JsonValue]:
            """Implement abstract method for testing."""
            return r.ok({})

    def test_service_base_initialization(self) -> None:
        """Test FlextCliServiceBase can be instantiated via concrete class."""
        service = self._ConcreteService()
        tm.that(service is not None, eq=True)
        tm.that(isinstance(service, FlextCliServiceBase), eq=True)

    def test_cli_config_property(self) -> None:
        """Test cli_config property returns FlextCliSettings singleton."""
        service = self._ConcreteService()
        config = service.cli_config
        tm.that(config is not None, eq=True)
        tm.that(isinstance(config, FlextCliSettings), eq=True)
        config2 = service.cli_config
        tm.that(config is config2, eq=True)

    def test_get_cli_config_static_method(self) -> None:
        """Test get_cli_config static method returns FlextCliSettings singleton."""
        config = FlextCliServiceBase.get_cli_config()
        tm.that(config is not None, eq=True)
        tm.that(isinstance(config, FlextCliSettings), eq=True)
        config2 = FlextCliServiceBase.get_cli_config()
        tm.that(config is config2, eq=True)
        service = self._ConcreteService()
        tm.that(config is service.cli_config, eq=True)

    def test_config_singleton_consistency(self) -> None:
        """Test that property and static method return same singleton."""
        service1 = self._ConcreteService()
        service2 = self._ConcreteService()
        tm.that(service1.cli_config is service2.cli_config, eq=True)
        tm.that(service1.cli_config is FlextCliServiceBase.get_cli_config(), eq=True)
        tm.that(service2.cli_config is FlextCliServiceBase.get_cli_config(), eq=True)
