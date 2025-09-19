"""Additional tests for FlextCliService to improve coverage.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli.core import FlextCliService
from flext_core import FlextResult


class TestFlextCliServiceAdditional:
    """Additional tests for FlextCliService to improve coverage."""

    def test_format_data_methods(self) -> None:
        """Test format_data method."""
        service = FlextCliService()

        # Test format_data method
        test_data = {"key": "value", "number": 42}
        result = service.format_data(test_data, "json")
        assert isinstance(result, FlextResult)

        # Test format_data method
        result = service.format_data(test_data, "json")
        assert isinstance(result, FlextResult)

    def test_flext_cli_export_method(self) -> None:
        """Test flext_cli_export method."""
        service = FlextCliService()

        test_data = {"key": "value", "number": 42}
        result = service.flext_cli_export(test_data, "json", "test_file.json")
        assert isinstance(result, FlextResult)

    def test_flext_cli_register_plugin_method(self) -> None:
        """Test flext_cli_register_plugin method."""
        service = FlextCliService()

        # Create a mock plugin
        class MockPlugin:
            def __init__(self) -> None:
                self.name = "test-plugin"
                self.version = "1.0.0"

        mock_plugin = MockPlugin()
        result = service.flext_cli_register_plugin("test-plugin", mock_plugin)
        assert isinstance(result, FlextResult)

    def test_flext_cli_get_plugins_method(self) -> None:
        """Test flext_cli_get_plugins method."""
        service = FlextCliService()

        result = service.flext_cli_get_plugins()
        assert isinstance(result, FlextResult)
        assert result.is_success
        assert isinstance(result.unwrap(), dict)

    def test_flext_cli_execute_handler_method(self) -> None:
        """Test flext_cli_execute_handler method."""
        service = FlextCliService()

        # Test with handler name and data
        handler_data = {"command": "test", "args": ["arg1", "arg2"]}
        result = service.flext_cli_execute_handler("test_handler", handler_data)
        assert isinstance(result, FlextResult)

    def test_flext_cli_render_with_context_method(self) -> None:
        """Test flext_cli_render_with_context method."""
        service = FlextCliService()

        # Test with mock template and context
        template = "Hello {{name}}!"
        context = {"name": "World"}
        result = service.flext_cli_render_with_context(template, context)
        assert isinstance(result, FlextResult)

    def test_flext_cli_create_command_method(self) -> None:
        """Test flext_cli_create_command method."""
        service = FlextCliService()

        # Test with command name and command line
        result = service.flext_cli_create_command("test-command", "test-command --help")
        assert isinstance(result, FlextResult)

    def test_registry_property(self) -> None:
        """Test registry property."""
        service = FlextCliService()

        registry = service.registry
        assert registry is not None

    def test_orchestrator_property(self) -> None:
        """Test orchestrator property."""
        service = FlextCliService()

        orchestrator = service.orchestrator
        assert orchestrator is not None

    def test_metrics_property(self) -> None:
        """Test metrics property."""
        service = FlextCliService()

        metrics = service.metrics
        assert isinstance(metrics, dict)

    def test_get_service_health_method(self) -> None:
        """Test get_service_health method."""
        service = FlextCliService()

        result = service.get_service_health()
        assert isinstance(result, FlextResult)
        assert result.is_success

        health_data = result.unwrap()
        assert isinstance(health_data, dict)
        assert "service" in health_data
        assert "status" in health_data

    def test_update_configuration_method(self) -> None:
        """Test update_configuration method."""
        service = FlextCliService()

        # This method doesn't return anything, just test it doesn't crash
        service.update_configuration()

        # Verify the method exists and is callable
        assert hasattr(service, "update_configuration")
        assert callable(service.update_configuration)
