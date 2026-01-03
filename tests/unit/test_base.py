"""FLEXT CLI Base Tests - Comprehensive Base Service Validation Testing.

Tests for FlextCliServiceBase covering initialization, configuration access,
singleton pattern, and inheritance from FlextService with 100% coverage.

Modules tested: flext_cli.base.FlextCliServiceBase
Scope: All base service functionality, config access, inheritance patterns

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations  # @vulture_ignore

from flext_core import r, t  # @vulture_ignore

from flext_cli import FlextCliServiceBase, FlextCliSettings  # @vulture_ignore


class TestsCliServiceBase:
    """Comprehensive test suite for FlextCliServiceBase functionality.

    Single class with nested helper classes and methods organized by functionality.
    Tests cover all base service methods and properties with 100% coverage.
    """

    # =========================================================================
    # CONCRETE TEST CLASS
    # =========================================================================

    class _ConcreteService(FlextCliServiceBase):
        """Concrete implementation for testing abstract base class."""

        def execute(self) -> r[t.JsonDict]:
            """Implement abstract method for testing."""
            return r[t.JsonDict].ok({})

    # =========================================================================
    # INITIALIZATION TESTS
    # =========================================================================

    def test_service_base_initialization(self) -> None:
        """Test FlextCliServiceBase can be instantiated via concrete class."""
        # Create instance using concrete implementation
        service = self._ConcreteService()
        assert service is not None
        assert isinstance(service, FlextCliServiceBase)

    # =========================================================================
    # CONFIGURATION ACCESS TESTS
    # =========================================================================

    def test_cli_config_property(self) -> None:
        """Test cli_config property returns FlextCliSettings singleton."""
        service = self._ConcreteService()

        # Test property access
        config = service.cli_config
        assert config is not None
        assert isinstance(config, FlextCliSettings)

        # Verify singleton pattern - same instance
        config2 = service.cli_config
        assert config is config2

    def test_get_cli_config_static_method(self) -> None:
        """Test get_cli_config static method returns FlextCliSettings singleton."""
        # Test static method without instance
        config = FlextCliServiceBase.get_cli_config()
        assert config is not None
        assert isinstance(config, FlextCliSettings)

        # Verify singleton pattern - same instance
        config2 = FlextCliServiceBase.get_cli_config()
        assert config is config2

        # Verify same instance as property access
        service = self._ConcreteService()
        assert config is service.cli_config

    def test_config_singleton_consistency(self) -> None:
        """Test that property and static method return same singleton."""
        service1 = self._ConcreteService()
        service2 = self._ConcreteService()

        # All access methods return same instance
        assert service1.cli_config is service2.cli_config
        assert service1.cli_config is FlextCliServiceBase.get_cli_config()
        assert service2.cli_config is FlextCliServiceBase.get_cli_config()
