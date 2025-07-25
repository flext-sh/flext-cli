"""Functional tests for FlextCli core classes.

Tests all FlextCli core classes with actual functionality validation.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import json
from typing import Any
from unittest.mock import Mock, patch

import yaml
from flext_cli import (
    FlextCliBuilder,
    FlextCliFormatter,
    FlextCliInput,
    FlextCliValidator,
    flext_cli_create_builder,
    flext_cli_format_output,
    flext_cli_validate_inputs,
)
from flext_core import FlextResult


class TestFlextCliValidator:
    """Test FlextCliValidator validation functionality."""

    def test_validator_initialization(self) -> None:
        """Test validator creation."""
        validator = FlextCliValidator({"email": "email", "port": lambda x: 1 <= int(x) <= 65535})

        assert validator.validations["email"] == "email"
        assert callable(validator.validations["port"])
        assert validator.has_validations()

    def test_email_validation(self) -> None:
        """Test email validation."""
        validator = FlextCliValidator({"email": "email"})

        # Valid email
        result = validator.validate("email", "test@example.com")
        assert result.success
        assert result.unwrap() == "test@example.com"

        # Invalid email
        result = validator.validate("email", "invalid-email")
        assert not result.success
        assert "doesn't match email" in result.error

    def test_custom_validation(self) -> None:
        """Test custom callable validation."""
        validator = FlextCliValidator({"port": lambda x: 1 <= int(x) <= 65535})

        # Valid port
        result = validator.validate("port", "8080")
        assert result.success

        # Invalid port
        result = validator.validate("port", "99999")
        assert not result.success

    def test_dict_validation(self) -> None:
        """Test dictionary validation."""
        validator = FlextCliValidator({
            "email": "email",
            "port": lambda x: 1 <= int(x) <= 65535,
        })

        # Valid data
        data = {"email": "test@example.com", "port": "8080"}
        result = validator.validate_dict(data)
        assert result.success

        # Invalid data
        data = {"email": "invalid", "port": "99999"}
        result = validator.validate_dict(data)
        assert not result.success

    def test_factory_methods(self) -> None:
        """Test validator factory methods."""
        web_validator = FlextCliValidator.create_web_validator()
        assert "url" in web_validator.validations

        security_validator = FlextCliValidator.create_security_validator()
        assert "password" in security_validator.validations

        network_validator = FlextCliValidator.create_network_validator()
        assert "ip" in network_validator.validations

    def test_expanded_validation_patterns(self) -> None:
        """Test expanded validation patterns."""
        validator = FlextCliValidator({
            "jwt": "jwt",
            "ipv6": "ipv6",
            "datetime_iso": "datetime_iso",
            "credit_card": "credit_card",
            "isbn": "isbn",
            "domain": "domain",
        })

        # Test JWT validation
        jwt_result = validator.validate("jwt", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c")
        assert jwt_result.success

        # Test IPv6 validation
        ipv6_result = validator.validate("ipv6", "2001:0db8:85a3:0000:0000:8a2e:0370:7334")
        assert ipv6_result.success

        # Test datetime ISO validation
        datetime_result = validator.validate("datetime_iso", "2025-07-25T10:30:00.000Z")
        assert datetime_result.success

        # Test domain validation
        domain_result = validator.validate("domain", "example.com")
        assert domain_result.success

    def test_available_patterns(self) -> None:
        """Test getting available validation patterns."""
        validator = FlextCliValidator()
        patterns = validator.get_available_patterns()

        # Check for key patterns
        assert "email" in patterns
        assert "url" in patterns
        assert "jwt" in patterns
        assert "ipv6" in patterns
        assert "datetime_iso" in patterns
        assert "credit_card" in patterns
        assert "isbn" in patterns
        assert len(patterns) > 20  # Should have many patterns

    def test_dynamic_validation_addition(self) -> None:
        """Test adding validation rules dynamically."""
        validator = FlextCliValidator()

        # Add new validation
        validator.add_validation("custom", lambda x: len(str(x)) > 5)

        # Test the new validation
        result = validator.validate("custom", "short")
        assert not result.success

        result = validator.validate("custom", "long enough")
        assert result.success


class TestFlextCliFormatter:
    """Test FlextCliFormatter output functionality."""

    def test_formatter_creation(self) -> None:
        """Test formatter creation."""
        formatter = FlextCliFormatter()
        assert formatter.style == "rich"

        json_formatter = FlextCliFormatter("json")
        assert json_formatter.style == "json"

    def test_json_formatting(self) -> None:
        """Test JSON formatting."""
        formatter = FlextCliFormatter("json")
        data = {"key": "value", "number": 42}

        result = formatter.format(data, "Test Data")
        assert "# Test Data" in result

        # Verify it's valid JSON
        json_part = result.split("\n", 1)[1]
        parsed = json.loads(json_part)
        assert parsed["key"] == "value"

    def test_yaml_formatting(self) -> None:
        """Test YAML formatting."""
        formatter = FlextCliFormatter("yaml")
        data = {"key": "value", "number": 42}

        result = formatter.format(data, "Test Data")
        assert "# Test Data" in result

        # Verify it's valid YAML
        yaml_part = result.split("\n", 1)[1]
        parsed = yaml.safe_load(yaml_part)
        assert parsed["key"] == "value"

    def test_table_formatting(self) -> None:
        """Test table formatting."""
        formatter = FlextCliFormatter("table")
        data = [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 25},
        ]

        result = formatter.format(data)
        assert "Alice" in result
        assert "Bob" in result
        assert "|" in result

    def test_factory_methods(self) -> None:
        """Test formatter factory methods."""
        json_formatter = FlextCliFormatter.create_json_formatter()
        assert json_formatter.style == "json"

        table_formatter = FlextCliFormatter.create_table_formatter()
        assert table_formatter.style == "table"

    def test_available_styles(self) -> None:
        """Test available styles."""
        formatter = FlextCliFormatter()
        styles = formatter.get_available_styles()

        assert "rich" in styles
        assert "json" in styles
        assert "yaml" in styles
        assert "table" in styles

    def test_tree_formatting(self) -> None:
        """Test tree formatting functionality."""
        formatter = FlextCliFormatter()
        data = {
            "root": {
                "branch1": {"leaf1": "value1", "leaf2": "value2"},
                "branch2": ["item1", "item2", {"nested": "data"}],
            },
        }

        result = formatter.format_tree(data, "Test Tree")
        assert "Test Tree" in result
        assert "root" in result
        assert "branch1" in result
        assert "value1" in result

    def test_panel_formatting(self) -> None:
        """Test panel formatting functionality."""
        formatter = FlextCliFormatter()
        content = "This is panel content"

        result = formatter.format_panel(content, "Test Panel", "green")
        assert "This is panel content" in result
        # Rich formatting will contain the content

    def test_columns_formatting(self) -> None:
        """Test columns formatting functionality."""
        formatter = FlextCliFormatter()
        data = ["item1", "item2", "item3", "item4", "item5"]

        result = formatter.format_columns(data, columns=3)
        # Should contain all items
        for item in data:
            assert item in result

    def test_message_formatting(self) -> None:
        """Test message formatting methods."""
        formatter = FlextCliFormatter()

        # Test with mock console to capture output
        from unittest.mock import Mock
        formatter.console = Mock()

        formatter.success("Success message", "Success Title")
        formatter.error("Error message", "Error Title")
        formatter.warning("Warning message", "Warning Title")
        formatter.info("Info message", "Info Title")

        # Verify console.print was called
        assert formatter.console.print.call_count == 8  # 2 calls per message type


class TestFlextCliInput:
    """Test FlextCliInput collection functionality."""

    @patch("flext_cli.core.input.Prompt.ask")
    def test_text_input(self, mock_ask: Mock) -> None:
        """Test text input collection."""
        mock_ask.return_value = "test input"

        input_collector = FlextCliInput()
        result = input_collector.text("Enter text")

        assert result.success
        assert result.unwrap() == "test input"

    @patch("flext_cli.core.input.Prompt.ask")
    def test_text_input_with_validation(self, mock_ask: Mock) -> None:
        """Test text input with validation."""
        mock_ask.side_effect = ["invalid-email", "valid@example.com"]

        input_collector = FlextCliInput()
        result = input_collector.text("Enter email", validator="email")

        assert result.success
        assert result.unwrap() == "valid@example.com"

    @patch("flext_cli.core.input.IntPrompt.ask")
    def test_integer_input(self, mock_ask: Mock) -> None:
        """Test integer input."""
        mock_ask.return_value = 42

        input_collector = FlextCliInput()
        result = input_collector.integer("Enter number")

        assert result.success
        assert result.unwrap() == 42

    @patch("flext_cli.core.input.Confirm.ask")
    def test_boolean_input(self, mock_ask: Mock) -> None:
        """Test boolean input."""
        mock_ask.return_value = True

        input_collector = FlextCliInput()
        result = input_collector.boolean("Continue?")

        assert result.success
        assert result.unwrap() is True

    def test_email_convenience(self) -> None:
        """Test email convenience method."""
        input_collector = FlextCliInput()

        with patch.object(input_collector, "text") as mock_text:
            mock_text.return_value = FlextResult.ok("test@example.com")

            result = input_collector.email()
            assert result.success

    def test_factory_methods(self) -> None:
        """Test input factory methods."""
        web_input = FlextCliInput.create_web_input()
        assert web_input.validator is not None

        security_input = FlextCliInput.create_security_input()
        assert security_input.validator is not None


class TestFlextCliBuilder:
    """Test FlextCliBuilder CLI creation functionality."""

    def test_builder_creation(self) -> None:
        """Test builder creation."""
        builder = FlextCliBuilder()
        assert builder.name == "cli"
        assert builder.version == "1.0.0"

    def test_builder_custom_params(self) -> None:
        """Test builder with custom parameters."""
        builder = FlextCliBuilder("myapp", "2.0.0", "My App")
        assert builder.name == "myapp"
        assert builder.version == "2.0.0"
        assert builder.description == "My App"

    def test_fluent_command_addition(self) -> None:
        """Test fluent command addition."""
        builder = FlextCliBuilder()

        def hello() -> str:
            return "Hello World!"

        result = builder.add_command("hello", hello, help_text="Say hello")
        assert result is builder  # Fluent interface
        assert "hello" in builder._commands

    def test_fluent_option_addition(self) -> None:
        """Test fluent option addition."""
        builder = FlextCliBuilder()
        result = builder.add_option("--debug", is_flag=True, help="Debug mode")
        assert result is builder

    def test_validator_setting(self) -> None:
        """Test validator setting."""
        builder = FlextCliBuilder()
        result = builder.set_validator(email="email")
        assert result is builder
        assert builder._validator is not None

    def test_formatter_setting(self) -> None:
        """Test formatter setting."""
        builder = FlextCliBuilder()
        result = builder.set_formatter("json")
        assert result is builder
        assert builder._formatter is not None

    def test_data_validation(self) -> None:
        """Test data validation."""
        builder = FlextCliBuilder()
        builder.set_validator(email="email")

        # Valid data
        result = builder.validate_data({"email": "test@example.com"})
        assert result.success

        # Invalid data
        result = builder.validate_data({"email": "invalid"})
        assert not result.success

    def test_output_formatting(self) -> None:
        """Test output formatting."""
        builder = FlextCliBuilder()

        data = {"message": "Hello World"}
        result = builder.format_output(data, "json")

        assert result.success
        assert "Hello World" in result.unwrap()

    def test_callable_interface(self) -> None:
        """Test builder as callable."""
        builder = FlextCliBuilder()

        with patch.object(builder, "run") as mock_run:
            mock_run.return_value = FlextResult.ok(None)
            result = builder()
            assert result.success

    def test_advanced_builder_features(self) -> None:
        """Test advanced builder features."""
        builder = FlextCliBuilder()

        # Test middleware addition
        def test_middleware(data: dict[str, Any]) -> dict[str, Any]:
            data["processed"] = True
            return data

        result = builder.add_middleware(test_middleware)
        assert result is builder
        assert hasattr(builder, "_middleware")
        assert len(builder._middleware) == 1

        # Test error handler
        def error_handler(exc: Exception) -> str:
            return f"Custom error: {exc}"

        result = builder.set_error_handler(error_handler)
        assert result is builder
        assert hasattr(builder, "_error_handler")

        # Test global flag addition
        result = builder.add_global_flag("--test", "Test flag", True)
        assert result is builder

        # Test config file support
        result = builder.add_config_file_support("test.yaml")
        assert result is builder
        assert hasattr(builder, "_config_loader")

    def test_subcommand_group(self) -> None:
        """Test subcommand group creation."""
        builder = FlextCliBuilder("main")

        # Add subcommand group
        subgroup = builder.add_subcommand_group("database", "Database operations")

        # Verify subgroup is FlextCliBuilder
        assert isinstance(subgroup, FlextCliBuilder)
        assert subgroup.name == "database"
        assert "database" in builder._commands

    def test_interactive_input_integration(self) -> None:
        """Test interactive input integration."""
        builder = FlextCliBuilder()

        schema = {
            "name": {"type": str, "prompt": "Enter name"},
            "age": {"type": int, "prompt": "Enter age", "min_value": 0},
        }

        # Mock the input collection
        with patch("flext_cli.core.input.FlextCliInput.collect_dict") as mock_collect:
            mock_collect.return_value = {"name": "Alice", "age": 30}

            result = builder.interactive_input(schema)
            assert result.success
            data = result.unwrap()
            assert data["name"] == "Alice"
            assert data["age"] == 30


class TestUtilityFunctions:
    """Test utility functions."""

    def test_create_builder(self) -> None:
        """Test CLI builder creation utility."""
        builder = flext_cli_create_builder("testapp")
        assert isinstance(builder, FlextCliBuilder)
        assert builder.name == "testapp"

    def test_validate_inputs(self) -> None:
        """Test validation utility."""
        validator = flext_cli_validate_inputs(email="email")
        assert isinstance(validator, FlextCliValidator)
        assert "email" in validator.validations

    def test_format_output(self) -> None:
        """Test output formatting utility."""
        data = {"key": "value"}
        result = flext_cli_format_output(data, "json")

        assert result.success
        assert '"key": "value"' in result.unwrap()


class TestIntegration:
    """Integration tests for complete workflows."""

    def test_complete_cli_workflow(self) -> None:
        """Test complete CLI workflow."""
        # Create builder
        builder = flext_cli_create_builder("testapp", version="1.0.0")

        # Configure validation and formatting
        builder.set_validator(email="email")
        builder.set_formatter("json")

        # Define command function
        def create_user(name: str, email: str) -> FlextResult[dict[str, str]]:
            validation_result = builder.validate_data({"email": email})
            if not validation_result.success:
                return FlextResult.fail(validation_result.error)

            user_data = {"name": name, "email": email, "status": "created"}
            return FlextResult.ok(user_data)

        # Add command
        builder.add_command("create", create_user, help_text="Create user")

        # Test command function directly
        result = create_user("Alice", "alice@example.com")
        assert result.success

        user_data = result.unwrap()
        assert user_data["name"] == "Alice"
        assert user_data["email"] == "alice@example.com"

    def test_utility_integration(self) -> None:
        """Test utility functions working together."""
        # Create validator
        validator = flext_cli_validate_inputs(email="email")

        # Validate data
        result = validator.validate("email", "test@example.com")
        assert result.success

        # Format output
        data = {"email": result.unwrap(), "status": "valid"}
        format_result = flext_cli_format_output(data, "json")
        assert format_result.success
        assert "test@example.com" in format_result.unwrap()

    def test_error_handling(self) -> None:
        """Test error handling across components."""
        builder = FlextCliBuilder()
        builder.set_validator(email="email")

        # Test validation error propagation
        result = builder.validate_data({"email": "invalid-email"})
        assert not result.success
        assert "doesn't match email" in result.error

    def test_fluent_api_chaining(self) -> None:
        """Test fluent API chaining."""
        # Test method chaining
        builder = (FlextCliBuilder("chainapp")
                  .set_validator(email="email")
                  .set_formatter("json")
                  .add_command("test", lambda: "test", help_text="Test command")
                  .add_option("--verbose", is_flag=True))

        assert builder.name == "chainapp"
        assert "test" in builder._commands
        assert builder._validator is not None
        assert builder._formatter is not None

    def test_comprehensive_functionality(self) -> None:
        """Test comprehensive library functionality integration."""
        # Create complex CLI with all features
        builder = (FlextCliBuilder("comprehensive-app", "2.0.0", "Full feature app")
                  .set_validator(email="email", port=lambda x: 1 <= int(x) <= 65535)
                  .set_formatter("rich")
                  .add_global_flag("--debug", "Enable debug mode")
                  .add_config_file_support("app.yaml"))

        # Add middleware
        def logging_middleware(data: dict[str, Any]) -> dict[str, Any]:
            data["logged"] = True
            return data

        builder.add_middleware(logging_middleware)

        # Add multiple commands
        def user_command(name: str, email: str) -> FlextResult[dict[str, str]]:
            validation_result = builder.validate_data({"email": email})
            if not validation_result.success:
                return FlextResult.fail(validation_result.error)
            return FlextResult.ok({"name": name, "email": email, "status": "created"})

        def server_command(port: str) -> FlextResult[dict[str, str]]:
            validation_result = builder.validate_data({"port": port})
            if not validation_result.success:
                return FlextResult.fail(validation_result.error)
            return FlextResult.ok({"server": "started", "port": port})

        builder.add_command("user", user_command, help_text="Create user")
        builder.add_command("server", server_command, help_text="Start server")

        # Test command functionality
        user_result = user_command("Alice", "alice@example.com")
        assert user_result.success

        server_result = server_command("8080")
        assert server_result.success

        # Test validation failure
        invalid_user = user_command("Bob", "invalid-email")
        assert not invalid_user.success

        # Test output formatting
        format_result = builder.format_output(user_result.unwrap(), "json")
        assert format_result.success
        assert "alice@example.com" in format_result.unwrap()

    def test_error_resilience(self) -> None:
        """Test error handling and resilience."""
        builder = FlextCliBuilder()

        # Test with invalid validation patterns
        try:
            builder.set_validator(invalid_field="[invalid_regex")
            # Should not raise here, only when compiling
        except ValueError:
            pass  # Expected for invalid patterns

        # Test output formatting with invalid style
        result = builder.format_output({"test": "data"}, "invalid_style")
        # Should default to simple formatting
        assert result.success

        # Test validation with non-existent field
        validator = FlextCliValidator({"email": "email"})
        result = validator.validate("nonexistent", "any_value")
        assert result.success  # Should pass for non-configured fields
