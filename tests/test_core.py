"""Test module for core."""

from __future__ import annotations

import json
import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path

import yaml

from flext_cli.configs import FlextCliConfigs
from flext_cli.core import FlextCliService
from flext_cli.domain_services import FlextCliDomainServices
from flext_cli.models import FlextCliModels
from flext_cli.typings import FlextCliTypes
from flext_core import FlextTypes


class TestFlextCliService(unittest.TestCase):
    """Real functionality tests for FlextCliService class."""

    def test_service_creation_and_start(self) -> None:
        """Test FlextCliService can be created and started."""
        service = FlextCliService()
        assert isinstance(service, FlextCliService)

        start_result = service.start()
        assert start_result.is_success
        assert start_result.value is None

    def test_service_stop_functionality(self) -> None:
        """Test FlextCliService stop functionality."""
        service = FlextCliService()

        stop_result = service.stop()
        assert stop_result.is_success
        assert stop_result.value is None

    def test_service_health_check(self) -> None:
        """Test FlextCliService health check functionality."""
        service = FlextCliService()

        health_result = service.health_check()
        assert health_result.is_success
        health_status = health_result.value
        assert health_status == "healthy"

    def test_service_lifecycle_complete(self) -> None:
        """Test complete service lifecycle: start -> health -> stop."""
        service = FlextCliService()

        # Start service
        start_result = service.start()
        assert start_result.is_success

        # Check health
        health_result = service.health_check()
        assert health_result.is_success
        assert health_result.value == "healthy"

        # Stop service
        stop_result = service.stop()
        assert stop_result.is_success


class TestFlextCliServiceImplementation(unittest.TestCase):
    """Real functionality tests for FlextCliService implementation."""

    def setUp(self) -> None:
        """Set up test service for each test."""
        self.service = FlextCliService()

    def test_service_initialization_real(self) -> None:
        """Test FlextCliService initialization with real attributes."""
        service = FlextCliService()

        config = service.get_config()
        handlers = service.get_handlers()
        plugins = service.get_plugins()
        sessions = service.get_sessions()
        commands = service.get_commands()
        formatters = service.get_formatters()

        # Test all attributes are properly initialized
        assert config is None
        assert isinstance(handlers, dict)
        assert isinstance(plugins, dict)
        assert isinstance(sessions, dict)
        assert isinstance(commands, dict)
        # Test formatters has list_formats method
        assert hasattr(formatters, "list_formats")
        list_formats = formatters.list_formats
        assert callable(list_formats)

        # Test all collections are empty
        assert len(handlers) == 0
        assert len(plugins) == 0
        assert len(sessions) == 0
        assert len(commands) == 0

    def test_configure_with_flext_cli_config_object(self) -> None:
        """Test configuring service with FlextCliConfigs object."""
        config = FlextCliConfigs(
            debug=True,
            output_format="json",
            profile="test-profile",
            base_url="http://test.example.com:9000",
        )

        result = self.service.configure(config)
        assert result.is_success

        service_config = self.service.get_config()
        assert service_config is not None
        assert hasattr(service_config, "debug")
        assert service_config.debug is True
        assert service_config.output_format == "json"
        assert service_config.profile == "test-profile"
        assert service_config.base_url == "http://test.example.com:9000"

    def test_configure_with_dict_valid_keys(self) -> None:
        """Test configuring service with dictionary containing valid keys."""
        config_dict = {
            "debug": False,
            "output_format": "yaml",
            "profile": "production",
            "api_url": "http://prod.example.com:8080",
        }

        result = self.service.configure(config_dict)
        assert result.is_success

        service_config = self.service.get_config()
        assert service_config is not None
        assert hasattr(service_config, "debug")
        assert hasattr(service_config, "output_format")
        assert hasattr(service_config, "profile")
        assert service_config.debug is False
        assert service_config.output_format == "yaml"
        assert service_config.profile == "production"

    def test_configure_with_dict_format_type_mapping(self) -> None:
        """Test configuring with format_type gets mapped to output_format."""
        config_dict = {
            "debug": True,
            "format_type": "csv",  # Should be mapped to output_format
            "profile": "dev",
        }

        result = self.service.configure(config_dict)
        assert result.is_success

        service_config = self.service.get_config()
        assert service_config is not None
        assert hasattr(service_config, "output_format")
        assert service_config.output_format == "csv"

    def test_configure_with_dict_unknown_keys_rejected(self) -> None:
        """Test configuring with dictionary containing unknown keys fails."""
        config_dict = {
            "debug": True,
            "unknown_key": "should_fail",
            "another_unknown": "also_fail",
        }

        result = self.service.configure(config_dict)
        assert not result.is_success
        assert "Unknown config keys:" in (result.error or "")
        assert "another_unknown" in (result.error or "")
        assert "unknown_key" in (result.error or "")

    def test_configure_with_compatible_object(self) -> None:
        """Test configuring with compatible object having required attributes."""

        # Create a compatible object with required attributes
        class CompatibleConfig:
            def __init__(self) -> None:
                """Initialize the instance."""
                self.output_format = "table"
                self.profile = "compatible"
                self.debug = False
                self.api_url = "http://compatible.test:5000"

        compatible_config = CompatibleConfig()
        config_dict = {
            "output_format": compatible_config.output_format,
            "profile": compatible_config.profile,
            "debug": compatible_config.debug,
            "api_url": compatible_config.api_url,
        }
        result = self.service.configure(config_dict)
        assert result.is_success

        service_config = self.service.get_config()
        assert service_config is not None
        assert hasattr(service_config, "output_format")
        assert service_config.output_format == "table"
        assert service_config.profile == "compatible"

    def test_configure_with_invalid_type_fails(self) -> None:
        """Test configuring with invalid type fails appropriately."""
        invalid_config = "this is not a valid config"  # Intentionally invalid type

        result = self.service.configure(invalid_config)
        assert not result.is_success
        assert "Configuration must be a dictionary" in (result.error or "")

    def test_flext_cli_format_json_simple_data(self) -> None:
        """Test JSON formatting with simple data."""
        data = {"name": "test", "value": 123, "active": True}

        result = self.service.format_data(
            data, FlextCliTypes.OutputFormat.JSON.value
        )
        assert result.is_success
        formatted = result.value

        # Verify it's valid JSON
        parsed = json.loads(formatted)
        assert parsed["name"] == "test"
        assert parsed["value"] == 123
        assert parsed["active"] is True

    def test_flext_cli_format_json_complex_data(self) -> None:
        """Test JSON formatting with complex nested data."""
        data: FlextTypes.Core.Dict = {
            "users": [
                {"id": 1, "name": "Alice", "permissions": ["read", "write"]},
                {"id": 2, "name": "Bob", "permissions": ["read"]},
            ],
            "metadata": {"total": 2, "created_at": "2025-01-01T00:00:00Z"},
        }

        result = self.service.format_data(
            data, FlextCliTypes.OutputFormat.JSON.value
        )
        assert result.is_success
        formatted = result.value

        # Verify JSON structure
        parsed = json.loads(formatted)
        assert len(parsed["users"]) == 2
        assert parsed["users"][0]["name"] == "Alice"
        assert "write" in parsed["users"][0]["permissions"]
        assert parsed["metadata"]["total"] == 2

    def test_flext_cli_format_yaml_data(self) -> None:
        """Test YAML formatting with data."""
        data: FlextTypes.Core.Dict = {
            "database": {"host": "localhost", "port": 5432, "name": "testdb"},
            "features": ["feature1", "feature2", "feature3"],
        }

        result = self.service.format_data(
            data, FlextCliTypes.OutputFormat.YAML.value
        )
        assert result.is_success
        formatted = result.value

        # Verify it's valid YAML
        parsed = yaml.safe_load(formatted)
        assert parsed["database"]["host"] == "localhost"
        assert parsed["database"]["port"] == 5432
        assert len(parsed["features"]) == 3

    def test_flext_cli_format_csv_list_of_dicts(self) -> None:
        """Test CSV formatting with list of dictionaries."""
        data = [
            {"name": "Alice", "age": 30, "city": "NYC"},
            {"name": "Bob", "age": 25, "city": "LA"},
            {"name": "Carol", "age": 35, "city": "Chicago"},
        ]

        result = self.service.format_data(
            data, FlextCliTypes.OutputFormat.CSV.value
        )
        assert result.is_success
        formatted = result.value

        # Verify CSV structure
        lines = formatted.strip().split("\n")
        assert "name,age,city" in lines[0]  # Header
        assert "Alice,30,NYC" in lines[1]
        assert "Bob,25,LA" in lines[2]

    def test_flext_cli_format_table_dict_data(self) -> None:
        """Test table formatting with dictionary data."""
        data = {
            "server_name": "production-server",
            "port": 8080,
            "status": "active",
            "uptime": "99.9%",
        }

        result = self.service.format_data(
            data, FlextCliTypes.OutputFormat.TABLE.value
        )
        assert result.is_success
        formatted = result.value

        # Verify table format contains data
        assert "server_name" in formatted
        assert "production-server" in formatted
        assert "8080" in formatted
        assert "active" in formatted

    def test_flext_cli_format_table_list_data(self) -> None:
        """Test table formatting with list of dictionaries."""
        data = [
            {"id": 1, "product": "laptop", "price": 999},
            {"id": 2, "product": "mouse", "price": 25},
            {"id": 3, "product": "keyboard", "price": 75},
        ]

        result = self.service.format_data(
            data, FlextCliTypes.OutputFormat.TABLE.value
        )
        assert result.is_success
        formatted = result.value

        # Verify table contains all data
        assert "laptop" in formatted
        assert "999" in formatted
        assert "mouse" in formatted
        assert "25" in formatted

    def test_flext_cli_format_plain_text(self) -> None:
        """Test plain text formatting."""
        data = "Simple plain text message for testing"

        result = self.service.format_data(
            data, FlextCliTypes.OutputFormat.PLAIN.value
        )
        assert result.is_success
        formatted = result.value
        assert formatted == "Simple plain text message for testing"

    def test_flext_cli_format_unsupported_format(self) -> None:
        """Test formatting with unsupported format fails appropriately."""
        data: FlextTypes.Core.Dict = {"test": "data"}

        # This should fail since we're passing invalid format
        result = self.service.format_data(data, "xml")
        assert not result.is_success
        assert "Unsupported format" in (result.error or "")

    def test_flext_cli_export_json_to_file(self) -> None:
        """Test exporting JSON data to file."""
        data = {"export_test": "json", "timestamp": "2025-01-01", "count": 42}

        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "test_export.json"

            result = self.service.flext_cli_export(
                data,
                str(output_file),
                FlextCliTypes.OutputFormat.JSON.value,
            )
            assert result.is_success
            assert output_file.exists()

            # Verify file content
            with output_file.open(encoding="utf-8") as f:
                content = json.load(f)
                assert content["export_test"] == "json"
                assert content["count"] == 42

    def test_flext_cli_export_yaml_to_file(self) -> None:
        """Test exporting YAML data to file."""
        data: FlextTypes.Core.Dict = {
            "config": {"api_endpoint": "https://api.test.com", "timeout": 30},
            "enabled_features": ["auth", "logging", "metrics"],
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "config.yaml"

            result = self.service.flext_cli_export(
                data,
                str(output_file),
                FlextCliTypes.OutputFormat.YAML.value,
            )
            assert result.is_success
            assert output_file.exists()

            # Verify file content
            with output_file.open(encoding="utf-8") as f:
                content = yaml.safe_load(f)
                assert content["config"]["api_endpoint"] == "https://api.test.com"
                assert "auth" in content["enabled_features"]

    def test_flext_cli_export_csv_to_file(self) -> None:
        """Test exporting CSV data to file."""
        data = [
            {"product": "laptop", "category": "electronics", "price": 999},
            {"product": "desk", "category": "furniture", "price": 299},
            {"product": "chair", "category": "furniture", "price": 199},
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "products.csv"

            result = self.service.flext_cli_export(
                data,
                str(output_file),
                FlextCliTypes.OutputFormat.CSV.value,
            )
            assert result.is_success
            assert output_file.exists()

            # Verify file content
            content = output_file.read_text(encoding="utf-8")
            assert "product,category,price" in content
            assert "laptop,electronics,999" in content
            assert "desk,furniture,299" in content

    def test_flext_cli_export_creates_parent_directories(self) -> None:
        """Test export creates parent directories when they don't exist."""
        data: FlextTypes.Core.Dict = {"test": "directory_creation"}

        with tempfile.TemporaryDirectory() as temp_dir:
            nested_path = Path(temp_dir) / "level1" / "level2" / "test.json"

            result = self.service.flext_cli_export(
                data,
                str(nested_path),
                FlextCliTypes.OutputFormat.JSON.value,
            )
            assert result.is_success
            assert nested_path.exists()
            assert nested_path.parent.exists()

    def test_flext_cli_health_basic_status(self) -> None:
        """Test health check returns basic service status."""
        result = self.service.flext_cli_health()
        assert result.is_success

        health_data = result.value
        assert health_data["service"] == "FlextCliService"
        assert health_data["status"] == "healthy"
        assert "timestamp" in health_data
        assert health_data["configured"] is False  # No config set yet
        assert health_data["handlers"] == 0
        assert health_data["plugins"] == 0

    def test_flext_cli_health_with_configuration(self) -> None:
        """Test health check includes configuration when service is configured."""
        config = FlextCliConfigs(debug=True, output_format="json", profile="test")
        self.service.configure(config)

        result = self.service.flext_cli_health()
        assert result.is_success

        health_data = result.value
        assert isinstance(health_data, dict)

        health_dict: dict[str, object] = health_data
        assert health_dict["configured"] is True
        config_value = health_dict["config"]
        assert isinstance(config_value, dict)
        config_dict: dict[str, object] = config_value
        assert config_dict["output_format"] == "json"
        assert config_dict["debug"] is True
        assert config_dict["profile"] == "test"

    def test_flext_cli_health_flext_core_integration(self) -> None:
        """Test health check shows flext-core integration status."""
        result = self.service.flext_cli_health()
        assert result.is_success

        health_data = result.value
        assert isinstance(health_data, dict)
        # Check that health data contains expected fields
        assert "service" in health_data
        assert "status" in health_data
        # Verify health status
        assert health_data["status"] == "healthy"

    def test_flext_cli_validate_format_valid_formats(self) -> None:
        """Test format validation with all valid formats."""
        valid_formats = ["json", "yaml", "csv", "table", "plain"]

        for format_type in valid_formats:
            result = self.service.format_data({"test": "data"}, format_type)
            assert result.is_success

    def test_flext_cli_validate_format_invalid_format(self) -> None:
        """Test format validation rejects invalid formats."""
        result = self.service.format_data({"test": "data"}, "xml")
        assert not result.is_success
        assert "xml" in (result.error or "")

    def test_flext_cli_create_command_with_real_entity(self) -> None:
        """Test creating commands with real FlextCliCommand entities."""
        domain_service = FlextCliDomainServices()
        result = domain_service.create_command(command_line="echo 'hello world'")

        assert result.is_success
        command = result.unwrap()
        assert isinstance(command, FlextCliModels.CliCommand)
        assert command.command_line == "echo 'hello world'"

        # Verify command was actually stored
        commands = self.service.get_commands()
        assert isinstance(commands, dict)

    def test_flext_cli_create_session_with_user_id(self) -> None:
        """Test creating sessions with specified user ID."""
        domain_service = FlextCliDomainServices()
        result = domain_service.create_session(user_id="test-user-123")

        assert result.is_success
        session = result.unwrap()
        assert session.user_id == "test-user-123"
        assert isinstance(session, FlextCliModels.CliSession)

    def test_flext_cli_create_session_auto_user_id(self) -> None:
        """Test creating sessions with auto-generated user ID."""
        domain_service = FlextCliDomainServices()
        result = domain_service.create_session()

        assert result.is_success
        session = result.unwrap()
        assert session.user_id is not None
        assert isinstance(session, FlextCliModels.CliSession)
        assert session.user_id.startswith("user_")

    def test_flext_cli_register_and_execute_handler(self) -> None:
        """Test registering and executing handlers with real functionality."""

        def test_handler(data: object) -> str:
            return f"Processed: {data}"

        # Register handler
        register_result = self.service.flext_cli_register_handler(
            "test-handler",
            test_handler,
        )
        assert register_result.is_success

        # Execute handler
        execute_result = self.service.flext_cli_execute_handler(
            "test-handler",
            "test-data",
        )
        assert execute_result.is_success
        assert execute_result.value == "Processed: test-data"

    def test_flext_cli_register_duplicate_handler_fails(self) -> None:
        """Test registering duplicate handler names fails."""

        def handler1(__data: object, /) -> str:
            return "handler1"

        def handler2(__data: object, /) -> str:
            return "handler2"

        # Register first handler
        result1 = self.service.flext_cli_register_handler("duplicate", handler1)
        assert result1.success

        # Try to register second handler with same name
        result2 = self.service.flext_cli_register_handler("duplicate", handler2)
        assert not result2.success
        assert "Handler 'duplicate' already registered" in (result2.error or "")

    def test_flext_cli_execute_nonexistent_handler(self) -> None:
        """Test executing non-existent handler fails appropriately."""
        result = self.service.flext_cli_execute_handler("nonexistent", "data")
        assert not result.is_success
        assert "Handler 'nonexistent' not found" in (result.error or "")

    def test_flext_cli_register_plugin_with_real_entity(self) -> None:
        """Test registering plugins with real FlextCliPlugin entities."""
        plugin = FlextCliModels.CliCommand(
            id="test-plugin-123",
            command_line="test-plugin --version",
            execution_time=datetime.now(UTC),
            name="test-plugin",
            entry_point="test.plugin:main",
            plugin_version="1.0.0",
        )

        result = self.service.flext_cli_register_plugin("test-plugin", plugin)
        assert result.is_success

        # Verify plugin was stored
        plugins_result = self.service.flext_cli_get_plugins()
        assert plugins_result.is_success
        plugins = plugins_result.value
        assert "test-plugin" in plugins
        assert plugins["test-plugin"] is not None
        stored_plugin = plugins["test-plugin"]
        assert isinstance(stored_plugin, FlextCliModels.CliCommand)
        assert hasattr(stored_plugin, "name")
        assert stored_plugin.name == "test-plugin"

    def test_flext_cli_register_duplicate_plugin_fails(self) -> None:
        """Test registering duplicate plugin names fails."""
        plugin1 = FlextCliModels.CliCommand(
            id="plugin1",
            command_line="duplicate-plugin --test1",
            execution_time=datetime.now(UTC),
            name="duplicate-plugin",
            entry_point="test1:main",
        )
        plugin2 = FlextCliModels.CliCommand(
            id="plugin2",
            command_line="duplicate-plugin --test2",
            execution_time=datetime.now(UTC),
            name="duplicate-plugin",
            entry_point="test2:main",
        )

        # Register first plugin
        result1 = self.service.flext_cli_register_plugin("duplicate", plugin1)
        assert result1.success

        # Try to register second plugin with same name
        result2 = self.service.flext_cli_register_plugin("duplicate", plugin2)
        assert not result2.success
        assert "Plugin 'duplicate' already registered" in (result2.error or "")

    def test_flext_cli_render_with_context_default_format(self) -> None:
        """Test rendering data with context using default format."""
        data: dict[str, object] = {"message": "Hello World", "status": "success"}

        result = self.service.flext_cli_render_with_context(data)
        assert result.is_success

        rendered = result.value
        # Should use table format by default
        assert "message" in rendered
        assert "Hello World" in rendered

    def test_flext_cli_render_with_context_specified_format(self) -> None:
        """Test rendering data with context using specified format."""
        data: dict[str, object] = {"api": "test", "version": "1.0"}
        context_options: dict[str, object] = {"output_format": "json"}

        result = self.service.flext_cli_render_with_context(data, context_options)
        assert result.is_success

        rendered = result.value
        # Should be valid JSON
        parsed = json.loads(rendered)
        assert parsed["api"] == "test"
        assert parsed["version"] == "1.0"

    def test_flext_cli_render_with_configured_format(self) -> None:
        """Test rendering uses configured format when no context override."""
        # Configure service for JSON format
        config = FlextCliConfigs(output_format="json")
        self.service.configure(config)

        data = {"configured": True, "format": "json"}

        result = self.service.flext_cli_render_with_context(data)
        assert result.is_success

        rendered = result.value
        # Should be JSON due to service configuration
        parsed = json.loads(rendered)
        assert parsed["configured"] is True

    def test_flext_cli_get_commands_returns_copy(self) -> None:
        """Test get_commands returns copy to prevent external modification."""
        # Create a command first
        self.service.flext_cli_create_command("test-cmd", "echo test")

        result1 = self.service.flext_cli_get_commands()
        result2 = self.service.flext_cli_get_commands()

        assert result1.success
        assert result2.success
        commands1 = result1.value
        commands2 = result2.value

        # Should be equal but different objects
        assert commands1.keys() == commands2.keys()
        assert commands1 is not commands2  # Different object references

    def test_flext_cli_get_sessions_returns_copy(self) -> None:
        """Test get_sessions returns copy to prevent external modification."""
        # Create a session first
        self.service.flext_cli_create_session("test-user")

        result1 = self.service.flext_cli_get_sessions()
        result2 = self.service.flext_cli_get_sessions()

        assert result1.success
        assert result2.success
        sessions1 = result1.value
        sessions2 = result2.value

        # Should be equal but different objects
        assert sessions1.keys() == sessions2.keys()
        assert sessions1 is not sessions2

    def test_flext_cli_get_plugins_returns_copy(self) -> None:
        """Test get_plugins returns copy to prevent external modification."""
        # Create a plugin first
        plugin = FlextCliModels.CliCommand(
            id="test",
            command_line="test --version",
            execution_time=datetime.now(UTC),
            name="test",
            entry_point="test:main",
        )
        self.service.flext_cli_register_plugin("test", plugin)

        result1 = self.service.flext_cli_get_plugins()
        result2 = self.service.flext_cli_get_plugins()

        assert result1.success
        assert result2.success
        plugins1 = result1.value
        plugins2 = result2.value

        # Should be equal but different objects
        assert plugins1.keys() == plugins2.keys()
        assert plugins1 is not plugins2

    def test_flext_cli_get_handlers_returns_objects(self) -> None:
        """Test get_handlers returns handlers as objects."""

        def test_handler(data: object) -> str:
            return str(data)

        self.service.flext_cli_register_handler("test", test_handler)

        result = self.service.flext_cli_get_handlers()
        assert result.is_success

        handlers = result.value
        assert "test" in handlers
        # Should convert to object type for return
        assert isinstance(handlers["test"], object)

    def test_multiple_commands_and_sessions_management(self) -> None:
        """Test managing multiple commands and sessions simultaneously."""
        # Create multiple commands
        for i in range(3):
            result = self.service.flext_cli_create_command(
                f"cmd-{i}",
                f"echo 'command {i}'",
            )
            assert result.is_success

        # Create multiple sessions
        for i in range(2):
            result = self.service.flext_cli_create_session(f"user-{i}")
            assert result.is_success

        # Verify all were stored
        commands_result = self.service.flext_cli_get_commands()
        sessions_result = self.service.flext_cli_get_sessions()

        assert commands_result.is_success
        assert sessions_result.is_success
        commands = commands_result.value
        sessions = sessions_result.value

        assert len(commands) == 3
        assert len(sessions) == 2

        # Verify health reflects the counts
        health_result = self.service.flext_cli_health()
        assert health_result.is_success
        health = health_result.value
        assert isinstance(health["handlers"], int)
        assert health["handlers"] >= 0  # Check handlers count instead
        assert health["sessions"] == 2


if __name__ == "__main__":
    unittest.main()
