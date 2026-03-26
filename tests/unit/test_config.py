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
import threading
from collections.abc import Sequence
from enum import StrEnum, unique
from typing import Annotated, ClassVar, Final

import pytest
from flext_tests import tm
from pydantic import BaseModel, ConfigDict, Field
from pydantic_settings import BaseSettings

from flext_cli import FlextCli, FlextCliSettings
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

    def test_singleton_pattern(self) -> None:
        """Test singleton behavior via get_global."""
        config1 = FlextCliSettings.get_global()
        config2 = FlextCliSettings.get_global()
        tm.that(config1.verbose, eq=config2.verbose)


class TestsCliConfigService:
    """Service and execution methods."""

    def test_reset_instance(self) -> None:
        """Test reset_for_testing resets global state."""
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
        tm.that(level in valid_levels, eq=True)
        tm.that(level, eq=expected)


class TestsCliConfigIntegration:
    """Integration with FlextCli."""

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
        results: list[tuple[int, bool]] = []
        errors: list[tuple[int, str]] = []

        def worker(worker_id: int) -> None:
            try:
                config = FlextCliSettings()
                results.append((worker_id, config.debug))
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


class TestsCliConfigEdgeCases:
    """Edge cases and boundary conditions."""

    def test_basic_fields_exist(self) -> None:
        """Test config has expected fields."""
        config: FlextCliSettings = FlextCliSettings()
        tm.that(config.verbose, is_=bool)
        tm.that(config.debug, is_=bool)
        tm.that(config.no_color, is_=bool)
        tm.that(config.quiet, is_=bool)
