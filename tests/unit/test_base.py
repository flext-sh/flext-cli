"""FLEXT CLI Base Tests - Comprehensive Base Service Validation Testing.

Tests for FlextCliServiceBase covering initialization, configuration access,
singleton pattern, and inheritance from s with 100% coverage.

Modules tested: flext_cli.base.FlextCliServiceBase
Scope: All base service functionality, settings access, inheritance patterns

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Mapping
from typing import override

from flext_tests import tm

from flext_cli import FlextCliServiceBase, FlextCliSettings
from flext_core import p, r
from tests import t


class TestsCliServiceBase:
    """Comprehensive test suite for FlextCliServiceBase functionality.

    Single class with nested helper classes and methods organized by functionality.
    Tests cover all base service methods and properties with 100% coverage.
    """

    class _ConcreteService(FlextCliServiceBase):
        """Concrete implementation for testing abstract base class."""

        @override
        def execute(self) -> p.Result[Mapping[str, t.Cli.JsonValue]]:
            """Implement abstract method for testing."""
            return r[Mapping[str, t.Cli.JsonValue]].ok({})

    def test_service_base_initialization(self) -> None:
        """Test FlextCliServiceBase can be instantiated via concrete class."""
        service = self._ConcreteService()
        tm.that(service, none=False)
        tm.that(service, is_=FlextCliServiceBase)

    def test_settings_property(self) -> None:
        """Test settings property returns FlextCliSettings singleton."""
        service = self._ConcreteService()
        settings = service.settings
        tm.that(settings, none=False)
        tm.that(settings, is_=FlextCliSettings)
        config2 = service.settings
        tm.that(settings is config2, eq=True)

    def test_config_singleton_consistency(self) -> None:
        """Test that settings returns same singleton across instances."""
        service1 = self._ConcreteService()
        service2 = self._ConcreteService()
        tm.that(service1.settings is service2.settings, eq=True)
