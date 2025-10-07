"""CLI core service using flext-core directly.

Production-ready CLI service that uses flext-core services directly without
duplication. Implements standardized architecture patterns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from flext_core import (
    FlextContainer,
    FlextLogger,
    FlextResult,
    FlextService,
    FlextTypes,
)

from flext_cli.config import FlextCliConfig
from flext_cli.constants import FlextCliConstants
from flext_cli.file_tools import FlextCliFileTools
from flext_cli.models import FlextCliModels
from flext_cli.output import FlextCliOutput
from flext_cli.processors import FlextCliProcessors
from flext_cli.prompts import FlextCliPrompts
from flext_cli.typings import FlextCliTypes


class FlextCliCore(FlextService[FlextCliTypes.Data.CliDataDict]):
    """Core CLI service providing comprehensive command-line functionality.

    Manages CLI operations, command execution, configuration, and session handling
    using flext-core patterns with CLI domain-specific types.
    Extends FlextService with CLI-specific data dictionary types.
    """

    def __init__(
        self,
        config: FlextCliTypes.Configuration.CliConfigSchema | None = None,
        **data: object,
    ) -> None:
        """Initialize CLI service with specialized service injection and Phase 1 context enrichment.

        Args:
            config: CLI configuration schema using domain-specific types
            **data: Additional service initialization data

        """
        super().__init__(**data)

        # Phase 1 Enhancement: Context enrichment happens automatically in FlextService.__init__
        # The parent class already calls _enrich_context with service metadata
        # Logger and container are inherited from FlextService via FlextMixins

        # Inject specialized domain services for delegation
        self._config_service = FlextCliConfig()
        self._output = FlextCliOutput()
        self._file_tools = FlextCliFileTools()
        self._processors = FlextCliProcessors()
        self._prompts = FlextCliPrompts()

        # Type-safe configuration initialization
        # Use dict type for internal config management
        self._config: dict[str, object] = config or {}
        self._commands: FlextTypes.Dict = {}
        self._plugins: FlextTypes.Dict = {}
        self._sessions: FlextTypes.Dict = {}
        self._session_active = False

    # ==========================================================================
    # CLI COMMAND MANAGEMENT - Using FlextCliTypes.CliCommand types
    # ==========================================================================

    def register_command(
        self,
        command: FlextCliModels.CliCommand,
    ) -> FlextResult[None]:
        """Register CLI command using CliCommand model instance.

        Args:
            command: CliCommand model instance with validated data

        Returns:
            FlextResult[None]: Registration success or failure result

        """
        # Validation is handled by Pydantic model, no isinstance checks needed
        self._commands[command.name] = command.model_dump()
        self.logger.info(f"Command '{command.name}' registered successfully")
        return FlextResult[None].ok(None)

    def get_command(
        self,
        name: str,
    ) -> FlextResult[FlextCliTypes.CliCommand.CommandDefinition]:
        """Retrieve registered command definition.

        Args:
            name: Command identifier to retrieve

        Returns:
            FlextResult[FlextCliTypes.CliCommand.CommandDefinition]: Command definition or error

        """
        if not name or not isinstance(name, str):
            return FlextResult[FlextCliTypes.CliCommand.CommandDefinition].fail(
                "Command name must be a non-empty string",
            )

        if name not in self._commands:
            return FlextResult[FlextCliTypes.CliCommand.CommandDefinition].fail(
                f"Command '{name}' not found",
            )

        try:
            command_def = self._commands[name]
            # Type-safe conversion to CLI command definition
            if isinstance(command_def, dict):
                typed_def: FlextCliTypes.CliCommand.CommandDefinition = command_def
                return FlextResult[FlextCliTypes.CliCommand.CommandDefinition].ok(
                    typed_def,
                )
            return FlextResult[FlextCliTypes.CliCommand.CommandDefinition].fail(
                f"Invalid command definition type for '{name}'",
            )
        except Exception as e:
            return FlextResult[FlextCliTypes.CliCommand.CommandDefinition].fail(
                f"Command retrieval failed: {e}",
            )

    def execute_command(
        self,
        name: str,
        context: FlextCliTypes.CliCommand.CommandContext
        | FlextTypes.StringList
        | None = None,
        timeout: float | None = None,
    ) -> FlextResult[FlextCliTypes.CliCommand.CommandResult]:
        """Execute registered command with context.

        Args:
            name: Command identifier to execute
            context: Optional execution context with CLI-specific data
            timeout: Optional timeout for command execution

        Returns:
            FlextResult[FlextCliTypes.CliCommand.CommandResult]: Execution result or error

        """
        command_result = self.get_command(name)
        if command_result.is_failure:
            return FlextResult[FlextCliTypes.CliCommand.CommandResult].fail(
                command_result.error or "Command not found",
            )

        try:
            # Execute command with CLI-specific context handling
            if isinstance(context, list):
                # Convert list of strings to context dict
                execution_context = {"args": context}
            else:
                execution_context = context or {}

            # Basic command execution simulation
            result_data: FlextCliTypes.CliCommand.CommandResult = {
                "command": name,
                "status": True,
                "context": execution_context,
                "timestamp": datetime.now(UTC).isoformat(),
                "timeout": timeout,  # Include timeout parameter in result
            }

            self.logger.info(f"Command '{name}' executed successfully")
            return FlextResult[FlextCliTypes.CliCommand.CommandResult].ok(result_data)

        except Exception as e:
            return FlextResult[FlextCliTypes.CliCommand.CommandResult].fail(
                f"Command execution failed: {e}",
            )

    def list_commands(self) -> FlextResult[FlextTypes.StringList]:
        """List all registered commands.

        Returns:
            FlextResult[FlextTypes.StringList]: List of command names or error

        """
        try:
            command_names = list(self._commands.keys())
            return FlextResult[FlextTypes.StringList].ok(command_names)
        except Exception as e:
            return FlextResult[FlextTypes.StringList].fail(
                f"Command listing failed: {e}"
            )

    # ==========================================================================
    # CLI CONFIGURATION MANAGEMENT - Using FlextCliTypes.Configuration types
    # ==========================================================================

    def update_configuration(
        self,
        config: FlextCliTypes.Configuration.CliConfigSchema,
    ) -> FlextResult[None]:
        """Update CLI configuration with enhanced validation.

        Args:
            config: New configuration schema with CLI-specific structure

        Returns:
            FlextResult[None]: Configuration update result

        """
        if not config or not isinstance(config, dict):
            return FlextResult[None].fail("Configuration must be a valid dictionary")

        try:
            # Merge with existing configuration
            self._config.update(config)
            self.logger.info("CLI configuration updated successfully")
            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"Configuration update failed: {e}")

    def get_configuration(
        self,
    ) -> FlextResult[dict[str, object]]:
        """Get current CLI configuration.

        Returns:
            FlextResult[dict[str, object]]: Current configuration or error

        """
        try:
            return FlextResult[FlextCliTypes.Configuration.CliConfigSchema].ok(
                self._config,
            )
        except Exception as e:
            return FlextResult[FlextCliTypes.Configuration.CliConfigSchema].fail(
                f"Configuration retrieval failed: {e}",
            )

    def create_profile(
        self,
        name: str,
        profile_config: FlextCliTypes.Configuration.ProfileConfiguration,
    ) -> FlextResult[None]:
        """Create CLI configuration profile.

        Args:
            name: Profile identifier
            profile_config: Profile-specific configuration

        Returns:
            FlextResult[None]: Profile creation result

        """
        if not name or not isinstance(name, str):
            return FlextResult[None].fail("Profile name must be a non-empty string")

        if not profile_config or not isinstance(profile_config, dict):
            return FlextResult[None].fail("Profile config must be a valid dictionary")

        try:
            # Store profile in configuration
            if "profiles" not in self._config:
                self._config["profiles"] = {}

            # Type-safe profile storage
            profiles_section = self._config["profiles"]
            if isinstance(profiles_section, dict):
                profiles_section[name] = profile_config
                self.logger.info(f"Profile '{name}' created successfully")
                return FlextResult[None].ok(None)
            return FlextResult[None].fail("Invalid profiles configuration structure")

        except Exception as e:
            return FlextResult[None].fail(f"Profile creation failed: {e}")

    # ==========================================================================
    # SESSION MANAGEMENT - Using FlextCliTypes.Configuration types
    # ==========================================================================

    def start_session(
        self,
        session_config: FlextCliTypes.Configuration.SessionConfiguration | None = None,
    ) -> FlextResult[None]:
        """Start CLI session with configuration.

        Args:
            session_config: Optional session-specific configuration

        Returns:
            FlextResult[None]: Session start result

        """
        if self._session_active:
            return FlextResult[None].fail("Session is already active")

        try:
            # Initialize session with CLI-specific configuration
            self._session_config = session_config or {}
            self._session_active = True
            self._session_start_time = datetime.now(UTC).isoformat()

            self.logger.info("CLI session started successfully")
            return FlextResult[None].ok(None)

        except Exception as e:
            return FlextResult[None].fail(f"Session start failed: {e}")

    def end_session(self) -> FlextResult[None]:
        """End current CLI session.

        Returns:
            FlextResult[None]: Session end result

        """
        if not self._session_active:
            return FlextResult[None].fail("No active session to end")

        try:
            self._session_active = False
            if hasattr(self, "_session_config"):
                delattr(self, "_session_config")
            if hasattr(self, "_session_start_time"):
                delattr(self, "_session_start_time")

            self.logger.info("CLI session ended successfully")
            return FlextResult[None].ok(None)

        except Exception as e:
            return FlextResult[None].fail(f"Session end failed: {e}")

    def is_session_active(self) -> bool:
        """Check if CLI session is currently active.

        Returns:
            bool: True if session is active, False otherwise

        """
        return self._session_active

    # ==========================================================================
    # STATISTICS AND MONITORING - Using FlextCliTypes.Data types
    # ==========================================================================

    def get_command_statistics(self) -> FlextResult[FlextCliTypes.Data.CliDataDict]:
        """Get command usage statistics using CLI-specific data types.

        Returns:
            FlextResult[FlextCliTypes.Data.CliDataDict]: Statistics data or error

        """
        try:
            stats: FlextCliTypes.Data.CliDataDict = {
                "total_commands": len(self._commands),
                "registered_commands": list(self._commands.keys()),
                "session_active": self._session_active,
                "timestamp": datetime.now(UTC).isoformat(),
            }
            return FlextResult[FlextCliTypes.Data.CliDataDict].ok(stats)
        except Exception as e:
            return FlextResult[FlextCliTypes.Data.CliDataDict].fail(
                f"Statistics collection failed: {e}",
            )

    def get_service_info(self) -> FlextTypes.Dict:
        """Get comprehensive service information.

        Returns:
            FlextTypes.Dict: Service information

        """
        try:
            # Collect comprehensive service information
            commands_count = len(self._commands)
            config_keys = list(self._config.keys()) if self._config else []

            info_data: FlextTypes.Dict = {
                "service_name": "FlextCliService",
                "commands_registered": commands_count,
                "configuration_sections": config_keys,
                "session_active": self._session_active,
                "service_ready": commands_count > 0,
                "timestamp": datetime.now(UTC).isoformat(),
            }

            return info_data

        except Exception as e:
            self.logger.exception("Service info collection failed")
            return {"error": str(e)}

    def get_session_statistics(self) -> FlextResult[FlextCliTypes.Data.CliDataDict]:
        """Get session-specific statistics using CLI data types.

        Returns:
            FlextResult[FlextCliTypes.Data.CliDataDict]: Session statistics or error

        """
        if not self._session_active:
            return FlextResult[FlextCliTypes.Data.CliDataDict].fail(
                "No active session for statistics",
            )

        try:
            # Calculate session duration if session is active
            session_duration = 0
            if hasattr(self, "_session_start_time") and self._session_start_time:
                current_time = datetime.now(UTC)
                # Parse ISO format string back to datetime for duration calculation
                start_time = datetime.fromisoformat(self._session_start_time)
                duration_delta = current_time - start_time
                session_duration = int(duration_delta.total_seconds())

            # Collect session-specific statistics
            statistics: FlextCliTypes.Data.CliDataDict = {
                "session_active": self._session_active,
                "session_duration_seconds": session_duration,
                "commands_available": len(self._commands),
                "configuration_loaded": bool(self._config),
                "session_config_keys": (
                    list(self._session_config.keys())
                    if hasattr(self, "_session_config") and self._session_config
                    else []
                ),
                "start_time": (
                    self._session_start_time
                    if hasattr(self, "_session_start_time")
                    else "unknown"
                ),
                "current_time": datetime.now(UTC).isoformat(),
            }

            return FlextResult[FlextCliTypes.Data.CliDataDict].ok(statistics)

        except Exception as e:
            return FlextResult[FlextCliTypes.Data.CliDataDict].fail(
                f"Session statistics collection failed: {e}",
            )

    # ==========================================================================
    # SERVICE EXECUTION METHODS - FlextService protocol implementation
    # ==========================================================================

    # Attribute declarations - override FlextService optional types
    # These are guaranteed initialized in __init__
    logger: FlextLogger
    _container: FlextContainer
    _config: FlextCliTypes.Configuration.CliConfigSchema | None

    def execute(self) -> FlextResult[FlextCliTypes.Data.CliDataDict]:
        """Execute CLI service operations.

        Returns:
            FlextResult[FlextCliTypes.Data.CliDataDict]: Service execution result

        """
        try:
            # Validate service state before execution
            if not self._commands:
                return FlextResult[FlextCliTypes.Data.CliDataDict].fail(
                    "No commands registered for execution",
                )

            # Execute service with comprehensive status data
            status_data: FlextCliTypes.Data.CliDataDict = {
                "service_executed": True,
                "commands_count": len(self._commands),
                "session_active": self._session_active,
                "execution_timestamp": datetime.now(UTC).isoformat(),
                "service_ready": True,
            }

            return FlextResult[FlextCliTypes.Data.CliDataDict].ok(status_data)

        except Exception as e:
            return FlextResult[FlextCliTypes.Data.CliDataDict].fail(
                f"Service execution failed: {e}",
            )

    def execute_cli_command_with_context(
        self,
        command_name: str,
        user_id: str | None = None,
        **context_data: object,
    ) -> FlextResult[FlextCliTypes.Data.CliDataDict]:
        """Execute CLI command with automatic context enrichment (Phase 1 pattern).

        Demonstrates the new execute_with_context_enrichment() pattern from flext-core
        Phase 1 architectural enhancement for CLI operations.

        Args:
            command_name: Name of the command to execute
            user_id: Optional user ID for audit context
            **context_data: Additional context data for enriched logging

        Returns:
            FlextResult[FlextCliTypes.Data.CliDataDict]: Command execution result

        Example:
            ```python
            cli_core = FlextCliCore()
            result = cli_core.execute_cli_command_with_context(
                command_name="list-users",
                user_id="REDACTED_LDAP_BIND_PASSWORD",
                operation_type="query",
                environment="production",
            )
            ```

        Note:
            This uses the inherited execute_with_context_enrichment() from FlextService,
            demonstrating how flext-cli integrates Phase 1 enhancements.

        """
        # Use the inherited execute_with_context_enrichment() pattern from FlextService
        # This automatically handles:
        # - Correlation ID generation/propagation
        # - Operation context enrichment
        # - User context binding
        # - Performance tracking
        # - Structured logging with context
        return self.execute_with_context_enrichment(
            operation_name=f"cli_command_{command_name}",
            correlation_id=None,  # Auto-generated if None
            user_id=user_id,
            command_name=command_name,
            **context_data,
        )

    def health_check(self) -> FlextResult[FlextTypes.Dict]:
        """Perform health check on the CLI service.

        Returns:
            FlextResult[FlextTypes.Dict]: Health check result

        """
        try:
            return FlextResult[FlextTypes.Dict].ok({
                "service_healthy": True,
                "commands_count": len(self._commands),
                "session_active": self._session_active,
                "timestamp": datetime.now(UTC).isoformat(),
            })
        except Exception as e:
            return FlextResult[FlextTypes.Dict].fail(f"Health check failed: {e}")

    def get_config(self) -> FlextResult[FlextTypes.Dict]:
        """Get current service configuration.

        Returns:
            FlextResult[FlextTypes.Dict]: Configuration data

        """
        try:
            return FlextResult[FlextTypes.Dict].ok(
                dict(self._config) if self._config else {}
            )
        except Exception as e:
            return FlextResult[FlextTypes.Dict].fail(f"Get config failed: {e}")

    def get_handlers(self) -> FlextResult[FlextTypes.StringList]:
        """Get list of registered command handlers.

        Returns:
            FlextResult[FlextTypes.StringList]: List of handler names

        """
        try:
            return FlextResult[FlextTypes.StringList].ok(
                list(self._commands.keys()) if self._commands else []
            )
        except Exception as e:
            return FlextResult[FlextTypes.StringList].fail(f"Get handlers failed: {e}")

    def get_plugins(self) -> FlextResult[FlextTypes.StringList]:
        """Get list of registered plugins.

        Returns:
            FlextResult[FlextTypes.StringList]: List of plugin names

        """
        try:
            return FlextResult[FlextTypes.StringList].ok(
                list(self._plugins.keys()) if self._plugins else []
            )
        except Exception as e:
            return FlextResult[FlextTypes.StringList].fail(f"Get plugins failed: {e}")

    def get_sessions(self) -> FlextResult[FlextTypes.StringList]:
        """Get list of active sessions.

        Returns:
            FlextResult[FlextTypes.StringList]: List of session IDs

        """
        try:
            return FlextResult[FlextTypes.StringList].ok(
                list(self._sessions.keys()) if self._sessions else []
            )
        except Exception as e:
            return FlextResult[FlextTypes.StringList].fail(f"Get sessions failed: {e}")

    def get_commands(self) -> FlextResult[FlextTypes.StringList]:
        """Get list of registered commands.

        Returns:
            FlextResult[FlextTypes.StringList]: List of command names

        """
        try:
            return FlextResult[FlextTypes.StringList].ok(
                list(self._commands.keys()) if self._commands else []
            )
        except Exception as e:
            return FlextResult[FlextTypes.StringList].fail(f"Get commands failed: {e}")

    def get_formatters(self) -> FlextResult[FlextTypes.StringList]:
        """Get list of available formatters from constants.

        Returns:
            FlextResult[FlextTypes.StringList]: List of formatter names

        """
        return FlextResult[FlextTypes.StringList].ok(
            FlextCliConstants.OUTPUT_FORMATS_LIST
        )

    def load_configuration(self, config_path: str) -> FlextResult[FlextTypes.Dict]:
        """Load configuration from file.

        Args:
            config_path: Path to configuration file

        Returns:
            FlextResult[FlextTypes.Dict]: Loaded configuration

        """
        if not config_path or not config_path.strip():
            return FlextResult[FlextTypes.Dict].fail(
                "Configuration path cannot be empty"
            )

        try:
            config_file = Path(config_path)

            if not config_file.exists():
                return FlextResult[FlextTypes.Dict].fail(
                    f"Configuration file not found: {config_path}"
                )

            if not config_file.is_file():
                return FlextResult[FlextTypes.Dict].fail(
                    f"Path is not a file: {config_path}"
                )

            # Read and parse JSON configuration
            content = config_file.read_text(encoding="utf-8")
            config_data = json.loads(content)

            if not isinstance(config_data, dict):
                return FlextResult[FlextTypes.Dict].fail(
                    "Configuration must be a JSON object"
                )

            return FlextResult[FlextTypes.Dict].ok(config_data)

        except json.JSONDecodeError as e:
            return FlextResult[FlextTypes.Dict].fail(
                f"Invalid JSON in configuration file: {e}"
            )
        except Exception as e:
            return FlextResult[FlextTypes.Dict].fail(f"Load configuration failed: {e}")

    def save_configuration(
        self, config_path: str, config_data: FlextTypes.Dict
    ) -> FlextResult[None]:
        """Save configuration to file.

        Args:
            config_path: Path to save configuration file
            config_data: Configuration data to save

        Returns:
            FlextResult[None]: Success or error

        """
        try:
            path = Path(config_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"Save configuration failed: {e}")

    def validate_configuration(self, _config: FlextCliConfig) -> FlextResult[None]:
        """Validate configuration using FlextCliConfig Pydantic model.

        Args:
            _config: FlextCliConfig model instance (validation automatic via Pydantic)

        Returns:
            FlextResult[None]: Success (validation happens during model instantiation)

        Note:
            Validation is automatically performed by Pydantic field validators
            when FlextCliConfig instance is created. This method validates the
            configuration is correct and returns success if config is valid.

        """
        # Validation already performed by Pydantic during instantiation
        return FlextResult[None].ok(None)

    # ==========================================================================
    # END OF CORE CLI SERVICE METHODS
    # ==========================================================================
    # NOTE: File operations, JSON/YAML parsing, validation, HTTP requests,
    # and output formatting are now accessed directly through their respective
    # services via the FlextCli facade:
    #   - File operations: Use cli.file_tools.* directly
    #   - Validation: Use FlextUtilities.Validation.* from flext-core
    #   - HTTP: Use flext-api domain library
    #   - Output: Use cli.output.* directly
    # ==========================================================================


__all__ = ["FlextCliCore"]
