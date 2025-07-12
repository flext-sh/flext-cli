"""Unit tests for CLI commands.

Modern unit tests for Click commands with full isolation.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import yaml

if TYPE_CHECKING:
    from typing import Any

    from click import Command
    from click.testing import CliRunner
    from click.testing import Result


class TestPipelineCommands:
    """Test pipeline-related CLI commands."""

    def test_list_pipelines_json_output(
        self,
        cli: Command,
        cli_runner: CliRunner,
        mock_api_client: Any,
        mocker: Any,
    ) -> None:
        """Test pipeline list command with JSON output format.

        Args:
            cli: Main CLI command.
            cli_runner: Click test runner.
            mock_api_client: Mock API client.
            mocker: Pytest mocker fixture.

        """
        # Mock the API client in the CLI module
        mocker.patch(
            "flext_cli.commands.pipeline.get_api_client",
            return_value=mock_api_client,
        )

        result: Result = cli_runner.invoke(
            cli,
            ["pipeline", "list", "--output", "json"],
        )

        assert result.exit_code == 0
        assert "pipeline-1" in result.output
        assert "pipeline-2" in result.output
        assert mock_api_client.list_pipelines.called

    def test_list_pipelines_table_output(
        self,
        cli: Command,
        cli_runner: CliRunner,
        mock_api_client: Any,
        mocker: Any,
    ) -> None:
        """Test pipeline list command with table output format.

        Args:
            cli: Main CLI command.
            cli_runner: Click test runner.
            mock_api_client: Mock API client.
            mocker: Pytest mocker fixture.

        """
        mocker.patch(
            "flext_cli.commands.pipeline.get_api_client",
            return_value=mock_api_client,
        )

        result: Result = cli_runner.invoke(
            cli,
            ["pipeline", "list", "--output", "table"],
        )

        assert result.exit_code == 0
        assert "│" in result.output  # Table borders
        assert "test-pipeline-1" in result.output
        assert "active" in result.output

    def test_get_pipeline(
        self,
        cli: Command,
        cli_runner: CliRunner,
        mock_api_client: Any,
        mocker: Any,
    ) -> None:
        """Test get single pipeline command.

        Args:
            cli: Main CLI command.
            cli_runner: Click test runner.
            mock_api_client: Mock API client.
            mocker: Pytest mocker fixture.

        """
        mocker.patch(
            "flext_cli.commands.pipeline.get_api_client",
            return_value=mock_api_client,
        )

        result: Result = cli_runner.invoke(
            cli,
            ["pipeline", "get", "pipeline-1"],
        )

        assert result.exit_code == 0
        assert "pipeline-1" in result.output
        mock_api_client.get_pipeline.assert_called_once_with("pipeline-1")

    def test_create_pipeline_with_config_file(
        self,
        cli: Command,
        isolated_cli_runner: CliRunner,
        mock_api_client: Any,
        pipeline_config: dict[str, Any],
        mocker: Any,
    ) -> None:
        """Test pipeline creation with configuration file.

        Args:
            cli: Main CLI command.
            isolated_cli_runner: Isolated CLI test runner.
            mock_api_client: Mock API client.
            pipeline_config: Pipeline configuration dictionary.
            mocker: Pytest mocker fixture.

        """
        # Create config file in isolated filesystem
        config_path = Path("pipeline.yaml")
        config_path.write_text(yaml.dump(pipeline_config), encoding="utf-8")

        mocker.patch(
            "flext_cli.commands.pipeline.get_api_client",
            return_value=mock_api_client,
        )

        result: Result = isolated_cli_runner.invoke(
            cli,
            ["pipeline", "create", "--config", "pipeline.yaml"],
        )

        assert result.exit_code == 0
        assert "pipeline-new" in result.output
        mock_api_client.create_pipeline.assert_called_once()

    def test_delete_pipeline_with_confirmation(
        self,
        cli: Command,
        cli_runner: CliRunner,
        mock_api_client: Any,
        mock_confirm: Any,
        mocker: Any,
    ) -> None:
        """Test pipeline deletion with user confirmation.

        Args:
            cli: Main CLI command.
            cli_runner: Click test runner.
            mock_api_client: Mock API client.
            mock_confirm: Mock confirmation prompt.
            mocker: Pytest mocker fixture.

        """
        mocker.patch(
            "flext_cli.commands.pipeline.get_api_client",
            return_value=mock_api_client,
        )
        mock_api_client.delete_pipeline.return_value = None

        result: Result = cli_runner.invoke(
            cli,
            ["pipeline", "delete", "pipeline-1"],
        )

        assert result.exit_code == 0
        assert mock_confirm.called
        mock_api_client.delete_pipeline.assert_called_once_with("pipeline-1")

    def test_run_pipeline(
        self,
        cli: Command,
        cli_runner: CliRunner,
        mock_api_client: Any,
        mocker: Any,
    ) -> None:
        """Test pipeline execution command.

        Args:
            cli: Main CLI command.
            cli_runner: Click test runner.
            mock_api_client: Mock API client.
            mocker: Pytest mocker fixture.

        """
        mocker.patch(
            "flext_cli.commands.pipeline.get_api_client",
            return_value=mock_api_client,
        )
        mock_api_client.run_pipeline.return_value = {
            "run_id": "run-123",
            "status": "running",
        }

        result: Result = cli_runner.invoke(
            cli,
            ["pipeline", "run", "pipeline-1"],
        )

        assert result.exit_code == 0
        assert "run-123" in result.output
        mock_api_client.run_pipeline.assert_called_once_with("pipeline-1")


class TestConfigCommands:
    """Test configuration commands."""

    def test_config_show(
        self,
        cli: Command,
        cli_runner: CliRunner,
        config_file: Any,
        mocker: Any,
    ) -> None:
        """Test configuration show command.

        Args:
            cli: Main CLI command.
            cli_runner: Click test runner.
            config_file: Configuration file fixture.
            mocker: Pytest mocker fixture.

        """
        mocker.patch("flext_cli.config.get_config_path", return_value=config_file)

        result: Result = cli_runner.invoke(cli, ["config", "show"])

        assert result.exit_code == 0
        assert "http://localhost:8000" in result.output
        assert "test-token-123" in result.output

    def test_config_set(
        self,
        cli: Command,
        isolated_cli_runner: CliRunner,
    ) -> None:
        """Test configuration set command.

        Args:
            cli: Main CLI command.
            isolated_cli_runner: Isolated CLI test runner.

        """
        result: Result = isolated_cli_runner.invoke(
            cli,
            ["config", "set", "api.url", "http://new-api:9000"],
        )

        assert result.exit_code == 0
        assert "Updated" in result.output

        # Verify the value was set
        show_result: Result = isolated_cli_runner.invoke(cli, ["config", "show"])
        assert "http://new-api:9000" in show_result.output

    def test_config_get(
        self,
        cli: Command,
        cli_runner: CliRunner,
        config_file: Any,
        mocker: Any,
    ) -> None:
        """Test configuration get command.

        Args:
            cli: Main CLI command.
            cli_runner: Click test runner.
            config_file: Configuration file fixture.
            mocker: Pytest mocker fixture.

        """
        mocker.patch("flext_cli.config.get_config_path", return_value=config_file)

        result: Result = cli_runner.invoke(cli, ["config", "get", "api.url"])

        assert result.exit_code == 0
        assert "http://localhost:8000" in result.output


class TestAuthCommands:
    """Test authentication commands."""

    def test_login_interactive(
        self,
        cli: Command,
        cli_runner: CliRunner,
        mock_api_client: Any,
        mocker: Any,
    ) -> None:
        """Test interactive login command.

        Args:
            cli: Main CLI command.
            cli_runner: Click test runner.
            mock_api_client: Mock API client.
            mocker: Pytest mocker fixture.

        """
        mocker.patch(
            "flext_cli.commands.auth.get_api_client",
            return_value=mock_api_client,
        )
        mocker.patch("getpass.getpass", return_value="password123")

        mock_api_client.login.return_value = {"token": "new-token-456"}

        result: Result = cli_runner.invoke(
            cli,
            ["auth", "login", "--username", "testuser"],
        )

        assert result.exit_code == 0
        assert "Successfully logged in" in result.output
        mock_api_client.login.assert_called_once_with("testuser", "password123")

    def test_logout(
        self,
        cli: Command,
        cli_runner: CliRunner,
        mocker: Any,
    ) -> None:
        """Test logout command.

        Args:
            cli: Main CLI command.
            cli_runner: Click test runner.
            mocker: Pytest mocker fixture.

        """
        mock_config = mocker.patch("flext_cli.commands.auth.remove_auth_token")

        result: Result = cli_runner.invoke(cli, ["auth", "logout"])

        assert result.exit_code == 0
        assert "Successfully logged out" in result.output
        mock_config.assert_called_once()

    def test_whoami(
        self,
        cli: Command,
        cli_runner: CliRunner,
        mock_api_client: Any,
        mocker: Any,
    ) -> None:
        """Test whoami command for current user info.

        Args:
            cli: Main CLI command.
            cli_runner: Click test runner.
            mock_api_client: Mock API client.
            mocker: Pytest mocker fixture.

        """
        mocker.patch(
            "flext_cli.commands.auth.get_api_client",
            return_value=mock_api_client,
        )
        mock_api_client.get_current_user.return_value = {
            "username": "testuser",
            "email": "test@example.com",
            "roles": ["REDACTED_LDAP_BIND_PASSWORD", "developer"],
        }

        result: Result = cli_runner.invoke(cli, ["auth", "whoami"])

        assert result.exit_code == 0
        assert "testuser" in result.output
        assert "test@example.com" in result.output
