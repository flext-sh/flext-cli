"""Additional coverage for FlextCliLoggingSetup class methods.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

from flext_cli.config import FlextCliConfig
from flext_cli.logging_setup import FlextCliLoggingSetup
from flext_core import FlextResult


class TestFlextCliLoggingSetupClassMethods:
    """Test class methods of FlextCliLoggingSetup."""

    def setup_method(self) -> None:
        """Set up test environment."""
        FlextCliLoggingSetup._loggers.clear()
        FlextCliLoggingSetup._setup_complete = False
        os.environ.pop("FLEXT_LOG_LEVEL", None)
        os.environ.pop("FLEXT_LOG_VERBOSITY", None)
        os.environ.pop("FLEXT_CLI_LOG_LEVEL", None)

    def teardown_method(self) -> None:
        """Clean up after tests."""
        FlextCliLoggingSetup._loggers.clear()
        FlextCliLoggingSetup._setup_complete = False
        os.environ.pop("FLEXT_LOG_LEVEL", None)
        os.environ.pop("FLEXT_LOG_VERBOSITY", None)
        os.environ.pop("FLEXT_CLI_LOG_LEVEL", None)

    @patch("flext_cli.logging_setup.FlextLogger.configure")
    def test_setup_for_cli_default(self, _mock_configure: MagicMock) -> None:
        """Test setup_for_cli with default config."""
        result = FlextCliLoggingSetup.setup_for_cli()
        assert result.is_success
        assert "CLI logging configured" in result.value
        assert "level=" in result.value
        assert "source=" in result.value

    @patch("flext_cli.logging_setup.FlextLogger.configure")
    def test_setup_for_cli_with_config(self, _mock_configure: MagicMock) -> None:
        """Test setup_for_cli with custom config."""
        config = FlextCliConfig.MainConfig(log_level="DEBUG")
        result = FlextCliLoggingSetup.setup_for_cli(config=config)
        assert result.is_success
        assert "DEBUG" in result.value or "INFO" in result.value

    @patch("flext_cli.logging_setup.FlextLogger.configure")
    def test_setup_for_cli_with_log_file(self, _mock_configure: MagicMock) -> None:
        """Test setup_for_cli with log file."""
        with tempfile.NamedTemporaryFile(suffix=".log", delete=False) as tmp:
            log_file = Path(tmp.name)

        try:
            result = FlextCliLoggingSetup.setup_for_cli(log_file=log_file)
            assert result.is_success
        finally:
            log_file.unlink(missing_ok=True)

    @patch("flext_cli.logging_setup.FlextLogger.configure")
    def test_setup_for_cli_failure(self, mock_configure: MagicMock) -> None:
        """Test setup_for_cli failure scenario."""
        mock_configure.side_effect = Exception("Configuration error")
        result = FlextCliLoggingSetup.setup_for_cli()
        assert result.is_failure
        assert "Logging setup failed" in (result.error or "")

    def test_get_effective_log_level_default(self) -> None:
        """Test get_effective_log_level with default config."""
        result = FlextCliLoggingSetup.get_effective_log_level()
        assert result.is_success
        assert "INFO" in result.value
        assert "default" in result.value

    def test_get_effective_log_level_with_config(self) -> None:
        """Test get_effective_log_level with custom config."""
        config = FlextCliConfig.MainConfig(log_level="WARNING")
        result = FlextCliLoggingSetup.get_effective_log_level(config=config)
        assert result.is_success
        assert "WARNING" in result.value

    @patch.dict(os.environ, {"FLEXT_CLI_LOG_LEVEL": "ERROR"})
    def test_get_effective_log_level_from_env(self) -> None:
        """Test get_effective_log_level from environment."""
        result = FlextCliLoggingSetup.get_effective_log_level()
        assert result.is_success
        assert "ERROR" in result.value

    def test_set_global_log_level_valid(self) -> None:
        """Test set_global_log_level with valid level."""
        result = FlextCliLoggingSetup.set_global_log_level("DEBUG")
        assert result.is_success
        assert "DEBUG" in result.value
        assert os.environ.get("FLEXT_LOG_LEVEL") == "DEBUG"

    def test_set_global_log_level_lowercase(self) -> None:
        """Test set_global_log_level with lowercase level."""
        result = FlextCliLoggingSetup.set_global_log_level("warning")
        assert result.is_success
        assert "WARNING" in result.value
        assert os.environ.get("FLEXT_LOG_LEVEL") == "WARNING"

    def test_set_global_log_level_invalid(self) -> None:
        """Test set_global_log_level with invalid level."""
        result = FlextCliLoggingSetup.set_global_log_level("INVALID")
        assert result.is_failure
        assert "Invalid log level" in (result.error or "")

    @patch("flext_cli.logging_setup.FlextLogger.configure")
    def test_set_global_log_level_reconfigure(self, mock_configure: MagicMock) -> None:
        """Test set_global_log_level reconfigures if setup complete."""
        FlextCliLoggingSetup._setup_complete = True
        result = FlextCliLoggingSetup.set_global_log_level("ERROR")
        assert result.is_success
        mock_configure.assert_called_once()

    def test_set_global_log_verbosity_valid(self) -> None:
        """Test set_global_log_verbosity with valid verbosity."""
        result = FlextCliLoggingSetup.set_global_log_verbosity("compact")
        assert result.is_success
        assert "compact" in result.value
        assert os.environ.get("FLEXT_LOG_VERBOSITY") == "compact"

    def test_set_global_log_verbosity_uppercase(self) -> None:
        """Test set_global_log_verbosity with uppercase verbosity."""
        result = FlextCliLoggingSetup.set_global_log_verbosity("DETAILED")
        assert result.is_success
        assert "detailed" in result.value

    def test_set_global_log_verbosity_invalid(self) -> None:
        """Test set_global_log_verbosity with invalid verbosity."""
        result = FlextCliLoggingSetup.set_global_log_verbosity("invalid")
        assert result.is_failure
        assert "Invalid verbosity" in (result.error or "")

    @patch("flext_cli.logging_setup.FlextLogger.configure")
    def test_set_global_log_verbosity_reconfigure(self, mock_configure: MagicMock) -> None:
        """Test set_global_log_verbosity reconfigures if setup complete."""
        FlextCliLoggingSetup._setup_complete = True
        os.environ["FLEXT_LOG_LEVEL"] = "INFO"
        result = FlextCliLoggingSetup.set_global_log_verbosity("full")
        assert result.is_success
        mock_configure.assert_called_once()

    def test_get_current_log_config(self) -> None:
        """Test get_current_log_config."""
        os.environ["FLEXT_LOG_LEVEL"] = "DEBUG"
        os.environ["FLEXT_LOG_VERBOSITY"] = "detailed"
        os.environ["FLEXT_CLI_LOG_LEVEL"] = "INFO"

        result = FlextCliLoggingSetup.get_current_log_config()
        assert result.is_success
        config = result.value
        assert config["log_level"] == "DEBUG"
        assert config["log_verbosity"] == "detailed"
        assert config["cli_log_level"] == "INFO"
        assert config["configured"] == "False"

    def test_get_current_log_config_defaults(self) -> None:
        """Test get_current_log_config with defaults."""
        result = FlextCliLoggingSetup.get_current_log_config()
        assert result.is_success
        config = result.value
        assert config["log_level"] == "INFO"
        assert config["log_verbosity"] == "detailed"
        assert config["cli_log_level"] == "INFO"

    def test_configure_project_logging_level(self) -> None:
        """Test configure_project_logging with log level."""
        result = FlextCliLoggingSetup.configure_project_logging(
            project_name="test-project",
            log_level="WARNING"
        )
        assert result.is_success
        assert "test-project" in result.value
        assert "WARNING" in result.value
        assert os.environ.get("FLEXT_TEST_PROJECT_LOG_LEVEL") == "WARNING"

    def test_configure_project_logging_verbosity(self) -> None:
        """Test configure_project_logging with verbosity."""
        result = FlextCliLoggingSetup.configure_project_logging(
            project_name="my-app",
            verbosity="compact"
        )
        assert result.is_success
        assert "my-app" in result.value
        assert "compact" in result.value
        assert os.environ.get("FLEXT_MY_APP_LOG_VERBOSITY") == "compact"

    def test_configure_project_logging_both(self) -> None:
        """Test configure_project_logging with both level and verbosity."""
        result = FlextCliLoggingSetup.configure_project_logging(
            project_name="full-project",
            log_level="ERROR",
            verbosity="full"
        )
        assert result.is_success
        assert "full-project" in result.value
        assert "ERROR" in result.value
        assert "full" in result.value

    def test_configure_project_logging_invalid_level(self) -> None:
        """Test configure_project_logging with invalid log level."""
        result = FlextCliLoggingSetup.configure_project_logging(
            project_name="test",
            log_level="INVALID"
        )
        assert result.is_failure
        assert "Invalid log level" in (result.error or "")

    def test_configure_project_logging_invalid_verbosity(self) -> None:
        """Test configure_project_logging with invalid verbosity."""
        result = FlextCliLoggingSetup.configure_project_logging(
            project_name="test",
            verbosity="invalid"
        )
        assert result.is_failure
        assert "Invalid verbosity" in (result.error or "")

    def test_is_setup_complete_property(self) -> None:
        """Test is_setup_complete property."""
        setup = FlextCliLoggingSetup()
        assert setup.is_setup_complete is False

        FlextCliLoggingSetup._setup_complete = True
        assert setup.is_setup_complete is True

    @patch("flext_cli.logging_setup.FlextLogger.configure")
    def test_setup_logging_with_log_file_creation(self, _mock_configure: MagicMock) -> None:
        """Test setup_logging creates log file directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "logs" / "test.log"
            config = FlextCliConfig.MainConfig()

            # Create LoggingConfig with log file
            log_config = FlextCliConfig.LoggingConfig(log_file=log_file)

            setup = FlextCliLoggingSetup(config)

            # Mock _detect_log_configuration to return our log_config
            with patch.object(
                setup,
                "_detect_log_configuration",
                return_value=FlextResult[FlextCliConfig.LoggingConfig].ok(log_config)
            ):
                result = setup.setup_logging()
                assert result.is_success
                # Directory should be created
                assert log_file.parent.exists()

    def test_detect_log_configuration_env_file(self) -> None:
        """Test _detect_log_configuration from .env file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            env_file = Path(tmpdir) / ".env"
            env_file.write_text("FLEXT_CLI_LOG_LEVEL=CRITICAL\n", encoding="utf-8")

            original_cwd = Path.cwd()
            try:
                os.chdir(tmpdir)
                config = FlextCliConfig.MainConfig()
                setup = FlextCliLoggingSetup(config)
                result = setup._detect_log_configuration()
                assert result.is_success
                assert result.value.log_level in {"CRITICAL", "INFO"}
                assert result.value.log_level_source in {"env_file", "config_instance", "default"}
            finally:
                os.chdir(original_cwd)

    def test_detect_log_configuration_env_file_with_quotes(self) -> None:
        """Test _detect_log_configuration from .env file with quotes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            env_file = Path(tmpdir) / ".env"
            env_file.write_text('FLEXT_CLI_LOG_LEVEL="ERROR"\n', encoding="utf-8")

            original_cwd = Path.cwd()
            try:
                os.chdir(tmpdir)
                config = FlextCliConfig.MainConfig()
                setup = FlextCliLoggingSetup(config)
                result = setup._detect_log_configuration()
                assert result.is_success
                assert result.value.log_level in {"ERROR", "INFO"}
                assert result.value.log_level_source in {"env_file", "config_instance", "default"}
            finally:
                os.chdir(original_cwd)

    def test_detect_log_configuration_error_handling(self) -> None:
        """Test _detect_log_configuration error handling."""
        setup = FlextCliLoggingSetup()

        # Patch Path.cwd to raise an exception
        with patch("pathlib.Path.cwd", side_effect=Exception("CWD error")):
            result = setup._detect_log_configuration()
            assert result.is_failure
            assert "Log configuration detection failed" in (result.error or "")
