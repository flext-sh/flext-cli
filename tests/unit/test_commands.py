"""Unit tests for CLI commands."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import Mock

import pytest
from click.testing import CliRunner
from flext_cli import flext_cli_create_builder


class TestCommands:
    """Test CLI commands functionality."""

    @pytest.fixture
    def cli(self) -> Any:
        """Create CLI instance for testing."""
        return flext_cli_create_builder("test-cli")

    @pytest.fixture
    def cli_runner(self) -> CliRunner:
        """Create CLI runner for testing."""
        return CliRunner()

    @pytest.fixture
    def mock_api_client(self) -> Mock:
        """Mock API client."""
        return Mock()

    @pytest.fixture
    def mocker(self) -> Mock:
        """Mock object."""
        return Mock()

    def test_pipeline_list_command_json_output(
        self,
        cli: Any,
        cli_runner: CliRunner,
        mock_api_client: Mock,
        mocker: Mock,
    ) -> None:
        """Test pipeline list command with JSON output."""
        # Mock API response
        mock_response = [
            {"id": "pipeline-1", "name": "Test Pipeline", "status": "running"},
            {"id": "pipeline-2", "name": "Another Pipeline", "status": "stopped"},
        ]
        mock_api_client.list_pipelines.return_value = mock_response

        # Mock the API client
        mocker.patch(
            "flext_cli.core.api_client.get_api_client",
            return_value=mock_api_client,
        )

        # Run command
        result = cli_runner.invoke(cli, ["pipeline", "list", "--format", "json"])

        assert result.exit_code == 0
        assert "pipeline-1" in result.output
        assert "Test Pipeline" in result.output

    def test_pipeline_list_command_table_output(
        self,
        cli: Any,
        cli_runner: CliRunner,
        mock_api_client: Mock,
        mocker: Mock,
    ) -> None:
        """Test pipeline list command with table output."""
        # Mock API response
        mock_response = [
            {"id": "pipeline-1", "name": "Test Pipeline", "status": "running"},
            {"id": "pipeline-2", "name": "Another Pipeline", "status": "stopped"},
        ]
        mock_api_client.list_pipelines.return_value = mock_response

        # Mock the API client
        mocker.patch(
            "flext_cli.core.api_client.get_api_client",
            return_value=mock_api_client,
        )

        # Run command
        result = cli_runner.invoke(cli, ["pipeline", "list", "--format", "table"])

        assert result.exit_code == 0
        assert "Test Pipeline" in result.output

    def test_pipeline_get_command(
        self,
        cli: Any,
        cli_runner: CliRunner,
        mock_api_client: Mock,
        mocker: Mock,
    ) -> None:
        """Test pipeline get command."""
        # Mock API response
        mock_response = {
            "id": "pipeline-1",
            "name": "Test Pipeline",
            "status": "running",
            "created_at": "2023-01-01T00:00:00Z",
        }
        mock_api_client.get_pipeline.return_value = mock_response

        # Mock the API client
        mocker.patch(
            "flext_cli.core.api_client.get_api_client",
            return_value=mock_api_client,
        )

        # Run command
        result = cli_runner.invoke(cli, ["pipeline", "get", "pipeline-1"])

        assert result.exit_code == 0
        assert "Test Pipeline" in result.output
        assert "running" in result.output

    def test_pipeline_create_command_with_config_file(
        self,
        cli: Any,
        isolated_cli_runner: CliRunner,
        mock_api_client: Mock,
        pipeline_config: dict[str, Any],
        mocker: Mock,
    ) -> None:
        """Test pipeline creation with configuration file."""
        # Mock API response
        mock_response = {
            "id": "new-pipeline-id",
            "name": "new-pipeline",
            "status": "created",
        }
        mock_api_client.create_pipeline.return_value = mock_response

        # Mock the API client
        mocker.patch(
            "flext_cli.core.api_client.get_api_client",
            return_value=mock_api_client,
        )

        # Create temporary config file
        with isolated_cli_runner.isolated_filesystem():
            with Path("pipeline_config.json").open("w") as f:
                import json

                json.dump(pipeline_config, f)

            # Run command
            result = isolated_cli_runner.invoke(
                cli,
                ["pipeline", "create", "--config", "pipeline_config.json"],
            )

            assert result.exit_code == 0
            assert "new-pipeline-id" in result.output

    def test_pipeline_delete_command_with_confirmation(
        self,
        cli: Any,
        cli_runner: CliRunner,
        mock_api_client: Mock,
        mocker: Mock,
    ) -> None:
        """Test pipeline delete command with confirmation."""
        # Mock API response
        mock_api_client.delete_pipeline.return_value = {"status": "deleted"}

        # Mock the API client
        mocker.patch(
            "flext_cli.core.api_client.get_api_client",
            return_value=mock_api_client,
        )

        # Mock confirmation
        mocker.patch("click.confirm", return_value=True)

        # Run command
        result = cli_runner.invoke(cli, ["pipeline", "delete", "pipeline-1"])

        assert result.exit_code == 0
        assert "deleted" in result.output

    def test_pipeline_execute_command(
        self,
        cli: Any,
        cli_runner: CliRunner,
        mock_api_client: Mock,
        mocker: Mock,
    ) -> None:
        """Test pipeline execute command."""
        # Mock API response
        mock_response = {"execution_id": "exec-123", "status": "started"}
        mock_api_client.execute_pipeline.return_value = mock_response

        # Mock the API client
        mocker.patch(
            "flext_cli.core.api_client.get_api_client",
            return_value=mock_api_client,
        )

        # Run command
        result = cli_runner.invoke(cli, ["pipeline", "execute", "pipeline-1"])

        assert result.exit_code == 0
        assert "exec-123" in result.output

    def test_config_show_command(
        self,
        cli: Any,
        cli_runner: CliRunner,
        config_file: Any,
        mocker: Mock,
    ) -> None:
        """Test config show command."""
        # Mock config file
        mocker.patch("pathlib.Path.exists", return_value=True)
        mocker.patch(
            "pathlib.Path.read_text",
            return_value='{"api_url": "http://localhost:8000"}',
        )

        # Run command
        result = cli_runner.invoke(cli, ["config", "show"])

        assert result.exit_code == 0
        assert "api_url" in result.output

    def test_config_get_command(
        self,
        cli: Any,
        cli_runner: CliRunner,
        config_file: Any,
        mocker: Mock,
    ) -> None:
        """Test config get command."""
        # Mock config file
        mocker.patch("pathlib.Path.exists", return_value=True)
        mocker.patch(
            "pathlib.Path.read_text",
            return_value='{"api_url": "http://localhost:8000"}',
        )

        # Run command
        result = cli_runner.invoke(cli, ["config", "get", "api_url"])

        assert result.exit_code == 0
        assert "http://localhost:8000" in result.output

    def test_auth_login_command(
        self,
        cli: Any,
        cli_runner: CliRunner,
        mock_api_client: Mock,
        mocker: Mock,
    ) -> None:
        """Test auth login command."""
        # Mock API response
        mock_response = {"access_token": "token123", "user": "testuser"}
        mock_api_client.login.return_value = mock_response

        # Mock the API client
        mocker.patch(
            "flext_cli.core.api_client.get_api_client",
            return_value=mock_api_client,
        )

        # Mock user input
        mocker.patch("click.prompt", side_effect=["testuser", "password123"])

        # Run command
        result = cli_runner.invoke(cli, ["auth", "login"])

        assert result.exit_code == 0
        assert "Logged in successfully" in result.output

    def test_auth_logout_command(
        self,
        cli: Any,
        cli_runner: CliRunner,
        mocker: Mock,
    ) -> None:
        """Test auth logout command."""
        # Mock config file operations
        mocker.patch("pathlib.Path.exists", return_value=True)
        mocker.patch("pathlib.Path.unlink", return_value=None)

        # Run command
        result = cli_runner.invoke(cli, ["auth", "logout"])

        assert result.exit_code == 0
        assert "Logged out successfully" in result.output

    def test_whoami_command(
        self,
        cli: Any,
        cli_runner: CliRunner,
        mock_api_client: Mock,
        mocker: Mock,
    ) -> None:
        """Test whoami command."""
        # Mock API response
        mock_response = {"user": "testuser", "email": "test@example.com"}
        mock_api_client.get_current_user.return_value = mock_response

        # Mock the API client
        mocker.patch(
            "flext_cli.core.api_client.get_api_client",
            return_value=mock_api_client,
        )

        # Run command
        result = cli_runner.invoke(cli, ["whoami"])

        assert result.exit_code == 0
        assert "testuser" in result.output
        assert "test@example.com" in result.output
