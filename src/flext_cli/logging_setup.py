"""FLEXT CLI Logging Setup - Automatic logging configuration from multiple sources.

Provides automatic logging level configuration from CLI parameters, environment variables,
or .env files following SOLID principles and flext-core integration patterns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import ClassVar

from flext_core import FlextLogger, FlextResult
from pydantic import BaseModel, Field

from flext_cli.config import FlextCliConfig


class FlextCliLoggingConfig(BaseModel):
    """Logging configuration with automatic source detection.

    Supports multiple configuration sources with precedence:
    1. CLI parameter (--log-level) - Highest precedence
    2. Environment variable (FLEXT_CLI_LOG_LEVEL)
    3. .env file (FLEXT_CLI_LOG_LEVEL=DEBUG)
    4. Config file settings
    5. Default (INFO) - Lowest precedence
    """

    log_level: str = Field(
        default="INFO",
        description="Logging level from any supported source",
    )
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log message format string",
    )
    log_file: Path | None = Field(default=None, description="Optional log file path")
    console_logging: bool = Field(
        default=True,
        description="Enable console logging output",
    )

    # Configuration source tracking for debugging
    log_level_source: str = Field(
        default="default",
        description="Source of log level configuration (for debugging)",
    )


class FlextCliLoggingSetup:
    """Logging setup following SOLID principles.

    Single responsibility: Logging configuration and setup.
    Uses FlextLogger integration with multiple source support.
    """

    # Class-level state for singleton behavior
    _loggers: ClassVar[dict[str, logging.Logger]] = {}
    _setup_complete: ClassVar[bool] = False

    def __init__(self, config: FlextCliConfig | None = None) -> None:
        """Initialize logging setup using FlextConfig singleton as SINGLE SOURCE OF TRUTH."""
        self.config = config or FlextCliConfig.get_global_instance()
        self._logger = logging.getLogger(__name__)

    def setup_logging(self) -> FlextResult[FlextCliLoggingConfig]:
        """Setup logging with automatic source detection."""
        try:
            # Prevent duplicate setup calls
            if FlextCliLoggingSetup._setup_complete:
                log_config_result = self._detect_log_configuration()
                if log_config_result.is_success:
                    return FlextResult[FlextCliLoggingConfig].ok(
                        log_config_result.value
                    )
                return log_config_result

            # Detect log level and its source
            log_config_result = self._detect_log_configuration()
            if log_config_result.is_failure:
                return log_config_result

            log_config = log_config_result.value

            # Configure FlextLogger for entire CLI application
            FlextLogger.configure(
                log_level=log_config.log_level,
                structured_output=False,
                json_output=False,
                include_source=False,
            )

            # Add custom file handler if specified
            if log_config.log_file:
                logging_level = getattr(logging, log_config.log_level, logging.INFO)
                log_config.log_file.parent.mkdir(parents=True, exist_ok=True)
                file_handler = logging.FileHandler(log_config.log_file)
                file_handler.setLevel(logging_level)
                formatter = logging.Formatter(log_config.log_format)
                file_handler.setFormatter(formatter)
                logging.getLogger().addHandler(file_handler)

            # Log configuration success
            flext_logger = FlextLogger("flext_cli")
            flext_logger.info(
                "Logging configured: level=%s, source=%s",
                log_config.log_level,
                log_config.log_level_source,
            )

            FlextCliLoggingSetup._setup_complete = True
            return FlextResult[FlextCliLoggingConfig].ok(log_config)
        except Exception as e:
            return FlextResult[FlextCliLoggingConfig].fail(f"Logging setup failed: {e}")

    def _detect_log_configuration(self) -> FlextResult[FlextCliLoggingConfig]:
        """Detect log configuration from multiple sources with precedence."""
        try:
            log_config = FlextCliLoggingConfig()

            # Source 1: Check CLI configuration (highest precedence)
            if hasattr(self.config, "log_level") and self.config.log_level != "INFO":
                log_config.log_level = self.config.log_level
                log_config.log_level_source = "config_instance"
                return FlextResult[FlextCliLoggingConfig].ok(log_config)

            # Source 2: Check environment variable
            env_log_level = os.environ.get("FLEXT_CLI_LOG_LEVEL")
            if env_log_level:
                log_config.log_level = env_log_level.upper()
                log_config.log_level_source = "environment_variable"
                return FlextResult[FlextCliLoggingConfig].ok(log_config)

            # Source 3: Check .env file
            env_file_path = Path.cwd() / ".env"
            if env_file_path.exists():
                env_content = env_file_path.read_text(encoding="utf-8")
                for raw_line in env_content.split("\n"):
                    line = raw_line.strip()
                    if line.startswith("FLEXT_CLI_LOG_LEVEL="):
                        env_value = line.split("=", 1)[1].strip().strip("'\"")
                        if env_value:
                            log_config.log_level = env_value.upper()
                            log_config.log_level_source = "env_file"
                            return FlextResult[FlextCliLoggingConfig].ok(log_config)

            # Source 4: Use default
            log_config.log_level_source = "default"
            return FlextResult[FlextCliLoggingConfig].ok(log_config)
        except Exception as e:
            return FlextResult[FlextCliLoggingConfig].fail(
                f"Log configuration detection failed: {e}"
            )

    @classmethod
    def setup_for_cli(
        cls,
        config: FlextCliConfig | None = None,
        log_file: Path | None = None,
    ) -> FlextResult[str]:
        """Setup logging specifically for CLI usage using FlextConfig singleton."""
        try:
            # Use FlextConfig singleton if no config provided
            if config is None:
                config = FlextCliConfig.get_global_instance()
            setup_instance = cls(config)

            # Configure log file if specified
            if log_file:
                pass  # Handle in setup_logging

            result = setup_instance.setup_logging()
            if result.is_failure:
                return FlextResult[str].fail(result.error or "Logging setup failed")

            log_config = result.value
            message = (
                f"CLI logging configured: level={log_config.log_level}, "
                f"source={log_config.log_level_source}"
            )

            return FlextResult[str].ok(message)
        except Exception as e:
            return FlextResult[str].fail(f"CLI logging setup failed: {e}")

    @classmethod
    def get_effective_log_level(
        cls,
        config: FlextCliConfig | None = None,
    ) -> FlextResult[str]:
        """Get the effective log level that would be used using FlextConfig singleton."""
        try:
            # Use FlextConfig singleton if no config provided
            if config is None:
                config = FlextCliConfig.get_global_instance()
            setup_instance = cls(config)
            detection_result = setup_instance._detect_log_configuration()

            if detection_result.is_failure:
                return FlextResult[str].fail(
                    detection_result.error or "Log level detection failed"
                )

            log_config = detection_result.value
            return FlextResult[str].ok(
                f"{log_config.log_level} (from {log_config.log_level_source})"
            )
        except Exception as e:
            return FlextResult[str].fail(f"Log level detection failed: {e}")

    @property
    def is_setup_complete(self) -> bool:
        """Check if logging setup has been completed."""
        return FlextCliLoggingSetup._setup_complete


__all__ = [
    "FlextCliLoggingConfig",
    "FlextCliLoggingSetup",
]
