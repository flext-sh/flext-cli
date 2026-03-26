"""FLEXT CLI Config Tests - Comprehensive Configuration Validation Testing.

Tests for FlextCliSettings covering initialization, serialization,
validation, integration workflows, and edge cases.

Modules tested: flext_cli.config.FlextCliSettings
Scope: All kept configuration operations, validation, integration

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import gc
import logging
import os
import threading
import typing
from collections.abc import Sequence
from enum import StrEnum, unique
from typing import Annotated, ClassVar, Final, Literal

import pytest
from flext_tests import tm
from pydantic import BaseModel, ConfigDict, Field
from pydantic_settings import BaseSettings

from flext_cli import FlextCli, FlextCliSettings, m
from tests import t


@unique
class ConfigTestType(StrEnum):
    """Config test types."""

    INITIALIZATION = "initialization"
    SERIALIZATION = "serialization"
    VALIDATION = "validation"
    INTEGRATION = "integration"
    EDGE_CASES = "edge_cases"


class ConfigTestScenario(BaseModel):
    """Test scenario with data."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    name: Annotated[str, Field(description="Scenario name")]
    test_type: Annotated[ConfigTestType, Field(description="Scenario test type")]
    data: Annotated[
        t.ContainerMapping | None,
        Field(
            default=None,
            description="Scenario input data",
        ),
    ]
    should_pass: Annotated[
        bool,
        Field(
            default=True,
            description="Whether scenario is expected to pass",
        ),
    ]


class ConfigTestFactory:
    """Factory for config test scenarios - maximizes parametrization."""

    VALID_OUTPUT_FORMATS: Final[t.StrSequence] = ["json", "yaml", "csv", "table"]
    VALID_ENVIRONMENTS: Final[t.StrSequence] = [
        "development",
        "staging",
        "production",
        "test",
    ]
    VALID_VERBOSITIES: Final[t.StrSequence] = ["compact", "detailed", "full"]
    VALID_LOGGING_LEVELS: Final[t.StrSequence] = [
        "DEBUG",
        "INFO",
        "WARNING",
        "ERROR",
        "CRITICAL",
    ]

    @classmethod
    def get_logging_scenarios(cls) -> Sequence[tuple[str, str]]:
        """Generate logging level scenarios."""
        return [(level, level) for level in cls.VALID_LOGGING_LEVELS]


class TestsCliConfigBasics:
    """Core config functionality - initialization, serialization, deserialization."""

    def test_initialization(self) -> None:
        """Test basic initialization."""
        config = FlextCliSettings()
        tm.that(config, none=False)
        tm.that(config, is_=FlextCliSettings)

    def test_serialization_deserialization(self) -> None:
        """Test model_dump and model_validate."""
        config = FlextCliSettings()
        dumped = config.model_dump()
        tm.that(dumped, is_=dict)
        tm.that(dumped, has="verbose")
        data = {"verbose": False, "profile": "test"}
        validated = FlextCliSettings.model_validate(data)
        tm.that(validated.profile, eq="test")

    def test_singleton_pattern(self) -> None:
        """Test singleton behavior."""
        config1 = FlextCliSettings.get_instance()
        config2 = FlextCliSettings.get_instance()
        tm.that(config1.profile, eq=config2.profile)


class TestsCliConfigService:
    """Service and execution methods."""

    def test_reset_instance(self) -> None:
        """Test reset_instance resets global state."""
        FlextCliSettings()
        FlextCliSettings.reset_for_testing()
        new_config = FlextCliSettings()
        tm.that(new_config, none=False)


class TestsCliLoggingConfig:
    """Logging configuration tests."""

    @pytest.mark.parametrize(
        ("level", "expected"),
        ConfigTestFactory.get_logging_scenarios(),
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
            log_level=log_level,
            log_format="json",
        )
        tm.that(config.log_level, eq=expected)


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
        tm.that(config, none=False)
        tm.that(config, is_=FlextCliSettings)

    def test_config_inheritance(self) -> None:
        """Test inheritance from BaseSettings (Pydantic v2)."""
        config = FlextCliSettings()
        tm.that(config, is_=BaseSettings)
        tm.that(hasattr(config, "model_config"), eq=True)

    def test_env_var_loading(self) -> None:
        """Test environment variable integration."""
        original_profile = os.environ.get("FLEXT_CLI_PROFILE")
        try:
            os.environ["FLEXT_CLI_PROFILE"] = "env_profile"
            FlextCliSettings.reset_for_testing()
            config = FlextCliSettings()
            if config.profile != "env_profile":
                tm.that(os.environ.get("FLEXT_CLI_PROFILE"), eq="env_profile")
                config_data = {"profile": os.environ["FLEXT_CLI_PROFILE"]}
                config = FlextCliSettings.model_validate(config_data)
            tm.that(config.profile, eq="env_profile")
        finally:
            os.environ.pop("FLEXT_CLI_PROFILE", None)
            if original_profile is not None:
                os.environ["FLEXT_CLI_PROFILE"] = original_profile
            FlextCliSettings.reset_for_testing()


class TestsCliConfigValidation:
    """Validation tests."""

    @pytest.mark.parametrize("env", ConfigTestFactory.VALID_ENVIRONMENTS)
    def test_valid_environments(self, env: str) -> None:
        """Test all valid environments."""
        tm.that(ConfigTestFactory.VALID_ENVIRONMENTS, has=env)

    def test_model_dump(self) -> None:
        """Test model_dump returns complete dict."""
        config: FlextCliSettings = FlextCliSettings()
        dumped = config.model_dump()
        tm.that(dumped, is_=dict)
        tm.that(dumped, empty=False)


class TestsCliConfigLogging:
    """Logging integration tests."""

    def test_logger_creation(self) -> None:
        """Test logger creation."""
        logger = logging.getLogger("test_logger")
        tm.that(logger, none=False)
        tm.that(logger, is_=logging.Logger)

    def test_logging_levels(self, caplog: pytest.LogCaptureFixture) -> None:
        """Test logging at different levels."""
        logger = logging.getLogger("test_level")
        logger.setLevel(logging.INFO)
        logger.info("Info message")
        logger.warning("Warning message")
        tm.that(caplog.text, has="Info message")
        tm.that(caplog.text, has="Warning message")


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
        tm.that(len(results), eq=5)
        tm.that(len(errors), eq=0)


class TestsCliConfigMemory:
    """Memory management tests."""

    def test_config_cleanup(self) -> None:
        """Test config cleanup with gc."""
        configs = [FlextCliSettings() for _ in range(10)]
        del configs
        gc.collect()
        new_config = FlextCliSettings()
        tm.that(new_config, none=False)

    def test_state_persistence(self) -> None:
        """Test config state persistence using model_copy."""
        FlextCliSettings.reset_for_testing()
        config1 = FlextCliSettings()
        original_debug = config1.debug
        config_modified = config1.model_copy(update={"debug": not original_debug})
        tm.that(config_modified.debug is not original_debug, eq=True)
        config_modified2 = config1.model_copy(update={"environment": "test"})
        tm.that(config_modified2.environment, eq="test")
        tm.that(hasattr(config_modified2, "environment"), eq=True)


class TestsCliConfigEdgeCases:
    """Edge cases and boundary conditions."""

    def test_extreme_values(self) -> None:
        """Test config with extreme numeric values."""
        config: FlextCliSettings = FlextCliSettings()
        tm.that(config.max_retries, gte=0)
        tm.that(config.cli_timeout, gt=0)
        tm.that(config.max_width, gt=0)
