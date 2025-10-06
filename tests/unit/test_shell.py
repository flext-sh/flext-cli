"""Tests for flext_cli.shell module."""

from unittest.mock import Mock

from flext_cli.shell import FlextCliShell


class TestFlextCliShell:
    """Test FlextCliShell class."""

    def test_shell_creation(self) -> None:
        """Test shell instance creation."""
        mock_cli_main = Mock()
        shell = FlextCliShell(cli_main=mock_cli_main)
        assert isinstance(shell, FlextCliShell)

    def test_shell_with_prompt(self) -> None:
        """Test shell with custom prompt."""
        mock_cli_main = Mock()
        shell = FlextCliShell(cli_main=mock_cli_main, prompt="test> ")
        assert shell._prompt == "test> "

    def test_shell_with_history(self) -> None:
        """Test shell with history file."""
        mock_cli_main = Mock()
        shell = FlextCliShell(cli_main=mock_cli_main, history_file="test_history")
        assert shell._history_file is not None

    def test_shell_builder_pattern(self) -> None:
        """Test shell builder pattern."""
        mock_cli_main = Mock()
        shell = FlextCliShell.create_builder(mock_cli_main)
        assert isinstance(shell, FlextCliShell)

    def test_shell_chain_methods(self) -> None:
        """Test shell chaining methods."""
        mock_cli_main = Mock()
        shell = FlextCliShell(cli_main=mock_cli_main)

        # Test chaining
        result = (
            shell.with_prompt("test> ").with_history("test_history").with_completion()
        )
        assert result is shell
        assert shell._prompt == "test> "
        assert shell._history_file is not None
        assert shell._enable_completion is True
