"""FLEXT CLI Logging Setup - Automatic logging configuration from multiple sources.

Provides automatic logging level configuration from CLI parameters, environment variables,
or .env files following SOLID principles and flext-core integration patterns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import ClassVar, override

from flext_cli.config import FlextCliConfig
from flext_cli.models import FlextCliModels
from flext_core import (
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

    # LoggingConfig class reference for direct access
    LoggingConfigModel: ClassVar[type[FlextCliModels.LoggingConfig]] = (
        FlextCliModels.LoggingConfig
    )

    # Class-level state for singleton behavior
    _loggers: ClassVar[dict[str, logging.Logger]] = {}
    _setup_complete: ClassVar[bool] = False

    @override
    def __init__(self, config: FlextCliConfig | None = None) -> None:
        """Initialize logging setup using FlextConfig singleton as SINGLE SOURCE OF TRUTH."""
        super().__init__()
        self._container = FlextContainer.get_global()
        self._logger = FlextLogger(__name__)

        # Use resolved config without storing as instance attribute (FlextService is frozen)
        self._resolved_config = config or FlextCliConfig()

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
            if not log_config_result.is_success:
                return log_config_result

            log_config = log_config_result.value

            # Configure FlextLogger for entire CLI application with enhanced formatting
            config = FlextCliConfig.get_global_instance()
            verbosity = (
                config.cli_log_verbosity
                if config.cli_log_verbosity != config.log_verbosity
                else config.log_verbosity
            )
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
                log_file_path = Path(log_config.log_file)
                log_file_path.parent.mkdir(parents=True, exist_ok=True)
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

    def _detect_log_configuration(self) -> FlextResult[FlextCliModels.LoggingConfig]:
        """Detect log configuration from FlextCliConfig singleton."""
        try:
            # Use FlextCliConfig singleton as single source of truth
            config = FlextCliConfig.get_global_instance()

            # Use CLI-specific log level if it differs from global, otherwise use global
            if config.cli_log_level != config.log_level:
                log_level = config.cli_log_level
                log_level_source = "FlextCliConfig.cli_log_level"
            else:
                log_level = config.log_level
                log_level_source = "FlextCliConfig.log_level"

            # Create logging configuration using standardized config
            log_config = FlextCliModels.LoggingConfig(
                log_level=log_level,
                log_level_source=log_level_source,
                console_output=True,
                log_file=str(config.log_file) if config.log_file else None,
            )

            return FlextResult[FlextCliModels.LoggingConfig].ok(log_config)
        except Exception as e:
            return FlextResult[FlextCliModels.LoggingConfig].fail(
                f"Log configuration detection failed: {e}"
            )

    @classmethod
    def setup_for_cli(
        cls,
        config: FlextCliConfig | None = None,
        log_file: Path | None = None,
    ) -> FlextResult[str]:
        """Setup logging specifically for CLI usage using FlextConfig singleton.

        Returns:
            FlextResult[str]: Description of return value.

        """
        try:
            # Use FlextConfig singleton if no config provided
            if config is None:
                config = FlextCliConfig()
            setup_instance = cls(config)

            # Configure log file if specified
            if log_file:
                # Update FlextCliConfig singleton with log file path
                config.log_file = str(log_file)

            result = setup_instance.setup_logging()
            if not result.is_success:
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
        """Get the effective log level that would be used using FlextConfig singleton.

        Returns:
            FlextResult[str]: Description of return value.

        """
        try:
            # Use FlextConfig singleton if no config provided
            if config is None:
                config = FlextCliConfig()
            setup_instance = cls(config)
            detection_result = setup_instance._detect_log_configuration()

            if not detection_result.is_success:
                return FlextResult[str].fail(
                    detection_result.error or "Log level detection failed"
                )

            log_config = detection_result.value
            return FlextResult[str].ok(log_config.log_level)
        except Exception as e:
            return FlextResult[str].fail(f"Log level detection failed: {e}")

    @property
    def is_setup_complete(self: object) -> bool:
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

            # Update FlextCliConfig singleton for cross-project control
            config = FlextCliConfig.get_global_instance()
            config.log_level = level_upper

            # Reconfigure FlextLogger if already configured
            if cls._setup_complete:
                verbosity = config.log_verbosity
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

            # Update FlextCliConfig singleton for cross-project control
            config = FlextCliConfig.get_global_instance()
            config.log_verbosity = verbosity_lower

            # Reconfigure FlextLogger if already configured
            if cls._setup_complete:
                current_level = config.log_level
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
    def get_current_log_config(cls: object) -> FlextResult[dict[str, str]]:
        """Get current logging configuration for all FLEXT projects.

        Returns:
            FlextResult[dict[str, str]]: Description of return value.

        """
        try:
            cli_config = FlextCliConfig.get_global_instance()
            config: dict[str, str] = {
                "log_level": cli_config.log_level,
                "log_verbosity": cli_config.log_verbosity,
                "cli_log_level": cli_config.cli_log_level,
                "cli_log_verbosity": cli_config.cli_log_verbosity,
                "configured": str(FlextCliLoggingSetup._setup_complete),
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

                # Update FlextCliConfig singleton for project-specific settings
                config = FlextCliConfig.get_global_instance()
                if project_name.lower() == "cli":
                    config.cli_log_level = level_upper
                else:
                    config.log_level = level_upper
                messages.append(f"Log level for {project_name} set to {level_upper}")

            if verbosity:
                valid_verbosity = {"compact", "detailed", "full"}
                verbosity_lower = verbosity.lower()
                if verbosity_lower not in valid_verbosity:
                    return FlextResult[str].fail(
                        f"Invalid verbosity '{verbosity}'. Valid levels: {', '.join(valid_verbosity)}"
                    )

                # Update FlextCliConfig singleton for project-specific settings
                config = FlextCliConfig.get_global_instance()
                if project_name.lower() == "cli":
                    config.cli_log_verbosity = verbosity_lower
                else:
                    config.log_verbosity = verbosity_lower
                messages.append(
                    f"Log verbosity for {project_name} set to {verbosity_lower}"
                )

            return FlextResult[str].ok("; ".join(messages))
        except Exception as e:
            return FlextResult[str].fail(f"Failed to configure project logging: {e}")

    @override
    def execute(self) -> FlextResult[dict[str, object]]:
        """Execute the main logging setup operation.

        Returns:
            FlextResult[dict[str, object]]: Logging setup execution result

        """
        try:
            self._logger.info("Executing logging setup service")

            # Perform logging setup
            setup_result = self.setup_logging()
            if setup_result.is_failure:
                return FlextResult[dict[str, object]].fail(
                    setup_result.error or "Setup failed"
                )

            # Return setup status
            config = FlextCliConfig.get_global_instance()
            status_data: dict[str, object] = {
                "service": FlextCliLoggingSetup,
                "status": "configured",
                "setup_complete": self.is_setup_complete,
                "log_level": config.log_level,
                "log_verbosity": config.log_verbosity,
            }

            return FlextResult[dict[str, object]].ok(status_data)
        except Exception as e:
            return FlextResult[dict[str, object]].fail(
                f"Logging setup execution failed: {e}"
            )

    async def execute_async(self) -> FlextResult[dict[str, object]]:
        """Execute the main logging setup operation asynchronously.

        Returns:
            FlextResult[dict[str, object]]: Async logging setup execution result

        """
        try:
            self._logger.info("Executing logging setup service asynchronously")

            # Perform logging setup asynchronously
            setup_result = self.setup_logging()
            if setup_result.is_failure:
                return FlextResult[dict[str, object]].fail(
                    setup_result.error or "Setup failed"
                )

            # Simulate async operation
            await asyncio.sleep(0.001)

            # Return setup status
            config = FlextCliConfig.get_global_instance()
            status_data: dict[str, object] = {
                "service": FlextCliLoggingSetup,
                "status": "configured_async",
                "setup_complete": self.is_setup_complete,
                "log_level": config.log_level,
                "log_verbosity": config.log_verbosity,
            }

            return FlextResult[dict[str, object]].ok(status_data)
        except Exception as e:
            return FlextResult[dict[str, object]].fail(
                f"Async logging setup execution failed: {e}"
            )


__all__ = [
    "FlextCliLoggingSetup",
]
