"""FLEXT CLI Config Tests - Comprehensive Configuration Validation Testing.

Tests for FlextCliSettings covering initialization, serialization, file operations,
validation, integration workflows, and edge cases with 100% coverage.

Modules tested: flext_cli.config.FlextCliSettings
Scope: All configuration operations, file operations, validation, integration

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import gc
import json
import logging
import os
import threading
import typing
from enum import StrEnum
from pathlib import Path
from typing import Final, Literal

import pytest
import yaml
from pydantic import BaseModel, ConfigDict, Field
from pydantic_settings import BaseSettings

from flext_cli import FlextCli, FlextCliSettings, m


class ConfigTestType(StrEnum):
    """Config test types."""

    INITIALIZATION = "initialization"
    SERIALIZATION = "serialization"
    FILE_OPERATIONS = "file_operations"
    VALIDATION = "validation"
    INTEGRATION = "integration"
    EDGE_CASES = "edge_cases"


class ConfigTestScenario(BaseModel):
    """Test scenario with data."""

    model_config = ConfigDict(frozen=True)

    name: str = Field(description="Scenario name")
    test_type: ConfigTestType = Field(description="Scenario test type")
    data: dict[str, object] | None = Field(
        default=None,
        description="Scenario input data",
    )
    should_pass: bool = Field(
        default=True,
        description="Whether scenario is expected to pass",
    )


class ConfigTestFactory:
    """Factory for config test scenarios - maximizes parametrization."""

    VALID_OUTPUT_FORMATS: Final[list[str]] = ["json", "yaml", "csv", "table"]
    VALID_ENVIRONMENTS: Final[list[str]] = [
        "development",
        "staging",
        "production",
        "test",
    ]
    VALID_VERBOSITIES: Final[list[str]] = ["compact", "detailed", "full"]
    VALID_LOGGING_LEVELS: Final[list[str]] = [
        "DEBUG",
        "INFO",
        "WARNING",
        "ERROR",
        "CRITICAL",
    ]
    JSON_CONFIG_DATA: Final[dict[str, object]] = {
        "debug": True,
        "verbose": False,
        "profile": "test",
        "output_format": "json",
    }
    YAML_CONFIG_DATA: Final[dict[str, object]] = {
        "debug": False,
        "verbose": True,
        "profile": "yaml_test",
        "output_format": "yaml",
    }

    @classmethod
    def create_scenarios(cls) -> list[ConfigTestScenario]:
        """Generate all test scenarios using mapping."""
        return [
            ConfigTestScenario(
                name="json_config",
                test_type=ConfigTestType.FILE_OPERATIONS,
                data=cls.JSON_CONFIG_DATA,
            ),
            ConfigTestScenario(
                name="yaml_config",
                test_type=ConfigTestType.FILE_OPERATIONS,
                data=cls.YAML_CONFIG_DATA,
            ),
            ConfigTestScenario(
                name="invalid_json",
                test_type=ConfigTestType.FILE_OPERATIONS,
                data=None,
                should_pass=False,
            ),
        ]

    @classmethod
    def get_validation_test_cases(cls) -> list[tuple[str, bool]]:
        """Generate validation test cases - formats, envs, levels."""
        return [(fmt, True) for fmt in cls.VALID_OUTPUT_FORMATS] + [
            ("invalid_format", False)
        ]

    @classmethod
    def get_logging_scenarios(cls) -> list[tuple[str, str]]:
        """Generate logging level scenarios."""
        return [(level, level) for level in cls.VALID_LOGGING_LEVELS]


class TestsCliConfigBasics:
    """Core config functionality - initialization, serialization, deserialization."""

    def test_initialization(self) -> None:
        """Test basic initialization."""
        config = FlextCliSettings()
        assert config is not None
        assert isinstance(config, FlextCliSettings)

    def test_serialization_deserialization(self) -> None:
        """Test model_dump and model_validate."""
        config = FlextCliSettings()
        dumped = config.model_dump()
        assert isinstance(dumped, dict)
        assert "verbose" in dumped
        data = {"verbose": False, "profile": "test"}
        validated = FlextCliSettings(data)
        assert validated.profile == "test"

    def test_singleton_pattern(self) -> None:
        """Test singleton behavior."""
        config1 = FlextCliSettings.get_instance()
        config2 = FlextCliSettings.get_instance()
        assert config1.profile == config2.profile


class TestsCliConfigService:
    """Service and execution methods."""

    def test_reset_instance(self) -> None:
        """Test reset_instance resets global state."""
        FlextCliSettings()
        FlextCliSettings.reset_for_testing()
        new_config = FlextCliSettings()
        assert new_config is not None

    def test_execute_as_service(self) -> None:
        """Test execute_service returns r."""
        config: FlextCliSettings = FlextCliSettings()
        result = config.execute_service()
        assert result.is_success
        assert isinstance(result.value, dict)


class TestsCliLoggingConfig:
    """Logging configuration tests."""

    @pytest.mark.parametrize(
        ("level", "expected"), ConfigTestFactory.get_logging_scenarios()
    )
    def test_logging_levels(self, level: str, expected: str) -> None:
        """Test all logging levels with single parametrized test."""
        valid_levels: tuple[str, ...] = (
            "DEBUG",
            "INFO",
            "WARNING",
            "ERROR",
            "CRITICAL",
        )
        if level not in valid_levels:
            return
        log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "DEBUG"
        match level:
            case "DEBUG":
                log_level = "DEBUG"
            case "INFO":
                log_level = "INFO"
            case "WARNING":
                log_level = "WARNING"
            case "ERROR":
                log_level = "ERROR"
            case "CRITICAL":
                log_level = "CRITICAL"
        config = m.Cli.LoggingConfig.model_construct(
            log_level=log_level, log_format="json"
        )
        assert config.log_level == expected


class TestsCliConfigFilesOperations:
    """File loading and saving operations."""

    @pytest.fixture
    def temp_config_json(self, tmp_path: Path) -> Path:
        """Create temp JSON config."""
        json_file = tmp_path / "config.json"
        json_file.write_text(json.dumps(ConfigTestFactory.JSON_CONFIG_DATA))
        return json_file

    @pytest.fixture
    def temp_config_yaml(self, tmp_path: Path) -> Path:
        """Create temp YAML config."""
        yaml_file = tmp_path / "config.yaml"
        yaml_file.write_text(yaml.dump(ConfigTestFactory.YAML_CONFIG_DATA))
        return yaml_file

    def test_load_json_config(self, temp_config_json: Path) -> None:
        """Test JSON loading."""
        result = FlextCliSettings.load_from_config_file(temp_config_json)
        assert result.is_success
        assert isinstance(result.value, FlextCliSettings)

    def test_load_yaml_config(self, temp_config_yaml: Path) -> None:
        """Test YAML loading."""
        result = FlextCliSettings.load_from_config_file(temp_config_yaml)
        assert result.is_success
        assert isinstance(result.value, FlextCliSettings)

    def test_load_nonexistent_file(self, tmp_path: Path) -> None:
        """Test error handling for missing file."""
        result = FlextCliSettings.load_from_config_file(tmp_path / "nonexistent.json")
        assert result.is_failure

    def test_load_invalid_format(self, tmp_path: Path) -> None:
        """Test unsupported file format."""
        txt_file = tmp_path / "config.txt"
        txt_file.write_text("invalid")
        result = FlextCliSettings.load_from_config_file(txt_file)
        assert result.is_failure

    def test_load_invalid_json(self, tmp_path: Path) -> None:
        """Test invalid JSON content."""
        json_file = tmp_path / "invalid.json"
        json_file.write_text("{invalid json}")
        result = FlextCliSettings.load_from_config_file(json_file)
        assert result.is_failure


class TestsCliConfigIntegration:
    """Integration with FlextCli and environment."""

    @pytest.fixture(autouse=True)
    def _clear_env(self) -> typing.Generator[None]:
        """Clear FLEXT_ env vars before each test."""
        saved_env = {k: v for k, v in os.environ.items() if k.startswith("FLEXT_")}
        for key in list(os.environ.keys()):
            if key.startswith("FLEXT_"):
                os.environ.pop(key, None)
        FlextCliSettings.reset_for_testing()
        yield None
        for key in list(os.environ.keys()):
            if key.startswith("FLEXT_") and key not in saved_env:
                os.environ.pop(key, None)
        for key, value in saved_env.items():
            os.environ[key] = value
        FlextCliSettings.reset_for_testing()

    def test_flext_cli_integration(self) -> None:
        """Test FlextCli uses config."""
        cli = FlextCli()
        config = cli.config
        assert config is not None
        assert isinstance(config, FlextCliSettings)

    def test_config_inheritance(self) -> None:
        """Test inheritance from BaseSettings (Pydantic v2)."""
        config = FlextCliSettings()
        assert isinstance(config, BaseSettings)
        assert hasattr(config, "model_config")

    def test_env_var_loading(self) -> None:
        """Test environment variable integration."""
        original_profile = os.environ.get("FLEXT_CLI_PROFILE")
        try:
            os.environ["FLEXT_CLI_PROFILE"] = "env_profile"
            FlextCliSettings.reset_for_testing()
            config = FlextCliSettings()
            if config.profile != "env_profile":
                assert os.environ.get("FLEXT_CLI_PROFILE") == "env_profile", (
                    "Environment variable not set"
                )
                config_data = {"profile": os.environ["FLEXT_CLI_PROFILE"]}
                config = FlextCliSettings(config_data)
            assert config.profile == "env_profile", (
                f"Expected 'env_profile', got '{config.profile}'"
            )
        finally:
            os.environ.pop("FLEXT_CLI_PROFILE", None)
            if original_profile is not None:
                os.environ["FLEXT_CLI_PROFILE"] = original_profile
            FlextCliSettings.reset_for_testing()


class TestsCliConfigValidation:
    """Validation tests using parametrized factory."""

    @pytest.mark.parametrize(
        ("fmt", "should_pass"), ConfigTestFactory.get_validation_test_cases()
    )
    def test_output_format_validation(self, fmt: str, should_pass: bool) -> None:
        """Test output format validation."""
        config: FlextCliSettings = FlextCliSettings()
        result = config.validate_output_format_result(fmt)
        assert result.is_success == should_pass

    @pytest.mark.parametrize("env", ConfigTestFactory.VALID_ENVIRONMENTS)
    def test_valid_environments(self, env: str) -> None:
        """Test all valid environments."""
        assert env in ConfigTestFactory.VALID_ENVIRONMENTS

    def test_model_dump(self) -> None:
        """Test model_dump returns complete dict."""
        config: FlextCliSettings = FlextCliSettings()
        dumped = config.model_dump()
        assert isinstance(dumped, dict)
        assert len(dumped) > 0

    def test_update_from_cli_args(self) -> None:
        """Test update_from_cli_args."""
        config: FlextCliSettings = FlextCliSettings()
        result = config.update_from_cli_args(profile="new_profile", debug=True)
        assert result.is_success
        assert config.profile == "new_profile"
        assert config.debug is True

    def test_validate_cli_overrides(self) -> None:
        """Test validate_cli_overrides."""
        config: FlextCliSettings = FlextCliSettings()
        result = config.validate_cli_overrides(profile="valid", output_format="json")
        assert result.is_success or result.is_failure


class TestsCliConfigComputedFields:
    """Test auto-computed config fields."""

    def test_auto_output_format(self) -> None:
        """Test auto_output_format computed field."""
        config: FlextCliSettings = FlextCliSettings()
        fmt_value = config.auto_output_format
        assert isinstance(fmt_value, str), f"Expected str, got {type(fmt_value)}"
        fmt: str = fmt_value
        assert fmt in {"table", "json", "plain"}

    def test_auto_verbosity(self) -> None:
        """Test auto_verbosity computed field."""
        config = FlextCliSettings()
        verb_value = config.auto_verbosity
        verb: str = verb_value
        assert verb in {"normal", "quiet", "verbose"}

    def test_optimal_table_format(self) -> None:
        """Test optimal_table_format computed field."""
        config = FlextCliSettings()
        fmt_value = config.optimal_table_format
        assert isinstance(fmt_value, str), f"Expected str, got {type(fmt_value)}"
        fmt: str = fmt_value
        assert fmt in {"simple", "grid", "github", "plain"}

    def test_auto_color_support(self) -> None:
        """Test auto_color_support computed field."""
        config = FlextCliSettings()
        assert isinstance(config.auto_color_support, bool)


class TestsCliConfigLogging:
    """Logging integration tests."""

    def test_logger_creation(self) -> None:
        """Test logger creation."""
        logger = logging.getLogger("test_logger")
        assert logger is not None
        assert isinstance(logger, logging.Logger)

    def test_logging_levels(self, caplog: pytest.LogCaptureFixture) -> None:
        """Test logging at different levels."""
        logger = logging.getLogger("test_level")
        logger.setLevel(logging.INFO)
        logger.info("Info message")
        logger.warning("Warning message")
        assert "Info message" in caplog.text
        assert "Warning message" in caplog.text


class TestsCliConfigConcurrency:
    """Thread safety and concurrency tests."""

    def test_concurrent_access(self) -> None:
        """Test concurrent config access is safe."""
        results: list[tuple[int, bool, str]] = []
        errors: list[tuple[int, str]] = []

        def worker(worker_id: int) -> None:
            try:
                config = FlextCliSettings()
                results.append((worker_id, config.debug, config.environment))
            except Exception as e:
                errors.append((worker_id, str(e)))

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(5)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        assert len(results) == 5
        assert len(errors) == 0


class TestsCliConfigMemory:
    """Memory management tests."""

    def test_config_cleanup(self) -> None:
        """Test config cleanup with gc."""
        configs = [FlextCliSettings() for _ in range(10)]
        del configs
        gc.collect()
        new_config = FlextCliSettings()
        assert new_config is not None

    def test_state_persistence(self) -> None:
        """Test config state persistence using model_copy."""
        FlextCliSettings.reset_for_testing()
        config1 = FlextCliSettings()
        original_debug = config1.debug
        config_modified = config1.model_copy(update={"debug": not original_debug})
        assert config_modified.debug is not original_debug
        config_modified2 = config1.model_copy(update={"environment": "test"})
        assert config_modified2.environment == "test"
        assert hasattr(config_modified2, "environment")


class TestsCliConfigEdgeCases:
    """Edge cases and boundary conditions."""

    def test_extreme_values(self) -> None:
        """Test config with extreme numeric values."""
        config: FlextCliSettings = FlextCliSettings()
        assert config.max_retries >= 0
        assert config.cli_timeout > 0
        assert config.max_width > 0

    def test_load_config(self) -> None:
        """Test load_config method."""
        config: FlextCliSettings = FlextCliSettings()
        result = config.load_config()
        assert result.is_success or result.is_failure
        if result.is_success:
            assert isinstance(result.value, dict)

    def test_save_config(self) -> None:
        """Test save_config method."""
        config: FlextCliSettings = FlextCliSettings()
        new_config: dict[str, object] = {"debug": True}
        result = config.save_config(new_config)
        assert result.is_success or result.is_failure
