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

from flext_cli.models import FlextCliModels
from flext_core import (
    FlextConstants,
    FlextContainer,
    FlextLogger,
    FlextResult,
    FlextService,
)


class FlextCliLoggingSetup(FlextService[dict[str, object]]):
    """Unified logging setup service using FlextService.

    Single responsibility with nested helpers pattern.
    No loose helper functions - all functionality encapsulated.
    """

    # FlextCliModels.LoggingConfig class reference for direct access
    LoggingConfigModel: ClassVar[type[FlextCliModels.LoggingConfig]] = (
        FlextCliModels.LoggingConfig
    )

    # Class-level state for singleton behavior
    _loggers: ClassVar[dict[str, logging.Logger]] = {}
    _setup_complete: ClassVar[bool] = False

    def __init__(self, config: FlextCliModels.FlextCliConfig | None = None) -> None:
        """Initialize logging setup using FlextConfig singleton as SINGLE SOURCE OF TRUTH."""
        super().__init__()
        self._container = FlextContainer.get_global()
        self._logger = FlextLogger(__name__)

        # Use resolved config without storing as instance attribute (FlextService is frozen)
        self._resolved_config = config or FlextCliModels.FlextCliConfig()

    def execute(self) -> FlextResult[dict[str, object]]:
        """Execute logging setup - FlextService interface.

        Returns:
            FlextResult[dict[str, object]]: Description of return value.

        """
        self._logger.info("Executing logging setup")
        return FlextResult[dict[str, object]].ok({
            "status": "completed",
            "message": "Logging setup executed",
        })

    def setup_logging(self) -> FlextResult[FlextCliModels.LoggingConfig]:
        """Setup logging with automatic source detection.

        Returns:
            FlextResult[FlextCliModels.LoggingConfig]: Description of return value.

        """
        try:
            # Prevent duplicate setup calls
            if FlextCliLoggingSetup._setup_complete:
                log_config_result = self._detect_log_configuration()
                if log_config_result.is_success:
                    return FlextResult[FlextCliModels.LoggingConfig].ok(
                        log_config_result.value
                    )
                return log_config_result

            # Detect log level and its source
            log_config_result = self._detect_log_configuration()
            if log_config_result.is_failure:
                return log_config_result

            log_config = log_config_result.value

            # Configure FlextLogger for entire CLI application with enhanced formatting
            verbosity = os.environ.get("FLEXT_LOG_VERBOSITY", "detailed")
            FlextLogger.configure(
                log_level=log_config.log_level,
                structured_output=True,  # Enable enhanced console renderer
                json_output=False,
                include_source=False,
                log_verbosity=verbosity,
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
            return FlextResult[FlextCliModels.LoggingConfig].fail(
                f"Logging setup failed: {e}"
            )

    def _detect_log_configuration(
        self,
    ) -> FlextResult[FlextCliModels.LoggingConfig]:
        """Detect log configuration from multiple sources with precedence.

        Returns:
            FlextResult[FlextCliModels.LoggingConfig]: Description of return value.

        """
        try:
            log_config = FlextCliModels.LoggingConfig()

            # Source 1: Check CLI configuration (highest precedence)
            if (
                hasattr(self._resolved_config, "log_level")
                and getattr(self._resolved_config, "log_level", None)
                != FlextConstants.Logging.INFO
            ):
                log_config.log_level = getattr(
                    self._resolved_config, "log_level", FlextConstants.Logging.INFO
                )
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
                env_content = env_file_path.read_text(
                    encoding=FlextConstants.Mixins.DEFAULT_ENCODING
                )
                for raw_line in env_content.split("\n"):
                    line = raw_line.strip()
                    if line.startswith("FLEXT_CLI_LOG_LEVEL="):
                        env_value = line.split("=", 1)[1].strip().strip("'\"")
                        if env_value:
                            log_config.log_level = env_value.upper()
                            log_config.log_level_source = "env_file"
                            return FlextResult[FlextCliModels.LoggingConfig].ok(
                                log_config
                            )

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
        config: FlextCliModels.FlextCliConfig | None = None,
        log_file: Path | None = None,
    ) -> FlextResult[str]:
        """Setup logging specifically for CLI usage using FlextConfig singleton.

        Returns:
            FlextResult[str]: Description of return value.

        """
        try:
            # Use FlextConfig singleton if no config provided
            if config is None:
                config = FlextCliModels.FlextCliConfig()
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
        config: FlextCliModels.FlextCliConfig | None = None,
    ) -> FlextResult[str]:
        """Get the effective log level that would be used using FlextConfig singleton.

        Returns:
            FlextResult[str]: Description of return value.

        """
        try:
            # Use FlextConfig singleton if no config provided
            if config is None:
                config = FlextCliModels.FlextCliConfig()
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
        """Check if logging setup has been completed.

        Returns:
            bool: Description of return value.

        """
        return FlextCliLoggingSetup._setup_complete

    @classmethod
    def set_global_log_level(cls, level: str) -> FlextResult[str]:
        """Set global log level for all FLEXT projects.

        Returns:
            FlextResult[str]: Description of return value.

        """
        try:
            # Validate log level
            valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
            level_upper = level.upper()
            if level_upper not in valid_levels:
                return FlextResult[str].fail(
                    f"Invalid log level '{level}'. Valid levels: {', '.join(valid_levels)}"
                )

            # Set environment variable for cross-project control
            os.environ["FLEXT_LOG_LEVEL"] = level_upper

            # Reconfigure FlextLogger if already configured
            if cls._setup_complete:
                verbosity = os.environ.get("FLEXT_LOG_VERBOSITY", "detailed")
                FlextLogger.configure(
                    log_level=level_upper,
                    structured_output=True,
                    json_output=False,
                    include_source=False,
                    log_verbosity=verbosity,
                )

            return FlextResult[str].ok(f"Global log level set to {level_upper}")
        except Exception as e:
            return FlextResult[str].fail(f"Failed to set log level: {e}")

    @classmethod
    def set_global_log_verbosity(cls, verbosity: str) -> FlextResult[str]:
        """Set global log verbosity for all FLEXT projects.

        Returns:
            FlextResult[str]: Description of return value.

        """
        try:
            # Validate verbosity level
            valid_verbosity = {"compact", "detailed", "full"}
            verbosity_lower = verbosity.lower()
            if verbosity_lower not in valid_verbosity:
                return FlextResult[str].fail(
                    f"Invalid verbosity '{verbosity}'. Valid levels: {', '.join(valid_verbosity)}"
                )

            # Set environment variable for cross-project control
            os.environ["FLEXT_LOG_VERBOSITY"] = verbosity_lower

            # Reconfigure FlextLogger if already configured
            if cls._setup_complete:
                current_level = os.environ.get("FLEXT_LOG_LEVEL", "INFO")
                FlextLogger.configure(
                    log_level=current_level,
                    structured_output=True,
                    json_output=False,
                    include_source=False,
                    log_verbosity=verbosity_lower,
                )

            return FlextResult[str].ok(f"Global log verbosity set to {verbosity_lower}")
        except Exception as e:
            return FlextResult[str].fail(f"Failed to set log verbosity: {e}")

    @classmethod
    def get_current_log_config(cls) -> FlextResult[dict[str, str]]:
        """Get current logging configuration for all FLEXT projects.

        Returns:
            FlextResult[dict[str, str]]: Description of return value.

        """
        try:
            config = {
                "log_level": os.environ.get("FLEXT_LOG_LEVEL", "INFO"),
                "log_verbosity": os.environ.get("FLEXT_LOG_VERBOSITY", "detailed"),
                "cli_log_level": os.environ.get("FLEXT_CLI_LOG_LEVEL", "INFO"),
                "configured": str(cls._setup_complete),
            }
            return FlextResult[dict[str, str]].ok(config)
        except Exception as e:
            return FlextResult[dict[str, str]].fail(f"Failed to get log config: {e}")

    @classmethod
    def configure_project_logging(
        cls,
        project_name: str,
        log_level: str | None = None,
        verbosity: str | None = None,
    ) -> FlextResult[str]:
        """Configure logging for a specific FLEXT project.

        Returns:
            FlextResult[str]: Description of return value.

        """
        try:
            messages: list[str] = []

            if log_level:
                valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
                level_upper = log_level.upper()
                if level_upper not in valid_levels:
                    return FlextResult[str].fail(
                        f"Invalid log level '{log_level}'. Valid levels: {', '.join(valid_levels)}"
                    )

                # Set project-specific environment variable
                env_var = f"FLEXT_{project_name.upper().replace('-', '_')}_LOG_LEVEL"
                os.environ[env_var] = level_upper
                messages.append(f"Log level for {project_name} set to {level_upper}")

            if verbosity:
                valid_verbosity = {"compact", "detailed", "full"}
                verbosity_lower = verbosity.lower()
                if verbosity_lower not in valid_verbosity:
                    return FlextResult[str].fail(
                        f"Invalid verbosity '{verbosity}'. Valid levels: {', '.join(valid_verbosity)}"
                    )

                # Set project-specific environment variable
                env_var = (
                    f"FLEXT_{project_name.upper().replace('-', '_')}_LOG_VERBOSITY"
                )
                os.environ[env_var] = verbosity_lower
                messages.append(
                    f"Log verbosity for {project_name} set to {verbosity_lower}"
                )

            return FlextResult[str].ok("; ".join(messages))
        except Exception as e:
            return FlextResult[str].fail(f"Failed to configure project logging: {e}")


__all__ = [
    "FlextCliLoggingSetup",
]
