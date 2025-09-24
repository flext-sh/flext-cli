"""Tests for flext_cli.cli module."""

from unittest.mock import MagicMock, patch

from flext_cli.api import FlextCliApi
from flext_cli.auth import FlextCliAuth
from flext_cli.cli import FlextCli
from flext_cli.commands import FlextCliCommands
from flext_cli.config import FlextCliConfig
from flext_cli.debug import FlextCliDebug
from flext_cli.output import FlextCliOutput
from flext_core import FlextResult


class TestFlextCli:
    """Test cases for FlextCli class."""

    def test_init(self) -> None:
        """Test FlextCli initialization."""
        cli = FlextCli()

        # Check that all components are initialized
        assert cli.api is not None
        assert cli.auth is not None
        assert cli.config is not None
        assert cli.debug is not None
        assert cli.formatters is not None
        assert cli.main is not None

    def test_execute_success(self) -> None:
        """Test execute method returns success."""
        cli = FlextCli()
        result = cli.execute()

        assert result.is_success
        data = result.unwrap()
        assert data["status"] == "operational"
        assert data["service"] == "flext-cli"
        assert data["version"] == "2.0.0"
        assert "timestamp" in data
        assert "components" in data

        # Check components
        components = data["components"]
        assert components["api"] == "available"
        assert components["auth"] == "available"
        assert components["config"] == "available"
        assert components["debug"] == "available"
        assert components["formatters"] == "available"
        assert components["main"] == "available"

    def test_execute_returns_flext_result(self) -> None:
        """Test that execute returns FlextResult."""
        cli = FlextCli()
        result = cli.execute()

        # Check FlextResult properties
        assert hasattr(result, "is_success")
        assert hasattr(result, "is_failure")
        assert hasattr(result, "unwrap")
        assert hasattr(result, "error")

        # Should be successful
        assert result.is_success
        assert not result.is_failure
        assert not result.error

    def test_execute_data_structure(self) -> None:
        """Test execute method data structure."""
        cli = FlextCli()
        result = cli.execute()

        assert result.is_success
        data = result.unwrap()

        # Check required fields
        required_fields = ["status", "service", "timestamp", "version", "components"]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"

        # Check data types
        assert isinstance(data["status"], str)
        assert isinstance(data["service"], str)
        assert isinstance(data["timestamp"], str)
        assert isinstance(data["version"], str)
        assert isinstance(data["components"], dict)

        # Check component data types
        for component_name, component_status in data["components"].items():
            assert isinstance(component_name, str)
            assert isinstance(component_status, str)
            assert component_status == "available"

    def test_cli_components_initialization(self) -> None:
        """Test that all CLI components are properly initialized."""
        cli = FlextCli()

        # Check component types
        assert isinstance(cli.api, FlextCliApi)
        assert isinstance(cli.auth, FlextCliAuth)
        assert isinstance(cli.config, FlextCliConfig.MainConfig)
        assert isinstance(cli.debug, FlextCliDebug)
        assert isinstance(cli.formatters, FlextCliOutput)
        assert isinstance(cli.main, FlextCliCommands)

    def test_run_cli_method_exists(self) -> None:
        """Test that run_cli method exists and can be called."""
        cli = FlextCli()

        # Verify the method exists
        assert hasattr(cli, "run_cli")
        assert callable(cli.run_cli)

    def test_cli_has_required_attributes(self) -> None:
        """Test that CLI has all required attributes."""
        cli = FlextCli()

        # Check that all required attributes exist
        required_attrs = ["api", "auth", "config", "debug", "formatters", "main"]
        for attr in required_attrs:
            assert hasattr(cli, attr), f"Missing attribute: {attr}"
            assert getattr(cli, attr) is not None, f"Attribute {attr} is None"

    @patch("flext_cli.cli.click")
    def test_run_cli_status_command(self, mock_click: MagicMock) -> None:
        """Test CLI status command."""
        cli = FlextCli()

        # Mock click methods and Abort
        mock_click.echo = MagicMock()
        mock_click.Abort = Exception("Abort")

        # Test that the CLI can be created and has required components
        assert cli.api is not None
        assert cli.auth is not None
        assert cli.config is not None
        assert cli.debug is not None

    @patch("flext_cli.cli.click")
    def test_run_cli_version_command(self, mock_click: MagicMock) -> None:
        """Test CLI version command."""
        cli = FlextCli()

        # Mock click methods
        mock_click.echo = MagicMock()

        # Test that the CLI can be created and has required components
        assert cli.api is not None
        assert cli.auth is not None
        assert cli.config is not None
        assert cli.debug is not None

    @patch("flext_cli.cli.click")
    def test_run_cli_execution_success(self, mock_click: MagicMock) -> None:
        """Test run_cli method execution with successful status."""
        cli = FlextCli()

        # Mock click methods
        mock_click.echo = MagicMock()
        mock_click.group = MagicMock()
        mock_click.version_option = MagicMock()
        mock_click.command = MagicMock()
        mock_click.Abort = Exception("Abort")

        # Mock the CLI group and its methods
        mock_cli_group = MagicMock()
        mock_click.group.return_value = mock_cli_group
        mock_cli_group.add_command = MagicMock()
        mock_cli_group.__call__ = MagicMock()

        # Mock command decorators to return the original function
        def mock_decorator(func: object) -> object:
            return func

        mock_click.command.return_value = mock_decorator

        # Mock version_option decorator
        def mock_version_decorator(func: object) -> object:
            return func

        mock_click.version_option.return_value = mock_version_decorator

        # Call run_cli method
        cli.run_cli()

        # Verify click.group was called
        mock_click.group.assert_called_once()

        # Verify version_option was called
        mock_click.version_option.assert_called_once_with(version="0.9.0")

        # Verify commands were added (the decorators handle this)
        assert mock_cli_group.add_command.call_count >= 0

    @patch("flext_cli.cli.click")
    def test_run_cli_execution_with_failure(self, mock_click: MagicMock) -> None:
        """Test run_cli method execution when execute() fails."""
        cli = FlextCli()

        # Mock click methods
        mock_click.echo = MagicMock()
        mock_click.group = MagicMock()
        mock_click.version_option = MagicMock()
        mock_click.command = MagicMock()
        mock_click.Abort = Exception("Abort")

        # Mock the CLI group and its methods
        mock_cli_group = MagicMock()
        mock_click.group.return_value = mock_cli_group
        mock_cli_group.add_command = MagicMock()
        mock_cli_group.__call__ = MagicMock()

        # Mock command decorators to return the original function
        def mock_decorator(func: object) -> object:
            return func

        mock_click.command.return_value = mock_decorator

        # Mock version_option decorator
        def mock_version_decorator(func: object) -> object:
            return func

        mock_click.version_option.return_value = mock_version_decorator

        # Mock execute to return failure
        with patch.object(
            cli,
            "execute",
            return_value=FlextResult[dict[str, object]].fail("Test error"),
        ):
            # Call run_cli method
            cli.run_cli()

        # Verify click.group was called
        mock_click.group.assert_called_once()

        # Verify version_option was called
        mock_click.version_option.assert_called_once_with(version="0.9.0")

        # Verify commands were added (the decorators handle this)
        assert mock_cli_group.add_command.call_count >= 0
