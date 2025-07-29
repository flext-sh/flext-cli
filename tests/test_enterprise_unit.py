"""Enterprise-level unit tests for FLEXT CLI.

Comprehensive unit testing suite validating all functionality
without any dead code, duplicated code, or mockup code.
"""

import pytest
from typing import Any, Dict
from pathlib import Path
import tempfile
import json

from flext_cli import (
    # Core classes
    FlextCliService, FlextCliApi,
    FlextCliCommand, FlextCliConfig, FlextCliContext, 
    FlextCliPlugin, FlextCliSession,
    # Enums
    FlextCliCommandStatus, FlextCliCommandType, FlextCliOutputFormat,
    # Functions
    flext_cli_format, flext_cli_export, flext_cli_health,
    flext_cli_create_command, flext_cli_create_session,
    flext_cli_register_handler, flext_cli_execute_handler,
    flext_cli_get_commands, flext_cli_get_sessions,
    flext_cli_get_plugins, flext_cli_get_handlers
)


class TestFlextCliTypes:
    """Test all CLI types and enums."""
    
    def test_command_status_enum(self):
        """Test FlextCliCommandStatus enum values."""
        assert FlextCliCommandStatus.PENDING == "pending"
        assert FlextCliCommandStatus.RUNNING == "running"
        assert FlextCliCommandStatus.COMPLETED == "completed"
        assert FlextCliCommandStatus.FAILED == "failed"
        assert FlextCliCommandStatus.CANCELLED == "cancelled"
    
    def test_command_type_enum(self):
        """Test FlextCliCommandType enum values."""
        assert FlextCliCommandType.SYSTEM == "system"
        assert FlextCliCommandType.PIPELINE == "pipeline"
        assert FlextCliCommandType.PLUGIN == "plugin"
        assert FlextCliCommandType.DATA == "data"
        assert FlextCliCommandType.CONFIG == "config"
        assert FlextCliCommandType.AUTH == "auth"
        assert FlextCliCommandType.MONITORING == "monitoring"
    
    def test_output_format_enum(self):
        """Test FlextCliOutputFormat enum values."""
        assert FlextCliOutputFormat.JSON == "json"
        assert FlextCliOutputFormat.YAML == "yaml"
        assert FlextCliOutputFormat.CSV == "csv"
        assert FlextCliOutputFormat.TABLE == "table"
        assert FlextCliOutputFormat.PLAIN == "plain"
    
    def test_command_entity_creation(self):
        """Test FlextCliCommand entity creation and methods."""
        from flext_core.utilities import FlextUtilities
        cmd = FlextCliCommand(
            id=FlextUtilities.generate_entity_id(),
            name="test-cmd",
            command_line="echo hello",
            options={"description": "Test command"}
        )
        
        assert cmd.name == "test-cmd"
        assert cmd.command_line == "echo hello"
        assert cmd.command_status == FlextCliCommandStatus.PENDING
        assert cmd.command_type == FlextCliCommandType.SYSTEM
        assert hasattr(cmd, 'id')
        assert hasattr(cmd, 'created_at')
        assert hasattr(cmd, 'updated_at')
        
        # Test execution lifecycle
        assert cmd.flext_cli_start_execution() is True
        assert cmd.flext_cli_is_running is True
        assert cmd.flext_cli_is_successful is False
        
        assert cmd.flext_cli_complete_execution(0, "hello") is True
        assert cmd.flext_cli_is_running is False
        assert cmd.flext_cli_is_successful is True
    
    def test_config_value_object(self):
        """Test FlextCliConfig value object."""
        config_data = {
            "debug": True,
            "output_format": "json",
            "api_url": "http://test.com"
        }
        
        config = FlextCliConfig(config_data)
        
        assert config.debug is True
        assert config.format_type == "json"
        assert config.api_url == "http://test.com"
        assert config.profile == "default"  # default value
        
        # Test configuration update
        assert config.configure({"debug": False}) is True
    
    def test_context_value_object(self):
        """Test FlextCliContext value object."""
        config = FlextCliConfig({"debug": True})
        context = FlextCliContext(config)
        
        assert context.debug is True
        assert hasattr(context, 'session_id')
        
        # Test context transformations
        debug_context = context.flext_cli_with_debug(False)
        assert debug_context.debug is False
        
        json_context = context.flext_cli_with_output_format(FlextCliOutputFormat.JSON)
        assert json_context.output_format == "json"
        
        prod_context = context.flext_cli_for_production()
        assert prod_context.debug is False
        assert prod_context.trace is False
        assert prod_context.profile == "production"
    
    def test_plugin_value_object(self):
        """Test FlextCliPlugin value object."""
        plugin = FlextCliPlugin("test-plugin", "1.0.0", 
                               description="Test plugin",
                               dependencies=["dep1", "dep2"])
        
        assert plugin.name == "test-plugin"
        assert plugin.version == "1.0.0"
        assert plugin.description == "Test plugin"
        assert plugin.enabled is True
        assert plugin.dependencies == ["dep1", "dep2"]
        assert hasattr(plugin, 'created_at')
    
    def test_session_entity(self):
        """Test FlextCliSession entity."""
        from flext_core.utilities import FlextUtilities
        session = FlextCliSession(
            id=FlextUtilities.generate_session_id(),
            user_id="test-user"
        )
        
        assert session.user_id == "test-user"
        assert hasattr(session, 'id')
        assert isinstance(session.commands_executed, list)
        assert hasattr(session, 'started_at')
        assert hasattr(session, 'last_activity')
        
        # Test command recording
        assert session.flext_cli_record_command("test-cmd") is True
        assert "test-cmd" in session.commands_executed


class TestFlextCliService:
    """Test core service functionality."""
    
    def test_service_initialization(self):
        """Test service initialization."""
        service = FlextCliService()
        
        assert hasattr(service, 'logger')
        assert hasattr(service, '_config')
        assert hasattr(service, '_handlers')
        assert hasattr(service, '_plugins')
        assert hasattr(service, '_sessions')
        assert hasattr(service, '_commands')
        assert hasattr(service, '_formats')
    
    def test_service_configuration(self):
        """Test service configuration."""
        service = FlextCliService()
        
        config_data = {"debug": True, "output_format": "json"}
        result = service.configure(config_data)
        
        assert result.is_success is True
        assert service._config is not None
        assert service._config.debug is True
    
    def test_format_validation(self):
        """Test format validation."""
        service = FlextCliService()
        
        # Valid format
        result = service.flext_cli_validate_format("json")
        assert result.is_success is True
        assert result.unwrap() == "json"
        
        # Invalid format
        result = service.flext_cli_validate_format("invalid")
        assert result.is_success is False
        assert "Unsupported format" in result.error
    
    def test_data_formatting(self):
        """Test all data formatters."""
        service = FlextCliService()
        test_data = {"name": "test", "value": 42}
        
        # JSON formatting
        result = service.flext_cli_format(test_data, "json")
        assert result.is_success is True
        json_output = result.unwrap()
        assert "test" in json_output
        assert "42" in json_output
        
        # Table formatting
        result = service.flext_cli_format(test_data, "table")
        assert result.is_success is True
        table_output = result.unwrap()
        assert "name" in table_output
        assert "test" in table_output
        
        # CSV formatting
        result = service.flext_cli_format([test_data], "csv")
        assert result.is_success is True
        csv_output = result.unwrap()
        assert "name,value" in csv_output or "value,name" in csv_output
        
        # Plain formatting
        result = service.flext_cli_format(test_data, "plain")
        assert result.is_success is True
        plain_output = result.unwrap()
        assert "test" in plain_output
    
    def test_data_export(self):
        """Test data export functionality."""
        service = FlextCliService()
        test_data = {"export": "test", "status": "working"}
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_path = f.name
        
        try:
            result = service.flext_cli_export(test_data, temp_path, "json")
            assert result.is_success is True
            assert result.unwrap() is True
            
            # Verify file content
            with open(temp_path, 'r') as f:
                content = json.load(f)
                assert content["export"] == "test"
                assert content["status"] == "working"
        finally:
            Path(temp_path).unlink(missing_ok=True)
    
    def test_command_management(self):
        """Test command creation and retrieval."""
        service = FlextCliService()
        
        # Create command
        result = service.flext_cli_create_command("test-cmd", "echo test", type="test")
        assert result.is_success is True
        assert "created" in result.unwrap()
        
        # Get commands
        result = service.flext_cli_get_commands()
        assert result.is_success is True
        commands = result.unwrap()
        assert isinstance(commands, dict)
        assert "test-cmd" in commands
    
    def test_session_management(self):
        """Test session creation and retrieval."""
        service = FlextCliService()
        
        # Create session
        result = service.flext_cli_create_session("test-user")
        assert result.is_success is True
        assert "created" in result.unwrap()
        
        # Get sessions
        result = service.flext_cli_get_sessions()
        assert result.is_success is True
        sessions = result.unwrap()
        assert isinstance(sessions, dict)
        assert len(sessions) > 0
    
    def test_handler_registration_and_execution(self):
        """Test handler registration and execution."""
        service = FlextCliService()
        
        def test_handler(message: str) -> str:
            return f"Processed: {message}"
        
        # Register handler
        result = service.flext_cli_register_handler("test_handler", test_handler)
        assert result.is_success is True
        
        # Execute handler
        result = service.flext_cli_execute_handler("test_handler", "hello")
        assert result.is_success is True
        assert result.unwrap() == "Processed: hello"
        
        # Test handler not found
        result = service.flext_cli_execute_handler("nonexistent", "test")
        assert result.is_success is False
        assert "not found" in result.error
    
    def test_plugin_registration(self):
        """Test plugin registration."""
        service = FlextCliService()
        plugin = FlextCliPlugin("test-plugin", "1.0.0")
        
        result = service.flext_cli_register_plugin("test-plugin", plugin)
        assert result.is_success is True
        
        # Get plugins
        result = service.flext_cli_get_plugins()
        assert result.is_success is True
        plugins = result.unwrap()
        assert "test-plugin" in plugins
    
    def test_context_rendering(self):
        """Test rendering with context."""
        service = FlextCliService()
        service.configure({"output_format": "json"})
        
        test_data = {"context": "test"}
        result = service.flext_cli_render_with_context(test_data, {"output_format": "table"})
        
        assert result.is_success is True
        output = result.unwrap()
        assert "context" in output
    
    def test_health_check(self):
        """Test service health check."""
        service = FlextCliService()
        
        result = service.flext_cli_health()
        assert result.is_success is True
        
        health = result.unwrap()
        assert health["service"] == "FlextCliService"
        assert health["status"] == "healthy"
        assert "supported_formats" in health
        assert "flext_core_integration" in health
        assert health["flext_core_integration"]["entities"] is True


class TestFlextCliApi:
    """Test API layer functionality."""
    
    def test_api_initialization(self):
        """Test API initialization."""
        api = FlextCliApi()
        
        assert hasattr(api, 'logger')
        assert hasattr(api, '_service')
        assert isinstance(api._service, FlextCliService)
    
    def test_api_configuration(self):
        """Test API configuration."""
        api = FlextCliApi()
        
        result = api.flext_cli_configure({"debug": True})
        assert result is True
    
    def test_api_format_and_export(self):
        """Test API format and export methods."""
        api = FlextCliApi()
        test_data = {"api": "test"}
        
        # Test formatting
        result = api.flext_cli_format(test_data, "json")
        assert isinstance(result, str)
        assert "api" in result
        
        # Test export
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_path = f.name
        
        try:
            result = api.flext_cli_export(test_data, temp_path, "json")
            assert result is True
        finally:
            Path(temp_path).unlink(missing_ok=True)
    
    def test_api_health_check(self):
        """Test API health check."""
        api = FlextCliApi()
        
        health = api.flext_cli_health()
        assert isinstance(health, dict)
        assert health["status"] == "healthy"
    
    def test_api_context_creation(self):
        """Test API context creation."""
        api = FlextCliApi()
        
        context = api.flext_cli_create_context({"debug": True})
        assert isinstance(context, FlextCliContext)
        assert context.debug is True


class TestPublicFunctions:
    """Test all public functions."""
    
    def test_format_function(self):
        """Test flext_cli_format function."""
        test_data = {"function": "test"}
        
        result = flext_cli_format(test_data, "json")
        assert isinstance(result, str)
        assert "function" in result
    
    def test_export_function(self):
        """Test flext_cli_export function."""
        test_data = {"export": "function_test"}
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_path = f.name
        
        try:
            result = flext_cli_export(test_data, temp_path, "json")
            assert result is True
        finally:
            Path(temp_path).unlink(missing_ok=True)
    
    def test_health_function(self):
        """Test flext_cli_health function."""
        health = flext_cli_health()
        assert isinstance(health, dict)
        assert health["status"] == "healthy"
    
    def test_command_functions(self):
        """Test command management functions."""
        # Create command
        result = flext_cli_create_command("func-test", "echo function")
        assert isinstance(result, bool)
        
        # Get commands
        commands = flext_cli_get_commands()
        assert isinstance(commands, dict)
    
    def test_session_functions(self):
        """Test session management functions."""
        # Create session
        result = flext_cli_create_session("func-user")
        assert isinstance(result, str)
        
        # Get sessions
        sessions = flext_cli_get_sessions()
        assert isinstance(sessions, dict)
    
    def test_handler_functions(self):
        """Test handler management functions."""
        def test_func_handler(msg):
            return f"Function: {msg}"
        
        # Register handler
        result = flext_cli_register_handler("func_handler", test_func_handler)
        assert result is True
        
        # Execute handler
        result = flext_cli_execute_handler("func_handler", "test")
        assert "Function: test" in str(result)
        
        # Get handlers
        handlers = flext_cli_get_handlers()
        assert isinstance(handlers, dict)
        assert "func_handler" in handlers


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])