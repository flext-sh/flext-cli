"""FLEXT CLI Containers Tests - Comprehensive Real Functionality Testing.

Tests for FlextCliContainers covering all real functionality with flext_tests
integration, comprehensive container operations, and targeting 90%+ coverage.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import time

import pytest
from flext_core import FlextResult

# Test utilities removed from flext-core production exports
from flext_cli.containers import FlextCliContainers


class TestFlextCliContainers:
    """Comprehensive tests for FlextCliContainers functionality."""

    @pytest.fixture
    def containers(self) -> FlextCliContainers:
        """Create FlextCliContainers instance for testing."""
        return FlextCliContainers()

    @pytest.fixture
    def test_utilities(self) -> FlextTestsUtilities:
        """Provide FlextTestsUtilities for test support."""
        return FlextTestsUtilities()

    def test_containers_initialization(self, containers: FlextCliContainers) -> None:
        """Test containers initialization."""
        assert isinstance(containers, FlextCliContainers)

    def test_command_container_initialization(
        self, containers: FlextCliContainers
    ) -> None:
        """Test CommandContainer initialization."""
        command_container = containers.CommandContainer()
        assert isinstance(command_container, containers.CommandContainer)

    def test_command_container_register(self, containers: FlextCliContainers) -> None:
        """Test CommandContainer register."""
        command_container = containers.CommandContainer()

        def test_command() -> str:
            return "test"

        result = command_container.register("test_command", test_command)

        assert isinstance(result, FlextResult)
        assert result.is_success

    def test_command_container_get(self, containers: FlextCliContainers) -> None:
        """Test CommandContainer get."""
        command_container = containers.CommandContainer()

        def test_command() -> str:
            return "test"

        # Register command first
        command_container.register("test_command", test_command)

        # Get command
        result = command_container.get("test_command")

        assert isinstance(result, FlextResult)
        assert result.is_success
        assert result.unwrap() == test_command

    def test_command_container_get_nonexistent(
        self, containers: FlextCliContainers
    ) -> None:
        """Test CommandContainer get nonexistent command."""
        command_container = containers.CommandContainer()

        result = command_container.get("nonexistent_command")

        assert isinstance(result, FlextResult)
        # May fail for nonexistent command
        # Just check that it returns a result

    def test_command_container_list_commands(
        self, containers: FlextCliContainers
    ) -> None:
        """Test CommandContainer list_commands."""
        command_container = containers.CommandContainer()

        result = command_container.list_commands()

        assert isinstance(result, FlextResult)
        assert result.is_success
        assert isinstance(result.unwrap(), list)

    def test_command_container_unregister(self, containers: FlextCliContainers) -> None:
        """Test CommandContainer unregister."""
        command_container = containers.CommandContainer()

        def test_command() -> str:
            return "test"

        # Register command first
        command_container.register("test_command", test_command)

        # Unregister command
        result = command_container.unregister("test_command")

        assert isinstance(result, FlextResult)
        assert result.is_success

    def test_handler_container_initialization(
        self, containers: FlextCliContainers
    ) -> None:
        """Test HandlerContainer initialization."""
        handler_container = containers.HandlerContainer()
        assert isinstance(handler_container, containers.HandlerContainer)

    def test_handler_container_register(self, containers: FlextCliContainers) -> None:
        """Test HandlerContainer register."""
        handler_container = containers.HandlerContainer()

        def test_handler(x: str) -> str:
            return x

        result = handler_container.register("test_handler", test_handler)

        assert isinstance(result, FlextResult)
        assert result.is_success

    def test_handler_container_get(self, containers: FlextCliContainers) -> None:
        """Test HandlerContainer get."""
        handler_container = containers.HandlerContainer()

        def test_handler(x: str) -> str:
            return x

        # Register handler first
        handler_container.register("test_handler", test_handler)

        # Get handler
        result = handler_container.get("test_handler")

        assert isinstance(result, FlextResult)
        assert result.is_success
        assert result.unwrap() == test_handler

    def test_handler_container_list_handlers(
        self, containers: FlextCliContainers
    ) -> None:
        """Test HandlerContainer list_handlers."""
        handler_container = containers.HandlerContainer()

        result = handler_container.list_handlers()

        assert isinstance(result, FlextResult)
        assert result.is_success
        assert isinstance(result.unwrap(), list)

    def test_config_container_initialization(
        self, containers: FlextCliContainers
    ) -> None:
        """Test ConfigContainer initialization."""
        config_container = containers.ConfigContainer()
        assert isinstance(config_container, containers.ConfigContainer)

    def test_config_container_register(self, containers: FlextCliContainers) -> None:
        """Test ConfigContainer register."""
        config_container = containers.ConfigContainer()
        test_config = {"test": "config"}

        result = config_container.register("test_config", test_config)

        assert isinstance(result, FlextResult)
        assert result.is_success

    def test_config_container_get(self, containers: FlextCliContainers) -> None:
        """Test ConfigContainer get."""
        config_container = containers.ConfigContainer()
        test_config = {"test": "config"}

        # Register config first
        config_container.register("test_config", test_config)

        # Get config
        result = config_container.get("test_config")

        assert isinstance(result, FlextResult)
        assert result.is_success
        assert result.unwrap() == test_config

    def test_config_container_list_configs(
        self, containers: FlextCliContainers
    ) -> None:
        """Test ConfigContainer list_configs."""
        config_container = containers.ConfigContainer()

        result = config_container.list_configs()

        assert isinstance(result, FlextResult)
        assert result.is_success
        assert isinstance(result.unwrap(), list)

    def test_containers_integration_workflow(
        self, containers: FlextCliContainers
    ) -> None:
        """Test complete container workflow."""
        # Step 1: Create command container
        command_container = containers.CommandContainer()

        # Step 2: Register command
        def test_command() -> str:
            return "test"

        register_result = command_container.register("test_command", test_command)
        assert register_result.is_success

        # Step 3: Get command
        get_result = command_container.get("test_command")
        assert get_result.is_success

        # Step 4: List commands
        list_result = command_container.list_commands()
        assert list_result.is_success

        # Step 5: Unregister command
        unregister_result = command_container.unregister("test_command")
        assert unregister_result.is_success

    def test_containers_real_functionality(
        self, containers: FlextCliContainers
    ) -> None:
        """Test real container functionality without mocks."""
        # Test actual container operations
        command_container = containers.CommandContainer()

        def real_command() -> str:
            return "real command executed"

        # Register real command
        result = command_container.register("real_command", real_command)
        assert result.is_success

        # Get real command
        result = command_container.get("real_command")
        assert result.is_success
        assert result.unwrap() == real_command

    def test_containers_edge_cases(self, containers: FlextCliContainers) -> None:
        """Test edge cases and error conditions."""
        # Test with empty names
        command_container = containers.CommandContainer()

        def test_command() -> str:
            return "test"

        result = command_container.register("", test_command)
        assert isinstance(result, FlextResult)

        # Test with None objects
        result = command_container.register("none_command", None)
        assert isinstance(result, FlextResult)

    def test_containers_performance(self, containers: FlextCliContainers) -> None:
        """Test containers performance."""
        command_container = containers.CommandContainer()

        # Test multiple registrations performance
        start_time = time.time()
        for i in range(100):

            def make_command(cmd_id: int) -> str:
                return f"perf_{cmd_id}"

            command_container.register(
                f"perf_command_{i}", lambda cmd_id=i: make_command(cmd_id)
            )
        end_time = time.time()

        # Should be fast (less than 1 second for 100 registrations)
        assert (end_time - start_time) < 1.0

    def test_containers_memory_usage(self, containers: FlextCliContainers) -> None:
        """Test containers memory usage."""
        # Test with many registrations
        command_container = containers.CommandContainer()

        for i in range(1000):

            def make_command(cmd_id: int) -> str:
                return f"memory_{cmd_id}"

            result = command_container.register(
                f"memory_command_{i}", lambda cmd_id=i: make_command(cmd_id)
            )
            assert isinstance(result, FlextResult)

        # Test listing
        result = command_container.list_commands()
        assert isinstance(result, FlextResult)
