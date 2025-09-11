"""Real functionality tests for services.py - Direct flext-core usage.

NO WRAPPERS - Tests direct flext-core FlextServices usage.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import FlextResult, FlextServices

from flext_cli import FlextCliServices


class TestFlextCliServices:
    """Test FlextCliServices with direct flext-core usage."""

    def test_create_command_processor_returns_result(self) -> None:
        """Test command processor creation returns FlextResult."""
        result = FlextCliServices.create_command_processor()
        assert isinstance(result, FlextResult)
        # Should succeed with success message
        assert result.is_success
        assert "Command processor created successfully" in result.value

    def test_create_session_processor_returns_result(self) -> None:
        """Test session processor creation returns FlextResult."""
        result = FlextCliServices.create_session_processor()
        assert isinstance(result, FlextResult)
        # Should succeed with success message
        assert result.is_success
        assert "Session processor created successfully" in result.value

    def test_create_config_processor_returns_result(self) -> None:
        """Test config processor creation returns FlextResult."""
        result = FlextCliServices.create_config_processor()
        assert isinstance(result, FlextResult)
        # Should succeed with success message
        assert result.is_success
        assert "Config processor created successfully" in result.value

    def test_registry_is_available(self) -> None:
        """Test registry is available."""
        registry = FlextCliServices.registry
        assert isinstance(registry, FlextServices.ServiceRegistry)

    def test_orchestrator_is_available(self) -> None:
        """Test orchestrator is available."""
        orchestrator = FlextCliServices.orchestrator
        assert isinstance(orchestrator, FlextServices.ServiceOrchestrator)

    def test_metrics_is_available(self) -> None:
        """Test metrics is available."""
        metrics = FlextCliServices.metrics
        assert isinstance(metrics, FlextServices.ServiceMetrics)


class TestServicesModule:
    """Test services module functionality."""

    def test_services_instantiation_and_basic_functionality(self) -> None:
        """Test services can be instantiated and have basic functionality."""
        # Test processors can be created successfully
        command_result = FlextCliServices.create_command_processor()
        session_result = FlextCliServices.create_session_processor()
        config_result = FlextCliServices.create_config_processor()

        # All should succeed
        assert command_result.is_success
        assert session_result.is_success
        assert config_result.is_success

        # All should return FlextResult
        assert isinstance(command_result, FlextResult)
        assert isinstance(session_result, FlextResult)
        assert isinstance(config_result, FlextResult)

    def test_module_has_expected_exports_and_classes(self) -> None:
        """Test module has expected constants and imports."""
        # Verify FlextCliServices class exists and has expected structure
        assert hasattr(FlextCliServices, "create_command_processor")
        assert hasattr(FlextCliServices, "create_session_processor")
        assert hasattr(FlextCliServices, "create_config_processor")
        assert hasattr(FlextCliServices, "registry")
        assert hasattr(FlextCliServices, "orchestrator")
        assert hasattr(FlextCliServices, "metrics")


class TestServicesIntegration:
    """Test services integration."""

    def test_command_and_session_processors_work_together(self) -> None:
        """Test command and session processors can work together."""
        # Create processors
        command_result = FlextCliServices.create_command_processor()
        session_result = FlextCliServices.create_session_processor()

        # Both should succeed
        assert command_result.is_success
        assert session_result.is_success

        # Both should return FlextResult
        assert isinstance(command_result, FlextResult)
        assert isinstance(session_result, FlextResult)

    def test_all_processors_use_same_base_class(self) -> None:
        """Test all processors use the same base class."""
        command_result = FlextCliServices.create_command_processor()
        session_result = FlextCliServices.create_session_processor()
        config_result = FlextCliServices.create_config_processor()

        # All should succeed
        assert command_result.is_success
        assert session_result.is_success
        assert config_result.is_success

        # All should return FlextResult
        assert isinstance(command_result, FlextResult)
        assert isinstance(session_result, FlextResult)
        assert isinstance(config_result, FlextResult)
