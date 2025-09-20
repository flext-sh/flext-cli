"""Tests for FlextCliMain - Consolidated CLI main class.

Comprehensive tests for the consolidated CLI functionality that replaced
cli.py, unified_cli.py, cli_bus.py, and cmd.py modules.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import pytest

from flext_cli import FlextCliMain as ImportedMain
from flext_cli.main import FlextCliMain


class TestFlextCliMain:
    """Test FlextCliMain - consolidated CLI main class."""

    def test_cli_main_initialization(self) -> None:
        """Test FlextCliMain can be initialized."""
        cli = FlextCliMain()
        assert cli is not None

    def test_cli_main_has_expected_methods(self) -> None:
        """Test FlextCliMain has expected CLI methods."""
        cli = FlextCliMain()

        # Check for key CLI methods from consolidated functionality
        expected_methods = [
            "register_command",
            "register_command_group",
            "add_command",
            "create_group",
            "run",
            "parse_args",
        ]

        for method_name in expected_methods:
            assert hasattr(cli, method_name), f"Missing method: {method_name}"
            assert callable(getattr(cli, method_name)), (
                f"Method not callable: {method_name}"
            )

    def test_cli_main_initialization_with_params(self) -> None:
        """Test FlextCliMain initialization with parameters."""
        cli = FlextCliMain(name="test-cli", description="Test CLI application")
        assert cli is not None
        assert cli.name == "test-cli"
        assert cli.description == "Test CLI application"

    def test_cli_main_register_command_basic(self) -> None:
        """Test basic command registration."""
        cli = FlextCliMain()

        def test_command() -> str:
            return "test"

        # Should be able to register a command
        result = cli.register_command("test", test_command)
        assert result is not None

    def test_cli_main_register_command_group_basic(self) -> None:
        """Test basic command group registration."""
        cli = FlextCliMain()

        commands = {"sub1": lambda: "sub1 result", "sub2": lambda: "sub2 result"}

        # Should be able to register a command group
        result = cli.register_command_group("group", commands)
        assert result is not None

    def test_cli_main_create_group_basic(self) -> None:
        """Test basic group creation."""
        cli = FlextCliMain()

        # Should be able to create a group
        group = cli.create_group("mygroup", description="Test group")
        assert group is not None

    def test_cli_main_has_nested_helper_classes(self) -> None:
        """Test FlextCliMain has nested helper classes."""
        cli = FlextCliMain()

        # Check for nested helper classes (from consolidated functionality)
        expected_helpers = [
            "_OptionsHelper",
            "_ContextHelper",
            "_VersionHelper",
            "_LoggingHelper",
            "_AuthCommands",
            "_ConfigCommands",
            "_SystemCommands",
        ]

        for helper_name in expected_helpers:
            assert hasattr(cli, helper_name), f"Missing helper class: {helper_name}"
            helper_class = getattr(cli, helper_name)
            assert callable(helper_class), f"Helper class not callable: {helper_name}"


class TestFlextCliMainAdvanced:
    """Advanced tests for FlextCliMain."""

    def test_cli_main_command_execution(self) -> None:
        """Test CLI command execution."""
        cli = FlextCliMain()

        executed = []

        def test_command() -> str:
            executed.append("test_command")
            return "success"

        cli.register_command("test", test_command)

        # Should be able to execute the command
        try:
            result = cli.run(["test"])
            assert "test_command" in executed or result is not None
        except SystemExit:
            # CLI might exit normally, which is acceptable
            pass

    def test_cli_main_handles_help_command(self) -> None:
        """Test CLI handles help command."""
        cli = FlextCliMain()

        # Should handle help without errors
        try:
            cli.run(["--help"])
        except SystemExit:
            # Help command typically exits, which is normal
            pass

    def test_cli_main_handles_version_command(self) -> None:
        """Test CLI handles version command."""
        cli = FlextCliMain()

        # Should handle version without errors
        try:
            cli.run(["--version"])
        except SystemExit:
            # Version command typically exits, which is normal
            pass

    def test_cli_main_nested_helpers_functionality(self) -> None:
        """Test nested helper classes functionality."""
        cli = FlextCliMain()

        # Test OptionsHelper
        options_helper = cli._OptionsHelper()
        assert options_helper is not None

        # Test ContextHelper
        context_helper = cli._ContextHelper()
        assert context_helper is not None

        # Test VersionHelper
        version_helper = cli._VersionHelper()
        assert version_helper is not None

    def test_cli_main_auth_commands_integration(self) -> None:
        """Test AuthCommands integration."""
        cli = FlextCliMain()

        auth_commands = cli._AuthCommands()
        assert auth_commands is not None

        # Should have auth command methods
        expected_auth_methods = ["login", "logout", "status"]
        for method in expected_auth_methods:
            assert hasattr(auth_commands, method), f"Missing auth method: {method}"

    def test_cli_main_config_commands_integration(self) -> None:
        """Test ConfigCommands integration."""
        cli = FlextCliMain()

        config_commands = cli._ConfigCommands()
        assert config_commands is not None

        # Should have config command methods
        expected_config_methods = ["get", "set", "list", "reset"]
        for method in expected_config_methods:
            assert hasattr(config_commands, method), f"Missing config method: {method}"


class TestFlextCliMainIntegration:
    """Integration tests for FlextCliMain."""

    def test_cli_main_can_be_imported_from_main_package(self) -> None:
        """Test FlextCliMain can be imported from main package."""
        cli = ImportedMain()
        assert cli is not None
        assert isinstance(cli, FlextCliMain)

    def test_cli_main_is_primary_cli_api(self) -> None:
        """Test FlextCliMain is designated as primary CLI API."""
        # Should be importable as the primary CLI class
        cli = FlextCliMain()
        assert cli is not None

        # Should have comprehensive CLI capabilities
        methods = dir(cli)
        cli_methods = [
            m for m in methods if "command" in m or "group" in m or "register" in m
        ]
        assert len(cli_methods) >= 3, "Should have multiple CLI methods"

    def test_cli_main_consolidates_old_functionality(self) -> None:
        """Test FlextCliMain consolidates functionality from old modules."""
        cli = FlextCliMain()

        # Should have consolidated functionality from:
        # - cli.py (main CLI functionality)
        # - unified_cli.py (unified CLI approach)
        # - cli_bus.py (command bus pattern)
        # - cmd.py (command implementations)

        # Check for methods that would come from each old module
        assert hasattr(cli, "register_command"), "Missing cli.py functionality"
        assert hasattr(cli, "create_group"), "Missing unified_cli.py functionality"
        assert hasattr(cli, "run"), "Missing command execution functionality"

        # Check for nested classes from consolidated modules
        assert hasattr(cli, "_AuthCommands"), "Missing cmd.py auth functionality"
        assert hasattr(cli, "_ConfigCommands"), "Missing cmd.py config functionality"


class TestFlextCliMainErrorHandling:
    """Error handling tests for FlextCliMain."""

    def test_cli_main_handles_invalid_commands(self) -> None:
        """Test CLI handles invalid commands gracefully."""
        cli = FlextCliMain()

        # Should handle invalid command without crashing
        try:
            result = cli.run(["nonexistent-command"])
            # If it returns, should indicate error
            assert result is None or result != 0
        except SystemExit as e:
            # CLI should exit with non-zero code for invalid commands
            assert e.code != 0  # noqa: PT017

    def test_cli_main_handles_empty_args(self) -> None:
        """Test CLI handles empty arguments."""
        cli = FlextCliMain()

        # Should handle empty args (typically shows help)
        try:
            cli.run([])
        except SystemExit:
            # May exit normally with help
            pass

    def test_cli_main_handles_malformed_registration(self) -> None:
        """Test CLI handles malformed command registration."""
        cli = FlextCliMain()

        # Should handle invalid command registration gracefully
        with pytest.raises((TypeError, ValueError, AttributeError)):
            cli.register_command(None, None)  # Invalid parameters
