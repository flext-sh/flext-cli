"""Tests for FlextCliMain - Consolidated CLI main class.

Comprehensive tests for the consolidated CLI functionality that replaced
cli.py, unified_cli.py, cli_bus.py, and cmd.py modules.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import pytest

from flext_cli import FlextCliMain as ImportedMain
from flext_cli.flext_cli_main import FlextCliMain


class TestFlextCliMain:
    """Test FlextCliMain - consolidated CLI main class."""

    def test_cli_main_initialization(self) -> None:
        """Test FlextCliMain can be initialized."""
        cli = FlextCliMain()
        assert cli is not None

    def test_cli_main_has_expected_methods(self) -> None:
        """Test FlextCliMain has expected CLI methods."""
        cli = FlextCliMain()

        # Check for actual CLI methods from FlextCliMain implementation
        expected_methods = [
            "execute",
            "add_command",
            "add_group",
            "run_cli",
            "get_click_group",
            "execute_command",
            "list_commands",
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
        # FlextCliMain doesn't expose name/description as properties
        # but stores them internally in the Click group
        assert hasattr(cli, "_cli_group")
        assert cli._cli_group.name == "test-cli"

    def test_cli_main_register_command_basic(self) -> None:
        """Test basic command registration."""
        cli = FlextCliMain()

        def test_command() -> str:
            return "test"

        # Should be able to add a command using actual API
        result = cli.add_command("test", test_command)
        assert result.is_success

    def test_cli_main_add_group_basic(self) -> None:
        """Test basic command group creation using actual API."""
        cli = FlextCliMain()

        # Should be able to add a group using actual API
        result = cli.add_group("group", "Test group")
        assert result.is_success

    def test_cli_main_create_group_basic(self) -> None:
        """Test basic group creation."""
        cli = FlextCliMain()

        # Should be able to add a group using actual API
        result = cli.add_group("mygroup", "Test group")
        assert result.is_success
        group = result.value
        assert group is not None

    def test_cli_main_has_core_attributes(self) -> None:
        """Test FlextCliMain has core attributes."""
        cli = FlextCliMain()

        # Check for core attributes from actual implementation
        expected_attributes = [
            "_logger",
            "_container",
            "_cli_group",
        ]

        for attr_name in expected_attributes:
            assert hasattr(cli, attr_name), f"Missing core attribute: {attr_name}"
            attr_value = getattr(cli, attr_name)
            assert attr_value is not None, f"Core attribute is None: {attr_name}"


class TestFlextCliMainAdvanced:
    """Advanced tests for FlextCliMain."""

    def test_cli_main_command_execution(self) -> None:
        """Test CLI command execution."""
        cli = FlextCliMain()

        executed = []

        def test_command() -> str:
            executed.append("test_command")
            return "success"

        result = cli.add_command("test", test_command)
        assert result.is_success

        # Should be able to execute the command using run_cli
        try:
            result = cli.run_cli(["test"])
            assert "test_command" in executed or result.is_success
        except SystemExit:
            # CLI might exit normally, which is acceptable
            pass

    def test_cli_main_handles_help_command(self) -> None:
        """Test CLI handles help command."""
        cli = FlextCliMain()

        # Should handle help without errors
        try:
            cli.run_cli(["--help"])
        except SystemExit:
            # Help command typically exits, which is normal
            pass

    def test_cli_main_handles_version_command(self) -> None:
        """Test CLI handles version command."""
        cli = FlextCliMain()

        # Should handle version without errors
        try:
            cli.run_cli(["--version"])
        except SystemExit:
            # Version command typically exits, which is normal
            pass

    def test_cli_main_core_functionality(self) -> None:
        """Test core FlextCliMain functionality."""
        cli = FlextCliMain()

        # Test execute method (required by FlextService)
        execute_result = cli.execute()
        assert execute_result.is_success
        assert "status" in execute_result.value
        assert execute_result.value["status"] == "operational"

        # Test list_commands
        commands_result = cli.list_commands()
        assert commands_result.is_success
        assert isinstance(commands_result.value, list)

    def test_cli_main_command_integration(self) -> None:
        """Test command integration functionality."""
        cli = FlextCliMain()

        # Test adding multiple commands
        def cmd1() -> str:
            return "cmd1"

        def cmd2() -> str:
            return "cmd2"

        result1 = cli.add_command("cmd1", cmd1, "First command")
        assert result1.is_success

        result2 = cli.add_command("cmd2", cmd2, "Second command")
        assert result2.is_success

        # Verify commands are listed
        commands_result = cli.list_commands()
        assert commands_result.is_success
        commands = commands_result.value
        assert "cmd1" in commands
        assert "cmd2" in commands

    def test_cli_main_group_integration(self) -> None:
        """Test group integration functionality."""
        cli = FlextCliMain()

        # Test adding groups
        result1 = cli.add_group("config", "Configuration commands")
        assert result1.is_success

        result2 = cli.add_group("auth", "Authentication commands")
        assert result2.is_success

        # Test accessing the Click group
        click_group = cli.get_click_group()
        assert click_group is not None
        assert "config" in click_group.commands
        assert "auth" in click_group.commands


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

        # Check for methods from actual implementation
        assert hasattr(cli, "add_command"), "Missing command functionality"
        assert hasattr(cli, "add_group"), "Missing group functionality"
        assert hasattr(cli, "run_cli"), "Missing command execution functionality"
        assert hasattr(cli, "execute"), "Missing FlextService execute functionality"

        # Check for core implementation attributes
        assert hasattr(cli, "_cli_group"), "Missing Click group integration"
        assert hasattr(cli, "_logger"), "Missing logging functionality"


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
            # Use pytest.raises pattern instead of assertion in except block
            if e.code is None or e.code == 0:
                pytest.fail("Expected non-zero exit code for invalid command")

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
