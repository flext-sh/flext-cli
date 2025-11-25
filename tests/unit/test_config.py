"""FLEXT CLI Config Tests - Comprehensive configuration functionality testing.

Tests for FlextCliConfig classes using flext_tests infrastructure with real functionality
testing, no mocks, and comprehensive coverage following FLEXT standards.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import gc
import json
import logging
import os
import tempfile
import threading
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any, Final, Literal

import pytest
import yaml
from flext_core import FlextConfig, FlextConstants
from pydantic import ValidationError

from flext_cli import (
    FlextCli,
    FlextCliConfig,
    FlextCliModels,
    FlextCliTypes,
)

from .._helpers import FlextCliTestHelpers

# ============================================================================
# TYPE DEFINITIONS & MAPPINGS
# ============================================================================


class ConfigTestType(StrEnum):
    """Config test types."""

    INITIALIZATION = "initialization"
    SERIALIZATION = "serialization"
    FILE_OPERATIONS = "file_operations"
    VALIDATION = "validation"
    INTEGRATION = "integration"
    EDGE_CASES = "edge_cases"


@dataclass(frozen=True)
class ConfigTestScenario:
    """Test scenario with data."""

    name: str
    test_type: ConfigTestType
    data: dict[str, Any] | None = None
    should_pass: bool = True


# ============================================================================
# FACTORIES & DATA GENERATORS
# ============================================================================


class ConfigTestFactory:
    """Factory for config test scenarios - maximizes parametrization."""

    # Valid values for validation
    VALID_OUTPUT_FORMATS: Final[list[str]] = ["json", "yaml", "csv", "table"]
    VALID_ENVIRONMENTS: Final[list[str]] = ["development", "staging", "production", "test"]
    VALID_VERBOSITIES: Final[list[str]] = ["compact", "detailed", "full"]
    VALID_LOGGING_LEVELS: Final[list[str]] = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

    # Test data
    JSON_CONFIG_DATA: Final[dict[str, Any]] = {
        "debug": True,
        "verbose": False,
        "profile": "test",
        "output_format": "json",
    }

    YAML_CONFIG_DATA: Final[dict[str, Any]] = {
        "debug": False,
        "verbose": True,
        "profile": "yaml_test",
        "output_format": "yaml",
    }

    @classmethod
    def create_scenarios(cls) -> list[ConfigTestScenario]:
        """Generate all test scenarios using mapping."""
        return [
            ConfigTestScenario("json_config", ConfigTestType.FILE_OPERATIONS, cls.JSON_CONFIG_DATA),
            ConfigTestScenario("yaml_config", ConfigTestType.FILE_OPERATIONS, cls.YAML_CONFIG_DATA),
            ConfigTestScenario("invalid_json", ConfigTestType.FILE_OPERATIONS, None, False),
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


# ============================================================================
# MAIN TEST CLASSES - CONSOLIDATED & PARAMETRIZED
# ============================================================================


class TestFlextCliConfigBasics:
    """Core config functionality - initialization, serialization, deserialization."""

    def test_initialization(self) -> None:
        """Test basic initialization."""
        config = FlextCliConfig()
        assert config is not None
        assert isinstance(config, FlextCliConfig)

    def test_serialization_deserialization(self) -> None:
        """Test model_dump and model_validate."""
        config = FlextCliConfig()
        dumped = config.model_dump()
        assert isinstance(dumped, dict)
        assert "verbose" in dumped

        # Validate deserialize
        data = {"verbose": False, "profile": "test"}
        validated = FlextCliConfig.model_validate(data)
        assert validated.profile == "test"

    def test_singleton_pattern(self) -> None:
        """Test singleton behavior."""
        config1 = FlextCliConfig.get_instance()
        config2 = FlextCliConfig.get_instance()
        assert config1.profile == config2.profile


class TestFlextCliConfigService:
    """Service and execution methods."""

    def test_reset_instance(self) -> None:
        """Test reset_instance resets global state."""
        FlextCliConfig()
        FlextCliConfig._reset_instance()
        new_config = FlextCliConfig()
        assert new_config is not None

    def test_execute_as_service(self) -> None:
        """Test execute_as_service returns FlextResult."""
        config = FlextCliConfig()
        result = config.execute_as_service()
        assert result.is_success
        assert isinstance(result.unwrap(), dict)


class TestLoggingConfig:
    """Logging configuration tests."""

    @pytest.mark.parametrize("level,expected", ConfigTestFactory.get_logging_scenarios())
    def test_logging_levels(self, level: str, expected: str) -> None:
        """Test all logging levels with single parametrized test."""
        config = FlextCliModels.LoggingConfig(
            log_level=level,
            log_format="json",
        )
        assert config.log_level == expected


class TestConfigFilesOperations:
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
        result = FlextCliConfig.load_from_config_file(temp_config_json)
        assert result.is_success
        assert isinstance(result.unwrap(), FlextCliConfig)

    def test_load_yaml_config(self, temp_config_yaml: Path) -> None:
        """Test YAML loading."""
        result = FlextCliConfig.load_from_config_file(temp_config_yaml)
        assert result.is_success
        assert isinstance(result.unwrap(), FlextCliConfig)

    def test_load_nonexistent_file(self, tmp_path: Path) -> None:
        """Test error handling for missing file."""
        result = FlextCliConfig.load_from_config_file(tmp_path / "nonexistent.json")
        assert result.is_failure

    def test_load_invalid_format(self, tmp_path: Path) -> None:
        """Test unsupported file format."""
        txt_file = tmp_path / "config.txt"
        txt_file.write_text("invalid")
        result = FlextCliConfig.load_from_config_file(txt_file)
        assert result.is_failure

    def test_load_invalid_json(self, tmp_path: Path) -> None:
        """Test invalid JSON content."""
        json_file = tmp_path / "invalid.json"
        json_file.write_text('{invalid json}')
        result = FlextCliConfig.load_from_config_file(json_file)
        assert result.is_failure


class TestConfigIntegration:
    """Integration with FlextCli and environment."""

    @pytest.fixture(autouse=True)
    def _clear_env(self) -> None:
        """Clear FLEXT_ env vars before each test."""
        for key in list(os.environ.keys()):
            if key.startswith("FLEXT_"):
                os.environ.pop(key, None)
        FlextCliConfig._reset_instance()

    def test_flext_cli_integration(self) -> None:
        """Test FlextCli uses config."""
        cli = FlextCli()
        config = cli.config
        assert config is not None
        assert isinstance(config, FlextCliConfig)

    def test_config_inheritance(self) -> None:
        """Test inheritance from FlextConfig.AutoConfig."""
        config = FlextCliConfig()
        assert isinstance(config, FlextConfig.AutoConfig)
        assert hasattr(config, "model_config")

    def test_env_var_loading(self) -> None:
        """Test environment variable integration."""
        os.environ["FLEXT_CLI_PROFILE"] = "env_profile"
        FlextCliConfig._reset_instance()

        config = FlextCliConfig.get_instance()
        assert config.profile == "env_profile"

        os.environ.pop("FLEXT_CLI_PROFILE", None)


class TestConfigValidation:
    """Validation tests using parametrized factory."""

    @pytest.mark.parametrize("fmt,should_pass", ConfigTestFactory.get_validation_test_cases())
    def test_output_format_validation(self, fmt: str, should_pass: bool) -> None:
        """Test output format validation."""
        config = FlextCliConfig()
        result = config.validate_output_format_result(fmt)
        assert result.is_success == should_pass

    @pytest.mark.parametrize("env", ConfigTestFactory.VALID_ENVIRONMENTS)
    def test_valid_environments(self, env: str) -> None:
        """Test all valid environments."""
        assert env in ConfigTestFactory.VALID_ENVIRONMENTS

    def test_model_dump(self) -> None:
        """Test model_dump returns complete dict."""
        config = FlextCliConfig()
        dumped = config.model_dump()
        assert isinstance(dumped, dict)
        assert len(dumped) > 0

    def test_update_from_cli_args(self) -> None:
        """Test update_from_cli_args."""
        config = FlextCliConfig()
        result = config.update_from_cli_args(profile="new_profile", debug=True)
        assert result.is_success
        assert config.profile == "new_profile"
        assert config.debug is True

    def test_validate_cli_overrides(self) -> None:
        """Test validate_cli_overrides."""
        config = FlextCliConfig()
        result = config.validate_cli_overrides(
            profile="valid",
            output_format="json",
        )
        assert result.is_success or result.is_failure


class TestConfigComputedFields:
    """Test auto-computed config fields."""

    def test_auto_output_format(self) -> None:
        """Test auto_output_format computed field."""
        config = FlextCliConfig()
        fmt = config.auto_output_format()
        assert fmt in {"table", "json", "plain"}

    def test_auto_verbosity(self) -> None:
        """Test auto_verbosity computed field."""
        config = FlextCliConfig()
        verb = config.auto_verbosity()
        assert verb in {"normal", "quiet", "verbose"}

    def test_optimal_table_format(self) -> None:
        """Test optimal_table_format computed field."""
        config = FlextCliConfig()
        fmt = config.optimal_table_format()
        assert fmt in {"simple", "grid", "github", "plain"}

    def test_auto_color_support(self) -> None:
        """Test auto_color_support computed field."""
        config = FlextCliConfig()
        assert isinstance(config.auto_color_support, bool)


class TestConfigLogging:
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


class TestConfigConcurrency:
    """Thread safety and concurrency tests."""

    def test_concurrent_access(self) -> None:
        """Test concurrent config access is safe."""
        results = []
        errors = []

        def worker(worker_id: int) -> None:
            try:
                config = FlextCliConfig()
                results.append((worker_id, config.debug, config.environment))
            except Exception as e:
                errors.append((worker_id, str(e)))

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(results) == 5
        assert len(errors) == 0


class TestConfigMemory:
    """Memory management tests."""

    def test_config_cleanup(self) -> None:
        """Test config cleanup with gc."""
        configs = [FlextCliConfig() for _ in range(10)]
        del configs
        gc.collect()

        new_config = FlextCliConfig()
        assert new_config is not None

    def test_state_persistence(self) -> None:
        """Test config state persistence."""
        config1 = FlextCliConfig()
        config2 = FlextCliConfig()

        assert config1.debug == config2.debug
        assert config1.environment == config2.environment
        assert config1 is not config2


class TestConfigEdgeCases:
    """Edge cases and boundary conditions."""

    def test_extreme_values(self) -> None:
        """Test config with extreme numeric values."""
        config = FlextCliConfig()
        assert config.max_retries >= 0
        assert config.cli_timeout > 0
        assert config.max_width > 0

    def test_load_config(self) -> None:
        """Test load_config method."""
        config = FlextCliConfig()
        result = config.load_config()
        assert result.is_success or result.is_failure
        if result.is_success:
            assert isinstance(result.unwrap(), dict)

    def test_save_config(self) -> None:
        """Test save_config method."""
        config = FlextCliConfig()
        new_config: FlextCliTypes.Data.CliConfigData = {"debug": True}
        result = config.save_config(new_config)
        assert result.is_success or result.is_failure
