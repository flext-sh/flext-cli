"""Core service responsável por comandos, sessões e configuração do flext-cli.

Agrupa registro/execução de comandos, perfis de configuração, sessões e plugins,
retornando `r[T]` para as operações consumidas pelo facade `FlextCli`.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import functools
import json
import time
from collections.abc import Callable, Mapping
from datetime import UTC, datetime
from importlib import metadata
from pathlib import Path
from typing import cast, override

import pluggy
from cachetools import LRUCache, TTLCache
from flext_core import (
    FlextConstants,
    FlextDecorators,
    FlextExceptions,
    FlextHandlers,
    FlextMixins,
    FlextModels,
    FlextProtocols,
    FlextRuntime,
    FlextService,
    r,
    t,
    u,
)

from flext_cli.base import FlextCliServiceBase
from flext_cli.config import FlextCliConfig
from flext_cli.constants import FlextCliConstants
from flext_cli.models import FlextCliModels
from flext_cli.protocols import FlextCliProtocols

# Aliases for static method calls and type references
# Use u.* for FlextUtilities static methods
# Use t.* for FlextTypes type references
# Use c.* for FlextConstants constants
# Use m.* for FlextModels model references
# Use p.* for FlextProtocols protocol references
# Use r.* for FlextResult methods
# Use e.* for FlextExceptions
# Use d.* for FlextDecorators decorators
# Use s.* for FlextService service base
# Use x.* for FlextMixins mixins
# Use h.* for FlextHandlers handlers
# u is already imported from flext_core
# t is already imported from flext_core
c = FlextConstants
m = FlextModels
p = FlextProtocols
e = FlextExceptions
d = FlextDecorators
s = FlextService
x = FlextMixins
h = FlextHandlers


class FlextCliCore(FlextCliServiceBase):  # noqa: PLR0904
    """Track command registry, configuration profiles and CLI sessions.

    Business Rules:
    ───────────────
    1. Command registry MUST validate command names (unique, non-empty)
    2. Command handlers MUST be callable and return r[T]
    3. Configuration validation MUST enforce business rules (trace requires debug)
    4. Session management MUST track command execution history
    5. Plugin system MUST validate plugin protocol compliance
    6. Cache operations MUST have TTL to prevent stale data
    7. All operations MUST use Railway-Oriented Programming (r)
    8. Configuration changes MUST be validated before application

    Architecture Implications:
    ───────────────────────────
    - Command registry uses dict[str, JsonDict] for O(1) lookup
    - Session tracking enables audit trail and state management
    - Plugin system uses pluggy for extensibility
    - Cache (LRUCache, TTLCache) improves performance for repeated operations
    - Configuration validation uses Pydantic validators for type safety
    - Service extends FlextCliServiceBase for consistent logging and context

    Audit Implications:
    ───────────────────
    - Command registrations MUST be logged with command name and handler info
    - Command executions MUST be logged with arguments (no sensitive data)
    - Configuration changes MUST be logged with before/after values
    - Session creation/termination MUST be logged with session ID and duration
    - Plugin loading MUST be logged with plugin name and version
    - Cache operations SHOULD be logged for performance monitoring
    - Error conditions MUST be logged with full stack trace (no sensitive data)
    - Remote plugin loading MUST use encrypted connections (TLS/SSL)

    Registra e recupera comandos via `FlextCliModels`, lida com configuração
    validada (`FlextCliConfig`), gerencia sessões e plugins e expõe
    diagnósticos consumidos pelo facade `FlextCli`.
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
            return u.when(
                condition=total > 0,
                then_value=self.cache_hits / total,
                else_value=0.0,
            )

    # Logger is provided by FlextMixins mixin

    def __init__(
        self,
        config: t.JsonDict | None = None,
        **data: t.GeneralValueType,
    ) -> None:
        """Initialize CLI core with optional configuration seed values."""
        super().__init__(**data)

        # Phase 1 Enhancement: Context enrichment happens automatically in FlextService.__init__
        # The parent class already calls _enrich_context with service metadata
        # Logger and container are inherited from FlextService via FlextMixins

        # Type-safe configuration initialization
        # Store CLI-specific config as dict (base class _config is FlextConfig | None)
        # Use mutable dict for CLI-specific configuration dictionary
        # Use FlextRuntime.is_dict_like for type checking
        self._cli_config: dict[str, t.GeneralValueType] = (
            dict(config)
            if config is not None and FlextRuntime.is_dict_like(config)
            else {}
        )
        self._commands: dict[str, t.JsonDict] = {}
        # Note: stores plugin objects implementing CliPlugin protocol
        self._plugins: dict[str, FlextCliProtocols.Cli.CliPlugin] = {}
        self._sessions: t.Json.JsonDict = {}
        self._session_active = False

        # Performance and async integration
        # Note: stores cache objects (TTLCache/LRUCache), not JsonValue
        # Cache types are from external library, using generic types
        self._caches: dict[
            str,
            TTLCache[str, t.GeneralValueType] | LRUCache[str, t.GeneralValueType],
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
    ) -> r[bool]:
        """Register CLI command using CliCommand model instance.

        Args:
            command: CliCommand model instance with validated data

        Returns:
            r[bool]: True if registration succeeded, failure on error

        """
        # Log detailed command registration initialization
        self.logger.debug(
            "Starting CLI command registration",
            command_name=u.when(
                condition=command, then_value=command.name, else_value=None
            ),
            command_type=u.when(
                condition=command, then_value=type(command).__name__, else_value=None
            ),
            operation="register_command",
            source="flext-cli/src/flext_cli/core.py",
        )

        self.logger.info(
            "STARTING CLI command registration",
            command_name=u.when(
                condition=command, then_value=command.name, else_value=None
            ),
            operation="register_command",
            source="flext-cli/src/flext_cli/core.py",
        )

        # Simple validation and registration (KISS principle) - fast fail
        # Note: command parameter is non-optional, but we check for None defensively
        # to handle cases where caller passes None despite type hints
        if not command.name:
            self.logger.error(
                "FAILED CLI command registration - command name is empty",
                command_name=command.name,
                operation="register_command",
                source="flext-cli/src/flext_cli/core.py",
            )
            return r[bool].fail(
                FlextCliConstants.ErrorMessages.COMMAND_NAME_EMPTY,
            )

        try:
            # model_dump() already returns dict with JSON-compatible values
            command_data: t.JsonDict = command.model_dump()
            self._commands[command.name] = command_data

            # Log successful registration with detailed context
            self.logger.debug(
                "Command registration completed successfully",
                command_name=command.name,
                command_data_keys=u.when(
                    condition=command_data,
                    then_value=u.keys(command_data),
                    else_value=[],
                ),
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

            return r[bool].ok(True)

        except Exception as e:
            # Log detailed registration error
            self.logger.exception(
                "FAILED CLI command registration with exception",
                command_name=command.name,
                error_type=type(e).__name__,
                operation="register_command",
                source="flext-cli/src/flext_cli/core.py",
            )
            return r[bool].fail(
                FlextCliConstants.ErrorMessages.COMMAND_REGISTRATION_FAILED.format(
                    command=command.name,
                    error=str(e),
                ),
            )

    def get_command(
        self,
        name: str,
    ) -> r[t.JsonDict]:
        """Retrieve registered command definition.

        Args:
            name: Command identifier to retrieve

        Returns:
            r[t.JsonDict]: Command definition or error

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
            return r[t.JsonDict].fail(
                FlextCliConstants.ErrorMessages.COMMAND_NAME_EMPTY,
            )

        # Use dict.get() to check command existence
        command_check = self._commands.get(name)
        if command_check is None:
            self.logger.warning(
                "Command not found in registry",
                operation="get_command",
                command_name=name,
                available_commands=list(self._commands.keys()),
                consequence="Command retrieval will fail",
                source="flext-cli/src/flext_cli/core.py",
            )
            return r[t.JsonDict].fail(
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

            # Use FlextRuntime.is_dict_like for type checking
            if FlextRuntime.is_dict_like(command_def):
                self.logger.debug(
                    "Command definition retrieved successfully",
                    operation="get_command",
                    command_name=name,
                    definition_keys=u.when(
                        condition=hasattr(command_def, "keys"),
                        then_value=u.keys(command_def),
                        else_value=[],
                    ),
                    source="flext-cli/src/flext_cli/core.py",
                )

                # command_def is already JsonDict - no conversion needed
                return r[t.JsonDict].ok(command_def)

            self.logger.error(
                "FAILED to retrieve command - invalid command type",
                operation="get_command",
                command_name=name,
                command_def_type=type(command_def).__name__,
                consequence="Command retrieval aborted",
                source="flext-cli/src/flext_cli/core.py",
            )
            return r[t.JsonDict].fail(
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
            return r[t.JsonDict].fail(
                FlextCliConstants.ErrorMessages.COMMAND_RETRIEVAL_FAILED.format(
                    error=e,
                ),
            )

    def _build_execution_context(
        self,
        context: t.JsonDict | list[str] | None,
    ) -> t.JsonDict:
        """Build execution context from various input formats."""
        if context is None:
            return {}
        if FlextRuntime.is_list_like(context):
            # Use build() DSL: process → normalize → ensure JSON-compatible
            # Reuse helpers from output module to avoid duplication
            from flext_cli.services.output import norm_json

            process_result = u.process(
                list(context),
                processor=lambda _k, item: norm_json(item),
                on_error="skip",
            )
            context_list = cast(
                "list[t.GeneralValueType]",
                u.val(process_result, default=[]),
            )
            return self._build_context_from_list(context_list)
        # Use FlextRuntime.is_dict_like for type checking
        if FlextRuntime.is_dict_like(context):
            # Context is already CliCommand.CommandContext compatible - direct assignment
            return context
        return {}

    def execute_command(
        self,
        name: str,
        context: t.JsonDict | list[str] | None = None,
        timeout: float | None = None,
    ) -> r[t.JsonDict]:
        """Execute registered command with context."""
        self.logger.info("STARTING CLI command execution", command_name=name)

        command_result = self.get_command(name)
        if command_result.is_failure:
            self.logger.error("FAILED - command not found", command_name=name)
            return r[t.JsonDict].fail(
                u.err(command_result, default="Command not found"),
            )

        try:
            execution_context = self._build_execution_context(context)
            result_dict: dict[str, t.GeneralValueType] = {
                FlextCliConstants.DictKeys.COMMAND: name,
                FlextCliConstants.DictKeys.STATUS: True,
                FlextCliConstants.DictKeys.TIMESTAMP: u.generate("timestamp"),
                FlextCliConstants.DictKeys.TIMEOUT: timeout,
                FlextCliConstants.DictKeys.CONTEXT: dict(execution_context),
            }
            self.logger.info("COMPLETED CLI command execution", command_name=name)
            return r[t.JsonDict].ok(result_dict)

        except Exception as e:
            self.logger.exception("FAILED CLI command execution", command_name=name)
            return r[t.JsonDict].fail(
                FlextCliConstants.ErrorMessages.COMMAND_EXECUTION_FAILED.format(
                    error=e
                ),
            )

    def list_commands(self) -> r[list[str]]:
        """List all registered commands using functional composition.

        Performs command listing with railway pattern and proper error handling.
        Uses functional approach to extract command names safely.

        Returns:
            r[list[str]]: List of command names or error with details

        """
        self.logger.debug(
            "Listing all registered commands",
            operation="list_commands",
            total_commands=len(self._commands),
            source="flext-cli/src/flext_cli/core.py",
        )

        # Functional command listing with railway pattern
        def extract_command_names() -> r[list[str]]:
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

                return r[list[str]].ok(command_names)
            except Exception as e:
                self.logger.exception(
                    "FAILED to list commands - operation aborted",
                    operation="list_commands",
                    error=str(e),
                    error_type=type(e).__name__,
                    consequence="Command list unavailable",
                    source="flext-cli/src/flext_cli/core.py",
                )
                return r[list[str]].fail(
                    FlextCliConstants.ErrorMessages.COMMAND_LISTING_FAILED.format(
                        error=e,
                    ),
                )

        # Railway pattern: extract and validate command names
        return extract_command_names()

    # ==========================================================================
    # PRIVATE HELPERS - Direct logger usage (no fallbacks)
    # ==========================================================================

    @staticmethod
    def _build_context_from_list(
        args: list[t.GeneralValueType],
    ) -> t.JsonDict:
        """Build command context from list of arguments.

        Business Rule:
        ──────────────
        Static method - converts argument list to JSON-compatible dict.
        No instance state needed.
        """
        # All values in args are already CliJsonValue compatible - direct assignment
        return {FlextCliConstants.DictKeys.ARGS: args}

    # ==========================================================================
    # CLI CONFIGURATION MANAGEMENT - Using FlextCliTypes.Configuration types
    # ==========================================================================

    def _log_config_update(self) -> None:
        """Log configuration update - direct logger usage."""
        self.logger.info(FlextCliConstants.LogMessages.CLI_CONFIG_UPDATED)

    def _validate_config_input(
        self,
        config: t.JsonDict,
    ) -> r[t.JsonDict]:
        """Validate input configuration for update operations."""
        if not config:
            self.logger.warning(
                "Configuration input is empty",
                operation="update_configuration",
                consequence="Configuration update will fail",
                source="flext-cli/src/flext_cli/core.py",
            )
            return r[t.JsonDict].fail(FlextCliConstants.ErrorMessages.CONFIG_NOT_DICT)

        self.logger.debug(
            "Configuration input validated",
            operation="update_configuration",
            config_keys=list(config.keys())
            if FlextRuntime.is_dict_like(config)
            else None,
            source="flext-cli/src/flext_cli/core.py",
        )
        # Use build() DSL for JSON conversion
        if not FlextRuntime.is_dict_like(config):
            return r[t.JsonDict].fail(FlextCliConstants.ErrorMessages.CONFIG_NOT_DICT)
        # Reuse to_dict_json helper from output module
        from flext_cli.services.output import to_dict_json, cast_if

        json_config = to_dict_json(config)
        return r[t.JsonDict].ok(cast_if(json_config, dict, config))

    def _validate_existing_config(
        self,
    ) -> r[t.JsonDict]:
        """Validate existing configuration state."""
        # self._cli_config is dict[str, GeneralValueType] - return as JsonDict
        if self._cli_config:
            return r[t.JsonDict].ok(self._cli_config)
        return r[t.JsonDict].fail(
            FlextCliConstants.ErrorMessages.CONFIG_NOT_INITIALIZED
        )

    def _merge_configurations(
        self,
        valid_config: t.JsonDict,
    ) -> r[bool]:
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

            existing_config_result = self._validate_existing_config()
            if existing_config_result.is_failure:
                self.logger.warning(
                    "Existing configuration validation failed",
                    operation="update_configuration",
                    error=u.err(existing_config_result, default=""),
                    consequence="Configuration merge will fail",
                    source="flext-cli/src/flext_cli/core.py",
                )
                return r[bool].fail(
                    u.err(existing_config_result, default="Config validation failed"),
                )

            existing_config_raw = u.val(existing_config_result, default={})
            # Convert to mutable dict for merging
            existing_config: dict[str, t.GeneralValueType] = (
                dict(existing_config_raw)
                if FlextRuntime.is_dict_like(existing_config_raw)
                else {}
            )
            # Use build() DSL: ensure dict → transform to JSON
            # Reuse to_dict_json helper from output module
            from flext_cli.services.output import to_dict_json

            transformed_config = to_dict_json(valid_config)
            # Use u.merge for intelligent deep merge
            merge_result = u.merge(
                existing_config,
                transformed_config,
                strategy="deep",  # Deep merge preserves nested structures
            )
            if merge_result.is_failure:
                return r[bool].fail(
                    u.err(merge_result, default="Failed to merge config")
                )
            # Update internal _cli_config with merged result
            self._cli_config = u.val(merge_result, default={})

            self.logger.debug(
                "Configuration merged successfully",
                operation="update_configuration",
                merged_keys=list(self._cli_config.keys())
                if FlextRuntime.is_dict_like(self._cli_config)
                else None,
                source="flext-cli/src/flext_cli/core.py",
            )

            self._log_config_update()
            self.logger.info(
                "Configuration update completed successfully",
                operation="update_configuration",
                source="flext-cli/src/flext_cli/core.py",
            )

            return r[bool].ok(True)

        except Exception as e:
            self.logger.exception(
                "FAILED to merge configurations - operation aborted",
                operation="update_configuration",
                error=str(e),
                error_type=type(e).__name__,
                consequence="Configuration update failed completely",
                source="flext-cli/src/flext_cli/core.py",
            )
            return r[bool].fail(
                FlextCliConstants.ErrorMessages.CONFIG_UPDATE_FAILED.format(error=e),
            )

    def update_configuration(
        self,
        config: t.JsonDict,
    ) -> r[bool]:
        """Update CLI configuration using railway pattern and functional composition.

        Performs configuration update with comprehensive validation and error handling.
        Uses functional pipeline to ensure safe configuration merging.

        Args:
            config: New configuration schema with CLI-specific structure

        Returns:
            r[bool]: True if configuration updated successfully, failure on error

        """
        self.logger.info(
            "Updating CLI configuration",
            operation="update_configuration",
            config_keys=list(config.keys())
            if FlextRuntime.is_dict_like(config)
            else None,
            current_config_keys=list(self._cli_config.keys())
            if FlextRuntime.is_dict_like(self._cli_config)
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

        # Railway pattern: validate input then merge configurations
        # Use build() DSL: ensure dict → transform to JSON
        if not FlextRuntime.is_dict_like(config):
            return r[bool].fail(FlextCliConstants.ErrorMessages.CONFIG_NOT_DICT)
        # Reuse to_dict_json helper from output module
        from flext_cli.services.output import to_dict_json

        validated_config_input = cast("t.JsonDict", to_dict_json(config))
        config_result = self._validate_config_input(validated_config_input)
        if config_result.is_failure:
            return r[bool].fail(
                u.err(config_result, default="Configuration validation failed")
            )

        return self._merge_configurations(u.val(config_result, default={}))

    def get_configuration(
        self,
    ) -> r[t.JsonDict]:
        """Get current CLI configuration using functional composition.

        Retrieves configuration with validation and error handling.
        Uses railway pattern to ensure configuration integrity.

        Returns:
            r[t.JsonDict]: Current configuration or error with details

        """

        # Functional configuration retrieval with railway pattern
        def validate_config_state() -> r[t.JsonDict]:
            """Validate that configuration is properly initialized."""
            try:
                self.logger.debug(
                    "Retrieving CLI configuration",
                    operation="get_configuration",
                    config_type=type(self._cli_config).__name__,
                    config_is_dict=FlextRuntime.is_dict_like(self._cli_config),
                    config_keys=list(self._cli_config.keys())
                    if FlextRuntime.is_dict_like(self._cli_config)
                    else None,
                    source="flext-cli/src/flext_cli/core.py",
                )
                if FlextRuntime.is_dict_like(self._cli_config):
                    self.logger.debug(
                        "Configuration retrieved successfully",
                        operation="get_configuration",
                        config_keys=list(self._cli_config.keys())
                        if FlextRuntime.is_dict_like(self._cli_config)
                        else None,
                        source="flext-cli/src/flext_cli/core.py",
                    )

                    self.logger.info(
                        "Configuration retrieval completed",
                        operation="get_configuration",
                        source="flext-cli/src/flext_cli/core.py",
                    )

                    # self._cli_config is dict[str, GeneralValueType] - return as JsonDict
                    return r[t.JsonDict].ok(
                        self._cli_config,
                    )

                self.logger.warning(
                    "Configuration not initialized",
                    operation="get_configuration",
                    consequence="Configuration retrieval will fail",
                    source="flext-cli/src/flext_cli/core.py",
                )
                return r[t.JsonDict].fail(
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
                return r[t.JsonDict].fail(
                    FlextCliConstants.ErrorMessages.CONFIG_RETRIEVAL_FAILED.format(
                        error=e,
                    ),
                )

        # Railway pattern: validate and return configuration
        return validate_config_state()

    def create_profile(
        self,
        name: str,
        profile_config: t.JsonDict,
    ) -> r[bool]:
        """Create CLI configuration profile using railway pattern.

        Performs profile creation with validation and error handling.

        Args:
            name: Profile identifier (validated for non-emptiness)
            profile_config: Profile-specific configuration

        Returns:
            r[bool]: True if profile created successfully, failure on error

        """
        # Input validation
        if not name:
            return r[bool].fail(
                FlextCliConstants.ErrorMessages.PROFILE_NAME_EMPTY,
            )

        if not profile_config:
            return r[bool].fail(
                FlextCliConstants.ErrorMessages.PROFILE_CONFIG_NOT_DICT,
            )

        if not (FlextRuntime.is_dict_like(self._cli_config) and self._cli_config):
            return r[bool].fail(
                FlextCliConstants.ErrorMessages.CONFIG_NOT_INITIALIZED,
            )

        # Store profile
        try:
            # Ensure config is mutable dict
            config: dict[str, t.GeneralValueType] = dict(self._cli_config)

            # Use u.extract to safely get profiles section with default
            profiles_result: r[t.GeneralValueType | None] = cast(
                "r[t.GeneralValueType | None]",
                u.extract(
                    config,
                    FlextCliConstants.DictKeys.PROFILES,
                    default={},
                ),
            )
            profiles_section_raw = u.val(profiles_result, default={})
            # Use u.ensure to ensure dict type and convert to mutable
            profiles_section: dict[str, t.GeneralValueType] = cast(
                "dict[str, t.GeneralValueType]",
                u.ensure(
                    profiles_section_raw
                    if FlextRuntime.is_dict_like(profiles_section_raw)
                    else {},
                    target_type="dict",
                    default={},
                ),
            )
            profiles_section[name] = profile_config
            # Update config with modified profiles section
            config[FlextCliConstants.DictKeys.PROFILES] = profiles_section
            # Update internal _cli_config
            self._cli_config = config
            self.logger.info(
                FlextCliConstants.LogMessages.PROFILE_CREATED.format(name=name),
            )
            return r[bool].ok(True)

        except Exception as e:
            return r[bool].fail(
                FlextCliConstants.ErrorMessages.PROFILE_CREATION_FAILED.format(error=e),
            )

    # ==========================================================================
    # SESSION MANAGEMENT - Using FlextCliTypes.Configuration types
    # ==========================================================================

    def start_session(
        self,
        session_config: t.JsonDict | None = None,
    ) -> r[bool]:
        """Start CLI session with configuration.

        Args:
            session_config: Optional session-specific configuration

        Returns:
            r[bool]: True if session started successfully, failure on error

        """
        if self._session_active:
            return r[bool].fail(
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
            self._session_start_time = u.generate("timestamp")

            # Log session start - direct logger usage
            self.logger.info(FlextCliConstants.LogMessages.SESSION_STARTED)

            return r[bool].ok(True)

        except Exception as e:
            return r[bool].fail(
                FlextCliConstants.ErrorMessages.SESSION_START_FAILED.format(error=e),
            )

    def end_session(self) -> r[bool]:
        """End current CLI session.

        Returns:
            r[bool]: True if session ended successfully, failure on error

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
                return r[bool].fail(
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

            return r[bool].ok(True)

        except Exception as e:
            self.logger.exception(
                "FAILED to end session - operation aborted",
                operation="end_session",
                error=str(e),
                error_type=type(e).__name__,
                consequence="Session end failed completely",
                source="flext-cli/src/flext_cli/core.py",
            )
            return r[bool].fail(
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
    ) -> r[t.JsonDict]:
        """Get command usage statistics using CLI-specific data types.

        Returns:
            r[t.JsonDict]: Statistics data or error

        Pydantic 2 Modernization:
            - Uses CommandStatistics model internally
            - Serializes to dict for API compatibility
            - Type-safe with automatic validation

        """
        try:
            # Create Pydantic model with type-safe fields
            # Note: Currently assumes all registered commands are successful
            # Failure tracking requires execution result storage (future enhancement)
            stats_model = FlextCliModels.CommandStatistics(
                total_commands=len(self._commands),
                successful_commands=len(self._commands),
                failed_commands=0,
            )
            # model_dump() already returns dict with JSON-compatible values
            # Direct assignment if model fields are already CliJsonValue compatible
            stats_dict: t.JsonDict = stats_model.model_dump()
            return r[t.JsonDict].ok(stats_dict)
        except Exception as e:
            return r[t.JsonDict].fail(
                FlextCliConstants.ErrorMessages.CLI_EXECUTION_ERROR.format(error=e),
            )

    def get_service_info(self) -> Mapping[str, t.FlexibleValue]:
        """Get comprehensive service information.

        Returns:
            CliJsonDict: Service information (matches FlextService signature)

        """
        try:
            # Collect comprehensive service information
            commands_count = len(self._commands)
            config_keys = u.when(
                condition=self._cli_config,
                then_value=u.keys(self._cli_config),
                else_value=[],
            )

            # Convert config_keys to Sequence[str] for FlexibleValue compatibility
            config_keys_list: list[str] = u.when(
                condition=config_keys,
                then_value=list(config_keys),
                else_value=[],
            )

            info_data: dict[str, t.FlexibleValue] = {
                FlextCliConstants.DictKeys.SERVICE: FlextCliConstants.FLEXT_CLI,
                FlextCliConstants.CoreServiceDictKeys.COMMANDS_REGISTERED: commands_count,
                FlextCliConstants.CoreServiceDictKeys.CONFIGURATION_SECTIONS: config_keys_list,
                FlextCliConstants.DictKeys.STATUS: (
                    FlextCliConstants.ServiceStatus.OPERATIONAL.value
                    if self._session_active
                    else FlextCliConstants.ServiceStatus.AVAILABLE.value
                ),
                FlextCliConstants.CoreServiceDictKeys.SERVICE_READY: commands_count > 0,
                FlextCliConstants.DictKeys.TIMESTAMP: u.generate("timestamp"),
            }

            # Return Mapping[str, FlexibleValue] to match base class signature
            return info_data

        except Exception as e:
            self.logger.exception(
                FlextCliConstants.CoreServiceLogMessages.SERVICE_INFO_COLLECTION_FAILED,
            )
            return {FlextCliConstants.DictKeys.MESSAGE: str(e)}

    def get_session_statistics(
        self,
    ) -> r[t.JsonDict]:
        """Get session-specific statistics using CLI data types.

        Returns:
            r[t.JsonDict]: Session statistics or error

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
            return r[t.JsonDict].fail(
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
                # Use UTC directly for current time
                current_time = datetime.now(UTC)
                # Parse ISO format string - strip trailing timezone info
                # Handle both 'Z' and '+00:00' suffixes
                start_time_str = self._session_start_time
                # Remove Z suffix
                start_time_str = start_time_str.removesuffix("Z")
                # Remove +00:00 suffix (may be duplicated)
                while start_time_str.endswith("+00:00"):
                    start_time_str = start_time_str[:-6]
                # Parse as naive and make aware
                start_time = datetime.fromisoformat(start_time_str).replace(tzinfo=UTC)
                duration_delta = current_time - start_time
                session_duration = int(duration_delta.total_seconds())

            # Session statistics only track basic metrics
            # Additional metadata can be added to context if needed

            # Create Pydantic model with type-safe fields
            # Note: Error tracking requires execution result storage (future enhancement)
            stats_model = FlextCliModels.SessionStatistics(
                commands_executed=len(self._commands),
                errors_count=0,
                session_duration_seconds=session_duration,
            )

            # model_dump() already returns dict with JSON-compatible values
            stats_dict: t.JsonDict = stats_model.model_dump()

            self.logger.debug(
                "Session statistics collected successfully",
                operation="get_session_statistics",
                session_duration=stats_model.session_duration_seconds,
                commands_executed=stats_model.commands_executed,
                source="flext-cli/src/flext_cli/core.py",
            )

            self.logger.info(
                "Session statistics retrieved",
                operation="get_session_statistics",
                session_duration_seconds=stats_model.session_duration_seconds,
                source="flext-cli/src/flext_cli/core.py",
            )

            return r[t.JsonDict].ok(stats_dict)

        except Exception as e:
            self.logger.exception(
                "FAILED to collect session statistics - operation aborted",
                operation="get_session_statistics",
                error=str(e),
                error_type=type(e).__name__,
                consequence="Statistics unavailable",
                source="flext-cli/src/flext_cli/core.py",
            )
            return r[t.JsonDict].fail(
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
    def execute(self, **_kwargs: t.JsonDict) -> r[t.JsonDict]:
        """Execute CLI service operations.

        Args:
            **kwargs: Additional execution parameters (for FlextService compatibility)

        FlextDecorators automatically:
        - Log operation start/completion/failure
        - Track performance metrics
        - Handle context propagation (correlation_id, operation_name)

        Returns:
            r[t.JsonDict]: Service execution result

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
            kwargs_keys=u.when(
                condition=_kwargs,
                then_value=u.keys(_kwargs),
                else_value=[],
            ),
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
                return r[t.JsonDict].fail(
                    FlextCliConstants.ErrorMessages.COMMAND_LISTING_FAILED.format(
                        error="No commands registered",
                    ),
                )

            # Create Pydantic model with type-safe fields
            result_model = FlextCliModels.ServiceExecutionResult(
                service_executed=True,
                commands_count=len(self._commands),
                session_active=self._session_active,
                execution_timestamp=u.generate("timestamp"),
                service_ready=True,
            )

            # model_dump() already returns dict with JSON-compatible values
            status_dict: t.JsonDict = result_model.model_dump()

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

            return r[t.JsonDict].ok(status_dict)

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
            return r[t.JsonDict].fail(
                FlextCliConstants.CoreServiceLogMessages.SERVICE_EXECUTION_FAILED.format(
                    error=e,
                ),
            )

    def execute_cli_command_with_context(
        self,
        command_name: str,
        user_id: str | None = None,
        **context_data: t.GeneralValueType,
    ) -> r[t.JsonDict]:
        """Execute CLI command with automatic context enrichment (Phase 1 pattern).

        Demonstrates the new execute_with_context_enrichment() pattern from flext-core
        Phase 1 architectural enhancement for CLI operations.

        Args:
            command_name: Name of the command to execute
            user_id: Optional user ID for audit context
            **context_data: Additional context data for enriched logging

        Returns:
            r[t.JsonDict]: Command execution result

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
            command_name=command_name,
            exit_code=0,  # Success
            output="",  # No output for context result
            context={
                **dict(context_data),  # Convert kwargs to dict
                "user_id": effective_user_id,
                "timestamp": u.generate("timestamp"),
            },
        )

        # model_dump() already returns dict with JSON-compatible values
        result_dict: t.JsonDict = result_model.model_dump()
        return r[t.JsonDict].ok(result_dict)

    def health_check(self) -> r[t.Json.JsonDict]:
        """Perform health check on the CLI service.

        Returns:
            r[t.Json.JsonDict]: Health check result

        """
        try:
            return r[t.Json.JsonDict].ok({
                FlextCliConstants.DictKeys.STATUS: FlextCliConstants.ServiceStatus.HEALTHY.value,
                FlextCliConstants.CoreServiceDictKeys.COMMANDS_COUNT: len(
                    self._commands,
                ),
                FlextCliConstants.CoreServiceDictKeys.SESSION_ACTIVE: self._session_active,
                FlextCliConstants.DictKeys.TIMESTAMP: u.generate("timestamp"),
            })
        except Exception as e:
            return r[t.Json.JsonDict].fail(
                FlextCliConstants.ErrorMessages.CLI_EXECUTION_ERROR.format(error=e),
            )

    def get_config(self) -> r[t.Json.JsonDict]:
        """Get current service configuration.

        Returns:
            r[t.Json.JsonDict]: Configuration data

        """
        try:
            # Type narrowing: self._cli_config is dict[str, GeneralValueType] - return as JsonDict
            # Fast-fail if config is empty - no fallback
            if not self._cli_config:
                return r[t.Json.JsonDict].fail(
                    FlextCliConstants.ErrorMessages.CONFIG_NOT_INITIALIZED,
                )
            return r[t.Json.JsonDict].ok(self._cli_config)
        except Exception as e:
            return r[t.Json.JsonDict].fail(
                FlextCliConstants.ErrorMessages.CONFIG_RETRIEVAL_FAILED.format(error=e),
            )

    @staticmethod
    def _get_dict_keys(
        data_dict: Mapping[str, t.GeneralValueType] | None,
        error_message: str,
    ) -> r[list[str]]:
        """Generic method to safely get keys from a dictionary.

        Business Rule:
        ──────────────
        Static method - extracts keys from dict safely with None handling.
        No instance state needed.

        Args:
            data_dict: Dictionary to extract keys from (None-safe)
            error_message: Error message template to use on failure

        Returns:
            r[list[str]] with list of keys or error

        """
        try:
            return r[list[str]].ok(
                u.when(
                    condition=data_dict,
                    then_value=u.keys(data_dict),
                    else_value=[],
                ),
            )
        except Exception as e:
            return r[list[str]].fail(error_message.format(error=e))

    def get_handlers(self) -> r[list[str]]:
        """Get list of registered command handlers.

        Returns:
            r[list[str]]: List of handler names

        """
        # Type cast: JsonDict is compatible with Mapping[str, JsonValue]
        return self._get_dict_keys(
            self._commands,
            FlextCliConstants.ErrorMessages.COMMAND_LISTING_FAILED,
        )

    def get_plugins(self) -> r[list[str]]:
        """Get list of registered plugins.

        Returns:
            r[list[str]]: List of plugin names

        """
        try:
            # Extract keys from plugins dict directly
            plugin_names = list(self._plugins.keys())
            return r[list[str]].ok(plugin_names)
        except Exception as e:
            return r[list[str]].fail(
                FlextCliConstants.ErrorMessages.FAILED_GET_LOADED_PLUGINS.format(
                    error=e,
                ),
            )

    def get_sessions(self) -> r[list[str]]:
        """Get list of active sessions.

        Returns:
            r[list[str]]: List of session IDs

        """
        # Convert _sessions (JsonDict) to Mapping[str, CliJsonValue] for type compatibility
        # Type narrowing: ensure all values are CliJsonValue compatible
        sessions_dict: Mapping[str, t.GeneralValueType] | None = None
        # Use build() DSL for JSON conversion
        # Reuse to_dict_json helper from output module
        from flext_cli.services.output import to_dict_json

        if FlextRuntime.is_dict_like(self._sessions):
            sessions_dict = to_dict_json(dict(self._sessions)) or None
        return self._get_dict_keys(
            sessions_dict,
            FlextCliConstants.ErrorMessages.SESSION_END_FAILED,
        )

    def get_commands(self) -> r[list[str]]:
        """Get list of registered commands.

        Delegates to list_commands() for consistency.

        Returns:
            r[list[str]]: List of command names

        """
        return self.list_commands()

    @staticmethod
    def get_formatters() -> r[list[str]]:
        """Get list of available formatters from constants.

        Returns:
            r[list[str]]: List of formatter names

        """
        return r[list[str]].ok(FlextCliConstants.OUTPUT_FORMATS_LIST)

    @staticmethod
    def _validate_config_path(config_path: str) -> r[Path]:
        """Validate config path and return Path object if valid."""
        if not config_path:
            return r[Path].fail(
                FlextCliConstants.ErrorMessages.CONFIG_FILE_NOT_FOUND.format(file=""),
            )
        config_file = Path(config_path)
        if not config_file.exists():
            return r[Path].fail(
                FlextCliConstants.ErrorMessages.CONFIG_FILE_NOT_FOUND.format(
                    file=config_path
                ),
            )
        if not config_file.is_file():
            return r[Path].fail(
                FlextCliConstants.ErrorMessages.FAILED_LOAD_CONFIG_FROM_FILE.format(
                    file=config_path,
                    error=FlextCliConstants.ErrorMessages.CONFIG_NOT_DICT,
                ),
            )
        return r[Path].ok(config_file)

    def load_configuration(self, config_path: str) -> r[t.Json.JsonDict]:
        """Load configuration from file."""
        path_result = self._validate_config_path(config_path)
        if path_result.is_failure:
            return r[t.Json.JsonDict].fail(u.err(path_result, default="Invalid path"))

        try:
            config_file = u.val(path_result, default=Path())
            content = config_file.read_text(
                encoding=FlextCliConstants.FileIODefaults.ENCODING_DEFAULT,
            )
            config_data = json.loads(content)

            if not FlextRuntime.is_dict_like(config_data):
                return r[t.Json.JsonDict].fail(
                    FlextCliConstants.ErrorMessages.CONFIG_NOT_DICT,
                )
            # Use build() DSL for JSON conversion
            # Reuse to_dict_json helper from output module
            from flext_cli.services.output import to_dict_json, cast_if

            json_dict = cast(
                "t.Json.JsonDict", cast_if(to_dict_json(config_data), dict, config_data)
            )
            return r[t.Json.JsonDict].ok(json_dict)

        except json.JSONDecodeError as e:
            return r[t.Json.JsonDict].fail(
                FlextCliConstants.ErrorMessages.FAILED_LOAD_CONFIG_FROM_FILE.format(
                    file=config_path,
                    error=str(e),
                ),
            )
        except Exception as e:
            return r[t.Json.JsonDict].fail(
                FlextCliConstants.ErrorMessages.LOAD_FAILED.format(error=e),
            )

    @staticmethod
    def save_configuration(
        config_path: str,
        config_data: t.Json.JsonDict,
    ) -> r[bool]:
        """Save configuration to file.

        Args:
            config_path: Path to save configuration file
            config_data: Configuration data to save

        Returns:
            r[bool]: True if saved successfully, failure on error

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
            return r[bool].ok(True)
        except Exception as e:
            return r[bool].fail(
                FlextCliConstants.ErrorMessages.SAVE_FAILED.format(error=e),
            )

    @staticmethod
    def validate_configuration(_config: FlextCliConfig) -> r[bool]:
        """Validate configuration using FlextCliConfig Pydantic model.

        Args:
            _config: FlextCliConfig model instance (validation automatic via Pydantic)

        Returns:
            r[bool]: True if configuration is valid, failure on error

        Note:
            Validation is automatically performed by Pydantic field validators
            when FlextCliConfig instance is created. This method validates the
            configuration is correct and returns success if config is valid.

        """
        # Validation already performed by Pydantic during instantiation
        # If we reach here, config is valid
        return r[bool].ok(True)

    # ==========================================================================
    # PERFORMANCE OPTIMIZATIONS - Integrated into core service
    # ==========================================================================

    def create_ttl_cache(
        self,
        name: str,
        maxsize: int = 128,
        ttl: int = 300,
    ) -> r[TTLCache[str, t.GeneralValueType]]:
        """Create TTL cache with time-based expiration.

        Args:
            name: Cache identifier
            maxsize: Maximum number of items
            ttl: Time-to-live in seconds

        Returns:
            r[TTLCache]: Created cache instance

        """
        try:
            if name in self._caches:
                return r[TTLCache[str, t.GeneralValueType]].fail(
                    f"Cache '{name}' already exists",
                )

            # Validate parameters
            if maxsize < 0:
                return r[TTLCache[str, t.GeneralValueType]].fail(
                    f"Invalid maxsize '{maxsize}': must be non-negative",
                )
            if ttl < 0:
                return r[TTLCache[str, t.GeneralValueType]].fail(
                    f"Invalid ttl '{ttl}': must be non-negative",
                )

            cache: TTLCache[str, t.GeneralValueType] = TTLCache(
                maxsize=maxsize,
                ttl=ttl,
            )
            self._caches[name] = cache
            return r[TTLCache[str, t.GeneralValueType]].ok(cache)
        except Exception as e:
            return r[TTLCache[str, t.GeneralValueType]].fail(str(e))

    def memoize[**P](
        self,
        cache_name: str = "default",
        ttl: int | None = None,
    ) -> Callable[
        [Callable[P, t.GeneralValueType]],
        Callable[P, t.GeneralValueType],
    ]:
        """Create memoization decorator for functions."""

        def decorator(
            func: Callable[P, t.GeneralValueType],
        ) -> Callable[P, t.GeneralValueType]:
            # Use dict.get() to check cache existence
            cache_check = self._caches.get(cache_name)
            if cache_check is None:
                if ttl:
                    self._caches[cache_name] = TTLCache(maxsize=128, ttl=ttl)
                else:
                    self._caches[cache_name] = LRUCache(maxsize=128)

            cache_obj = self._caches[cache_name]
            # Type narrowing: cache_obj is TTLCache or LRUCache from type system
            # No runtime check needed - type system guarantees this

            @functools.wraps(func)
            def wrapper(
                *args: P.args,
                **kwargs: P.kwargs,
            ) -> t.GeneralValueType:
                # Create cache key from function arguments - convert to str for cache
                cache_key_tuple = u.when(
                    condition=kwargs,
                    then_value=(args, tuple(sorted(kwargs.items()))),
                    else_value=args,
                )
                cache_key = str(hash(cache_key_tuple))

                start = time.time()
                try:
                    # Try to get result from cache
                    cached_value = cache_obj[cache_key]
                    # Type cast: cache stores JsonValue but we know it's type T
                    result: t.GeneralValueType = cached_value
                    time_saved = time.time() - start
                    self._cache_stats.record_hit(time_saved)
                    return result
                except KeyError:
                    # Cache miss - compute result and store in cache
                    self._cache_stats.record_miss()
                    result = func(*args, **kwargs)
                    # Type cast: store T as JsonValue in cache
                    cache_obj[cache_key] = result
                    return result

            return wrapper

        return decorator

    def get_cache_stats(self, cache_name: str) -> r[t.Json.JsonDict]:
        """Get statistics for a specific cache."""
        try:
            # Use dict.get() to check cache existence
            cache_check = self._caches.get(cache_name)
            if cache_check is None:
                return r[t.Json.JsonDict].fail(
                    f"Cache '{cache_name}' not found",
                )

            cache_obj = self._caches[cache_name]
            # Type narrowing: cache_obj is TTLCache or LRUCache from type system
            # No isinstance check needed - type system guarantees this
            stats: t.Json.JsonDict = {
                "size": len(cache_obj),
                "maxsize": cache_obj.maxsize,
                "hits": self._cache_stats.cache_hits,
                "misses": self._cache_stats.cache_misses,
                "hit_rate": self._cache_stats.get_hit_rate(),
                "time_saved": self._cache_stats.total_time_saved,
            }
            return r[t.Json.JsonDict].ok(stats)
        except Exception as e:
            return r[t.Json.JsonDict].fail(str(e))

    # ==========================================================================
    # EXECUTOR SUPPORT - Thread pool execution for blocking operations
    # ==========================================================================

    @staticmethod
    def run_in_executor[**P](
        func: Callable[P, t.GeneralValueType],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> r[t.GeneralValueType]:
        """Execute function synchronously (formerly in thread pool).

        Note: This method now executes synchronously. Thread pool execution
        has been removed in v0.10.0 to maintain synchronous-only codebase.
        The API is maintained for backward compatibility but behavior changed.
        """
        # Use r.create_from_callable() for unified error handling (DSL pattern)
        return r.create_from_callable(lambda: func(*args, **kwargs))

    # ==========================================================================
    # PLUGIN SYSTEM - Integrated into core service
    # ==========================================================================

    def register_plugin(self, _plugin: FlextCliProtocols.Cli.CliPlugin) -> r[bool]:
        """Register a plugin with the plugin manager.

        Returns:
            r[bool]: True if plugin registered successfully, failure on error

        """
        try:
            plugin_name = self._plugin_manager.register(_plugin)
            if plugin_name:
                # Protocol check validates all required attributes at runtime
                # Type narrowing: _plugin is already CliPlugin from parameter type
                self._plugins[plugin_name] = _plugin
            return r[bool].ok(True)
        except Exception as e:
            return r[bool].fail(str(e))

    def discover_plugins(self) -> r[list[str]]:
        """Discover and register plugins via entry points."""
        try:
            # Use u.process() for unified plugin discovery (DSL pattern)
            def process_distribution(dist: metadata.Distribution) -> list[str]:
                """Process distribution entry points."""
                discovered: list[str] = []

                def process_entry_point(ep: metadata.EntryPoint) -> str | None:
                    """Process single entry point."""
                    if ep.group != "flext_cli.plugins":
                        return None
                    try:
                        plugin_class = ep.load()
                        plugin_instance = plugin_class()
                        self._plugin_manager.register(plugin_instance)
                        self._plugins[ep.name] = plugin_instance
                        return ep.name
                    except Exception as e:
                        self.logger.debug(
                            "Failed to load plugin",
                            extra={"plugin_name": ep.name, "exception": str(e)},
                        )
                        return None

                # Process entry points using u.process()
                entry_points_result = u.process(
                    list(dist.entry_points),
                    processor=process_entry_point,
                    on_error="skip",
                )
                if entry_points_result.is_success:
                    discovered.extend(
                        cast(
                            "list[str]",
                            u.filter(
                                entry_points_result.value, lambda x: x is not None
                            ),
                        )
                    )
                return discovered

            # Process all distributions using u.process()
            distributions_result = u.process(
                list(metadata.distributions()),
                processor=process_distribution,
                on_error="skip",
            )
            # Flatten list of lists using u.process() with nested processing (DSL pattern)
            if distributions_result.is_success:
                # Use u.process() to flatten nested lists
                def flatten_sublist(sublist: list[str]) -> list[str]:
                    """Return sublist as-is for flattening."""
                    return sublist

                flattened_result = u.process(
                    distributions_result.value,
                    processor=flatten_sublist,
                    on_error="skip",
                )
                # Extract and flatten manually (u.flatten doesn't exist)
                discovered_plugins = [
                    item
                    for sublist in (u.val(flattened_result, default=[]))
                    for item in sublist
                ]
            else:
                discovered_plugins = []

            return r[list[str]].ok(discovered_plugins)
        except Exception as e:
            return r[list[str]].fail(str(e))

    def call_plugin_hook(
        self,
        hook_name: str,
        **kwargs: t.GeneralValueType,
    ) -> r[list[t.GeneralValueType]]:
        """Call a plugin hook with arguments."""
        try:
            hook_caller = u.get(self._plugin_manager.hook, hook_name, default=None)

            if hook_caller is None:
                return r[list[t.GeneralValueType]].fail(
                    f"Hook '{hook_name}' not found",
                )

            results = hook_caller(**kwargs)
            # Fast-fail: hook must return list or None (converted to empty list)
            # No fallback to fake data
            if results is None:
                return r[list[t.GeneralValueType]].ok([])
            if not FlextRuntime.is_list_like(results):
                # Single result - wrap in list (not a fallback, valid conversion)
                return r[list[t.GeneralValueType]].ok([results])

            # Use build() DSL: map → ensure dict → transform to JSON
            # Reuse to_json helper from output module
            from flext_cli.services.output import to_json

            results_list = cast(
                "list[t.GeneralValueType]",
                u.map(list(results), mapper=to_json),
            )
            return r[list[t.GeneralValueType]].ok(results_list)
        except Exception as e:
            return r[list[t.GeneralValueType]].fail(str(e))

    # ==========================================================================
    # END OF CORE CLI SERVICE METHODS
    # ==========================================================================
    # NOTE: File operations, JSON/YAML parsing, validation, HTTP requests,
    # and output formatting are now accessed directly through their respective
    # services via the FlextCli facade:
    #   - File operations: Use cli.file_tools.* directly
    #   - Validation: Use u.validate() with u.V.* validators from flext-core
    #   - HTTP: Use flext-api domain library
    #   - Output: Use cli.output.* directly
    # ==========================================================================


__all__ = ["FlextCliCore"]
