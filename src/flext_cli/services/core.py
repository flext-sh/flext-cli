"""Core service for commands, sessions, and configuration of flext-cli.

Groups command registration/execution, configuration profiles, sessions, and plugins,
returning `r[T]` for operations consumed by the facade `FlextCli`.

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
from typing import override

import pluggy
from cachetools import LRUCache, TTLCache

from flext_core import FlextDecorators, FlextRuntime, FlextUtilities, r
from flext_cli.base import FlextCliServiceBase
from flext_cli.constants import c
from flext_cli.models import (
    m,
)
from flext_cli.protocols import p
from flext_cli.services.output import FlextCliOutput
from flext_cli.settings import FlextCliSettings
from flext_cli.typings import t
from flext_cli.utilities import FlextCliUtilities


class FlextCliCore(FlextCliServiceBase):
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
    validada (`FlextCliSettings`), gerencia sessões e plugins e expõe
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
            # Use conditional expression to avoid division by zero
            # FlextCliUtilities.when() evaluates both values, so we can't use it here
            return self.cache_hits / total if total > 0 else 0.0

    # Logger is provided by FlextMixins mixin

    # Private attributes for internal state management
    # These are set via object.__setattr__ in __init__ to support frozen parent models
    _cli_config: dict[str, t.GeneralValueType]
    _commands: dict[str, dict[str, t.GeneralValueType]]
    _plugins: dict[str, p.Cli.CliPlugin]
    _sessions: dict[str, t.GeneralValueType]
    _session_active: bool
    _session_config: dict[str, t.GeneralValueType]
    _session_start_time: str
    _caches: dict[
        str,
        TTLCache[str, t.GeneralValueType] | LRUCache[str, t.GeneralValueType],
    ]
    _cache_stats: _CacheStats
    _plugin_manager: pluggy.PluginManager

    def __init__(
        self,
        config: Mapping[str, t.GeneralValueType] | None = None,
    ) -> None:
        """Initialize CLI core with optional configuration seed values.

        Args:
            config: Optional configuration dictionary for CLI-specific settings
                (stored separately, not passed to parent FlextService.__init__)

        """
        # FlextService.__init__ accepts **data: t.GeneralValueType
        # FlextCliServiceBase extends FlextService[dict[str, t.GeneralValueType]]
        # The generic type parameter TDomainResult doesn't affect __init__ signature
        # Note: config is CLI-specific and stored separately, not passed to parent
        # because FlextService uses Pydantic with extra="forbid"
        # _data is unused but kept for API compatibility
        super().__init__()

        # Phase 1 Enhancement: Context enrichment happens automatically in FlextService.__init__
        # The parent class already calls _enrich_context with service metadata
        # Logger and container are inherited from FlextService via FlextMixins

        # Type-safe configuration initialization
        # Store CLI-specific config as dict (base class _config is FlextSettings | None)
        # Use mutable dict for CLI-specific configuration dictionary
        # Use FlextRuntime.is_dict_like for type checking
        # Use object.__setattr__ for private attributes in case parent is frozen
        object.__setattr__(
            self,
            "_cli_config",
            dict(config)
            if config is not None and FlextRuntime.is_dict_like(config)
            else {},
        )
        object.__setattr__(self, "_commands", {})
        # Note: stores plugin objects implementing CliPlugin protocol
        object.__setattr__(self, "_plugins", {})
        object.__setattr__(self, "_sessions", {})
        object.__setattr__(self, "_session_active", False)

        # Performance and async integration
        # Note: stores cache objects (TTLCache/LRUCache), not JsonValue
        # Cache types are from external library, using generic types
        # Use object.__setattr__ for private attributes in case parent is frozen
        object.__setattr__(
            self,
            "_caches",
            {},
        )
        object.__setattr__(self, "_cache_stats", self._CacheStats())
        object.__setattr__(self, "_plugin_manager", pluggy.PluginManager("flext_cli"))

        # Type narrowing: is_dict_like ensures config is dict-like
        config_dict: Mapping[str, t.GeneralValueType] | None = (
            config if FlextRuntime.is_dict_like(config) else None
        )
        self.logger.debug(
            "Initialized CLI core service",
            operation="__init__",
            has_config=config is not None,
            config_keys=list(config_dict.keys()) if config_dict else None,
            commands_count=0,
            plugins_count=0,
            sessions_count=0,
            source="flext-cli/src/flext_cli/core.py",
        )

    # ==========================================================================
    # CLI COMMAND MANAGEMENT - Using t.FlextCliCommandT types
    # ==========================================================================

    def register_command(
        self,
        command: p.Cli.Command,
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
                c.Cli.ErrorMessages.COMMAND_NAME_EMPTY,
            )

        try:
            # Type narrowing: check if command is instance of CliCommand (not just protocol)
            if not isinstance(command, m.Cli.CliCommand):
                self.logger.error(
                    "FAILED CLI command registration - command is not CliCommand instance",
                    command_name=command.name,
                    command_type=type(command).__name__,
                    operation="register_command",
                    source="flext-cli/src/flext_cli/core.py",
                )
                return r[bool].fail(
                    c.Cli.ErrorMessages.COMMAND_REGISTRATION_FAILED.format(
                        command=command.name,
                        error="Command must be CliCommand instance",
                    ),
                )
            # Build command_data dict without using model_dump() to avoid DomainEvent forward reference error
            # Extract model fields directly instead of calling model_dump() which triggers model_rebuild()
            command_data: dict[str, t.GeneralValueType] = {
                "name": command.name,
                "unique_id": command.unique_id,
                "status": command.status.value
                if hasattr(command.status, "value")
                else str(command.status),
                "created_at": command.created_at.isoformat()
                if hasattr(command.created_at, "isoformat")
                else str(command.created_at),
                "description": command.description or "",
                "command_line": getattr(command, "command_line", ""),
                "usage": getattr(command, "usage", ""),
                "entry_point": getattr(command, "entry_point", ""),
                "args": list(getattr(command, "args", [])),
            }
            self._commands[command.name] = command_data

            # Log successful registration with detailed context
            self.logger.debug(
                "Command registration completed successfully",
                command_name=command.name,
                # Business Rule: Dict keys MUST be extracted using list() constructor (Python 3.13+)
                # Architecture: Direct list() conversion is type-safe and efficient
                # Audit Implication: Key extraction is deterministic and safe
                # Python 3.13: model_dump() always returns dict, isinstance check is unnecessary
                command_data_keys=list(command_data.keys()),
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
                c.Cli.ErrorMessages.COMMAND_REGISTRATION_FAILED.format(
                    command=command.name,
                    error=str(e),
                ),
            )

    def get_command(
        self,
        name: str,
    ) -> r[dict[str, t.GeneralValueType]]:
        """Retrieve registered command definition.

        Args:
            name: Command identifier to retrieve

        Returns:
            r[dict[str, t.GeneralValueType]]: Command definition or error

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
            return r[dict[str, t.GeneralValueType]].fail(
                c.Cli.ErrorMessages.COMMAND_NAME_EMPTY,
            )

        # Use mapper().get() to check command existence
        command_check = FlextUtilities.mapper().get(self._commands, name)
        if command_check is None:
            self.logger.warning(
                "Command not found in registry",
                operation="get_command",
                command_name=name,
                available_commands=list(self._commands.keys()),
                consequence="Command retrieval will fail",
                source="flext-cli/src/flext_cli/core.py",
            )
            return r[dict[str, t.GeneralValueType]].fail(
                c.Cli.ErrorMessages.COMMAND_NOT_FOUND.format(name=name),
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
                    # Business Rule: Dict keys MUST be extracted using list() constructor (Python 3.13+)
                    # Architecture: Direct list() conversion is type-safe and efficient
                    # Audit Implication: Key extraction is deterministic and safe
                    # Python 3.13: command_def from dict already has .keys(), isinstance check is unnecessary
                    definition_keys=list(command_def.keys()),
                    source="flext-cli/src/flext_cli/core.py",
                )

                # command_def is already JsonDict - no conversion needed
                return r[dict[str, t.GeneralValueType]].ok(command_def)

            self.logger.error(
                "FAILED to retrieve command - invalid command type",
                operation="get_command",
                command_name=name,
                command_def_type=type(command_def).__name__,
                consequence="Command retrieval aborted",
                source="flext-cli/src/flext_cli/core.py",
            )
            return r[dict[str, t.GeneralValueType]].fail(
                c.Cli.ErrorMessages.INVALID_COMMAND_TYPE.format(name=name),
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
            return r[dict[str, t.GeneralValueType]].fail(
                c.Cli.ErrorMessages.COMMAND_RETRIEVAL_FAILED.format(
                    error=e,
                ),
            )

    def _build_execution_context(
        self,
        context: dict[str, t.GeneralValueType] | list[str] | None,
    ) -> dict[str, t.GeneralValueType]:
        """Build execution context from various input formats."""
        if context is None:
            return {}
        if FlextRuntime.is_list_like(context):
            # Use build() DSL: process → normalize → ensure JSON-compatible
            # Reuse helpers from output module to avoid duplication
            process_result = FlextCliUtilities.process(
                list(context),
                processor=FlextCliOutput.norm_json,
                on_error="skip",
            )
            # Python 3.13: Direct attribute access - unwrap() provides safe access
            context_list_raw = process_result.value or []
            context_list: list[t.GeneralValueType] = (
                context_list_raw if isinstance(context_list_raw, list) else []
            )
            return self._build_context_from_list(context_list)
        # Use FlextRuntime.is_dict_like for type checking
        # Type narrowing: is_dict_like ensures context is dict-like
        if FlextRuntime.is_dict_like(context):
            # Context is already CliCommand.CommandContext compatible - direct assignment
            # Type assertion: is_dict_like ensures it's Mapping-like
            if isinstance(context, Mapping):
                return dict(context)
            # If it's not a Mapping but is_dict_like returned True, it might be a dict-like object
            # But if it's a list, we can't convert it to dict - return empty dict
            if isinstance(context, list):
                return {}
            # Try to convert dict-like object to dict
            if hasattr(context, "__iter__") and not isinstance(context, (str, bytes)):
                try:
                    # Only convert if it's actually dict-like (has items() method)
                    if hasattr(context, "items"):
                        return dict(context.items())
                except (TypeError, ValueError):
                    pass
            return {}
        return {}

    def execute_command(
        self,
        name: str,
        context: dict[str, t.GeneralValueType] | list[str] | None = None,
        timeout: float | None = None,
    ) -> r[dict[str, t.GeneralValueType]]:
        """Execute registered command with context."""
        self.logger.info("STARTING CLI command execution", command_name=name)

        command_result = self.get_command(name)
        if command_result.is_failure:
            self.logger.error("FAILED - command not found", command_name=name)
            # Python 3.13: Direct attribute access - more elegant and type-safe
            return r[dict[str, t.GeneralValueType]].fail(
                command_result.error or "Command not found",
            )

        try:
            execution_context = self._build_execution_context(context)
            result_dict: dict[str, t.GeneralValueType] = {
                c.Cli.DictKeys.COMMAND: name,
                c.Cli.DictKeys.STATUS: True,
                c.Cli.DictKeys.TIMESTAMP: FlextCliUtilities.generate("timestamp"),
                c.Cli.DictKeys.TIMEOUT: timeout,
                c.Cli.DictKeys.CONTEXT: dict(execution_context),
            }
            self.logger.info("COMPLETED CLI command execution", command_name=name)
            return r[dict[str, t.GeneralValueType]].ok(result_dict)

        except Exception as e:
            self.logger.exception("FAILED CLI command execution", command_name=name)
            return r[dict[str, t.GeneralValueType]].fail(
                c.Cli.ErrorMessages.COMMAND_EXECUTION_FAILED.format(error=e),
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
                    c.Cli.ErrorMessages.COMMAND_LISTING_FAILED.format(
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
    ) -> dict[str, t.GeneralValueType]:
        """Build command context from list of arguments.

        Business Rule:
        ──────────────
        Static method - converts argument list to JSON-compatible dict.
        No instance state needed.
        """
        # All values in args are already t.GeneralValueType compatible - direct assignment
        return {c.Cli.DictKeys.ARGS: args}

    # ==========================================================================
    # CLI CONFIGURATION MANAGEMENT - Using t.Configuration types
    # ==========================================================================

    def _log_config_update(self) -> None:
        """Log configuration update - direct logger usage."""
        self.logger.info(c.Cli.LogMessages.CLI_CONFIG_UPDATED)

    def _validate_config_input(
        self,
        config: Mapping[str, t.GeneralValueType],
    ) -> r[dict[str, t.GeneralValueType]]:
        """Validate input configuration for update operations."""
        if not config:
            self.logger.warning(
                "Configuration input is empty",
                operation="update_configuration",
                consequence="Configuration update will fail",
                source="flext-cli/src/flext_cli/core.py",
            )
            return r[dict[str, t.GeneralValueType]].fail(
                c.Cli.ErrorMessages.CONFIG_NOT_DICT,
            )

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
            return r[dict[str, t.GeneralValueType]].fail(
                c.Cli.ErrorMessages.CONFIG_NOT_DICT,
            )
        # Reuse to_dict_json helper from output module
        json_config = FlextCliOutput.to_dict_json(config)
        return r[dict[str, t.GeneralValueType]].ok(
            FlextCliOutput.cast_if(json_config, dict, config),
        )

    def _validate_existing_config(
        self,
    ) -> r[dict[str, t.GeneralValueType]]:
        """Validate existing configuration state."""
        # self._cli_config is dict[str, t.GeneralValueType] - return as JsonDict
        if self._cli_config:
            return r[dict[str, t.GeneralValueType]].ok(self._cli_config)
        return r[dict[str, t.GeneralValueType]].fail(
            c.Cli.ErrorMessages.CONFIG_NOT_INITIALIZED,
        )

    def _merge_configurations(
        self,
        valid_config: dict[str, t.GeneralValueType],
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
                # Python 3.13: Direct attribute access - more elegant and type-safe
                error_msg = existing_config_result.error or ""
                self.logger.warning(
                    "Existing configuration validation failed",
                    operation="update_configuration",
                    error=error_msg,
                    consequence="Configuration merge will fail",
                    source="flext-cli/src/flext_cli/core.py",
                )
                return r[bool].fail(
                    existing_config_result.error or "Config validation failed",
                )

            # Python 3.13: Direct attribute access - unwrap() provides safe access
            # Convert Mapping to dict for mutability
            existing_config_raw: dict[str, t.GeneralValueType] = dict(
                existing_config_result.value or {},
            )
            # Convert to mutable dict for merging
            existing_config: dict[str, t.GeneralValueType] = (
                dict(existing_config_raw)
                if FlextRuntime.is_dict_like(existing_config_raw)
                else {}
            )
            # Use build() DSL: ensure dict → transform to JSON
            # Reuse to_dict_json helper from output module
            transformed_config = FlextCliOutput.to_dict_json(valid_config)
            # Use FlextCliUtilities.merge for intelligent deep merge
            merge_result = FlextCliUtilities.merge(
                existing_config,
                transformed_config,
                strategy="deep",  # Deep merge preserves nested structures
            )
            if merge_result.is_failure:
                # Python 3.13: Direct attribute access - more elegant and type-safe
                return r[bool].fail(
                    merge_result.error or "Failed to merge config",
                )
            # Update internal _cli_config with merged result
            # Business Rule: Frozen model attributes MUST be set using object.__setattr__()
            # Architecture: Pydantic frozen models require object.__setattr__() for attribute mutation
            # Python 3.13: Direct attribute access - unwrap() provides safe access
            merged_config: dict[str, t.GeneralValueType] = merge_result.value or {}
            # merged_config is guaranteed to be not None by FlextCliUtilities.val default
            object.__setattr__(self, "_cli_config", merged_config)

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
                c.Cli.ErrorMessages.CONFIG_UPDATE_FAILED.format(error=e),
            )

    def update_configuration(
        self,
        config: Mapping[str, t.GeneralValueType],
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
            return r[bool].fail(c.Cli.ErrorMessages.CONFIG_NOT_DICT)
        # Reuse to_dict_json helper from output module
        # Python 3.13: to_dict_json() always returns dict, isinstance check is unnecessary
        validated_config_input: dict[str, t.GeneralValueType] = (
            FlextCliOutput.to_dict_json(config)
        )
        config_result = self._validate_config_input(validated_config_input)
        if config_result.is_failure:
            # Python 3.13: Direct attribute access - more elegant and type-safe
            return r[bool].fail(
                config_result.error or "Configuration validation failed",
            )

        # Python 3.13: Direct attribute access - unwrap() provides safe access
        # Convert Mapping to dict for mutability
        merged_config_val: dict[str, t.GeneralValueType] = dict(
            config_result.value or {},
        )
        # merged_config_val is guaranteed to be not None by FlextCliUtilities.val default
        return self._merge_configurations(merged_config_val)

    def get_configuration(
        self,
    ) -> r[dict[str, t.GeneralValueType]]:
        """Get current CLI configuration using functional composition.

        Retrieves configuration with validation and error handling.
        Uses railway pattern to ensure configuration integrity.

        Returns:
            r[dict[str, t.GeneralValueType]]: Current configuration or error with details

        """

        # Functional configuration retrieval with railway pattern
        def validate_config_state() -> r[dict[str, t.GeneralValueType]]:
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

                    # self._cli_config is dict[str, t.GeneralValueType] - return as JsonDict
                    return r[dict[str, t.GeneralValueType]].ok(
                        self._cli_config,
                    )

                self.logger.warning(
                    "Configuration not initialized",
                    operation="get_configuration",
                    consequence="Configuration retrieval will fail",
                    source="flext-cli/src/flext_cli/core.py",
                )
                return r[dict[str, t.GeneralValueType]].fail(
                    c.Cli.ErrorMessages.CONFIG_NOT_INITIALIZED,
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
                return r[dict[str, t.GeneralValueType]].fail(
                    c.Cli.ErrorMessages.CONFIG_RETRIEVAL_FAILED.format(
                        error=e,
                    ),
                )

        # Railway pattern: validate and return configuration
        return validate_config_state()

    def create_profile(
        self,
        name: str,
        profile_config: dict[str, t.GeneralValueType],
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
                c.Cli.ErrorMessages.PROFILE_NAME_EMPTY,
            )

        if not profile_config:
            return r[bool].fail(
                c.Cli.ErrorMessages.PROFILE_CONFIG_NOT_DICT,
            )

        if not (FlextRuntime.is_dict_like(self._cli_config) and self._cli_config):
            return r[bool].fail(
                c.Cli.ErrorMessages.CONFIG_NOT_INITIALIZED,
            )

        # Store profile
        try:
            # Ensure config is mutable dict
            config: dict[str, t.GeneralValueType] = dict(self._cli_config)

            # Use FlextCliUtilities.extract to safely get profiles section with default
            # FlextCliUtilities.extract returns RuntimeResult, convert to FlextResult
            # Type annotation: default={} makes T = dict[str, t.GeneralValueType]
            # Call extract method - type is inferred from default parameter
            default_dict: dict[str, t.GeneralValueType] = {}
            profiles_result_raw = FlextCliUtilities.extract(
                config,
                c.Cli.DictKeys.PROFILES,  # path parameter
                default=default_dict,
            )
            # Convert RuntimeResult to FlextResult
            profiles_result_typed: r[dict[str, t.GeneralValueType] | None] = (
                r[dict[str, t.GeneralValueType] | None].ok(profiles_result_raw.value)
                if profiles_result_raw.is_success
                else r[dict[str, t.GeneralValueType] | None].fail(
                    profiles_result_raw.error or "Failed to extract profiles",
                )
            )
            # Python 3.13: Direct attribute access - unwrap() provides safe access
            profiles_section_raw: dict[str, t.GeneralValueType] = (
                profiles_result_typed.value or {}
            )
            # Python 3.13: profiles_section_raw is already dict, isinstance check is unnecessary
            profiles_section: dict[str, t.GeneralValueType] = (
                profiles_section_raw
                if FlextRuntime.is_dict_like(profiles_section_raw)
                else {}
            )
            profiles_section[name] = profile_config
            # Update config with modified profiles section
            config[c.Cli.DictKeys.PROFILES] = profiles_section
            # Update internal _cli_config
            # Business Rule: Frozen model attributes MUST be set using object.__setattr__()
            object.__setattr__(self, "_cli_config", config)
            self.logger.info(
                c.Cli.LogMessages.PROFILE_CREATED.format(name=name),
            )
            return r[bool].ok(True)

        except Exception as e:
            return r[bool].fail(
                c.Cli.ErrorMessages.PROFILE_CREATION_FAILED.format(error=e),
            )

    # ==========================================================================
    # SESSION MANAGEMENT - Using t.Configuration types
    # ==========================================================================

    def start_session(
        self,
        session_config: dict[str, t.GeneralValueType] | None = None,
    ) -> r[bool]:
        """Start CLI session with configuration.

        Args:
            session_config: Optional session-specific configuration

        Returns:
            r[bool]: True if session started successfully, failure on error

        """
        if self._session_active:
            return r[bool].fail(
                c.Cli.ErrorMessages.SESSION_ALREADY_ACTIVE,
            )

        try:
            # Initialize session with CLI-specific configuration
            # Validate explicitly - no fallback to empty dict
            # Business Rule: Frozen model attributes MUST be set using object.__setattr__()
            if session_config is not None:
                object.__setattr__(self, "_session_config", session_config)
            else:
                object.__setattr__(self, "_session_config", {})
            object.__setattr__(self, "_session_active", True)
            # Generate ISO format timestamp for session tracking
            object.__setattr__(
                self,
                "_session_start_time",
                datetime.now(UTC).isoformat(),
            )

            # Log session start - direct logger usage
            self.logger.info(c.Cli.LogMessages.SESSION_STARTED)

            return r[bool].ok(True)

        except Exception as e:
            return r[bool].fail(
                c.Cli.ErrorMessages.SESSION_START_FAILED.format(error=e),
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
                    c.Cli.ErrorMessages.NO_ACTIVE_SESSION,
                )
            # Business Rule: Frozen model attributes MUST be set using object.__setattr__()
            object.__setattr__(self, "_session_active", False)
            if hasattr(self, c.Cli.PrivateAttributes.SESSION_CONFIG):
                delattr(self, c.Cli.PrivateAttributes.SESSION_CONFIG)
            if hasattr(self, c.Cli.PrivateAttributes.SESSION_START_TIME):
                delattr(self, c.Cli.PrivateAttributes.SESSION_START_TIME)

            self.logger.debug(
                "Session terminated successfully",
                operation="end_session",
                total_sessions=len(self._sessions),
                source="flext-cli/src/flext_cli/core.py",
            )

            # Log session end - direct logger usage
            self.logger.info(c.Cli.LogMessages.SESSION_ENDED)

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
                c.Cli.ErrorMessages.SESSION_END_FAILED.format(error=e),
            )

    def is_session_active(self) -> bool:
        """Check if CLI session is currently active.

        Returns:
            bool: True if session is active, False otherwise

        """
        return self._session_active

    # ==========================================================================
    # STATISTICS AND MONITORING - Using t.Data types
    # ==========================================================================

    def get_command_statistics(
        self,
    ) -> r[dict[str, t.GeneralValueType]]:
        """Get command usage statistics using CLI-specific data types.

        Returns:
            r[dict[str, t.GeneralValueType]]: Statistics data or error

        Pydantic 2 Modernization:
            - Uses CommandStatistics model internally
            - Serializes to dict for API compatibility
            - Type-safe with automatic validation

        """
        try:
            # Create Pydantic model with type-safe fields
            # Note: Currently assumes all registered commands are successful
            # Failure tracking requires execution result storage (future enhancement)
            stats_model = m.Cli.CommandStatistics(
                total_commands=len(self._commands),
                successful_commands=len(self._commands),
                failed_commands=0,
            )
            # model_dump() already returns dict with JSON-compatible values
            # Direct assignment if model fields are already t.GeneralValueType compatible
            stats_dict: dict[str, t.GeneralValueType] = stats_model.model_dump()
            return r[dict[str, t.GeneralValueType]].ok(stats_dict)
        except Exception as e:
            return r[dict[str, t.GeneralValueType]].fail(
                c.Cli.ErrorMessages.CLI_EXECUTION_ERROR.format(error=e),
            )

    def get_service_info(self) -> Mapping[str, t.FlexibleValue]:
        """Get comprehensive service information.

        Returns:
            t.JsonDict: Service information (matches FlextService signature)

        """
        try:
            # Collect comprehensive service information
            commands_count = len(self._commands)
            # Business Rule: Dict keys MUST be extracted using list() constructor (Python 3.13+)
            # Architecture: Direct list() conversion is type-safe and efficient
            # Audit Implication: Key extraction is deterministic and safe
            # Python 3.13: _cli_config is already typed as dict, isinstance check is unnecessary
            config_keys = list(self._cli_config.keys())

            # Convert config_keys to Sequence[str] for FlexibleValue compatibility
            config_keys_list: list[str] = list(config_keys) if config_keys else []

            info_data: dict[str, t.FlexibleValue] = {
                c.Cli.DictKeys.SERVICE: c.Cli.FLEXT_CLI,
                c.Cli.CoreServiceDictKeys.COMMANDS_REGISTERED: commands_count,
                c.Cli.CoreServiceDictKeys.CONFIGURATION_SECTIONS: config_keys_list,
                c.Cli.DictKeys.STATUS: (
                    c.Cli.ServiceStatus.OPERATIONAL.value
                    if self._session_active
                    else c.Cli.ServiceStatus.AVAILABLE.value
                ),
                c.Cli.CoreServiceDictKeys.SERVICE_READY: commands_count > 0,
                c.Cli.DictKeys.TIMESTAMP: FlextCliUtilities.generate("timestamp"),
            }

            # Return Mapping[str, FlexibleValue] to match base class signature
            return info_data

        except Exception as e:
            self.logger.exception(
                c.Cli.CoreServiceLogMessages.SERVICE_INFO_COLLECTION_FAILED,
            )
            return {c.Cli.DictKeys.MESSAGE: str(e)}

    def get_session_statistics(
        self,
    ) -> r[dict[str, t.GeneralValueType]]:
        """Get session-specific statistics using CLI data types.

        Returns:
            r[dict[str, t.GeneralValueType]]: Session statistics or error

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
            return r[dict[str, t.GeneralValueType]].fail(
                c.Cli.ErrorMessages.NO_ACTIVE_SESSION,
            )

        try:
            # Calculate session duration if session is active
            session_duration = c.Cli.CoreServiceDefaults.SESSION_DURATION_INIT
            if (
                hasattr(self, c.Cli.PrivateAttributes.SESSION_START_TIME)
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
            stats_model = m.Cli.SessionStatistics(
                commands_executed=len(self._commands),
                errors_count=0,
                session_duration_seconds=session_duration,
            )

            # model_dump() already returns dict with JSON-compatible values
            stats_dict: dict[str, t.GeneralValueType] = stats_model.model_dump()

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

            return r[dict[str, t.GeneralValueType]].ok(stats_dict)

        except Exception as e:
            self.logger.exception(
                "FAILED to collect session statistics - operation aborted",
                operation="get_session_statistics",
                error=str(e),
                error_type=type(e).__name__,
                consequence="Statistics unavailable",
                source="flext-cli/src/flext_cli/core.py",
            )
            return r[dict[str, t.GeneralValueType]].fail(
                c.Cli.CoreServiceLogMessages.SESSION_STATS_COLLECTION_FAILED.format(
                    error=e,
                ),
            )

    # ==========================================================================
    # SERVICE EXECUTION METHODS - FlextService protocol implementation
    # ==========================================================================

    @override
    @FlextDecorators.log_operation("cli_core_health_check")
    @FlextDecorators.track_performance()
    def execute(self) -> r[dict[str, t.GeneralValueType]]:
        """Execute CLI service operations.

        FlextDecorators automatically:
        - Log operation start/completion/failure
        - Track performance metrics
        - Handle context propagation (correlation_id, operation_name)

        Returns:
            r[dict[str, t.GeneralValueType]]: Service execution result

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
            # Business Rule: Dict keys MUST be extracted using list() constructor (Python 3.13+)
            # Architecture: Direct list() conversion is type-safe and efficient
            # Audit Implication: Key extraction is deterministic and safe
            # No additional parameters
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
                return r[dict[str, t.GeneralValueType]].fail(
                    c.Cli.ErrorMessages.COMMAND_LISTING_FAILED.format(
                        error="No commands registered",
                    ),
                )

            # Create Pydantic model with type-safe fields
            result_model = m.Cli.ServiceExecutionResult(
                service_executed=True,
                commands_count=len(self._commands),
                session_active=self._session_active,
                execution_timestamp=FlextCliUtilities.generate("timestamp"),
                service_ready=True,
            )

            # model_dump() already returns dict with JSON-compatible values
            status_dict: dict[str, t.GeneralValueType] = result_model.model_dump()

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

            return r[dict[str, t.GeneralValueType]].ok(status_dict)

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
            return r[dict[str, t.GeneralValueType]].fail(
                c.Cli.CoreServiceLogMessages.SERVICE_EXECUTION_FAILED.format(
                    error=e,
                ),
            )

    def execute_cli_command_with_context(
        self,
        command_name: str,
        user_id: str | None = None,
        **context_data: t.GeneralValueType,
    ) -> r[dict[str, t.GeneralValueType]]:
        """Execute CLI command with automatic context enrichment (Phase 1 pattern).

        Demonstrates the new execute_with_context_enrichment() pattern from flext-core
        Phase 1 architectural enhancement for CLI operations.

        Args:
            command_name: Name of the command to execute
            user_id: Optional user ID for audit context
            **context_data: Additional context data for enriched logging

        Returns:
            r[dict[str, t.GeneralValueType]]: Command execution result

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
                f"{c.Cli.CoreServiceDefaults.CLI_COMMAND_PREFIX}{command_name}"
            ),
            user_id=user_id,
            **context_data,
        )

        # Enrich context with additional data
        self._enrich_context(
            command_name=command_name,
            operation_type=c.Cli.CoreServiceDefaults.OPERATION_TYPE_CLI_COMMAND,
            **context_data,
        )

        # Create Pydantic model with type-safe fields
        # Use default value if user_id is None (model requires str, not str | None)
        effective_user_id = (
            user_id if user_id is not None else c.Cli.CliSessionDefaults.DEFAULT_USER_ID
        )
        result_model = m.Cli.CommandExecutionContextResult(
            command_name=command_name,
            exit_code=0,  # Success
            output="",  # No output for context result
            context={
                **dict(context_data),  # Convert kwargs to dict
                "user_id": effective_user_id,
                "timestamp": FlextCliUtilities.generate("timestamp"),
            },
        )

        # model_dump() already returns dict with JSON-compatible values
        result_dict: dict[str, t.GeneralValueType] = result_model.model_dump()
        return r[dict[str, t.GeneralValueType]].ok(result_dict)

    def health_check(self) -> r[Mapping[str, t.GeneralValueType]]:
        """Perform health check on the CLI service.

        Returns:
            r[dict[str, t.GeneralValueType]]: Health check result

        """
        try:
            return r[dict[str, t.GeneralValueType]].ok({
                c.Cli.DictKeys.STATUS: c.Cli.ServiceStatus.HEALTHY.value,
                c.Cli.CoreServiceDictKeys.COMMANDS_COUNT: len(
                    self._commands,
                ),
                c.Cli.CoreServiceDictKeys.SESSION_ACTIVE: self._session_active,
                c.Cli.DictKeys.TIMESTAMP: FlextCliUtilities.generate("timestamp"),
            })
        except Exception as e:
            return r[dict[str, t.GeneralValueType]].fail(
                c.Cli.ErrorMessages.CLI_EXECUTION_ERROR.format(error=e),
            )

    def get_config(self) -> r[Mapping[str, t.GeneralValueType]]:
        """Get current service configuration.

        Returns:
            r[dict[str, t.GeneralValueType]]: Configuration data

        """
        try:
            # Type narrowing: self._cli_config is dict[str, t.GeneralValueType] - return as JsonDict
            # Fast-fail if config is empty - no fallback
            if not self._cli_config:
                return r[dict[str, t.GeneralValueType]].fail(
                    c.Cli.ErrorMessages.CONFIG_NOT_INITIALIZED,
                )
            return r[dict[str, t.GeneralValueType]].ok(self._cli_config)
        except Exception as e:
            return r[dict[str, t.GeneralValueType]].fail(
                c.Cli.ErrorMessages.CONFIG_RETRIEVAL_FAILED.format(error=e),
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
            # Python 3.13: Mapping has .keys(), isinstance check is unnecessary - just check None
            return r[list[str]].ok(
                list(data_dict.keys()) if data_dict is not None else [],
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
            c.Cli.ErrorMessages.COMMAND_LISTING_FAILED,
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
                c.Cli.ErrorMessages.FAILED_GET_LOADED_PLUGINS.format(
                    error=e,
                ),
            )

    def get_sessions(self) -> r[list[str]]:
        """Get list of active sessions.

        Returns:
            r[list[str]]: List of session IDs

        """
        # Convert _sessions (JsonDict) to Mapping[str, t.GeneralValueType] for type compatibility
        # Type narrowing: ensure all values are t.GeneralValueType compatible
        sessions_dict: Mapping[str, t.GeneralValueType] | None = None
        # Use build() DSL for JSON conversion
        # Reuse to_dict_json helper from output module
        if FlextRuntime.is_dict_like(self._sessions):
            sessions_dict = FlextCliOutput.to_dict_json(dict(self._sessions)) or None
        return self._get_dict_keys(
            sessions_dict,
            c.Cli.ErrorMessages.SESSION_END_FAILED,
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
        return r[list[str]].ok(c.Cli.OUTPUT_FORMATS_LIST)

    @staticmethod
    def _validate_config_path(config_path: str) -> r[Path]:
        """Validate config path and return Path object if valid."""
        if not config_path:
            return r[Path].fail(
                c.Cli.ErrorMessages.CONFIG_FILE_NOT_FOUND.format(file=""),
            )
        config_file = Path(config_path)
        if not config_file.exists():
            return r[Path].fail(
                c.Cli.ErrorMessages.CONFIG_FILE_NOT_FOUND.format(file=config_path),
            )
        if not config_file.is_file():
            return r[Path].fail(
                c.Cli.ErrorMessages.FAILED_LOAD_CONFIG_FROM_FILE.format(
                    file=config_path,
                    error=c.Cli.ErrorMessages.CONFIG_NOT_DICT,
                ),
            )
        return r[Path].ok(config_file)

    def load_configuration(
        self,
        config_path: str,
    ) -> r[Mapping[str, t.GeneralValueType]]:
        """Load configuration from file."""
        path_result = self._validate_config_path(config_path)
        if path_result.is_failure:
            # Python 3.13: Direct attribute access - more elegant and type-safe
            return r[dict[str, t.GeneralValueType]].fail(
                path_result.error or "Invalid path",
            )

        try:
            # Python 3.13: Direct attribute access - unwrap() provides safe access
            config_file: Path = path_result.value or Path()
            content = config_file.read_text(
                encoding=c.Cli.Utilities.DEFAULT_ENCODING,
            )
            config_data = json.loads(content)

            if not FlextRuntime.is_dict_like(config_data):
                return r[dict[str, t.GeneralValueType]].fail(
                    c.Cli.ErrorMessages.CONFIG_NOT_DICT,
                )
            # Python 3.13: to_dict_json() always returns dict, cast_if and isinstance are unnecessary
            # Reuse to_dict_json helper from output module
            json_dict: dict[str, t.GeneralValueType] = FlextCliOutput.to_dict_json(
                config_data,
            )
            return r[dict[str, t.GeneralValueType]].ok(json_dict)

        except json.JSONDecodeError as e:
            return r[dict[str, t.GeneralValueType]].fail(
                c.Cli.ErrorMessages.FAILED_LOAD_CONFIG_FROM_FILE.format(
                    file=config_path,
                    error=str(e),
                ),
            )
        except Exception as e:
            return r[dict[str, t.GeneralValueType]].fail(
                c.Cli.ErrorMessages.LOAD_FAILED.format(error=e),
            )

    @staticmethod
    def save_configuration(
        config_path: str,
        config_data: Mapping[str, t.GeneralValueType],
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
                c.Cli.FileIODefaults.FILE_WRITE_MODE,
                encoding=c.Cli.Utilities.DEFAULT_ENCODING,
            ) as f:
                json.dump(
                    config_data,
                    f,
                    indent=c.Cli.FileIODefaults.JSON_INDENT,
                    ensure_ascii=c.Cli.FileIODefaults.JSON_ENSURE_ASCII,
                )
            return r[bool].ok(True)
        except Exception as e:
            return r[bool].fail(
                c.Cli.ErrorMessages.SAVE_FAILED.format(error=e),
            )

    @staticmethod
    def validate_configuration(config: FlextCliSettings) -> r[bool]:
        """Validate configuration using FlextCliSettings Pydantic model.

        Args:
            config: FlextCliSettings model instance (validation automatic via Pydantic)

        Returns:
            r[bool]: True if configuration is valid, failure on error

        Note:
            Validation is automatically performed by Pydantic field validators
            when FlextCliSettings instance is created. This method validates the
            configuration is correct and returns success if config is valid.

        """
        # Validation already performed by Pydantic during instantiation
        # If we reach here, config is valid - perform basic validation check
        if not isinstance(config, FlextCliSettings):
            return r[bool].fail("Configuration must be FlextCliSettings instance")
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
            # Use mapper().get() to check cache existence
            cache_check = FlextUtilities.mapper().get(self._caches, cache_name)
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
                cache_key_tuple = (
                    (args, tuple(sorted(kwargs.items()))) if kwargs else args
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

    def get_cache_stats(self, cache_name: str) -> r[Mapping[str, t.GeneralValueType]]:
        """Get statistics for a specific cache."""
        try:
            # Use mapper().get() to check cache existence
            cache_check = FlextUtilities.mapper().get(self._caches, cache_name)
            if cache_check is None:
                return r[dict[str, t.GeneralValueType]].fail(
                    f"Cache '{cache_name}' not found",
                )

            cache_obj = self._caches[cache_name]
            # Type narrowing: cache_obj is TTLCache or LRUCache from type system
            # No isinstance check needed - type system guarantees this
            stats: dict[str, t.GeneralValueType] = {
                "size": len(cache_obj),
                "maxsize": cache_obj.maxsize,
                "hits": self._cache_stats.cache_hits,
                "misses": self._cache_stats.cache_misses,
                "hit_rate": self._cache_stats.get_hit_rate(),
                "time_saved": self._cache_stats.total_time_saved,
            }
            return r[dict[str, t.GeneralValueType]].ok(stats)
        except Exception as e:
            return r[dict[str, t.GeneralValueType]].fail(str(e))

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
        try:
            result = func(*args, **kwargs)
            return r[t.GeneralValueType].ok(result)
        except Exception as e:
            return r[t.GeneralValueType].fail(str(e))

    # ==========================================================================
    # PLUGIN SYSTEM - Integrated into core service
    # ==========================================================================

    def register_plugin(self, plugin: p.Cli.CliPlugin) -> r[bool]:
        """Register a plugin with the plugin manager.

        Returns:
            r[bool]: True if plugin registered successfully, failure on error

        """
        try:
            plugin_name = self._plugin_manager.register(plugin)
            if plugin_name:
                # Protocol check validates all required attributes at runtime
                # Type narrowing: plugin is already CliPlugin from parameter type
                self._plugins[plugin_name] = plugin
            return r[bool].ok(True)
        except Exception as e:
            return r[bool].fail(str(e))

    def _load_plugin_entry_point(self, ep: metadata.EntryPoint) -> str | None:
        """Load and register a single plugin entry point.

        Returns plugin name on success, None on failure.
        """
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

    def _process_distribution_entry_points(
        self,
        dist: metadata.Distribution,
    ) -> list[str]:
        """Process entry points from a distribution.

        Returns list of discovered plugin names.
        """
        entry_points_result = FlextCliUtilities.process(
            list(dist.entry_points),
            processor=self._load_plugin_entry_point,
            on_error="skip",
        )
        if not entry_points_result.is_success:
            return []
        entry_points_value = entry_points_result.value
        if isinstance(entry_points_value, list):
            filtered = FlextCliUtilities.filter(
                entry_points_value,
                predicate=lambda x: x is not None,
            )
            # Type narrowing: filtered contains only non-None values, all should be str
            filtered_list: list[str] = [
                str(item) for item in filtered if isinstance(item, str)
            ]
            return filtered_list
        return []

    def _flatten_plugin_lists(self, nested_lists: list[list[str]]) -> list[str]:
        """Flatten nested list of plugin names.

        Returns flat list of all plugin names.
        """
        return [
            item
            for sublist in nested_lists
            for item in (sublist if isinstance(sublist, list) else [])
        ]

    def discover_plugins(self) -> r[list[str]]:
        """Discover and register plugins via entry points."""
        try:
            distributions_result = FlextCliUtilities.process(
                list(metadata.distributions()),
                processor=self._process_distribution_entry_points,
                on_error="skip",
            )
            if distributions_result.is_success:
                distributions_value = distributions_result.value
                if isinstance(distributions_value, list):
                    discovered_plugins = self._flatten_plugin_lists(distributions_value)
                else:
                    discovered_plugins = []
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
            # Retrieve hook caller - if None, it means hook doesn't exist
            # Use getattr directly for proper type narrowing
            hook_caller_obj = getattr(self._plugin_manager.hook, hook_name, None)

            if hook_caller_obj is None:
                return r[list[t.GeneralValueType]].fail(
                    f"Hook '{hook_name}' not found",
                )

            # Type narrowing: hook_caller_obj is not None after check above
            # pluggy hooks are always callable, use directly
            # Callable[..., T] uses ... for variadic args (hook signatures vary)
            results = hook_caller_obj(**kwargs)
            # Fast-fail: hook must return list or None (converted to empty list)
            # No fallback to fake data
            if results is None:
                return r[list[t.GeneralValueType]].ok([])
            if not FlextRuntime.is_list_like(results):
                # Single result - wrap in list (not a fallback, valid conversion)
                return r[list[t.GeneralValueType]].ok([results])

            # Use build() DSL: map → ensure dict → transform to JSON
            # Reuse to_json helper from output module
            mapped_results = [
                FlextCliOutput.to_json(result) for result in list(results)
            ]
            # Type narrowing: FlextCliUtilities.Collection.map returns list, ensure it's list[t.GeneralValueType]
            results_list: list[t.GeneralValueType] = (
                list(mapped_results) if isinstance(mapped_results, list) else []
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
    #   - Validation: Use FlextCliUtilities.validate() with FlextCliUtilities.Validation.V.* validators
    #   - HTTP: Use flext-api domain library
    #   - Output: Use cli.output.* directly
    # ==========================================================================


__all__ = ["FlextCliCore"]
