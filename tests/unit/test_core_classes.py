"""Comprehensive tests for FlextCli core classes.

Tests all FlextCli core classes with complete coverage:
- FlextCliBuilder: Zero-boilerplate CLI creation
- FlextCliValidator: Input validation with patterns
- FlextCliFormatter: Output formatting with multiple styles
- FlextCliInput: Interactive input collection

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import json
from unittest.mock import Mock, patch

import yaml
from flext_cli import (
    FlextCliBuilder,
    FlextCliFormatter,
    FlextCliInput,
    FlextCliValidator,
)
from flext_core import FlextResult


class TestFlextCliValidator:
    """Test FlextCliValidator comprehensive validation patterns."""

    def test_validator_initialization(self) -> None:
        """Test validator creation with patterns."""
        validator = FlextCliValidator(validations={"email": "email", "port": lambda x: 1 <= int(x) <= 65535})

        assert validator.validations["email"] == "email"
        assert callable(validator.validations["port"])
        assert validator.has_validations()

    def test_email_validation(self) -> None:
        """Test email pattern validation."""
        validator = FlextCliValidator(validations={"email": "email"})

        # Valid emails
        result = validator.validate("email", "test@example.com")
        assert result.success
        assert result.unwrap() == "test@example.com"

        result = validator.validate("email", "user.name+tag@domain-name.co.uk")
        assert result.success

        # Invalid emails
        result = validator.validate("email", "invalid-email")
        assert not result.success
        assert "doesn't match email" in result.error

    def test_url_validation(self) -> None:
        """Test URL pattern validation."""
        validator = FlextCliValidator(validations={"url": "url"})

        # Valid URLs
        result = validator.validate("url", "https://example.com")
        assert result.success

        result = validator.validate("url", "http://localhost:8080/path?query=value")
        assert result.success

        # Invalid URLs
        result = validator.validate("url", "not-a-url")
        assert not result.success
        assert "doesn't match url" in result.error

    def test_custom_callable_validation(self) -> None:
        """Test custom callable validators."""
        validator = FlextCliValidator(validations={
            "port": lambda x: 1 <= int(x) <= 65535,
        })

        # Valid port
        result = validator.validate("port", "8080")
        assert result.success

        # Invalid port
        result = validator.validate("port", "99999")
        assert not result.success
        assert "Validation failed" in result.error

    def test_validate_dict_success(self) -> None:
        """Test dictionary validation success."""
        validator = FlextCliValidator(validations={
            "email": "email",
            "port": lambda x: 1 <= int(x) <= 65535,
        })

        data = {"email": "test@example.com", "port": "8080"}
        result = validator.validate_dict(data)

        assert result.success
        validated_data = result.unwrap()
        assert validated_data["email"] == "test@example.com"
        assert validated_data["port"] == "8080"

    def test_validate_dict_failure(self) -> None:
        """Test dictionary validation failure."""
        validator = FlextCliValidator(validations={
            "email": "email",
            "port": lambda x: 1 <= int(x) <= 65535,
        })

        data = {"email": "invalid-email", "port": "99999"}
        result = validator.validate_dict(data)

        assert not result.success
        assert "doesn't match email" in result.error
        assert "Validation failed" in result.error

    def test_add_validation_dynamically(self) -> None:
        """Test adding validation rules dynamically."""
        validator = FlextCliValidator()
        assert not validator.has_validations()

        validator.add_validation("username", "username")
        assert validator.has_validations()

        result = validator.validate("username", "valid_user123")
        assert result.success

        result = validator.validate("username", "invalid-user!")
        assert not result.success

    def test_factory_methods(self) -> None:
        """Test specialized validator factories."""
        # Web validator
        web_validator = FlextCliValidator.create_web_validator()
        assert "url" in web_validator.validations
        assert "email" in web_validator.validations

        # Security validator
        security_validator = FlextCliValidator.create_security_validator()
        assert "password" in security_validator.validations
        assert "username" in security_validator.validations

        # Network validator
        network_validator = FlextCliValidator.create_network_validator()
        assert "ip" in network_validator.validations
        assert "mac" in network_validator.validations

    def test_available_patterns(self) -> None:
        """Test getting available validation patterns."""
        validator = FlextCliValidator()
        patterns = validator.get_available_patterns()

        assert "email" in patterns
        assert "url" in patterns
        assert "password" in patterns
        assert "ipv4" in patterns


class TestFlextCliFormatter:
    """Test FlextCliFormatter output formatting capabilities."""

    def test_formatter_initialization(self) -> None:
        """Test formatter creation with styles."""
        formatter = FlextCliFormatter()
        assert formatter.style == "rich"
        assert formatter.console is not None

        json_formatter = FlextCliFormatter(style="json")
        assert json_formatter.style == "json"

    def test_rich_formatting(self) -> None:
        """Test Rich-style formatting."""
        formatter = FlextCliFormatter(style="rich")

        data = {"key": "value", "number": 42}
        result = formatter.format(data, "Test Data")

        assert isinstance(result, str)
        assert "Test Data" in result
        assert "key" in result
        assert "value" in result

    def test_json_formatting(self) -> None:
        """Test JSON formatting."""
        formatter = FlextCliFormatter(style="json")

        data = {"key": "value", "number": 42}
        result = formatter.format(data, "JSON Data")

        assert isinstance(result, str)
        assert "# JSON Data" in result

        # Verify valid JSON
        json_part = result.split("\n", 1)[1]
        parsed = json.loads(json_part)
        assert parsed["key"] == "value"
        assert parsed["number"] == 42

    def test_yaml_formatting(self) -> None:
        """Test YAML formatting."""
        formatter = FlextCliFormatter(style="yaml")

        data = {"key": "value", "number": 42}
        result = formatter.format(data, "YAML Data")

        assert isinstance(result, str)
        assert "# YAML Data" in result

        # Verify valid YAML
        yaml_part = result.split("\n", 1)[1]
        parsed = yaml.safe_load(yaml_part)
        assert parsed["key"] == "value"
        assert parsed["number"] == 42

    def test_table_formatting(self) -> None:
        """Test table formatting."""
        formatter = FlextCliFormatter(style="table")

        data = [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 25},
        ]
        result = formatter.format(data, "User Table")

        assert isinstance(result, str)
        assert "User Table" in result
        assert "Alice" in result
        assert "Bob" in result
        assert "|" in result  # Table separators

    def test_simple_formatting(self) -> None:
        """Test simple text formatting."""
        formatter = FlextCliFormatter(style="simple")

        result = formatter.format("Hello World", "Simple Message")
        assert result == "Simple Message: Hello World"

        result = formatter.format("No title")
        assert result == "No title"

    @patch("flext_cli.core.formatter.Console")
    def test_output_methods(self, mock_console_class) -> None:
        """Test output methods with mocked console."""
        mock_console = Mock()
        mock_console_class.return_value = mock_console

        formatter = FlextCliFormatter()

        # Test success output
        formatter.success("Operation completed", "Success")
        mock_console.print.assert_called()

        # Test error output
        formatter.error("Something failed", "Error")
        mock_console.print.assert_called()

        # Test warning output
        formatter.warning("Be careful", "Warning")
        mock_console.print.assert_called()

        # Test info output
        formatter.info("Information", "Info")
        mock_console.print.assert_called()

    def test_table_output(self) -> None:
        """Test Rich table output."""
        formatter = FlextCliFormatter()

        data = [
            {"name": "Alice", "role": "Admin"},
            {"name": "Bob", "role": "User"},
        ]

        # Should not raise exception
        formatter.table(data, "Users")

        # Test empty data
        formatter.table([], "Empty")
        formatter.table(None, "None")

    def test_code_output(self) -> None:
        """Test syntax-highlighted code output."""
        formatter = FlextCliFormatter()

        code = "def hello():\n    print('Hello World')"

        # Should not raise exception
        formatter.code(code, "python", "Example Code")

    def test_factory_methods(self) -> None:
        """Test formatter factory methods."""
        json_formatter = FlextCliFormatter.create_json_formatter()
        assert json_formatter.style == "json"

        table_formatter = FlextCliFormatter.create_table_formatter()
        assert table_formatter.style == "table"

        rich_formatter = FlextCliFormatter.create_rich_formatter()
        assert rich_formatter.style == "rich"

    def test_available_styles(self) -> None:
        """Test getting available formatting styles."""
        formatter = FlextCliFormatter()
        styles = formatter.get_available_styles()

        assert "rich" in styles
        assert "json" in styles
        assert "yaml" in styles
        assert "table" in styles
        assert "simple" in styles


class TestFlextCliInput:
    """Test FlextCliInput interactive input collection."""

    @patch("flext_cli.core.input.Prompt.ask")
    def test_text_input_success(self, mock_ask) -> None:
        """Test successful text input."""
        mock_ask.return_value = "test input"

        input_collector = FlextCliInput()
        result = input_collector.text("Enter text")

        assert result.success
        assert result.unwrap() == "test input"
        mock_ask.assert_called_once()

    @patch("flext_cli.core.input.Prompt.ask")
    def test_text_input_validation(self, mock_ask) -> None:
        """Test text input with validation."""
        mock_ask.side_effect = ["invalid-email", "valid@example.com"]

        input_collector = FlextCliInput()

        with patch.object(input_collector.console, "print") as mock_print:
            result = input_collector.text("Enter email", validator="email")

        assert result.success
        assert result.unwrap() == "valid@example.com"
        assert mock_ask.call_count == 2
        mock_print.assert_called()  # Error message shown

    @patch("flext_cli.core.input.Prompt.ask")
    def test_text_input_keyboard_interrupt(self, mock_ask) -> None:
        """Test text input with keyboard interrupt."""
        mock_ask.side_effect = KeyboardInterrupt()

        input_collector = FlextCliInput()
        result = input_collector.text("Enter text")

        assert not result.success
        assert "cancelled" in result.error

    @patch("flext_cli.core.input.Prompt.ask")
    def test_password_input(self, mock_ask) -> None:
        """Test password input."""
        mock_ask.return_value = "secret123"

        input_collector = FlextCliInput()
        result = input_collector.password("Enter password")

        assert result.success
        assert result.unwrap() == "secret123"
        mock_ask.assert_called_with("Enter password", password=True, console=input_collector.console)

    @patch("flext_cli.core.input.Prompt.ask")
    def test_password_confirmation(self, mock_ask) -> None:
        """Test password with confirmation."""
        mock_ask.side_effect = ["secret123", "secret123"]

        input_collector = FlextCliInput()
        result = input_collector.password("Enter password", confirm=True)

        assert result.success
        assert result.unwrap() == "secret123"
        assert mock_ask.call_count == 2

    @patch("flext_cli.core.input.Prompt.ask")
    def test_password_mismatch(self, mock_ask) -> None:
        """Test password confirmation mismatch."""
        mock_ask.side_effect = ["secret123", "different", "secret123", "secret123"]

        input_collector = FlextCliInput()

        with patch.object(input_collector.console, "print") as mock_print:
            result = input_collector.password("Enter password", confirm=True)

        assert result.success
        assert result.unwrap() == "secret123"
        assert mock_ask.call_count == 4
        mock_print.assert_called()  # Mismatch error shown

    @patch("flext_cli.core.input.IntPrompt.ask")
    def test_integer_input(self, mock_ask) -> None:
        """Test integer input."""
        mock_ask.return_value = 42

        input_collector = FlextCliInput()
        result = input_collector.integer("Enter number")

        assert result.success
        assert result.unwrap() == 42

    @patch("flext_cli.core.input.IntPrompt.ask")
    def test_integer_range_validation(self, mock_ask) -> None:
        """Test integer with range validation."""
        mock_ask.side_effect = [999, 50]  # First too high, second valid

        input_collector = FlextCliInput()

        with patch.object(input_collector.console, "print") as mock_print:
            result = input_collector.integer("Enter port", min_value=1, max_value=100)

        assert result.success
        assert result.unwrap() == 50
        assert mock_ask.call_count == 2
        mock_print.assert_called()  # Range error shown

    @patch("flext_cli.core.input.FloatPrompt.ask")
    def test_float_input(self, mock_ask) -> None:
        """Test float input."""
        mock_ask.return_value = 3.14

        input_collector = FlextCliInput()
        result = input_collector.float_input("Enter float")

        assert result.success
        assert result.unwrap() == 3.14

    @patch("flext_cli.core.input.Confirm.ask")
    def test_boolean_input(self, mock_ask) -> None:
        """Test boolean input."""
        mock_ask.return_value = True

        input_collector = FlextCliInput()
        result = input_collector.boolean("Continue?")

        assert result.success
        assert result.unwrap() is True

    @patch("flext_cli.core.input.Prompt.ask")
    def test_choice_input(self, mock_ask) -> None:
        """Test choice input."""
        mock_ask.return_value = "option2"

        input_collector = FlextCliInput()
        result = input_collector.choice("Choose", ["option1", "option2", "option3"])

        assert result.success
        assert result.unwrap() == "option2"

    def test_email_convenience_method(self) -> None:
        """Test email convenience method."""
        input_collector = FlextCliInput()

        with patch.object(input_collector, "text") as mock_text:
            mock_text.return_value = FlextResult.ok("test@example.com")

            result = input_collector.email("Enter email")

            assert result.success
            mock_text.assert_called_with("Enter email", default=None, validator="email")

    def test_url_convenience_method(self) -> None:
        """Test URL convenience method."""
        input_collector = FlextCliInput()

        with patch.object(input_collector, "text") as mock_text:
            mock_text.return_value = FlextResult.ok("https://example.com")

            result = input_collector.url("Enter URL")

            assert result.success
            mock_text.assert_called_with("Enter URL", default=None, validator="url")

    @patch("flext_cli.core.input.Prompt.ask")
    @patch("flext_cli.core.input.IntPrompt.ask")
    @patch("flext_cli.core.input.Confirm.ask")
    def test_collect_dict_schema(self, mock_confirm, mock_int, mock_prompt) -> None:
        """Test collecting input from schema."""
        mock_prompt.return_value = "John Doe"
        mock_int.return_value = 30
        mock_confirm.return_value = True

        input_collector = FlextCliInput()

        schema = {
            "name": {"type": str, "prompt": "Your name"},
            "age": {"type": int, "prompt": "Your age"},
            "active": {"type": bool, "prompt": "Active user?"},
        }

        result = input_collector.collect_dict(schema)

        assert result["name"] == "John Doe"
        assert result["age"] == 30
        assert result["active"] is True

    def test_factory_methods(self) -> None:
        """Test specialized input collector factories."""
        web_input = FlextCliInput.create_web_input()
        assert web_input.validator is not None

        security_input = FlextCliInput.create_security_input()
        assert security_input.validator is not None

        network_input = FlextCliInput.create_network_input()
        assert network_input.validator is not None


class TestFlextCliBuilder:
    """Test FlextCliBuilder CLI creation and execution."""

    def test_builder_initialization(self) -> None:
        """Test builder creation with defaults."""
        builder = FlextCliBuilder()

        assert builder.name == "cli"
        assert builder.version == "1.0.0"
        assert builder._commands == {}
        assert builder._console is not None
        assert builder._formatter is not None
        assert builder._validator is not None

    def test_builder_custom_initialization(self) -> None:
        """Test builder with custom parameters."""
        builder = FlextCliBuilder(
            name="myapp",
            version="2.0.0",
            description="My Application",
        )

        assert builder.name == "myapp"
        assert builder.version == "2.0.0"
        assert builder.description == "My Application"

    def test_add_command_fluent(self) -> None:
        """Test fluent command addition."""
        builder = FlextCliBuilder()

        def hello_cmd() -> str:
            return "Hello World!"

        result = builder.add_command("hello", hello_cmd, help="Say hello")

        # Fluent interface returns self
        assert result is builder
        assert "hello" in builder._commands
        assert builder._commands["hello"].name == "hello"
        assert builder._commands["hello"].func == hello_cmd
        assert builder._commands["hello"].help == "Say hello"

    def test_add_option_global(self) -> None:
        """Test adding global options."""
        builder = FlextCliBuilder()

        result = builder.add_option("--debug", help="Enable debug mode", is_flag=True)

        assert result is builder
        assert len(builder._global_options) > 2  # Includes defaults

    def test_add_option_command_specific(self) -> None:
        """Test adding command-specific options."""
        builder = FlextCliBuilder()
        builder.add_command("test", lambda: None)

        result = builder.add_option("--force", command_name="test", is_flag=True)

        assert result is builder
        assert len(builder._commands["test"].options) == 1

    def test_set_validator_fluent(self) -> None:
        """Test setting validator with fluent interface."""
        builder = FlextCliBuilder()

        result = builder.set_validator(email="email", port=lambda x: 1 <= int(x) <= 65535)

        assert result is builder
        assert builder._validator.validations["email"] == "email"

    def test_set_formatter_fluent(self) -> None:
        """Test setting formatter with fluent interface."""
        builder = FlextCliBuilder()

        result = builder.set_formatter("json")

        assert result is builder
        assert builder._formatter.style == "json"

    def test_interactive_input(self) -> None:
        """Test interactive input collection."""
        builder = FlextCliBuilder()

        schema = {
            "name": {"type": str, "prompt": "Your name", "default": "Test User"},
        }

        with patch("flext_cli.core.input.FlextCliInput.collect_dict") as mock_collect:
            mock_collect.return_value = {"name": "Test User"}

            result = builder.interactive_input(schema)

            assert result.success
            assert result.unwrap()["name"] == "Test User"

    def test_format_output(self) -> None:
        """Test output formatting."""
        builder = FlextCliBuilder()

        data = {"message": "Hello World"}
        result = builder.format_output(data, "json")

        assert result.success
        formatted = result.unwrap()
        assert isinstance(formatted, str)
        assert "Hello World" in formatted

    def test_validate_data(self) -> None:
        """Test data validation."""
        builder = FlextCliBuilder()
        builder.set_validator(email="email")

        valid_data = {"email": "test@example.com"}
        result = builder.validate_data(valid_data)

        assert result.success

        invalid_data = {"email": "invalid-email"}
        result = builder.validate_data(invalid_data)

        assert not result.success

    def test_builder_callable(self) -> None:
        """Test builder as callable."""
        builder = FlextCliBuilder()

        with patch.object(builder, "run") as mock_run:
            mock_run.return_value = FlextResult.ok(None)

            result = builder()

            assert result.success
            mock_run.assert_called_once()

    def test_build_click_group(self) -> None:
        """Test Click group building."""
        builder = FlextCliBuilder(name="testapp", version="1.0.0")

        def test_cmd() -> str:
            return "test result"

        builder.add_command("test", test_cmd, help="Test command")

        click_group = builder._build_click_group()

        assert click_group.name == "testapp"
        assert "test" in click_group.commands

    @patch("sys.argv", ["prog", "test"])
    def test_run_success(self) -> None:
        """Test successful CLI run."""
        builder = FlextCliBuilder()

        def test_cmd() -> str:
            return "success"

        builder.add_command("test", test_cmd)

        with patch("click.Group.__call__") as mock_call:
            builder.run()
            mock_call.assert_called_once()

    def test_run_with_args(self) -> None:
        """Test CLI run with custom args."""
        builder = FlextCliBuilder()

        def test_cmd() -> str:
            return "success"

        builder.add_command("test", test_cmd)

        with patch("click.Group.__call__") as mock_call:
            builder.run(["test"])
            mock_call.assert_called_with(["test"], standalone_mode=True)


# Integration test demonstrating the complete FlextCli ecosystem
class TestFlextCliIntegration:
    """Integration tests showing FlextCli components working together."""

    def test_complete_cli_workflow(self) -> None:
        """Test complete CLI workflow with all components."""
        # Create builder with all components
        builder = FlextCliBuilder(name="testapp", version="1.0.0")

        # Set up validation and formatting
        builder.set_validator(email="email")
        builder.set_formatter("json")

        # Create a command that uses all features
        def user_cmd(name: str, email: str):
            # Validate input
            validation_result = builder.validate_data({"email": email})
            if not validation_result.success:
                return FlextResult.fail(f"Invalid email: {validation_result.error}")

            # Format output
            user_data = {"name": name, "email": email, "status": "created"}
            format_result = builder.format_output(user_data)
            if format_result.success:
                return FlextResult.ok(format_result.unwrap())

            return FlextResult.fail("Formatting failed")

        # Add command with options
        builder.add_command("user", user_cmd, help="Create user")
        builder.add_option("--name", command_name="user", required=True)
        builder.add_option("--email", command_name="user", required=True)

        # Verify everything is set up correctly
        assert "user" in builder._commands
        assert builder._validator.validations["email"] == "email"
        assert builder._formatter.style == "json"

        # Test validation
        result = builder.validate_data({"email": "test@example.com"})
        assert result.success

        # Test formatting
        result = builder.format_output({"test": "data"})
        assert result.success
        assert '"test": "data"' in result.unwrap()

    def test_utility_functions_integration(self) -> None:
        """Test utility functions working with core classes."""
        from flext_cli import (
            flext_cli_create_builder,
            flext_cli_format_output,
            flext_cli_validate_inputs,
        )

        # Create builder using utility
        builder = flext_cli_create_builder("utiltest")
        assert isinstance(builder, FlextCliBuilder)
        assert builder.name == "utiltest"

        # Create validator using utility
        validator = flext_cli_validate_inputs(email="email", port=lambda x: 1 <= int(x) <= 65535)
        assert isinstance(validator, FlextCliValidator)

        # Format output using utility
        result = flext_cli_format_output({"key": "value"}, "json")
        assert result.success
        assert '"key": "value"' in result.unwrap()
