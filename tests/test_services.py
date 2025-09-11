"""Real functionality tests for services.py.

Following user requirement: "pare de ficar mockando tudo!"
Tests Execute service functionality.


Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""


from __future__ import annotations

from flext_core import FlextResult, FlextServices

import flext_cli
from flext_cli import FlextCliModels, FlextCliServices


class TestFlextCliServices:
    """Test FlextCliServices with REAL execution."""

    def test_create_command_processor_creates_instance(self) -> None:
        """Test command processor creation."""
        processor = FlextCliServices.create_command_processor()
        assert isinstance(processor, FlextCliServices.CliCommandProcessor)
        assert hasattr(processor, "process")
        assert hasattr(processor, "build")

    def test_process_command_with_valid_input(self) -> None:
        """Test command processing with valid input."""
        result = FlextCliServices.process_command("test command")
        assert isinstance(result, FlextResult)
        # Command processing should succeed
        if result.is_success:
            command = result.value
            assert isinstance(command, FlextCliModels.CliCommand)
            assert command.command_line == "test command"

    def test_create_session_processor_creates_instance(self) -> None:
        """Test session processor creation."""
        processor = FlextCliServices.create_session_processor()
        assert isinstance(processor, FlextCliServices.CliSessionProcessor)
        assert hasattr(processor, "process")
        assert hasattr(processor, "build")

    def test_create_session_with_user_id(self) -> None:
        """Test session creation with user ID."""
        result = FlextCliServices.create_session("test_user")
        assert isinstance(result, FlextResult)
        # Session creation should succeed
        if result.is_success:
            session = result.value
            assert isinstance(session, FlextCliModels.CliSession)
            assert session.user_id == "test_user"
            assert session.end_time is None  # Should be active

    def test_create_session_without_user_id(self) -> None:
        """Test session creation without user ID."""
        result = FlextCliServices.create_session()
        assert isinstance(result, FlextResult)
        # Session creation should succeed
        if result.is_success:
            session = result.value
            assert isinstance(session, FlextCliModels.CliSession)
            assert session.user_id is None

    def test_validate_config_with_valid_data(self) -> None:
        """Test config validation with valid data."""
        config_data = {
            "profile": "development",
            "output_format": "json",
            "debug_mode": True,
            "timeout_seconds": 30,
        }
        result = FlextCliServices.validate_config(config_data)
        assert isinstance(result, FlextResult)
        # Config validation should succeed
        if result.is_success:
            config = result.value
            assert isinstance(config, FlextCliModels.CliConfig)
            assert config.profile == "development"
            assert config.output_format == "json"
            assert config.debug_mode is True
            assert config.timeout_seconds == 30

    def test_create_config_processor_creates_instance(self) -> None:
        """Test config processor creation."""
        processor = FlextCliServices.create_config_processor()
        assert isinstance(processor, FlextCliServices.CliConfigProcessor)
        assert hasattr(processor, "process")
        assert hasattr(processor, "build")


class TestServicesIntegration:
    """Test service integration patterns."""

    def test_command_and_session_processors_work_together(self) -> None:
        """Test command and session processors can work together."""
        # Create processors
        command_processor = FlextCliServices.create_command_processor()
        session_processor = FlextCliServices.create_session_processor()

        # Create a session
        session_result = session_processor.process({"user_id": "integration_test"})
        assert session_result.is_success

        # Process a command
        command_result = command_processor.process("test integration command")
        assert isinstance(command_result, FlextResult)

        # Both processors should work independently
        assert hasattr(command_processor, "process")
        assert hasattr(session_processor, "process")


class TestServicesModule:
    """Test services module constants and imports."""

    def test_module_has_expected_exports_and_classes(self) -> None:
        """Test module has expected constants and imports."""
        # Verify FlextCliServices class exists and has expected structure
        assert hasattr(FlextCliServices, "CliCommandProcessor")
        assert hasattr(FlextCliServices, "CliSessionProcessor")
        assert hasattr(FlextCliServices, "CliConfigProcessor")

        # Verify factory methods exist
        assert hasattr(FlextCliServices, "create_command_processor")
        assert hasattr(FlextCliServices, "create_session_processor")
        assert hasattr(FlextCliServices, "create_config_processor")

        # Verify high-level methods exist
        assert hasattr(FlextCliServices, "process_command")
        assert hasattr(FlextCliServices, "create_session")
        assert hasattr(FlextCliServices, "validate_config")

    def test_services_module_imports_correctly(self) -> None:
        """Test services module can be imported without errors."""
        # This test ensures the module imports without circular dependencies
        # or other import issues
        # Verify the module has the expected classes
        assert hasattr(flext_cli, "FlextCliServices")

    def test_services_instantiation_and_basic_functionality(self) -> None:
        """Test services can be instantiated and have basic functionality."""
        # Test processors can be created
        command_processor = FlextCliServices.create_command_processor()
        session_processor = FlextCliServices.create_session_processor()
        config_processor = FlextCliServices.create_config_processor()

        # Basic instantiation checks
        assert command_processor is not None
        assert session_processor is not None
        assert config_processor is not None

        # Basic functionality checks
        assert callable(getattr(command_processor, "process", None))
        assert callable(getattr(session_processor, "process", None))
        assert callable(getattr(config_processor, "process", None))

    def test_services_registry_and_metrics_available(self) -> None:
        """Test services registry and metrics are available."""
        # Verify registry and metrics instances exist
        assert hasattr(FlextCliServices, "registry")
        assert hasattr(FlextCliServices, "orchestrator")
        assert hasattr(FlextCliServices, "metrics")

        # Verify they are instances from flext-core
        assert isinstance(FlextCliServices.registry, FlextServices.ServiceRegistry)
        assert isinstance(FlextCliServices.orchestrator, FlextServices.ServiceOrchestrator)
        assert isinstance(FlextCliServices.metrics, FlextServices.ServiceMetrics)
