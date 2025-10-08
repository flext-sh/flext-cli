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

from flext_core import FlextCore, FlextResult

from flext_cli.config import FlextCliConfig
from flext_cli.constants import FlextCliConstants
from flext_cli.models import FlextCliModels
from flext_cli.typings import FlextCliTypes


class FlextCliCore(FlextCore.Service[FlextCliTypes.Data.CliDataDict]):
    """Core CLI service providing comprehensive command-line functionality.

    Manages CLI operations, command execution, configuration, and session handling
    using flext-core patterns with CLI domain-specific types.
    Extends FlextCore.Service with CLI-specific data dictionary types.
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

        # Phase 1 Enhancement: Context enrichment happens automatically in FlextCore.Service.__init__
        # The parent class already calls _enrich_context with service metadata
        # Logger and container are inherited from FlextCore.Service via FlextMixins

        # Type-safe configuration initialization
        # Use dict type for internal config management
        self._config: FlextCliTypes.Configuration.CliConfigSchema = (
            config if config is not None else {}
        )
        self._commands: FlextCore.Types.Dict = {}
        self._plugins: FlextCore.Types.Dict = {}
        self._sessions: FlextCore.Types.Dict = {}
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
        self.logger.info(
            FlextCliConstants.LogMessages.COMMAND_REGISTERED.format(name=command.name)
        )
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
                FlextCliConstants.ErrorMessages.COMMAND_NAME_EMPTY,
            )

        if name not in self._commands:
            return FlextResult[FlextCliTypes.CliCommand.CommandDefinition].fail(
                FlextCliConstants.ErrorMessages.COMMAND_NOT_FOUND.format(name=name),
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
                FlextCliConstants.ErrorMessages.INVALID_COMMAND_TYPE.format(name=name),
            )
        except Exception as e:
            return FlextResult[FlextCliTypes.CliCommand.CommandDefinition].fail(
                FlextCliConstants.ErrorMessages.COMMAND_RETRIEVAL_FAILED.format(
                    error=e
                ),
            )

    def execute_command(
        self,
        name: str,
        context: FlextCliTypes.CliCommand.CommandContext
        | FlextCore.Types.StringList
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
                command_result.error
                or FlextCliConstants.ErrorMessages.COMMAND_NOT_FOUND.format(name=name),
            )

        try:
            # Execute command with CLI-specific context handling
            if isinstance(context, list):
                # Convert list of strings to context dict
                execution_context = {FlextCliConstants.DictKeys.ARGS: context}
            else:
                execution_context = context or {}

            # Basic command execution simulation
            result_data: FlextCliTypes.CliCommand.CommandResult = {
                FlextCliConstants.DictKeys.COMMAND: name,
                FlextCliConstants.DictKeys.STATUS: True,
                FlextCliConstants.DictKeys.CONTEXT: execution_context,
                FlextCliConstants.DictKeys.TIMESTAMP: datetime.now(UTC).isoformat(),
                FlextCliConstants.DictKeys.TIMEOUT: timeout,  # Include timeout parameter in result
            }

            self.logger.info(
                FlextCliConstants.LogMessages.COMMAND_EXECUTED.format(name=name)
            )
            return FlextResult[FlextCliTypes.CliCommand.CommandResult].ok(result_data)

        except Exception as e:
            return FlextResult[FlextCliTypes.CliCommand.CommandResult].fail(
                FlextCliConstants.ErrorMessages.COMMAND_EXECUTION_FAILED.format(
                    error=e
                ),
            )

    def list_commands(self) -> FlextResult[FlextCore.Types.StringList]:
        """List all registered commands.

        Returns:
            FlextResult[FlextCore.Types.StringList]: List of command names or error

        """
        try:
            command_names = list(self._commands.keys())
            return FlextResult[FlextCore.Types.StringList].ok(command_names)
        except Exception as e:
            return FlextResult[FlextCore.Types.StringList].fail(
                FlextCliConstants.ErrorMessages.COMMAND_LISTING_FAILED.format(error=e)
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
            return FlextResult[None].fail(
                FlextCliConstants.ErrorMessages.CONFIG_NOT_DICT
            )

        try:
            # Merge with existing configuration
            # Type guard: _config is always initialized as dict in __init__
            if isinstance(self._config, dict):
                self._config.update(config)
                self.logger.info(FlextCliConstants.LogMessages.CLI_CONFIG_UPDATED)
                return FlextResult[None].ok(None)
            return FlextResult[None].fail(
                FlextCliConstants.ErrorMessages.CONFIG_NOT_INITIALIZED
            )
        except Exception as e:
            return FlextResult[None].fail(
                FlextCliConstants.ErrorMessages.CONFIG_UPDATE_FAILED.format(error=e)
            )

    def get_configuration(
        self,
    ) -> FlextResult[FlextCliTypes.Configuration.CliConfigSchema]:
        """Get current CLI configuration.

        Returns:
            FlextResult[FlextCliTypes.Configuration.CliConfigSchema]: Current configuration or error

        """
        try:
            # Type guard: _config is always initialized as dict in __init__
            if isinstance(self._config, dict):
                return FlextResult[FlextCliTypes.Configuration.CliConfigSchema].ok(
                    self._config,
                )
            return FlextResult[FlextCliTypes.Configuration.CliConfigSchema].fail(
                FlextCliConstants.ErrorMessages.CONFIG_NOT_INITIALIZED,
            )
        except Exception as e:
            return FlextResult[FlextCliTypes.Configuration.CliConfigSchema].fail(
                FlextCliConstants.ErrorMessages.CONFIG_RETRIEVAL_FAILED.format(error=e),
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
            return FlextResult[None].fail(
                FlextCliConstants.ErrorMessages.PROFILE_NAME_EMPTY
            )

        if not profile_config or not isinstance(profile_config, dict):
            return FlextResult[None].fail(
                FlextCliConstants.ErrorMessages.PROFILE_CONFIG_NOT_DICT
            )

        try:
            # Type guard: _config is always initialized as dict in __init__
            if not isinstance(self._config, dict):
                return FlextResult[None].fail(
                    FlextCliConstants.ErrorMessages.CONFIG_NOT_INITIALIZED
                )

            # Store profile in configuration
            if FlextCliConstants.DictKeys.PROFILES not in self._config:
                self._config[FlextCliConstants.DictKeys.PROFILES] = {}

            # Type-safe profile storage
            profiles_section = self._config[FlextCliConstants.DictKeys.PROFILES]
            if isinstance(profiles_section, dict):
                profiles_section[name] = profile_config
                self.logger.info(
                    FlextCliConstants.LogMessages.PROFILE_CREATED.format(name=name)
                )
                return FlextResult[None].ok(None)
            return FlextResult[None].fail(
                FlextCliConstants.ErrorMessages.INVALID_PROFILES_STRUCTURE
            )

        except Exception as e:
            return FlextResult[None].fail(
                FlextCliConstants.ErrorMessages.PROFILE_CREATION_FAILED.format(error=e)
            )

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
            return FlextResult[None].fail(
                FlextCliConstants.ErrorMessages.SESSION_ALREADY_ACTIVE
            )

        try:
            # Initialize session with CLI-specific configuration
            self._session_config = session_config or {}
            self._session_active = True
            self._session_start_time = datetime.now(UTC).isoformat()

            self.logger.info(FlextCliConstants.LogMessages.SESSION_STARTED)
            return FlextResult[None].ok(None)

        except Exception as e:
            return FlextResult[None].fail(
                FlextCliConstants.ErrorMessages.SESSION_START_FAILED.format(error=e)
            )

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

    def get_command_statistics(
        self,
    ) -> FlextResult[FlextCliTypes.Data.CliDataDict]:
        """Get command usage statistics using CLI-specific data types.

        Returns:
            FlextResult[FlextCliTypes.Data.CliDataDict]: Statistics data or error

        """
        try:
            stats: FlextCliTypes.Data.CliDataDict = {
                FlextCliConstants.DictKeys.TOTAL_COMMANDS: len(self._commands),
                "registered_commands": list(self._commands.keys()),
                "session_active": self._session_active,
                FlextCliConstants.DictKeys.TIMESTAMP: datetime.now(UTC).isoformat(),
            }
            return FlextResult[FlextCliTypes.Data.CliDataDict].ok(stats)
        except Exception as e:
            return FlextResult[FlextCliTypes.Data.CliDataDict].fail(
                f"Statistics collection failed: {e}",
            )

    def get_service_info(self) -> FlextCore.Types.Dict:
        """Get comprehensive service information.

        Returns:
            FlextCore.Types.Dict: Service information

        """
        try:
            # Collect comprehensive service information
            commands_count = len(self._commands)
            config_keys = list(self._config.keys()) if self._config else []

            info_data: FlextCore.Types.Dict = {
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

    def get_session_statistics(
        self,
    ) -> FlextResult[FlextCliTypes.Data.CliDataDict]:
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
    # SERVICE EXECUTION METHODS - FlextCore.Service protocol implementation
    # ==========================================================================

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
            This uses the inherited execute_with_context_enrichment() from FlextCore.Service,
            demonstrating how flext-cli integrates Phase 1 enhancements.

        """
        # Use the inherited execute_with_context_enrichment() pattern from FlextCore.Service
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

    def health_check(self) -> FlextResult[FlextCore.Types.Dict]:
        """Perform health check on the CLI service.

        Returns:
            FlextResult[FlextCore.Types.Dict]: Health check result

        """
        try:
            return FlextResult[FlextCore.Types.Dict].ok({
                "service_healthy": True,
                "commands_count": len(self._commands),
                "session_active": self._session_active,
                "timestamp": datetime.now(UTC).isoformat(),
            })
        except Exception as e:
            return FlextResult[FlextCore.Types.Dict].fail(f"Health check failed: {e}")

    def get_config(self) -> FlextResult[FlextCore.Types.Dict]:
        """Get current service configuration.

        Returns:
            FlextResult[FlextCore.Types.Dict]: Configuration data

        """
        try:
            return FlextResult[FlextCore.Types.Dict].ok(
                dict(self._config) if self._config else {}
            )
        except Exception as e:
            return FlextResult[FlextCore.Types.Dict].fail(f"Get config failed: {e}")

    def get_handlers(self) -> FlextResult[FlextCore.Types.StringList]:
        """Get list of registered command handlers.

        Returns:
            FlextResult[FlextCore.Types.StringList]: List of handler names

        """
        try:
            return FlextResult[FlextCore.Types.StringList].ok(
                list(self._commands.keys()) if self._commands else []
            )
        except Exception as e:
            return FlextResult[FlextCore.Types.StringList].fail(
                f"Get handlers failed: {e}"
            )

    def get_plugins(self) -> FlextResult[FlextCore.Types.StringList]:
        """Get list of registered plugins.

        Returns:
            FlextResult[FlextCore.Types.StringList]: List of plugin names

        """
        try:
            return FlextResult[FlextCore.Types.StringList].ok(
                list(self._plugins.keys()) if self._plugins else []
            )
        except Exception as e:
            return FlextResult[FlextCore.Types.StringList].fail(
                f"Get plugins failed: {e}"
            )

    def get_sessions(self) -> FlextResult[FlextCore.Types.StringList]:
        """Get list of active sessions.

        Returns:
            FlextResult[FlextCore.Types.StringList]: List of session IDs

        """
        try:
            return FlextResult[FlextCore.Types.StringList].ok(
                list(self._sessions.keys()) if self._sessions else []
            )
        except Exception as e:
            return FlextResult[FlextCore.Types.StringList].fail(
                f"Get sessions failed: {e}"
            )

    def get_commands(self) -> FlextResult[FlextCore.Types.StringList]:
        """Get list of registered commands.

        Returns:
            FlextResult[FlextCore.Types.StringList]: List of command names

        """
        try:
            return FlextResult[FlextCore.Types.StringList].ok(
                list(self._commands.keys()) if self._commands else []
            )
        except Exception as e:
            return FlextResult[FlextCore.Types.StringList].fail(
                f"Get commands failed: {e}"
            )

    def get_formatters(self) -> FlextResult[FlextCore.Types.StringList]:
        """Get list of available formatters from constants.

        Returns:
            FlextResult[FlextCore.Types.StringList]: List of formatter names

        """
        return FlextResult[FlextCore.Types.StringList].ok(
            FlextCliConstants.OUTPUT_FORMATS_LIST
        )

    def load_configuration(self, config_path: str) -> FlextResult[FlextCore.Types.Dict]:
        """Load configuration from file.

        Args:
            config_path: Path to configuration file

        Returns:
            FlextResult[FlextCore.Types.Dict]: Loaded configuration

        """
        if not config_path or not config_path.strip():
            return FlextResult[FlextCore.Types.Dict].fail(
                "Configuration path cannot be empty"
            )

        try:
            config_file = Path(config_path)

            if not config_file.exists():
                return FlextResult[FlextCore.Types.Dict].fail(
                    f"Configuration file not found: {config_path}"
                )

            if not config_file.is_file():
                return FlextResult[FlextCore.Types.Dict].fail(
                    f"Path is not a file: {config_path}"
                )

            # Read and parse JSON configuration
            content = config_file.read_text(encoding="utf-8")
            config_data = json.loads(content)

            if not isinstance(config_data, dict):
                return FlextResult[FlextCore.Types.Dict].fail(
                    "Configuration must be a JSON object"
                )

            return FlextResult[FlextCore.Types.Dict].ok(config_data)

        except json.JSONDecodeError as e:
            return FlextResult[FlextCore.Types.Dict].fail(
                f"Invalid JSON in configuration file: {e}"
            )
        except Exception as e:
            return FlextResult[FlextCore.Types.Dict].fail(
                f"Load configuration failed: {e}"
            )

    def save_configuration(
        self, config_path: str, config_data: FlextCore.Types.Dict
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
    #   - Validation: Use FlextCore.Utilities.Validation.* from flext-core
    #   - HTTP: Use flext-api domain library
    #   - Output: Use cli.output.* directly
    # ==========================================================================


__all__ = ["FlextCliCore"]
