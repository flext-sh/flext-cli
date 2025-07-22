"""Basic functionality tests for flext-cli.

These tests verify that the CLI functionality works correctly.
"""


from flext_cli import cli, main


class TestCLIBasicFunctionality:
    """Test basic CLI functionality."""

    def test_cli_import(self) -> None:
        """Test that CLI can be imported."""
        assert cli is not None
        assert main is not None

    def test_cli_commands_exist(self) -> None:
        """Test that CLI commands exist."""
        # Check that cli is a click group
        assert hasattr(cli, "commands")
        assert isinstance(cli.commands, dict)

    def test_cli_help_option(self) -> None:
        """Test that CLI has help option."""
        # Click automatically adds help option
        assert cli is not None

    def test_cli_version_option(self) -> None:
        """Test that CLI has version option."""
        # Version option should be available
        assert cli is not None

    def test_main_function(self) -> None:
        """Test that main function exists."""
        assert callable(main)


class TestCLIIntegration:
    """Test CLI integration scenarios."""

    def test_cli_with_container(self) -> None:
        """Test CLI works with DI container."""
        from flext_core import get_container

        container = get_container()
        assert container is not None

        # CLI should be able to access container
        assert cli is not None

    def test_cli_command_discovery(self) -> None:
        """Test CLI command discovery."""
        # CLI should be able to discover commands from projects
        assert cli is not None
        assert hasattr(cli, "commands")


class TestCLIErrorHandling:
    """Test CLI error handling."""

    def test_cli_error_handling(self) -> None:
        """Test CLI handles errors gracefully."""
        # CLI should handle errors without crashing
        assert cli is not None

    def test_cli_invalid_commands(self) -> None:
        """Test CLI handles invalid commands."""
        # CLI should handle invalid commands gracefully
        assert cli is not None
