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

from flext_cli.configs import FlextCliConfigs
from flext_cli.models import FlextCliModels
from flext_core import FlextContainer, FlextDomainService, FlextLogger, FlextResult

# Type alias for LoggingConfig
LoggingConfig = FlextCliModels.LoggingConfig


class FlextCliLoggingSetup(FlextDomainService[str]):
    """Unified logging setup service using FlextDomainService.

    Single responsibility with nested helpers pattern.
    No loose helper functions - all functionality encapsulated.
    """

    # LoggingConfig access for tests compatibility
    LoggingConfig: ClassVar[type[FlextCliModels.LoggingConfig]] = FlextCliModels.LoggingConfig

    # Class-level state for singleton behavior
    _loggers: ClassVar[dict[str, logging.Logger]] = {}
    _setup_complete: ClassVar[bool] = False

    def __init__(self, config: FlextCliConfigs | None = None) -> None:
        """Initialize logging setup using FlextConfig singleton as SINGLE SOURCE OF TRUTH."""
        super().__init__()
        self._container = FlextContainer.get_global()
        self._logger = FlextLogger(__name__)

        # Use resolved config without storing as instance attribute (FlextDomainService is frozen)
        self._resolved_config = config or FlextCliConfigs.get_current()

    def execute(self) -> FlextResult[str]:
        """Execute logging setup - FlextDomainService interface."""
        self.log_info("Executing logging setup")
        return FlextResult[str].ok("Logging setup executed")

    def setup_logging(self) -> FlextResult[FlextCliModels.LoggingConfig]:
        """Setup logging with automatic source detection."""
        try:
            # Prevent duplicate setup calls
            if FlextCliLoggingSetup._setup_complete:
                log_config_result = self._detect_log_configuration()
                if log_config_result.is_success:
                    return FlextResult[FlextCliModels.LoggingConfig].ok(log_config_result.value)
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
            return FlextResult[FlextCliModels.LoggingConfig].ok(log_config)
        except Exception as e:
            return FlextResult[FlextCliModels.LoggingConfig].fail(f"Logging setup failed: {e}")

    def _detect_log_configuration(
        self,
    ) -> FlextResult[FlextCliModels.LoggingConfig]:
        """Detect log configuration from multiple sources with precedence."""
        try:
            log_config = FlextCliModels.LoggingConfig()

            # Source 1: Check CLI configuration (highest precedence)
            if (
                hasattr(self._resolved_config, "log_level")
                and self._resolved_config.log_level != "INFO"
            ):
                log_config.log_level = self._resolved_config.log_level
                log_config.log_level_source = "config_instance"
                return FlextResult[FlextCliModels.LoggingConfig].ok(log_config)

            # Source 2: Check environment variable
            # Python 3.13+ walrus operator pattern
            if env_log_level := os.environ.get("FLEXT_CLI_LOG_LEVEL"):
                log_config.log_level = env_log_level.upper()
                log_config.log_level_source = "environment_variable"
                return FlextResult[FlextCliModels.LoggingConfig].ok(log_config)

            # Source 3: Check .env file - Python 3.13+ walrus operator
            if (env_file_path := Path.cwd() / ".env").exists():
                env_content = env_file_path.read_text(encoding="utf-8")
                for raw_line in env_content.split("\n"):
                    line = raw_line.strip()
                    if line.startswith("FLEXT_CLI_LOG_LEVEL="):
                        env_value = line.split("=", 1)[1].strip().strip("'\"")
                        if env_value:
                            log_config.log_level = env_value.upper()
                            log_config.log_level_source = "env_file"
                            return FlextResult[FlextCliModels.LoggingConfig].ok(log_config)

            # Source 4: Use default
            log_config.log_level_source = "default"
            return FlextResult[FlextCliModels.LoggingConfig].ok(log_config)
        except Exception as e:
            return FlextResult[FlextCliModels.LoggingConfig].fail(
                f"Log configuration detection failed: {e}",
            )

    @classmethod
    def setup_for_cli(
        cls,
        config: FlextCliConfigs | None = None,
        log_file: Path | None = None,
    ) -> FlextResult[str]:
        """Setup logging specifically for CLI usage using FlextConfig singleton."""
        try:
            # Use FlextConfig singleton if no config provided
            if config is None:
                config = FlextCliConfigs.get_current()
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
        config: FlextCliConfigs | None = None,
    ) -> FlextResult[str]:
        """Get the effective log level that would be used using FlextConfig singleton."""
        try:
            # Use FlextConfig singleton if no config provided
            if config is None:
                config = FlextCliConfigs.get_current()
            setup_instance = cls(config)
            detection_result = setup_instance._detect_log_configuration()

            if detection_result.is_failure:
                return FlextResult[str].fail(
                    detection_result.error or "Log level detection failed",
                )

            log_config = detection_result.value
            return FlextResult[str].ok(
                f"{log_config.log_level} (from {log_config.log_level_source})",
            )
        except Exception as e:
            return FlextResult[str].fail(f"Log level detection failed: {e}")

    @property
    def is_setup_complete(self) -> bool:
        """Check if logging setup has been completed."""
        return FlextCliLoggingSetup._setup_complete


__all__ = [
    "FlextCliLoggingSetup",
]
