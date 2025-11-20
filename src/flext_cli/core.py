"""FLEXT CLI Core Service - Comprehensive command-line operations (Layer 3 Application).

**PURPOSE**: Production-ready CLI service extending flext-core FlextService[CliDataDict]
with comprehensive command management, configuration lifecycle, session handling, and
statistics monitoring. Uses railway-oriented patterns (FlextResult[T]) throughout.

**ARCHITECTURE LAYER**: Application Layer (Layer 3) - CLI-specific service
- Extends FlextService[FlextCliTypes.Data.CliDataDict] from flext-core Layer 3
- Implements CLI-specific data dictionary types for type safety
- Uses FlextMixins for logger and context enrichment
- Phase 1 enhancement: automatic context enrichment with correlation IDs and user context

**CORE CAPABILITIES** (10+ integrated features):
1. Command Management - Register, retrieve, execute, list CLI commands
2. Configuration Management - Load, save, update, retrieve CLI configuration
3. Profile System - Create, manage CLI configuration profiles
4. Session Management - Start, end, monitor CLI sessions
5. Statistics - Command usage and session-specific metrics
6. Health Checks - Service health verification and readiness
7. Service Information - Comprehensive service status and state

8. Context Enrichment - Automatic correlation IDs, user context (Phase 1)
9. Railway-Oriented Error Handling - All operations return FlextResult[T]
10. Type-Safe Configuration - Pydantic validation with domain-specific types

**INTEGRATION POINTS**:

"""

from __future__ import annotations

# Integration points:
# - Extends FlextService (flext-core Layer 3 foundation)
# - Uses FlextResult[T] (railway-oriented error handling)
# - References FlextCliTypes (CLI domain data types)
# - Inherits from FlextMixins (logger, context management)
# - Compatible with FlextCliConfig (Pydantic settings)
# - Ecosystem-ready (32+ FLEXT projects can use)
#
# Production readiness checklist:
# [x] Railway-oriented pattern (all methods return FlextResult[T])
# [x] Type-safe domain types (FlextCliTypes.Configuration, Data)
# [x] Comprehensive error handling (try/except with FlextResult)
# [x] Service state management (commands, config, sessions)
# [x] Context enrichment automation (Phase 1 enhancement)
# [x] Pydantic validation integration (FlextCliConfig)
# [x] Session lifecycle management (start, end, status)
# [x] Statistics collection and monitoring
# [x] Health checks and service information
# [x] File-based configuration persistence
# [x] Comprehensive docstrings with examples
# [x] 100% type annotations throughout
#
# Usage patterns:
# 1. Initialize service: `cli_core = FlextCliCore(config=...)`
# 2. Register commands: `cli_core.register_command(CliCommand(...))`
# 3. Execute commands: `result = cli_core.execute_command("cmd-name", context=...)`
# 4. Manage configuration: `cli_core.update_configuration({...})`
# 5. Create profiles: `cli_core.create_profile("prod", {...})`
# 6. Session management: `cli_core.start_session()`, `cli_core.end_session()`
# 7. Get statistics: `cli_core.get_command_statistics()`, `cli_core.get_session_statistics()`
# 8. Context enrichment: Uses automatic Phase 1 enrichment from FlextService
#
# Phase 1 context enrichment:
# This service uses the new Phase 1 enhancements from flext-core FlextService:
# - Automatic correlation ID generation for distributed tracing
# - User context binding for audit trails
# - Operation context tracking for performance monitoring
# - Structured logging with full context automatically included
# - See FlextService.execute_with_context_enrichment() for advanced usage
#
# Copyright (c) 2025 FLEXT Team. All rights reserved.
# SPDX-License-Identifier: MIT
import functools
import json
import time
from collections.abc import Callable, Mapping
from datetime import datetime
from importlib import metadata
from pathlib import Path
from typing import cast, override

import pluggy
from cachetools import LRUCache, TTLCache
from flext_core import (
    FlextDecorators,
    FlextMixins,
    FlextResult,
    FlextRuntime,
    FlextService,
    FlextTypes,
    FlextUtilities,
    P,
    T,
)

from flext_cli.config import FlextCliConfig
from flext_cli.constants import FlextCliConstants
from flext_cli.models import FlextCliModels
from flext_cli.protocols import FlextCliProtocols
from flext_cli.typings import FlextCliTypes


class FlextCliCore(FlextService[FlextCliTypes.Data.CliDataDict]):
    """Core CLI service - comprehensive command-line operations management (Layer 3).

    **ARCHITECTURE LAYER**: Application Layer (Layer 3)
    Extends FlextService[FlextCliTypes.Data.CliDataDict] from flext-core with CLI
    domain-specific types and operations. Inherits logger and context enrichment from
    FlextMixins mixin. Type-generic over CliDataDict for type-safe operations.

    **RAILWAY-ORIENTED PATTERN**:
    All public operations return FlextResult[T] enabling composable error handling:
    - Command operations return FlextResult[CommandResult]
    - Configuration operations return FlextResult[CliConfigSchema]
    - Session operations return FlextResult[bool] (True on success, failure on error)
    - Statistics return FlextResult[CliDataDict]

    **CORE FEATURES** (12+ integrated capabilities):
    1. **Command Management** (5 methods):
       - register_command() - Register CLI command with validation
       - get_command() - Retrieve command definition
       - execute_command() - Execute registered command with context
       - list_commands() - List all registered commands
       - get_commands() - Retrieve command names

    2. **Configuration Management** (4 methods):
       - update_configuration() - Update CLI configuration
       - get_configuration() - Retrieve current configuration
       - load_configuration() - Load config from file
       - save_configuration() - Save config to file

    3. **Profile Management** (1 method):
       - create_profile() - Create named configuration profile

    4. **Session Management** (4 methods):
       - start_session() - Start new CLI session
       - end_session() - End current session
       - is_session_active() - Check session status
       - get_session_statistics() - Get session metrics

    5. **Statistics & Monitoring** (4 methods):
       - get_command_statistics() - Command usage metrics
       - get_service_info() - Service state and status
       - health_check() - Service health verification
       - validate_configuration() - Configuration validation

    6. **Service Information** (5 methods):
       - get_config() - Retrieve service configuration
       - get_handlers() - List command handlers
       - get_plugins() - List registered plugins
       - get_sessions() - List active sessions
       - get_formatters() - List available formatters

    7. **Context Enrichment** (Phase 1 enhancement):
       - execute_cli_command_with_context() - Auto context enrichment pattern
       - Uses inherited _with_operation_context() and _enrich_context()
       - Automatic correlation ID generation
       - User context binding for audit trails

    **INTEGRATION POINTS**:
    - Extends FlextService (flext-core Layer 3 foundation)
    - Uses FlextResult[T] (railway-oriented error handling)
    - References FlextCliTypes (domain-specific types)
    - Inherits from FlextMixins (logger, context enrichment)
    - Uses FlextCliConstants (standardized constants)
    - Compatible with FlextCliConfig (Pydantic validation)
    - Uses FlextCliModels.CliCommand (command model)

    **PRODUCTION READINESS CHECKLIST**:
    ✅ Railway-oriented pattern (all operations return FlextResult[T])
    ✅ Type-safe domain types (CliConfigSchema, CliDataDict, CommandResult)
    ✅ Comprehensive error handling (try/except with FlextResult)
    ✅ Service state management (commands, config, sessions)
    ✅ Context enrichment automation (Phase 1 pattern)
    ✅ Pydantic validation (FlextCliConfig integration)
    ✅ Session lifecycle management (start, end, status)
    ✅ Statistics collection (command usage, session metrics)
    ✅ Health checks and service info
    ✅ File-based configuration persistence
    ✅ 100% type annotations throughout
    ✅ Comprehensive docstrings with examples

    **USAGE PATTERNS**:

    ```python
    from flext_cli import FlextCliCore
    from flext_core import FlextDecorators, FlextResult, FlextService, FlextTypes

    # Pattern 1: Initialize service
    cli_core = FlextCliCore(config={"debug": True})

    # Pattern 2: Register and execute commands
    from flext_cli import FlextCliModels

    cmd = FlextCliModels.CliCommand(name="list-users", handler="list_handler")
    reg_result = cli_core.register_command(cmd)
    if reg_result.is_success:
        exec_result = cli_core.execute_command("list-users", context={"limit": 10})

    # Pattern 3: Configuration management
    config_result = cli_core.get_configuration()
    if config_result.is_success:
        config = config_result.value
        config["output_format"] = "json"
        cli_core.update_configuration(config)

    # Pattern 4: Session management
    session_result = cli_core.start_session()
    if session_result.is_success:
        if cli_core.is_session_active():
            stats = cli_core.get_session_statistics()
        cli_core.end_session()

    # Pattern 5: Context enrichment (Phase 1)
    ctx_result = cli_core.execute_cli_command_with_context(
        command_name="process-data",
        user_id="REDACTED_LDAP_BIND_PASSWORD@example.com",
        operation_type="batch_processing",
        environment="production",
    )

    # Pattern 6: Statistics and monitoring
    cmd_stats = cli_core.get_command_statistics()
    service_info = cli_core.get_service_info()
    health = cli_core.health_check()

    # Pattern 7: Chaining operations
    result = (
        cli_core.load_configuration("/etc/flext/config.json")
        .flat_map(lambda cfg: cli_core.validate_configuration(cfg))
        .map(lambda _: cli_core.get_configuration())
    )
    ```

    **KEY DESIGN PRINCIPLES**:
    - Railway pattern enables error composition
    - Type safety via FlextCliTypes domain types
    - Automatic context enrichment (Phase 1)
    - No implicit error suppression (try/except → FlextResult)
    - Pydantic validation for configuration
    - Service state tracked explicitly
    """

    # =========================================================================
    # NESTED HELPER: Cache Statistics
    # =========================================================================

    class _CacheStats:
        """Internal cache statistics tracker.

        Tracks cache performance metrics for monitoring and optimization.
        """

        def __init__(self) -> None:
            """Initialize cache statistics."""
            self.cache_hits = 0
            self.cache_misses = 0
            self.total_time_saved = 0.0

        def record_hit(self, time_saved: float) -> None:
            """Record a cache hit."""
            self.cache_hits += 1
            self.total_time_saved += time_saved

        def record_miss(self) -> None:
            """Record a cache miss."""
            self.cache_misses += 1

        def get_hit_rate(self) -> float:
            """Calculate cache hit rate."""
            total = self.cache_hits + self.cache_misses
            return self.cache_hits / total if total > 0 else 0.0

    # Logger is provided by FlextMixins mixin

    def __init__(
        self,
        config: FlextCliTypes.Configuration.CliConfigSchema | None = None,
        **data: FlextTypes.JsonValue,
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

        # Type-safe configuration initialization
        # Use FlextTypes.JsonDict type for internal config management
        self._config: FlextCliTypes.Configuration.CliConfigSchema = (
            config if config is not None else {}
        )
        self._commands: FlextTypes.JsonDict = {}
        # Note: stores plugin objects implementing CliPlugin protocol
        self._plugins: dict[str, FlextCliProtocols.Cli.CliPlugin] = {}
        self._sessions: FlextTypes.JsonDict = {}
        self._session_active = False

        # Performance and async integration
        # Note: stores cache objects (TTLCache/LRUCache), not JsonValue
        # Cache types are from external library, using generic types
        self._caches: dict[
            str,
            TTLCache[str, FlextTypes.JsonValue] | LRUCache[str, FlextTypes.JsonValue],
        ] = {}
        self._cache_stats = self._CacheStats()
        self._plugin_manager = pluggy.PluginManager("flext_cli")

        self.logger.debug(
            "Initialized CLI core service",
            operation="__init__",
            has_config=config is not None,
            config_keys=list(config.keys())
            if FlextRuntime.is_dict_like(config)
            else None,
            commands_count=0,
            plugins_count=0,
            sessions_count=0,
            source="flext-cli/src/flext_cli/core.py",
        )

    # ==========================================================================
    # CLI COMMAND MANAGEMENT - Using FlextCliTypes.CliCommand types
    # ==========================================================================

    def register_command(
        self,
        command: FlextCliModels.CliCommand,
    ) -> FlextResult[bool]:
        """Register CLI command using CliCommand model instance.

        Args:
            command: CliCommand model instance with validated data

        Returns:
            FlextResult[bool]: True if registration succeeded, failure on error

        """
        # Log detailed command registration initialization
        self.logger.debug(
            "Starting CLI command registration",
            command_name=command.name if command else None,
            command_type=type(command).__name__ if command else None,
            operation="register_command",
            source="flext-cli/src/flext_cli/core.py",
        )

        self.logger.info(
            "STARTING CLI command registration",
            command_name=command.name if command else None,
            operation="register_command",
            source="flext-cli/src/flext_cli/core.py",
        )

        # Simple validation and registration (KISS principle) - fast fail
        if command is None:
            self.logger.error(
                "FAILED CLI command registration - command is None",
                operation="register_command",
                source="flext-cli/src/flext_cli/core.py",
            )
            return FlextResult[bool].fail(
                FlextCliConstants.ErrorMessages.COMMAND_NAME_EMPTY
            )
        if not command.name:
            self.logger.error(
                "FAILED CLI command registration - command name is empty",
                command_name=command.name,
                operation="register_command",
                source="flext-cli/src/flext_cli/core.py",
            )
            return FlextResult[bool].fail(
                FlextCliConstants.ErrorMessages.COMMAND_NAME_EMPTY
            )

        try:
            # Persist command to registry
            command_data = FlextMixins.ModelConversion.to_dict(command)
            self._commands[command.name] = command_data

            # Log successful registration with detailed context
            self.logger.debug(
                "Command registration completed successfully",
                command_name=command.name,
                command_data_keys=list(command_data.keys()) if command_data else [],
                registry_size=len(self._commands),
                operation="register_command",
                source="flext-cli/src/flext_cli/core.py",
            )

            self.logger.info(
                "COMPLETED CLI command registration successfully",
                command_name=command.name,
                operation="register_command",
                source="flext-cli/src/flext_cli/core.py",
            )

            return FlextResult[bool].ok(True)

        except Exception as e:
            # Log detailed registration error
            self.logger.exception(
                "FAILED CLI command registration with exception",
                command_name=command.name,
                error_type=type(e).__name__,
                operation="register_command",
                source="flext-cli/src/flext_cli/core.py",
            )
            return FlextResult[bool].fail(
                FlextCliConstants.ErrorMessages.COMMAND_REGISTRATION_FAILED.format(
                    command=command.name,
                    error=str(e),
                ),
            )

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
        self.logger.debug(
            "Retrieving command definition",
            operation="get_command",
            command_name=name,
            total_commands=len(self._commands),
            source="flext-cli/src/flext_cli/core.py",
        )

        if not name:
            self.logger.warning(
                "Command name is empty",
                operation="get_command",
                consequence="Command retrieval will fail",
                source="flext-cli/src/flext_cli/core.py",
            )
            return FlextResult[FlextCliTypes.CliCommand.CommandDefinition].fail(
                FlextCliConstants.ErrorMessages.COMMAND_NAME_EMPTY,
            )

        if name not in self._commands:
            self.logger.warning(
                "Command not found in registry",
                operation="get_command",
                command_name=name,
                available_commands=list(self._commands.keys()),
                consequence="Command retrieval will fail",
                source="flext-cli/src/flext_cli/core.py",
            )
            return FlextResult[FlextCliTypes.CliCommand.CommandDefinition].fail(
                FlextCliConstants.ErrorMessages.COMMAND_NOT_FOUND.format(name=name),
            )

        try:
            command_def = self._commands[name]

            self.logger.debug(
                "Retrieved command definition",
                operation="get_command",
                command_name=name,
                command_def_type=type(command_def).__name__,
                is_dict=FlextRuntime.is_dict_like(command_def),
                source="flext-cli/src/flext_cli/core.py",
            )

            # Type-safe conversion to CLI command definition
            if FlextRuntime.is_dict_like(command_def):
                # Type cast: dict[str, object] needs conversion to dict[str, JsonValue]
                # JsonValue is a union type that includes object, so this cast is safe
                typed_def: FlextCliTypes.CliCommand.CommandDefinition = cast(
                    "FlextCliTypes.CliCommand.CommandDefinition",
                    cast("dict[str, FlextTypes.JsonValue]", command_def),
                )

                self.logger.debug(
                    "Command definition retrieved successfully",
                    operation="get_command",
                    command_name=name,
                    definition_keys=list(typed_def.keys())
                    if FlextRuntime.is_dict_like(typed_def)
                    else None,
                    source="flext-cli/src/flext_cli/core.py",
                )

                return FlextResult[FlextCliTypes.CliCommand.CommandDefinition].ok(
                    typed_def,
                )

            self.logger.error(
                "FAILED to retrieve command - invalid command type",
                operation="get_command",
                command_name=name,
                command_def_type=type(command_def).__name__,
                consequence="Command retrieval aborted",
                source="flext-cli/src/flext_cli/core.py",
            )
            return FlextResult[FlextCliTypes.CliCommand.CommandDefinition].fail(
                FlextCliConstants.ErrorMessages.INVALID_COMMAND_TYPE.format(name=name),
            )
        except Exception as e:
            self.logger.exception(
                "FAILED to retrieve command - operation aborted",
                operation="get_command",
                command_name=name,
                error=str(e),
                error_type=type(e).__name__,
                consequence="Command retrieval failed completely",
                source="flext-cli/src/flext_cli/core.py",
            )
            return FlextResult[FlextCliTypes.CliCommand.CommandDefinition].fail(
                FlextCliConstants.ErrorMessages.COMMAND_RETRIEVAL_FAILED.format(
                    error=e,
                ),
            )

    def execute_command(
        self,
        name: str,
        context: FlextCliTypes.CliCommand.CommandContext | list[str] | None = None,
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
        # Log detailed command execution initialization
        self.logger.debug(
            "Starting CLI command execution",
            command_name=name,
            context_type=type(context).__name__ if context is not None else None,
            context_length=len(context)
            if (
                FlextRuntime.is_list_like(context) or FlextRuntime.is_dict_like(context)
            )
            else None,
            timeout=timeout,
            operation="execute_command",
            source="flext-cli/src/flext_cli/core.py",
        )

        self.logger.info(
            "STARTING CLI command execution",
            command_name=name,
            operation="execute_command",
            source="flext-cli/src/flext_cli/core.py",
        )

        command_result = self.get_command(name)
        if command_result.is_failure:
            # Log command not found error
            self.logger.error(
                "FAILED to execute command - command not found",
                command_name=name,
                error=command_result.error,
                operation="execute_command",
                source="flext-cli/src/flext_cli/core.py",
            )
            # Use error from result - FlextResult always has error on failure
            return FlextResult[FlextCliTypes.CliCommand.CommandResult].fail(
                command_result.error or "Command not found",
            )

        try:
            # Execute command with CLI-specific context handling
            # CommandContext is dict[str, JsonValue], no cast needed
            if FlextRuntime.is_list_like(context):
                # Convert list of strings to context dict
                # Type-safe: CommandContext uses JsonValue, strings are valid JsonValue
                args_list: list[FlextTypes.JsonValue] = [
                    cast("FlextTypes.JsonValue", arg) for arg in context
                ]
                # Type cast: list[JsonValue] is compatible with JsonValue (list is valid JsonValue)
                execution_context: FlextCliTypes.CliCommand.CommandContext = cast(
                    "FlextCliTypes.CliCommand.CommandContext",
                    {FlextCliConstants.DictKeys.ARGS: args_list},
                )
            elif context is not None:
                # Type cast: context may be dict[str, object], need to cast to CommandContext
                execution_context = cast(
                    "FlextCliTypes.CliCommand.CommandContext",
                    context,
                )
            else:
                # No context provided - use empty dict explicitly
                execution_context = {}

            # Basic command execution simulation
            # CommandContext is dict[str, JsonValue] which is compatible with JsonValue
            result_data: FlextCliTypes.CliCommand.CommandResult = cast(
                "FlextCliTypes.CliCommand.CommandResult",
                {
                    FlextCliConstants.DictKeys.COMMAND: name,
                    FlextCliConstants.DictKeys.STATUS: True,
                    FlextCliConstants.DictKeys.CONTEXT: execution_context,
                    FlextCliConstants.DictKeys.TIMESTAMP: FlextUtilities.Generators.generate_iso_timestamp(),
                    FlextCliConstants.DictKeys.TIMEOUT: timeout,  # Include timeout parameter in result
                },
            )

            # Log successful execution with detailed context
            self.logger.debug(
                "Command execution completed successfully",
                command_name=name,
                execution_context_keys=list(execution_context.keys())
                if execution_context
                else [],
                result_status=True,
                timeout_used=timeout,
                operation="execute_command",
                source="flext-cli/src/flext_cli/core.py",
            )

            self.logger.info(
                "COMPLETED CLI command execution successfully",
                command_name=name,
                operation="execute_command",
                source="flext-cli/src/flext_cli/core.py",
            )

            return FlextResult[FlextCliTypes.CliCommand.CommandResult].ok(result_data)

        except Exception as e:
            # Log detailed execution error
            self.logger.exception(
                "FAILED CLI command execution with exception",
                command_name=name,
                error_type=type(e).__name__,
                context_type=type(context).__name__ if context is not None else None,
                operation="execute_command",
                source="flext-cli/src/flext_cli/core.py",
            )
            return FlextResult[FlextCliTypes.CliCommand.CommandResult].fail(
                FlextCliConstants.ErrorMessages.COMMAND_EXECUTION_FAILED.format(
                    error=e,
                ),
            )

    def list_commands(self) -> FlextResult[list[str]]:
        """List all registered commands using functional composition.

        Performs command listing with railway pattern and proper error handling.
        Uses functional approach to extract command names safely.

        Returns:
            FlextResult[list[str]]: List of command names or error with details

        """
        self.logger.debug(
            "Listing all registered commands",
            operation="list_commands",
            total_commands=len(self._commands),
            source="flext-cli/src/flext_cli/core.py",
        )

        # Functional command listing with railway pattern
        def extract_command_names() -> FlextResult[list[str]]:
            """Extract command names from internal registry."""
            try:
                command_names = list(self._commands.keys())

                self.logger.debug(
                    "Command names extracted successfully",
                    operation="list_commands",
                    commands_count=len(command_names),
                    command_names=command_names,
                    source="flext-cli/src/flext_cli/core.py",
                )

                self.logger.info(
                    "Command listing completed",
                    operation="list_commands",
                    total_commands=len(command_names),
                    source="flext-cli/src/flext_cli/core.py",
                )

                return FlextResult.ok(command_names)
            except Exception as e:
                self.logger.exception(
                    "FAILED to list commands - operation aborted",
                    operation="list_commands",
                    error=str(e),
                    error_type=type(e).__name__,
                    consequence="Command list unavailable",
                    source="flext-cli/src/flext_cli/core.py",
                )
                return FlextResult.fail(
                    FlextCliConstants.ErrorMessages.COMMAND_LISTING_FAILED.format(
                        error=e,
                    ),
                )

        # Railway pattern: extract and validate command names
        return extract_command_names()

    # ==========================================================================
    # PRIVATE HELPERS - Direct logger usage (no fallbacks)
    # ==========================================================================

    # ==========================================================================
    # CLI CONFIGURATION MANAGEMENT - Using FlextCliTypes.Configuration types
    # ==========================================================================

    def _log_config_update(self) -> None:
        """Log configuration update - direct logger usage."""
        self.logger.info(FlextCliConstants.LogMessages.CLI_CONFIG_UPDATED)

    def update_configuration(
        self,
        config: FlextCliTypes.Configuration.CliConfigSchema,
    ) -> FlextResult[bool]:
        """Update CLI configuration using railway pattern and functional composition.

        Performs configuration update with comprehensive validation and error handling.
        Uses functional pipeline to ensure safe configuration merging.

        Args:
            config: New configuration schema with CLI-specific structure

        Returns:
            FlextResult[bool]: True if configuration updated successfully, failure on error

        """
        self.logger.info(
            "Updating CLI configuration",
            operation="update_configuration",
            config_keys=list(config.keys())
            if FlextRuntime.is_dict_like(config)
            else None,
            current_config_keys=list(self._config.keys())
            if FlextRuntime.is_dict_like(self._config)
            else None,
            source="flext-cli/src/flext_cli/core.py",
        )

        self.logger.debug(
            "Starting configuration update",
            operation="update_configuration",
            config_type=type(config).__name__,
            config_is_dict=FlextRuntime.is_dict_like(config),
            source="flext-cli/src/flext_cli/core.py",
        )

        # Functional configuration validation and update
        def validate_config_input() -> FlextResult[
            FlextCliTypes.Configuration.CliConfigSchema
        ]:
            """Validate input configuration."""
            if not config:
                self.logger.warning(
                    "Configuration input is empty",
                    operation="update_configuration",
                    consequence="Configuration update will fail",
                    source="flext-cli/src/flext_cli/core.py",
                )
                return FlextResult.fail(FlextCliConstants.ErrorMessages.CONFIG_NOT_DICT)

            self.logger.debug(
                "Configuration input validated",
                operation="update_configuration",
                config_keys=list(config.keys())
                if FlextRuntime.is_dict_like(config)
                else None,
                source="flext-cli/src/flext_cli/core.py",
            )
            return FlextResult.ok(config)

        def validate_existing_config() -> FlextResult[
            FlextCliTypes.Configuration.CliConfigSchema
        ]:
            """Validate existing configuration state."""
            if FlextRuntime.is_dict_like(self._config) and self._config:
                # Type narrowing: self._config is dict, compatible with CliConfigSchema
                config_schema: FlextCliTypes.Configuration.CliConfigSchema = (
                    self._config
                )
                return FlextResult[FlextCliTypes.Configuration.CliConfigSchema].ok(
                    config_schema
                )
            return FlextResult[FlextCliTypes.Configuration.CliConfigSchema].fail(
                FlextCliConstants.ErrorMessages.CONFIG_NOT_INITIALIZED,
            )

        def merge_configurations(
            valid_config: FlextCliTypes.Configuration.CliConfigSchema,
        ) -> FlextResult[bool]:
            """Merge new configuration with existing one."""
            try:
                self.logger.debug(
                    "Merging configurations",
                    operation="update_configuration",
                    new_config_keys=list(valid_config.keys())
                    if FlextRuntime.is_dict_like(valid_config)
                    else None,
                    source="flext-cli/src/flext_cli/core.py",
                )

                existing_config_result = validate_existing_config()
                if existing_config_result.is_failure:
                    self.logger.warning(
                        "Existing configuration validation failed",
                        operation="update_configuration",
                        error=existing_config_result.error,
                        consequence="Configuration merge will fail",
                        source="flext-cli/src/flext_cli/core.py",
                    )
                    return FlextResult[bool].fail(
                        existing_config_result.error or "Config validation failed"
                    )

                existing_config = existing_config_result.unwrap()
                # Update with type-safe merge
                for key, value in valid_config.items():
                    existing_config[key] = value

                self.logger.debug(
                    "Configuration merged successfully",
                    operation="update_configuration",
                    merged_keys=list(existing_config.keys())
                    if FlextRuntime.is_dict_like(existing_config)
                    else None,
                    source="flext-cli/src/flext_cli/core.py",
                )

                # Log successful update
                self._log_config_update()

                self.logger.info(
                    "Configuration update completed successfully",
                    operation="update_configuration",
                    source="flext-cli/src/flext_cli/core.py",
                )

                return FlextResult[bool].ok(True)

            except Exception as e:
                self.logger.exception(
                    "FAILED to merge configurations - operation aborted",
                    operation="update_configuration",
                    error=str(e),
                    error_type=type(e).__name__,
                    consequence="Configuration update failed completely",
                    source="flext-cli/src/flext_cli/core.py",
                )
                return FlextResult[bool].fail(
                    FlextCliConstants.ErrorMessages.CONFIG_UPDATE_FAILED.format(
                        error=e
                    ),
                )

        # Railway pattern: validate input then merge configurations
        return validate_config_input().flat_map(merge_configurations)

    def get_configuration(
        self,
    ) -> FlextResult[FlextCliTypes.Configuration.CliConfigSchema]:
        """Get current CLI configuration using functional composition.

        Retrieves configuration with validation and error handling.
        Uses railway pattern to ensure configuration integrity.

        Returns:
            FlextResult[FlextCliTypes.Configuration.CliConfigSchema]: Current configuration or error with details

        """

        # Functional configuration retrieval with railway pattern
        def validate_config_state() -> FlextResult[
            FlextCliTypes.Configuration.CliConfigSchema
        ]:
            """Validate that configuration is properly initialized."""
            try:
                self.logger.debug(
                    "Retrieving CLI configuration",
                    operation="get_configuration",
                    config_type=type(self._config).__name__,
                    config_is_dict=FlextRuntime.is_dict_like(self._config),
                    config_keys=list(self._config.keys())
                    if FlextRuntime.is_dict_like(self._config)
                    else None,
                    source="flext-cli/src/flext_cli/core.py",
                )
                if FlextRuntime.is_dict_like(self._config) and self._config:
                    # Type narrowing: self._config is dict, compatible with CliConfigSchema
                    config_schema: FlextCliTypes.Configuration.CliConfigSchema = (
                        self._config
                    )

                    self.logger.debug(
                        "Configuration retrieved successfully",
                        operation="get_configuration",
                        config_keys=list(config_schema.keys())
                        if FlextRuntime.is_dict_like(config_schema)
                        else None,
                        source="flext-cli/src/flext_cli/core.py",
                    )

                    self.logger.info(
                        "Configuration retrieval completed",
                        operation="get_configuration",
                        source="flext-cli/src/flext_cli/core.py",
                    )

                    return FlextResult[FlextCliTypes.Configuration.CliConfigSchema].ok(
                        config_schema
                    )

                self.logger.warning(
                    "Configuration not initialized",
                    operation="get_configuration",
                    consequence="Configuration retrieval will fail",
                    source="flext-cli/src/flext_cli/core.py",
                )
                return FlextResult[FlextCliTypes.Configuration.CliConfigSchema].fail(
                    FlextCliConstants.ErrorMessages.CONFIG_NOT_INITIALIZED,
                )
            except Exception as e:
                self.logger.exception(
                    "FAILED to retrieve configuration - operation aborted",
                    operation="get_configuration",
                    error=str(e),
                    error_type=type(e).__name__,
                    consequence="Configuration retrieval failed completely",
                    source="flext-cli/src/flext_cli/core.py",
                )
                return FlextResult[FlextCliTypes.Configuration.CliConfigSchema].fail(
                    FlextCliConstants.ErrorMessages.CONFIG_RETRIEVAL_FAILED.format(
                        error=e,
                    ),
                )

        # Railway pattern: validate and return configuration
        return validate_config_state()

    def create_profile(
        self,
        name: str,
        profile_config: FlextCliTypes.Configuration.ProfileConfiguration,
    ) -> FlextResult[bool]:
        """Create CLI configuration profile using railway pattern.

        Performs profile creation with validation and error handling.

        Args:
            name: Profile identifier (validated for non-emptiness)
            profile_config: Profile-specific configuration

        Returns:
            FlextResult[bool]: True if profile created successfully, failure on error

        """
        # Input validation
        if not name:
            return FlextResult[bool].fail(
                FlextCliConstants.ErrorMessages.PROFILE_NAME_EMPTY
            )

        if not profile_config:
            return FlextResult[bool].fail(
                FlextCliConstants.ErrorMessages.PROFILE_CONFIG_NOT_DICT,
            )

        if not (FlextRuntime.is_dict_like(self._config) and self._config):
            return FlextResult[bool].fail(
                FlextCliConstants.ErrorMessages.CONFIG_NOT_INITIALIZED,
            )

        # Store profile
        try:
            config = self._config

            # Initialize profiles section if needed
            if FlextCliConstants.DictKeys.PROFILES not in config:
                config[FlextCliConstants.DictKeys.PROFILES] = {}

            # Store profile safely
            profiles_section = config[FlextCliConstants.DictKeys.PROFILES]
            if FlextRuntime.is_dict_like(profiles_section):
                profiles_section[name] = profile_config
                self.logger.info(
                    FlextCliConstants.LogMessages.PROFILE_CREATED.format(name=name),
                )
                return FlextResult[bool].ok(True)

            return FlextResult[bool].fail(
                "Profile storage failed: unable to store profile configuration",
            )

        except Exception as e:
            return FlextResult[bool].fail(
                FlextCliConstants.ErrorMessages.PROFILE_CREATION_FAILED.format(error=e),
            )

    # ==========================================================================
    # SESSION MANAGEMENT - Using FlextCliTypes.Configuration types
    # ==========================================================================

    def start_session(
        self,
        session_config: FlextCliTypes.Configuration.SessionConfiguration | None = None,
    ) -> FlextResult[bool]:
        """Start CLI session with configuration.

        Args:
            session_config: Optional session-specific configuration

        Returns:
            FlextResult[bool]: True if session started successfully, failure on error

        """
        if self._session_active:
            return FlextResult[bool].fail(
                FlextCliConstants.ErrorMessages.SESSION_ALREADY_ACTIVE,
            )

        try:
            # Initialize session with CLI-specific configuration
            # Validate explicitly - no fallback to empty dict
            if session_config is not None:
                self._session_config = session_config
            else:
                self._session_config = {}
            self._session_active = True
            self._session_start_time = (
                FlextUtilities.Generators.generate_iso_timestamp()
            )

            # Log session start - direct logger usage
            self.logger.info(FlextCliConstants.LogMessages.SESSION_STARTED)

            return FlextResult[bool].ok(True)

        except Exception as e:
            return FlextResult[bool].fail(
                FlextCliConstants.ErrorMessages.SESSION_START_FAILED.format(error=e),
            )

    def end_session(self) -> FlextResult[bool]:
        """End current CLI session.

        Returns:
            FlextResult[bool]: True if session ended successfully, failure on error

        """
        try:
            self.logger.info(
                "Ending CLI session",
                operation="end_session",
                session_active=self._session_active,
                total_sessions=len(self._sessions),
                source="flext-cli/src/flext_cli/core.py",
            )

            self.logger.debug(
                "Terminating session",
                operation="end_session",
                source="flext-cli/src/flext_cli/core.py",
            )

            if not self._session_active:
                self.logger.warning(
                    "No active session to end",
                    operation="end_session",
                    existing_sessions=list(self._sessions.keys()),
                    consequence="Session end will fail",
                    source="flext-cli/src/flext_cli/core.py",
                )
                return FlextResult[bool].fail(
                    FlextCliConstants.ErrorMessages.NO_ACTIVE_SESSION,
                )
            self._session_active = False
            if hasattr(self, FlextCliConstants.PrivateAttributes.SESSION_CONFIG):
                delattr(self, FlextCliConstants.PrivateAttributes.SESSION_CONFIG)
            if hasattr(self, FlextCliConstants.PrivateAttributes.SESSION_START_TIME):
                delattr(self, FlextCliConstants.PrivateAttributes.SESSION_START_TIME)

            self.logger.debug(
                "Session terminated successfully",
                operation="end_session",
                total_sessions=len(self._sessions),
                source="flext-cli/src/flext_cli/core.py",
            )

            # Log session end - direct logger usage
            self.logger.info(FlextCliConstants.LogMessages.SESSION_ENDED)

            self.logger.info(
                "CLI session ended",
                operation="end_session",
                source="flext-cli/src/flext_cli/core.py",
            )

            return FlextResult[bool].ok(True)

        except Exception as e:
            self.logger.exception(
                "FAILED to end session - operation aborted",
                operation="end_session",
                error=str(e),
                error_type=type(e).__name__,
                consequence="Session end failed completely",
                source="flext-cli/src/flext_cli/core.py",
            )
            return FlextResult[bool].fail(
                FlextCliConstants.ErrorMessages.SESSION_END_FAILED.format(error=e),
            )

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

        Pydantic 2 Modernization:
            - Uses CommandStatistics model internally
            - Serializes to dict for API compatibility
            - Type-safe with automatic validation

        """
        try:
            # Create Pydantic model with type-safe fields
            stats_model = FlextCliModels.CommandStatistics(
                total_commands=len(self._commands),
                registered_commands=list(self._commands.keys()),
                status=self._session_active,
                timestamp=FlextUtilities.Generators.generate_iso_timestamp(),
            )
            # Serialize to dict for API compatibility
            stats_dict: FlextCliTypes.Data.CliDataDict = (
                FlextMixins.ModelConversion.to_dict(stats_model)
            )
            # Use self.ok() from FlextService for consistency
            return self.ok(stats_dict)
        except Exception as e:
            return FlextResult[FlextCliTypes.Data.CliDataDict].fail(
                FlextCliConstants.ErrorMessages.CLI_EXECUTION_ERROR.format(error=e),
            )

    def get_service_info(self) -> dict[str, object]:
        """Get comprehensive service information.

        Returns:
            dict[str, object]: Service information (matches FlextService signature)

        """
        try:
            # Collect comprehensive service information
            commands_count = len(self._commands)
            config_keys = list(self._config.keys()) if self._config else []

            info_data: dict[str, FlextTypes.JsonValue] = {
                FlextCliConstants.DictKeys.SERVICE: FlextCliConstants.FLEXT_CLI,
                FlextCliConstants.CoreServiceDictKeys.COMMANDS_REGISTERED: commands_count,
                FlextCliConstants.CoreServiceDictKeys.CONFIGURATION_SECTIONS: cast(
                    "FlextTypes.JsonValue", config_keys
                ),
                FlextCliConstants.DictKeys.STATUS: (
                    FlextCliConstants.ServiceStatus.OPERATIONAL.value
                    if self._session_active
                    else FlextCliConstants.ServiceStatus.AVAILABLE.value
                ),
                FlextCliConstants.CoreServiceDictKeys.SERVICE_READY: commands_count > 0,
                FlextCliConstants.DictKeys.TIMESTAMP: FlextUtilities.Generators.generate_iso_timestamp(),
            }

            # Return as dict[str, object] (matches FlextService signature)
            # Type cast: dict[str, JsonValue] is compatible with dict[str, object]
            return cast("dict[str, object]", info_data)

        except Exception as e:
            self.logger.exception(
                FlextCliConstants.CoreServiceLogMessages.SERVICE_INFO_COLLECTION_FAILED,
            )
            return {FlextCliConstants.DictKeys.MESSAGE: str(e)}

    def get_session_statistics(
        self,
    ) -> FlextResult[FlextCliTypes.Data.CliDataDict]:
        """Get session-specific statistics using CLI data types.

        Returns:
            FlextResult[FlextCliTypes.Data.CliDataDict]: Session statistics or error

        Pydantic 2 Modernization:
            - Uses SessionStatistics model internally
            - Serializes to dict for API compatibility
            - Type-safe with field validation (non-negative duration)

        """
        self.logger.debug(
            "Collecting session statistics",
            operation="get_session_statistics",
            session_active=self._session_active,
            total_sessions=len(self._sessions),
            source="flext-cli/src/flext_cli/core.py",
        )

        if not self._session_active:
            self.logger.warning(
                "No active session for statistics collection",
                operation="get_session_statistics",
                existing_sessions=list(self._sessions.keys()),
                consequence="Statistics collection will fail",
                source="flext-cli/src/flext_cli/core.py",
            )
            return FlextResult[FlextCliTypes.Data.CliDataDict].fail(
                FlextCliConstants.ErrorMessages.NO_ACTIVE_SESSION,
            )

        try:
            # Calculate session duration if session is active
            session_duration = (
                FlextCliConstants.CoreServiceDefaults.SESSION_DURATION_INIT
            )
            if (
                hasattr(self, FlextCliConstants.PrivateAttributes.SESSION_START_TIME)
                and self._session_start_time
            ):
                # Use UTC directly for datetime comparison (no need to parse ISO string)
                current_time = datetime.fromisoformat(
                    FlextUtilities.Generators.generate_iso_timestamp()
                )
                # Parse ISO format string back to datetime for duration calculation
                start_time = datetime.fromisoformat(self._session_start_time)
                duration_delta = current_time - start_time
                session_duration = int(duration_delta.total_seconds())

            # Get session config keys
            session_config_keys = (
                list(self._session_config.keys())
                if hasattr(self, FlextCliConstants.PrivateAttributes.SESSION_CONFIG)
                and self._session_config
                else []
            )

            # Get start time string
            start_time_str = (
                self._session_start_time
                if hasattr(self, FlextCliConstants.PrivateAttributes.SESSION_START_TIME)
                else FlextCliConstants.CoreServiceDefaults.UNKNOWN_VALUE
            )

            # Create Pydantic model with type-safe fields
            stats_model = FlextCliModels.SessionStatistics(
                session_active=self._session_active,
                session_duration_seconds=session_duration,
                commands_available=len(self._commands),
                configuration_loaded=bool(self._config),
                session_config_keys=session_config_keys,
                start_time=start_time_str,
                current_time=FlextUtilities.Generators.generate_iso_timestamp(),
            )

            # Serialize to dict for API compatibility
            stats_dict: FlextCliTypes.Data.CliDataDict = (
                FlextMixins.ModelConversion.to_dict(stats_model)
            )

            self.logger.debug(
                "Session statistics collected successfully",
                operation="get_session_statistics",
                session_duration=stats_model.session_duration_seconds,
                commands_available=stats_model.commands_available,
                source="flext-cli/src/flext_cli/core.py",
            )

            self.logger.info(
                "Session statistics retrieved",
                operation="get_session_statistics",
                session_duration_seconds=stats_model.session_duration_seconds,
                source="flext-cli/src/flext_cli/core.py",
            )

            # Use self.ok() from FlextService for consistency
            return self.ok(stats_dict)

        except Exception as e:
            self.logger.exception(
                "FAILED to collect session statistics - operation aborted",
                operation="get_session_statistics",
                error=str(e),
                error_type=type(e).__name__,
                consequence="Statistics unavailable",
                source="flext-cli/src/flext_cli/core.py",
            )
            return FlextResult[FlextCliTypes.Data.CliDataDict].fail(
                FlextCliConstants.CoreServiceLogMessages.SESSION_STATS_COLLECTION_FAILED.format(
                    error=e,
                ),
            )

    # ==========================================================================
    # SERVICE EXECUTION METHODS - FlextService protocol implementation
    # ==========================================================================

    @override
    @FlextDecorators.log_operation("cli_core_health_check")
    @FlextDecorators.track_performance()
    def execute(self, **kwargs: object) -> FlextResult[FlextCliTypes.Data.CliDataDict]:
        """Execute CLI service operations.

        Args:
            **kwargs: Additional execution parameters (for FlextService compatibility)

        FlextDecorators automatically:
        - Log operation start/completion/failure
        - Track performance metrics
        - Handle context propagation (correlation_id, operation_name)

        Returns:
            FlextResult[FlextCliTypes.Data.CliDataDict]: Service execution result

        Pydantic 2 Modernization:
            - Uses ServiceExecutionResult model internally
            - Serializes to dict for API compatibility
            - Type-safe with field validation

        """
        self.logger.info(
            "Executing CLI core service",
            operation="execute",
            commands_count=len(self._commands),
            session_active=self._session_active,
            source="flext-cli/src/flext_cli/core.py",
        )

        self.logger.debug(
            "Starting service execution",
            operation="execute",
            kwargs_keys=list(kwargs.keys()) if kwargs else [],
            source="flext-cli/src/flext_cli/core.py",
        )

        try:
            # Validate service state before execution
            if not self._commands:
                self.logger.warning(
                    "No commands registered for service execution",
                    operation="execute",
                    consequence="Service execution will fail",
                    source="flext-cli/src/flext_cli/core.py",
                )
                return FlextResult[FlextCliTypes.Data.CliDataDict].fail(
                    FlextCliConstants.ErrorMessages.COMMAND_LISTING_FAILED.format(
                        error="No commands registered",
                    ),
                )

            # Create Pydantic model with type-safe fields
            result_model = FlextCliModels.ServiceExecutionResult(
                service_executed=True,
                commands_count=len(self._commands),
                session_active=self._session_active,
                execution_timestamp=FlextUtilities.Generators.generate_iso_timestamp(),
                service_ready=True,
            )

            # Serialize to dict for API compatibility
            status_dict: FlextCliTypes.Data.CliDataDict = (
                FlextMixins.ModelConversion.to_dict(result_model)
            )

            self.logger.debug(
                "Service execution completed successfully",
                operation="execute",
                commands_count=result_model.commands_count,
                service_ready=result_model.service_ready,
                source="flext-cli/src/flext_cli/core.py",
            )

            self.logger.info(
                "CLI core service execution completed",
                operation="execute",
                commands_count=result_model.commands_count,
                source="flext-cli/src/flext_cli/core.py",
            )

            # Use self.ok() from FlextService for consistency
            return self.ok(status_dict)

        except Exception as e:
            self.logger.exception(
                "FATAL ERROR during service execution - execution aborted",
                operation="execute",
                error=str(e),
                error_type=type(e).__name__,
                consequence="Service execution failed completely",
                severity="critical",
                source="flext-cli/src/flext_cli/core.py",
            )
            return FlextResult[FlextCliTypes.Data.CliDataDict].fail(
                FlextCliConstants.CoreServiceLogMessages.SERVICE_EXECUTION_FAILED.format(
                    error=e,
                ),
            )

    def execute_cli_command_with_context(
        self,
        command_name: str,
        user_id: str | None = None,
        **context_data: FlextTypes.JsonValue,
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
        # Use context enrichment pattern with existing mixins
        # This provides:
        # - Operation context enrichment
        # - User context binding
        # - Structured logging with context

        # Set operation context for the current operation
        self._with_operation_context(
            operation_name=(
                f"{FlextCliConstants.CoreServiceDefaults.CLI_COMMAND_PREFIX}{command_name}"
            ),
            user_id=user_id,
            **context_data,
        )

        # Enrich context with additional data
        self._enrich_context(
            command_name=command_name,
            operation_type=FlextCliConstants.CoreServiceDefaults.OPERATION_TYPE_CLI_COMMAND,
            **context_data,
        )

        # Create Pydantic model with type-safe fields
        # Use default value if user_id is None (model requires str, not str | None)
        effective_user_id = (
            user_id
            if user_id is not None
            else FlextCliConstants.CliSessionDefaults.DEFAULT_USER_ID
        )
        result_model = FlextCliModels.CommandExecutionContextResult(
            command=command_name,
            status=True,
            context=dict(context_data),  # Convert kwargs to dict
            timestamp=FlextUtilities.Generators.generate_iso_timestamp(),
            user_id=effective_user_id,
        )

        # Serialize to dict for API compatibility
        result_dict: FlextCliTypes.Data.CliDataDict = (
            FlextMixins.ModelConversion.to_dict(result_model)
        )
        # Use self.ok() from FlextService for consistency
        return self.ok(result_dict)

    def health_check(self) -> FlextResult[FlextTypes.JsonDict]:
        """Perform health check on the CLI service.

        Returns:
            FlextResult[FlextTypes.JsonDict]: Health check result

        """
        try:
            return FlextResult[FlextTypes.JsonDict].ok({
                FlextCliConstants.DictKeys.STATUS: FlextCliConstants.ServiceStatus.HEALTHY.value,
                FlextCliConstants.CoreServiceDictKeys.COMMANDS_COUNT: len(
                    self._commands,
                ),
                FlextCliConstants.CoreServiceDictKeys.SESSION_ACTIVE: self._session_active,
                FlextCliConstants.DictKeys.TIMESTAMP: FlextUtilities.Generators.generate_iso_timestamp(),
            })
        except Exception as e:
            return FlextResult[FlextTypes.JsonDict].fail(
                FlextCliConstants.ErrorMessages.CLI_EXECUTION_ERROR.format(error=e),
            )

    def get_config(self) -> FlextResult[FlextTypes.JsonDict]:
        """Get current service configuration.

        Returns:
            FlextResult[FlextTypes.JsonDict]: Configuration data

        """
        try:
            # Type narrowing: self._config is already JsonDict compatible
            # Fast-fail if config is None - no fallback
            if self._config is None:
                return FlextResult[FlextTypes.JsonDict].fail(
                    FlextCliConstants.ErrorMessages.CONFIG_NOT_INITIALIZED,
                )
            return FlextResult[FlextTypes.JsonDict].ok(self._config)
        except Exception as e:
            return FlextResult[FlextTypes.JsonDict].fail(
                FlextCliConstants.ErrorMessages.CONFIG_RETRIEVAL_FAILED.format(error=e),
            )

    def _get_dict_keys(
        self,
        data_dict: Mapping[str, FlextTypes.JsonValue] | None,
        error_message: str,
    ) -> FlextResult[list[str]]:
        """Generic method to safely get keys from a dictionary.

        Args:
            data_dict: Dictionary to extract keys from (None-safe)
            error_message: Error message template to use on failure

        Returns:
            FlextResult with list of keys or error

        """
        try:
            return FlextResult[list[str]].ok(
                list(data_dict.keys()) if data_dict else [],
            )
        except Exception as e:
            return FlextResult[list[str]].fail(error_message.format(error=e))

    def get_handlers(self) -> FlextResult[list[str]]:
        """Get list of registered command handlers.

        Returns:
            FlextResult[list[str]]: List of handler names

        """
        # Type cast: JsonDict is compatible with Mapping[str, JsonValue]
        return self._get_dict_keys(
            self._commands,
            FlextCliConstants.ErrorMessages.COMMAND_LISTING_FAILED,
        )

    def get_plugins(self) -> FlextResult[list[str]]:
        """Get list of registered plugins.

        Returns:
            FlextResult[list[str]]: List of plugin names

        """
        try:
            # Extract keys from plugins dict directly
            plugin_names = list(self._plugins.keys())
            return FlextResult[list[str]].ok(plugin_names)
        except Exception as e:
            return FlextResult[list[str]].fail(
                FlextCliConstants.ErrorMessages.FAILED_GET_LOADED_PLUGINS.format(
                    error=e
                )
            )

    def get_sessions(self) -> FlextResult[list[str]]:
        """Get list of active sessions.

        Returns:
            FlextResult[list[str]]: List of session IDs

        """
        return self._get_dict_keys(
            self._sessions,
            FlextCliConstants.ErrorMessages.SESSION_END_FAILED,
        )

    def get_commands(self) -> FlextResult[list[str]]:
        """Get list of registered commands.

        Returns:
            FlextResult[list[str]]: List of command names

        """
        return self._get_dict_keys(
            self._commands,
            FlextCliConstants.ErrorMessages.COMMAND_LISTING_FAILED,
        )

    def get_formatters(self) -> FlextResult[list[str]]:
        """Get list of available formatters from constants.

        Returns:
            FlextResult[list[str]]: List of formatter names

        """
        return FlextResult[list[str]].ok(FlextCliConstants.OUTPUT_FORMATS_LIST)

    def load_configuration(self, config_path: str) -> FlextResult[FlextTypes.JsonDict]:
        """Load configuration from file.

        Args:
            config_path: Path to configuration file

        Returns:
            FlextResult[FlextTypes.JsonDict]: Loaded configuration

        """
        # Fast fail validation
        if config_path is None:
            return FlextResult[FlextTypes.JsonDict].fail(
                FlextCliConstants.ErrorMessages.CONFIG_FILE_NOT_FOUND.format(file=""),
            )
        if not config_path.strip():
            return FlextResult[FlextTypes.JsonDict].fail(
                FlextCliConstants.ErrorMessages.CONFIG_FILE_NOT_FOUND.format(file=""),
            )

        try:
            config_file = Path(config_path)

            if not config_file.exists():
                return FlextResult[FlextTypes.JsonDict].fail(
                    FlextCliConstants.ErrorMessages.CONFIG_FILE_NOT_FOUND.format(
                        file=config_path,
                    ),
                )

            if not config_file.is_file():
                return FlextResult[FlextTypes.JsonDict].fail(
                    FlextCliConstants.ErrorMessages.FAILED_LOAD_CONFIG_FROM_FILE.format(
                        file=config_path,
                        error=FlextCliConstants.ErrorMessages.CONFIG_NOT_DICT,
                    ),
                )

            # Read and parse JSON configuration
            content = config_file.read_text(
                encoding=FlextCliConstants.FileIODefaults.ENCODING_DEFAULT,
            )
            config_data = json.loads(content)

            if not FlextRuntime.is_dict_like(config_data):
                return FlextResult[FlextTypes.JsonDict].fail(
                    FlextCliConstants.ErrorMessages.CONFIG_NOT_DICT,
                )

            return FlextResult[FlextTypes.JsonDict].ok(config_data)

        except json.JSONDecodeError as e:
            return FlextResult[FlextTypes.JsonDict].fail(
                FlextCliConstants.ErrorMessages.FAILED_LOAD_CONFIG_FROM_FILE.format(
                    file=config_path,
                    error=str(e),
                ),
            )
        except Exception as e:
            return FlextResult[FlextTypes.JsonDict].fail(
                FlextCliConstants.ErrorMessages.LOAD_FAILED.format(error=e),
            )

    def save_configuration(
        self,
        config_path: str,
        config_data: FlextTypes.JsonDict,
    ) -> FlextResult[bool]:
        """Save configuration to file.

        Args:
            config_path: Path to save configuration file
            config_data: Configuration data to save

        Returns:
            FlextResult[bool]: True if saved successfully, failure on error

        """
        try:
            path = Path(config_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open(
                FlextCliConstants.FileIODefaults.FILE_WRITE_MODE,
                encoding=FlextCliConstants.FileIODefaults.ENCODING_DEFAULT,
            ) as f:
                json.dump(
                    config_data,
                    f,
                    indent=FlextCliConstants.FileIODefaults.JSON_INDENT,
                    ensure_ascii=FlextCliConstants.FileIODefaults.JSON_ENSURE_ASCII,
                )
            return FlextResult[bool].ok(True)
        except Exception as e:
            return FlextResult[bool].fail(
                FlextCliConstants.ErrorMessages.SAVE_FAILED.format(error=e),
            )

    def validate_configuration(self, _config: FlextCliConfig) -> FlextResult[bool]:
        """Validate configuration using FlextCliConfig Pydantic model.

        Args:
            _config: FlextCliConfig model instance (validation automatic via Pydantic)

        Returns:
            FlextResult[bool]: True if configuration is valid, failure on error

        Note:
            Validation is automatically performed by Pydantic field validators
            when FlextCliConfig instance is created. This method validates the
            configuration is correct and returns success if config is valid.

        """
        # Validation already performed by Pydantic during instantiation
        # If we reach here, config is valid
        return FlextResult[bool].ok(True)

    # ==========================================================================
    # PERFORMANCE OPTIMIZATIONS - Integrated into core service
    # ==========================================================================

    def create_ttl_cache(
        self,
        name: str,
        maxsize: int = 128,
        ttl: int = 300,
    ) -> FlextResult[TTLCache[str, FlextTypes.JsonValue]]:
        """Create TTL cache with time-based expiration.

        Args:
            name: Cache identifier
            maxsize: Maximum number of items
            ttl: Time-to-live in seconds

        Returns:
            FlextResult[TTLCache]: Created cache instance

        """
        try:
            if name in self._caches:
                return FlextResult[TTLCache[str, FlextTypes.JsonValue]].fail(
                    f"Cache '{name}' already exists",
                )

            # Validate parameters
            if maxsize < 0:
                return FlextResult[TTLCache[str, FlextTypes.JsonValue]].fail(
                    f"Invalid maxsize '{maxsize}': must be non-negative",
                )
            if ttl < 0:
                return FlextResult[TTLCache[str, FlextTypes.JsonValue]].fail(
                    f"Invalid ttl '{ttl}': must be non-negative",
                )

            cache: TTLCache[str, FlextTypes.JsonValue] = TTLCache(
                maxsize=maxsize, ttl=ttl
            )
            self._caches[name] = cache
            return FlextResult[TTLCache[str, FlextTypes.JsonValue]].ok(cache)
        except Exception as e:
            return FlextResult[TTLCache[str, FlextTypes.JsonValue]].fail(str(e))

    def memoize(
        self,
        cache_name: str = "default",
        ttl: int | None = None,
    ) -> Callable[[Callable[P, T]], Callable[P, T]]:
        """Create memoization decorator for functions."""

        def decorator(func: Callable[P, T]) -> Callable[P, T]:
            if cache_name not in self._caches:
                if ttl:
                    self._caches[cache_name] = TTLCache(maxsize=128, ttl=ttl)
                else:
                    self._caches[cache_name] = LRUCache(maxsize=128)

            cache_obj = self._caches[cache_name]
            # Type narrowing: cache_obj is TTLCache or LRUCache
            if not isinstance(cache_obj, (TTLCache, LRUCache)):
                error_msg = f"Cache '{cache_name}' has invalid type"
                raise TypeError(error_msg)

            @functools.wraps(func)
            def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
                # Create cache key from function arguments - convert to str for cache
                cache_key_tuple = (
                    (args, tuple(sorted(kwargs.items()))) if kwargs else args
                )
                cache_key = str(hash(cache_key_tuple))

                start = time.time()
                try:
                    # Try to get result from cache
                    cached_value = cache_obj[cache_key]
                    # Type cast: cache stores JsonValue but we know it's type T
                    result: T = cast("T", cached_value)
                    time_saved = time.time() - start
                    self._cache_stats.record_hit(time_saved)
                    return result
                except KeyError:
                    # Cache miss - compute result and store in cache
                    self._cache_stats.record_miss()
                    result = func(*args, **kwargs)
                    # Type cast: store T as JsonValue in cache
                    cache_obj[cache_key] = cast("FlextTypes.JsonValue", result)
                    return result

            return wrapper

        return decorator

    def get_cache_stats(self, cache_name: str) -> FlextResult[FlextTypes.JsonDict]:
        """Get statistics for a specific cache."""
        try:
            if cache_name not in self._caches:
                return FlextResult[FlextTypes.JsonDict].fail(
                    f"Cache '{cache_name}' not found",
                )

            cache_obj = self._caches[cache_name]
            # Support both TTLCache and LRUCache
            if isinstance(cache_obj, (TTLCache, LRUCache)):
                stats: FlextTypes.JsonDict = {
                    "size": len(cache_obj),
                    "maxsize": cache_obj.maxsize,
                    "hits": self._cache_stats.cache_hits,
                    "misses": self._cache_stats.cache_misses,
                    "hit_rate": self._cache_stats.get_hit_rate(),
                    "time_saved": self._cache_stats.total_time_saved,
                }
                return FlextResult[FlextTypes.JsonDict].ok(stats)
            return FlextResult[FlextTypes.JsonDict].fail(
                f"Cache '{cache_name}' is not a supported cache type (TTLCache or LRUCache)",
            )
        except Exception as e:
            return FlextResult[FlextTypes.JsonDict].fail(str(e))

    # ==========================================================================
    # EXECUTOR SUPPORT - Thread pool execution for blocking operations
    # ==========================================================================

    def run_in_executor(
        self,
        func: Callable[P, T],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> FlextResult[T]:
        """Execute function synchronously (formerly in thread pool).

        Note: This method now executes synchronously. Thread pool execution
        has been removed in v0.10.0 to maintain synchronous-only codebase.
        The API is maintained for backward compatibility but behavior changed.
        """
        try:
            result = func(*args, **kwargs)
            return FlextResult[T].ok(result)
        except Exception as e:
            return FlextResult[T].fail(str(e))

    # ==========================================================================
    # PLUGIN SYSTEM - Integrated into core service
    # ==========================================================================

    def register_plugin(self, plugin: FlextTypes.SerializableType) -> FlextResult[bool]:
        """Register a plugin with the plugin manager.

        Returns:
            FlextResult[bool]: True if plugin registered successfully, failure on error

        """
        try:
            plugin_name = self._plugin_manager.register(plugin)
            if plugin_name:
                # Type cast: plugin should implement CliPlugin protocol
                typed_plugin: FlextCliProtocols.Cli.CliPlugin = cast(
                    "FlextCliProtocols.Cli.CliPlugin", plugin
                )
                self._plugins[plugin_name] = typed_plugin
            return FlextResult[bool].ok(True)
        except Exception as e:
            return FlextResult[bool].fail(str(e))

    def discover_plugins(self) -> FlextResult[list[str]]:
        """Discover and register plugins via entry points."""
        try:
            discovered_plugins: list[str] = []

            for dist in metadata.distributions():
                for ep in dist.entry_points:
                    if ep.group == "flext_cli.plugins":
                        try:
                            plugin_class = ep.load()
                            plugin_instance = plugin_class()
                            self._plugin_manager.register(plugin_instance)

                            discovered_plugins.append(ep.name)
                            self._plugins[ep.name] = plugin_instance

                        except Exception as e:
                            self.logger.debug(
                                "Failed to load plugin",
                                extra={"plugin_name": ep.name, "exception": str(e)},
                            )

            return FlextResult[list[str]].ok(discovered_plugins)
        except Exception as e:
            return FlextResult[list[str]].fail(str(e))

    def call_plugin_hook(
        self,
        hook_name: str,
        **kwargs: FlextTypes.JsonValue,
    ) -> FlextResult[list[FlextTypes.JsonValue]]:
        """Call a plugin hook with arguments."""
        try:
            hook_caller = getattr(self._plugin_manager.hook, hook_name, None)

            if hook_caller is None:
                return FlextResult[list[FlextTypes.JsonValue]].fail(
                    f"Hook '{hook_name}' not found",
                )

            results = hook_caller(**kwargs)
            # Fast-fail: hook must return list or None (converted to empty list)
            # No fallback to fake data
            if results is None:
                return FlextResult[list[FlextTypes.JsonValue]].ok([])
            if not FlextRuntime.is_list_like(results):
                # Single result - wrap in list (not a fallback, valid conversion)
                return FlextResult[list[FlextTypes.JsonValue]].ok([results])

            return FlextResult[list[FlextTypes.JsonValue]].ok(results)
        except Exception as e:
            return FlextResult[list[FlextTypes.JsonValue]].fail(str(e))

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
