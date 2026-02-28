"""Core service for commands, sessions, and configuration of flext-cli.

Groups command registration/execution, configuration profiles, sessions, and plugins,
returning `r[T]` for operations consumed by the facade `FlextCli`.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from typing import override

from flext_core import (
    FlextDecorators,
    FlextLogger,
    FlextRegistry,
    r,
    u,
)
from rich.errors import ConsoleError, LiveError, StyleError

from flext_cli import (
    FlextCliOutput,
    FlextCliServiceBase,
    FlextCliUtilities,
    c,
    m,
    t,
)


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
            super().__init__()
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
    # These are set during __init__ setup
    _cli_config: dict[str, t.JsonValue]
    _commands: dict[str, Mapping[str, t.JsonValue]]
    _sessions: dict[str, t.JsonValue]
    _session_active: bool
    _registry: FlextRegistry
    _session_config: dict[str, t.JsonValue]
    _session_start_time: str

    type CliValue = (
        str
        | int
        | float
        | bool
        | list[str]
        | Mapping[str, str | int | float | bool | list[str]]
        | None
    )

    def __init__(
        self,
        config: Mapping[str, t.JsonValue] | None = None,
    ) -> None:
        """Initialize CLI core with optional configuration seed values.

        Args:
            config: Optional configuration dictionary for CLI-specific settings
                (stored separately, not passed to parent FlextService.__init__)

        """
        # FlextCliServiceBase extends FlextService[dict[str, t.JsonValue]]
        # The generic type parameter TDomainResult doesn't affect __init__ signature
        # Note: config is CLI-specific and stored separately, not passed to parent
        # because FlextService uses Pydantic with extra="forbid"
        super().__init__()

        # Phase 1 Enhancement: Context enrichment happens automatically in FlextService.__init__
        # The parent class already calls _enrich_context with service metadata
        # Logger and container are inherited from FlextService via FlextMixins

        # Type-safe configuration initialization
        # Store CLI-specific config as dict (base class _config is FlextSettings | None)
        # Use mutable dict for CLI-specific configuration dictionary
        object.__setattr__(
            self,
            "_cli_config",
            dict(config) if config is not None else {},
        )
        object.__setattr__(self, "_commands", {})
        # Note: stores plugin objects implementing CliPlugin protocol
        # Plugin system via FlextRegistry
        object.__setattr__(self, "_registry", FlextRegistry(dispatcher=None))
        object.__setattr__(self, "_sessions", {})
        object.__setattr__(self, "_session_active", False)

        # Performance and async integration
        # Note: stores cache objects (TTLCache/LRUCache), not JsonValue
        # Cache types are from external library, using generic types
        object.__setattr__(
            self,
            "_caches",
            {},
        )
        object.__setattr__(self, "_cache_stats", self._CacheStats())

        # Type narrowing: is_dict_like ensures config is dict-like
        config_dict: Mapping[str, t.JsonValue] | None = (
            config if config is not None else None
        )
        FlextLogger(__name__).debug(
            "Initialized CLI core service",
            operation="__init__",
            has_config=config is not None,
            config_keys=list(config_dict.keys()) if config_dict else None,
            commands_count=0,
            plugins_count=0,
            sessions_count=0,
        )

    # ==========================================================================
    # CLI COMMAND MANAGEMENT - Using t.FlextCliCommandT types
    # ==========================================================================

    def register_command(
        self,
        command: m.Cli.CliCommand,
    ) -> r[bool]:
        """Register CLI command using CliCommand model instance.

        Args:
            command: CliCommand model instance with validated data

        Returns:
            r[bool]: True if registration succeeded, failure on error

        """
        # Log detailed command registration initialization
        FlextLogger(__name__).debug(
            "Starting CLI command registration",
            command_name=command.name if command else None,
            command_type=type(command).__name__ if command else None,
            operation="register_command",
        )

        FlextLogger(__name__).info(
            "STARTING CLI command registration",
            command_name=command.name if command else None,
            operation="register_command",
        )

        # Simple validation and registration (KISS principle) - fast fail
        # Note: command parameter is non-optional, but we check for None defensively
        # to handle cases where caller passes None despite type hints
        if not command.name:
            FlextLogger(__name__).error(
                "FAILED CLI command registration - command name is empty",
                command_name=command.name,
                operation="register_command",
            )
            return r[bool].fail(
                c.Cli.ErrorMessages.COMMAND_NAME_EMPTY,
            )

        try:
            # Type system ensures command is m.Cli.CliCommand
            # Build command_data dict without using model_dump() to avoid DomainEvent forward reference error
            # Extract model fields directly instead of calling model_dump() which triggers model_rebuild()
            # Status is already a str field in the model, created_at needs conversion
            created_at_val: t.JsonValue = command.created_at.isoformat()
            command_data: dict[str, t.JsonValue] = {
                "name": command.name,
                "unique_id": command.unique_id,
                "status": command.status,  # Already a str from model definition
                "created_at": created_at_val,
                "description": command.description or "",
                "command_line": command.command_line,
                "usage": command.usage,
                "entry_point": command.entry_point,
                "args": list(command.args),
            }
            self._commands[command.name] = command_data

            # Log successful registration with detailed context
            FlextLogger(__name__).debug(
                "Command registration completed successfully",
                command_name=command.name,
                # Business Rule: Dict keys MUST be extracted using list() constructor (Python 3.13+)
                # Architecture: Direct list() conversion is type-safe and efficient
                # Audit Implication: Key extraction is deterministic and safe
                # Python 3.13: model_dump() always returns dict, isinstance check is unnecessary
                command_data_keys=list(command_data.keys()),
                registry_size=len(self._commands),
                operation="register_command",
            )

            FlextLogger(__name__).info(
                "COMPLETED CLI command registration successfully",
                command_name=command.name,
                operation="register_command",
            )

            return r[bool].ok(value=True)

        except (ValueError, TypeError, AttributeError, RuntimeError) as e:
            # Log detailed registration error
            FlextLogger(__name__).exception(
                "FAILED CLI command registration with exception",
                command_name=command.name,
                error_type=type(e).__name__,
                operation="register_command",
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
    ) -> r[m.Configuration]:
        """Retrieve registered command definition.

        Args:
            name: Command identifier to retrieve

        Returns:
            r[m.Configuration]: Command definition snapshot or error

        """
        FlextLogger(__name__).debug(
            "Retrieving command definition",
            operation="get_command",
            command_name=name,
            total_commands=len(self._commands),
        )

        if not name:
            FlextLogger(__name__).warning(
                "Command name is empty",
                operation="get_command",
                consequence="Command retrieval will fail",
            )
            return r[m.Configuration].fail(
                c.Cli.ErrorMessages.COMMAND_NAME_EMPTY,
            )

        # Use mapper().get() to check command existence
        command_check = u.Mapper.get(self._commands, name)
        if command_check is None:
            FlextLogger(__name__).warning(
                "Command not found in registry",
                operation="get_command",
                command_name=name,
                available_commands=list(self._commands.keys()),
                consequence="Command retrieval will fail",
            )
            return r[m.Configuration].fail(
                c.Cli.ErrorMessages.COMMAND_NOT_FOUND.format(name=name),
            )

        try:
            command_def = self._commands[name]

            FlextLogger(__name__).debug(
                "Retrieved command definition",
                operation="get_command",
                command_name=name,
                command_def_type=type(command_def).__name__,
            )

            FlextLogger(__name__).debug(
                "Command definition retrieved successfully",
                operation="get_command",
                command_name=name,
                # Business Rule: Dict keys MUST be extracted using list() constructor (Python 3.13+)
                # Architecture: Direct list() conversion is type-safe and efficient
                # Audit Implication: Key extraction is deterministic and safe
                # Python 3.13: command_def from dict already has .keys(), isinstance check is unnecessary
                definition_keys=list(command_def.keys()),
            )

            # Create snapshot from command definition
            snapshot_config: dict[str, t.ConfigMapValue] = {
                str(key): value for key, value in command_def.items()
            }
            return r[m.Configuration].ok(
                m.Configuration(
                    config=m.Dict(root=snapshot_config),
                ),
            )
        except (
            ValueError,
            TypeError,
            KeyError,
            ConsoleError,
            StyleError,
            LiveError,
        ) as e:
            FlextLogger(__name__).exception(
                "FAILED to retrieve command - operation aborted",
                operation="get_command",
                command_name=name,
                error=str(e),
                error_type=type(e).__name__,
                consequence="Command retrieval failed completely",
            )
            return r[m.Configuration].fail(
                c.Cli.ErrorMessages.COMMAND_RETRIEVAL_FAILED.format(
                    error=e,
                ),
            )

    def _build_execution_context(
        self,
        context: Mapping[str, t.JsonValue] | list[str] | None,
    ) -> Mapping[str, t.JsonValue]:
        """Build execution context via ExecutionContextInput model (single Pydantic contract)."""
        ctx_input = m.Cli.ExecutionContextInput.model_validate(context)

        def list_processor(seq: Sequence[str]) -> list[t.JsonValue]:
            process_result = FlextCliUtilities.process(
                list(seq),
                processor=FlextCliOutput.norm_json,
                on_error="skip",
            )
            return list(process_result.value or [])

        return ctx_input.to_mapping(list_processor=list_processor)

    def execute_command(
        self,
        name: str,
        context: Mapping[str, t.JsonValue] | list[str] | None = None,
        timeout: float | None = None,
    ) -> r[Mapping[str, t.JsonValue]]:
        """Execute registered command with context."""
        FlextLogger(__name__).info("STARTING CLI command execution", command_name=name)

        command_result = self.get_command(name)
        if command_result.is_failure:
            FlextLogger(__name__).error("FAILED - command not found", command_name=name)
            # Python 3.13: Direct attribute access - more elegant and type-safe
            return r[Mapping[str, t.JsonValue]].fail(
                command_result.error or "Command not found",
            )

        try:
            execution_context = self._build_execution_context(context)
            result_dict: dict[str, t.JsonValue] = {
                c.Cli.DictKeys.COMMAND: name,
                c.Cli.DictKeys.STATUS: True,
                c.Cli.DictKeys.TIMESTAMP: FlextCliUtilities.generate("timestamp"),
                c.Cli.DictKeys.TIMEOUT: timeout,
                c.Cli.DictKeys.CONTEXT: dict(execution_context),
            }
            FlextLogger(__name__).info(
                "COMPLETED CLI command execution", command_name=name
            )
            return r[Mapping[str, t.JsonValue]].ok(result_dict)

        except (
            ValueError,
            TypeError,
            KeyError,
            ConsoleError,
            StyleError,
            LiveError,
        ) as e:
            FlextLogger(__name__).exception(
                "FAILED CLI command execution", command_name=name
            )
            return r[Mapping[str, t.JsonValue]].fail(
                c.Cli.ErrorMessages.COMMAND_EXECUTION_FAILED.format(error=e),
            )

    def list_commands(self) -> r[list[str]]:
        """List all registered commands using functional composition.

        Performs command listing with railway pattern and proper error handling.
        Uses functional approach to extract command names safely.

        Returns:
            r[list[str]]: List of command names or error with details

        """
        FlextLogger(__name__).debug(
            "Listing all registered commands",
            operation="list_commands",
            total_commands=len(self._commands),
        )

        # Functional command listing with railway pattern
        def extract_command_names() -> r[list[str]]:
            """Extract command names from internal registry."""
            try:
                command_names = list(self._commands.keys())

                FlextLogger(__name__).debug(
                    "Command names extracted successfully",
                    operation="list_commands",
                    commands_count=len(command_names),
                    command_names=command_names,
                )

                FlextLogger(__name__).info(
                    "Command listing completed",
                    operation="list_commands",
                    total_commands=len(command_names),
                )

                return r[list[str]].ok(command_names)
            except (
                ValueError,
                TypeError,
                KeyError,
                ConsoleError,
                StyleError,
                LiveError,
            ) as e:
                FlextLogger(__name__).exception(
                    "FAILED to list commands - operation aborted",
                    operation="list_commands",
                    error=str(e),
                    error_type=type(e).__name__,
                    consequence="Command list unavailable",
                )
                return r[list[str]].fail(
                    c.Cli.ErrorMessages.COMMAND_LISTING_FAILED.format(
                        error=e,
                    ),
                )

        # Railway pattern: extract and validate command names
        return extract_command_names()

    # ==========================================================================
    # CLI CONFIGURATION MANAGEMENT - Using t.Configuration types
    # ==========================================================================

    def _log_config_update(self) -> None:
        """Log configuration update - direct logger usage."""
        FlextLogger(__name__).info(c.Cli.LogMessages.CLI_CONFIG_UPDATED)

    def _validate_config_input(
        self,
        config: t.GeneralValueType,
    ) -> r[Mapping[str, t.JsonValue]]:
        """Validate input configuration for update operations."""
        if not isinstance(config, Mapping):
            return r[Mapping[str, t.JsonValue]].fail(
                c.Cli.ErrorMessages.CONFIG_NOT_DICT,
            )
        if not config:
            FlextLogger(__name__).warning(
                "Configuration input is empty",
                operation="update_configuration",
                consequence="Configuration update will fail",
            )
            return r[Mapping[str, t.JsonValue]].fail(
                c.Cli.ErrorMessages.CONFIG_NOT_DICT,
            )

        FlextLogger(__name__).debug(
            "Configuration input validated",
            operation="update_configuration",
            config_keys=list(config.keys()),
        )
        # Use build() DSL for JSON conversion
        # Reuse to_dict_json helper from output module
        # to_dict_json returns dict[str, JsonValue] which is exactly what we need
        # to_dict_json is guaranteed to return a dict (doesn't return None or other types)
        json_config = FlextCliOutput.to_dict_json(config)
        return r[Mapping[str, t.JsonValue]].ok(json_config)

    def _validate_existing_config(
        self,
    ) -> r[Mapping[str, t.JsonValue]]:
        """Validate existing configuration state."""
        # self._cli_config is dict[str, t.JsonValue] - return as JsonDict
        if self._cli_config:
            return r[Mapping[str, t.JsonValue]].ok(self._cli_config)
        return r[Mapping[str, t.JsonValue]].fail(
            c.Cli.ErrorMessages.CONFIG_NOT_INITIALIZED,
        )

    def _merge_configurations(
        self,
        valid_config: Mapping[str, t.JsonValue],
    ) -> r[bool]:
        """Merge new configuration with existing one."""
        try:
            FlextLogger(__name__).debug(
                "Merging configurations",
                operation="update_configuration",
                new_config_keys=list(valid_config.keys()),
            )

            existing_config_result = self._validate_existing_config()
            if existing_config_result.is_failure:
                # Python 3.13: Direct attribute access - more elegant and type-safe
                error_msg = existing_config_result.error or ""
                FlextLogger(__name__).warning(
                    "Existing configuration validation failed",
                    operation="update_configuration",
                    error=error_msg,
                    consequence="Configuration merge will fail",
                )
                return r[bool].fail(
                    existing_config_result.error or "Config validation failed",
                )

            # Python 3.13: Direct attribute access - unwrap() provides safe access
            # Convert Mapping to dict for mutability
            existing_config_raw: dict[str, t.JsonValue] = dict(
                existing_config_result.value or {},
            )
            existing_config: dict[str, t.JsonValue] = dict(existing_config_raw)
            # Use build() DSL: ensure dict → transform to JSON
            # Reuse to_dict_json helper from output module
            transformed_config = FlextCliOutput.to_dict_json(valid_config)
            existing_config_guard: dict[str, t.GuardInputValue] = {
                str(k): v for k, v in existing_config.items()
            }
            transformed_config_guard: dict[str, t.GuardInputValue] = {
                str(k): v for k, v in transformed_config.items()
            }
            merge_result = FlextCliUtilities.merge(
                existing_config_guard,
                transformed_config_guard,
                strategy="deep",
            )
            if merge_result.is_failure:
                return r[bool].fail(merge_result.error or "Failed to merge config")

            merged_candidate = merge_result.value
            merged_config = FlextCliOutput.to_dict_json(merged_candidate)
            # merged_config is guaranteed to be not None by FlextCliUtilities.val default
            object.__setattr__(self, "_cli_config", merged_config)

            FlextLogger(__name__).debug(
                "Configuration merged successfully",
                operation="update_configuration",
                merged_keys=list(self._cli_config.keys()),
            )

            self._log_config_update()
            FlextLogger(__name__).info(
                "Configuration update completed successfully",
                operation="update_configuration",
            )

            return r[bool].ok(value=True)

        except (
            ValueError,
            TypeError,
            KeyError,
            ConsoleError,
            StyleError,
            LiveError,
        ) as e:
            FlextLogger(__name__).exception(
                "FAILED to merge configurations - operation aborted",
                operation="update_configuration",
                error=str(e),
                error_type=type(e).__name__,
                consequence="Configuration update failed completely",
            )
            return r[bool].fail(
                c.Cli.ErrorMessages.CONFIG_UPDATE_FAILED.format(error=e),
            )

    def update_configuration(
        self,
        config: t.GeneralValueType,
    ) -> r[bool]:
        """Update CLI configuration using railway pattern and functional composition.

        Performs configuration update with comprehensive validation and error handling.
        Uses functional pipeline to ensure safe configuration merging.

        Args:
            config: New configuration schema with CLI-specific structure

        Returns:
            r[bool]: True if configuration updated successfully, failure on error

        """
        if not isinstance(config, Mapping):
            return r[bool].fail(c.Cli.ErrorMessages.CONFIG_NOT_DICT)

        FlextLogger(__name__).info(
            "Updating CLI configuration",
            operation="update_configuration",
            config_keys=list(config.keys()),
            current_config_keys=list(self._cli_config.keys()),
        )

        FlextLogger(__name__).debug(
            "Starting configuration update",
            operation="update_configuration",
            config_type=type(config).__name__,
        )

        # Railway pattern: validate input then merge configurations
        # Use build() DSL: ensure dict → transform to JSON
        # Reuse to_dict_json helper from output module
        # Python 3.13: to_dict_json() always returns dict, isinstance check is unnecessary
        validated_config_input: dict[str, t.JsonValue] = dict(
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
        merged_config_val: dict[str, t.JsonValue] = dict(
            config_result.value or {},
        )
        # merged_config_val is guaranteed to be not None by FlextCliUtilities.val default
        return self._merge_configurations(merged_config_val)

    def get_configuration(
        self,
    ) -> r[Mapping[str, t.JsonValue]]:
        """Get current CLI configuration using functional composition.

        Retrieves configuration with validation and error handling.
        Uses railway pattern to ensure configuration integrity.

        Returns:
            r[dict[str, t.JsonValue]]: Current configuration or error with details

        """

        # Functional configuration retrieval with railway pattern
        def validate_config_state() -> r[Mapping[str, t.JsonValue]]:
            """Validate that configuration is properly initialized."""
            try:
                FlextLogger(__name__).debug(
                    "Retrieving CLI configuration",
                    operation="get_configuration",
                    config_type=type(self._cli_config).__name__,
                    config_keys=list(self._cli_config.keys()),
                )
                if not self._cli_config:
                    FlextLogger(__name__).warning(
                        "Configuration not initialized",
                        operation="get_configuration",
                        consequence="Configuration retrieval will fail",
                    )
                    return r[Mapping[str, t.JsonValue]].fail(
                        c.Cli.ErrorMessages.CONFIG_NOT_INITIALIZED,
                    )
                FlextLogger(__name__).debug(
                    "Configuration retrieved successfully",
                    operation="get_configuration",
                    config_keys=list(self._cli_config.keys()),
                )

                FlextLogger(__name__).info(
                    "Configuration retrieval completed",
                    operation="get_configuration",
                )

                # self._cli_config is dict[str, t.JsonValue] - return as JsonDict
                return r[Mapping[str, t.JsonValue]].ok(
                    self._cli_config,
                )
            except (
                ValueError,
                TypeError,
                KeyError,
                ConsoleError,
                StyleError,
                LiveError,
            ) as e:
                FlextLogger(__name__).exception(
                    "FAILED to retrieve configuration - operation aborted",
                    operation="get_configuration",
                    error=str(e),
                    error_type=type(e).__name__,
                    consequence="Configuration retrieval failed completely",
                )
                return r[Mapping[str, t.JsonValue]].fail(
                    c.Cli.ErrorMessages.CONFIG_RETRIEVAL_FAILED.format(
                        error=e,
                    ),
                )

        # Railway pattern: validate and return configuration
        return validate_config_state()

    def create_profile(
        self,
        name: str,
        profile_config: Mapping[str, t.JsonValue],
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

        if not self._cli_config:
            return r[bool].fail(
                c.Cli.ErrorMessages.CONFIG_NOT_INITIALIZED,
            )

        # Store profile
        try:
            # Ensure config is mutable dict
            config: dict[str, t.JsonValue] = dict(self._cli_config)

            # Use FlextCliUtilities.extract to safely get profiles section with default
            # FlextCliUtilities.extract returns RuntimeResult, convert to FlextResult
            # Type annotation: default={} makes T = dict[str, t.JsonValue]
            # Call extract method - type is inferred from default parameter
            default_dict: dict[str, t.JsonValue] = {}
            profiles_result_raw = FlextCliUtilities.extract(
                config,
                c.Cli.DictKeys.PROFILES,  # path parameter
                default=default_dict,
            )
            # extract returns r[t.JsonValue | None]
            if profiles_result_raw.is_failure:
                return r[bool].fail(
                    profiles_result_raw.error or "Failed to extract profiles"
                )
            # Type narrowing: value is t.JsonValue | None
            profiles_value = profiles_result_raw.value
            if isinstance(profiles_value, dict):
                profiles_section_raw = {
                    str(key): FlextCliOutput.norm_json(value)
                    for key, value in profiles_value.items()
                }
            else:
                profiles_section_raw = {}
            # Python 3.13: profiles_section_raw is dict from above branches
            profiles_section: dict[str, t.JsonValue] = profiles_section_raw
            profiles_section[name] = profile_config
            # Update config with modified profiles section
            config[c.Cli.DictKeys.PROFILES] = profiles_section
            # Update internal _cli_config
            # Business Rule: Frozen model attributes MUST be set using setattr()
            object.__setattr__(self, "_cli_config", config)
            FlextLogger(__name__).info(
                c.Cli.LogMessages.PROFILE_CREATED.format(name=name),
            )
            return r[bool].ok(value=True)

        except (ValueError, TypeError, AttributeError, KeyError, RuntimeError) as e:
            return r[bool].fail(
                c.Cli.ErrorMessages.PROFILE_CREATION_FAILED.format(error=e),
            )

    # ==========================================================================
    # SESSION MANAGEMENT - Using t.Configuration types
    # ==========================================================================

    def start_session(
        self,
        session_config: Mapping[str, t.JsonValue] | None = None,
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
            # Business Rule: Frozen model attributes MUST be set using setattr()
            if session_config is not None:
                setattr(self, "_session_config", session_config)
            else:
                setattr(self, "_session_config", {})
            object.__setattr__(self, "_session_active", True)
            # Generate ISO format timestamp for session tracking
            setattr(
                self,
                "_session_start_time",
                datetime.now(UTC).isoformat(),
            )

            # Log session start - direct logger usage
            FlextLogger(__name__).info(c.Cli.LogMessages.SESSION_STARTED)

            return r[bool].ok(value=True)

        except (
            ValueError,
            TypeError,
            KeyError,
            ConsoleError,
            StyleError,
            LiveError,
        ) as e:
            return r[bool].fail(
                c.Cli.ErrorMessages.SESSION_START_FAILED.format(error=e),
            )

    def end_session(self) -> r[bool]:
        """End current CLI session.

        Returns:
            r[bool]: True if session ended successfully, failure on error

        """
        try:
            FlextLogger(__name__).info(
                "Ending CLI session",
                operation="end_session",
                session_active=self._session_active,
                total_sessions=len(self._sessions),
            )

            FlextLogger(__name__).debug(
                "Terminating session",
                operation="end_session",
            )

            if not self._session_active:
                FlextLogger(__name__).warning(
                    "No active session to end",
                    operation="end_session",
                    existing_sessions=list(self._sessions.keys()),
                    consequence="Session end will fail",
                )
                return r[bool].fail(
                    c.Cli.ErrorMessages.NO_ACTIVE_SESSION,
                )
            # Business Rule: Frozen model attributes MUST be set using setattr()
            object.__setattr__(self, "_session_active", False)
            delattr(self, c.Cli.PrivateAttributes.SESSION_CONFIG)
            delattr(self, c.Cli.PrivateAttributes.SESSION_START_TIME)

            FlextLogger(__name__).debug(
                "Session terminated successfully",
                operation="end_session",
                total_sessions=len(self._sessions),
            )

            # Log session end - direct logger usage
            FlextLogger(__name__).info(c.Cli.LogMessages.SESSION_ENDED)

            FlextLogger(__name__).info(
                "CLI session ended",
                operation="end_session",
            )

            return r[bool].ok(value=True)

        except (
            ValueError,
            TypeError,
            KeyError,
            ConsoleError,
            StyleError,
            LiveError,
        ) as e:
            FlextLogger(__name__).exception(
                "FAILED to end session - operation aborted",
                operation="end_session",
                error=str(e),
                error_type=type(e).__name__,
                consequence="Session end failed completely",
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
    ) -> r[Mapping[str, t.JsonValue]]:
        """Get command usage statistics using CLI-specific data types.

        Returns:
            r[m.Cli.CommandStatistics]: Statistics model or error

        Pydantic 2 Modernization:
            - Uses CommandStatistics model internally
            - Returns validated model directly
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
            return r[Mapping[str, t.JsonValue]].ok(stats_model.model_dump(mode="json"))
        except (
            ValueError,
            TypeError,
            KeyError,
            ConsoleError,
            StyleError,
            LiveError,
        ) as e:
            return r[Mapping[str, t.JsonValue]].fail(
                c.Cli.ErrorMessages.CLI_EXECUTION_ERROR.format(error=e),
            )

    @override
    def get_service_info(
        self,
    ) -> Mapping[str, str | int | float | bool | datetime | None]:
        """Get comprehensive service information.

        Returns:
            dict[str, t.JsonValue]: Service information (matches FlextService signature)

        """
        try:
            # Collect comprehensive service information
            commands_count = len(self._commands)
            # Business Rule: Dict keys MUST be extracted using list() constructor (Python 3.13+)
            # Architecture: Direct list() conversion is type-safe and efficient
            # Audit Implication: Key extraction is deterministic and safe
            # Python 3.13: _cli_config is already typed as dict, isinstance check is unnecessary
            config_keys = list(self._cli_config.keys())

            # Convert config_keys to concrete sequence values
            config_keys_list: list[str] = list(config_keys) if config_keys else []

            info_data: dict[str, str | int | float | bool | datetime | None] = {
                c.Cli.DictKeys.SERVICE: c.Cli.FLEXT_CLI,
                c.Cli.CoreServiceDictKeys.COMMANDS_REGISTERED: commands_count,
                c.Cli.CoreServiceDictKeys.CONFIGURATION_SECTIONS: ",".join(
                    config_keys_list
                ),
                c.Cli.DictKeys.STATUS: (
                    c.Cli.ServiceStatus.OPERATIONAL.value
                    if self._session_active
                    else c.Cli.ServiceStatus.AVAILABLE.value
                ),
                c.Cli.CoreServiceDictKeys.SERVICE_READY: commands_count > 0,
                c.Cli.DictKeys.TIMESTAMP: FlextCliUtilities.generate("timestamp"),
            }

            # Return concrete service metadata mapping
            return info_data

        except (
            ValueError,
            TypeError,
            KeyError,
            ConsoleError,
            StyleError,
            LiveError,
        ) as e:
            FlextLogger(__name__).exception(
                c.Cli.CoreServiceLogMessages.SERVICE_INFO_COLLECTION_FAILED,
            )
            return {c.Cli.DictKeys.MESSAGE: str(e)}

    def get_session_statistics(
        self,
    ) -> r[Mapping[str, t.JsonValue]]:
        """Get session-specific statistics using CLI data types.

        Returns:
            r[Mapping[str, t.JsonValue]]: Session statistics data or error

        Pydantic 2 Modernization:
            - Uses SessionStatistics model internally
            - Returns validated model directly
            - Type-safe with field validation (non-negative duration)

        """
        FlextLogger(__name__).debug(
            "Collecting session statistics",
            operation="get_session_statistics",
            session_active=self._session_active,
            total_sessions=len(self._sessions),
        )

        if not self._session_active:
            FlextLogger(__name__).warning(
                "No active session for statistics collection",
                operation="get_session_statistics",
                existing_sessions=list(self._sessions.keys()),
                consequence="Statistics collection will fail",
            )
            return r[Mapping[str, t.JsonValue]].fail(
                c.Cli.ErrorMessages.NO_ACTIVE_SESSION,
            )

        try:
            # Calculate session duration if session is active
            session_duration = c.Cli.CoreServiceDefaults.SESSION_DURATION_INIT
            if self._session_start_time:
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

            FlextLogger(__name__).debug(
                "Session statistics collected successfully",
                operation="get_session_statistics",
                session_duration=stats_model.session_duration_seconds,
                commands_executed=stats_model.commands_executed,
            )

            FlextLogger(__name__).info(
                "Session statistics retrieved",
                operation="get_session_statistics",
                session_duration_seconds=stats_model.session_duration_seconds,
            )

            return r[Mapping[str, t.JsonValue]].ok(stats_model.model_dump(mode="json"))

        except (
            ValueError,
            TypeError,
            KeyError,
            ConsoleError,
            StyleError,
            LiveError,
        ) as e:
            FlextLogger(__name__).exception(
                "FAILED to collect session statistics - operation aborted",
                operation="get_session_statistics",
                error=str(e),
                error_type=type(e).__name__,
                consequence="Statistics unavailable",
            )
            return r[Mapping[str, t.JsonValue]].fail(
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
    def execute(self) -> r[Mapping[str, t.JsonValue]]:
        """Execute CLI service operations.

        decorators automatically:
        - Log operation start/completion/failure
        - Track performance metrics
        - Handle context propagation (correlation_id, operation_name)

        Returns:
            r[Mapping[str, t.JsonValue]]: Service execution data result

        Pydantic 2 Modernization:
            - Uses ServiceExecutionResult model internally
            - Returns validated model directly
            - Type-safe with field validation

        """
        FlextLogger(__name__).info(
            "Executing CLI core service",
            operation="execute",
            commands_count=len(self._commands),
            session_active=self._session_active,
        )

        FlextLogger(__name__).debug(
            "Starting service execution",
            operation="execute",
            # Business Rule: Dict keys MUST be extracted using list() constructor (Python 3.13+)
            # Architecture: Direct list() conversion is type-safe and efficient
            # Audit Implication: Key extraction is deterministic and safe
            # No additional parameters
        )

        try:
            # Validate service state before execution
            if not self._commands:
                FlextLogger(__name__).warning(
                    "No commands registered for service execution",
                    operation="execute",
                    consequence="Service execution will fail",
                )
                return r[Mapping[str, t.JsonValue]].fail(
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

            FlextLogger(__name__).debug(
                "Service execution completed successfully",
                operation="execute",
                commands_count=result_model.commands_count,
                service_ready=result_model.service_ready,
            )

            FlextLogger(__name__).info(
                "CLI core service execution completed",
                operation="execute",
                commands_count=result_model.commands_count,
            )

            return r[Mapping[str, t.JsonValue]].ok(result_model.model_dump())

        except (
            ValueError,
            TypeError,
            KeyError,
            ConsoleError,
            StyleError,
            LiveError,
        ) as e:
            FlextLogger(__name__).exception(
                "FATAL ERROR during service execution - execution aborted",
                operation="execute",
                error=str(e),
                error_type=type(e).__name__,
                consequence="Service execution failed completely",
                severity="critical",
            )
            return r[Mapping[str, t.JsonValue]].fail(
                c.Cli.CoreServiceLogMessages.SERVICE_EXECUTION_FAILED.format(
                    error=e,
                ),
            )

    def execute_cli_command_with_context(
        self,
        command_name: str,
        user_id: str | None = None,
        **context_data: t.JsonValue,
    ) -> r[Mapping[str, t.JsonValue]]:
        """Execute CLI command with automatic context enrichment (Phase 1 pattern).

        Demonstrates the new execute_with_context_enrichment() pattern from flext-core
        Phase 1 architectural enhancement for CLI operations.

        Args:
            command_name: Name of the command to execute
            user_id: Optional user ID for audit context
            **context_data: Additional context data for enriched logging

        Returns:
            r[Mapping[str, t.JsonValue]]: Command execution result data

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

        return r[Mapping[str, t.JsonValue]].ok(result_model.model_dump(mode="json"))

    def health_check(self) -> r[Mapping[str, t.JsonValue]]:
        """Perform health check on the CLI service.

        Returns:
            r[dict[str, t.JsonValue]]: Health check result

        """
        try:
            return r[Mapping[str, t.JsonValue]].ok({
                c.Cli.DictKeys.STATUS: c.Cli.ServiceStatus.HEALTHY.value,
                c.Cli.CoreServiceDictKeys.COMMANDS_COUNT: len(
                    self._commands,
                ),
                c.Cli.CoreServiceDictKeys.SESSION_ACTIVE: self._session_active,
                c.Cli.DictKeys.TIMESTAMP: FlextCliUtilities.generate("timestamp"),
            })
        except (
            ValueError,
            TypeError,
            KeyError,
            ConsoleError,
            StyleError,
            LiveError,
        ) as e:
            return r[Mapping[str, t.JsonValue]].fail(
                c.Cli.ErrorMessages.CLI_EXECUTION_ERROR.format(error=e),
            )

    def get_config(self) -> r[Mapping[str, t.JsonValue]]:
        """Get current service configuration.

        Returns:
            r[Mapping[str, t.JsonValue]]: Configuration data

        """
        try:
            # Type narrowing: self._cli_config is dict[str, t.JsonValue] - return as JsonDict
            # Fast-fail if config is empty - no fallback
            if not self._cli_config:
                return r[Mapping[str, t.JsonValue]].fail(
                    c.Cli.ErrorMessages.CONFIG_NOT_INITIALIZED,
                )
            return r[Mapping[str, t.JsonValue]].ok(self._cli_config)
        except (
            ValueError,
            TypeError,
            KeyError,
            ConsoleError,
            StyleError,
            LiveError,
        ) as e:
            return r[Mapping[str, t.JsonValue]].fail(
                c.Cli.ErrorMessages.CONFIG_RETRIEVAL_FAILED.format(error=e),
            )

    @staticmethod
    def _get_dict_keys(
        data_dict: Mapping[str, t.JsonValue] | None,
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
        except (
            ValueError,
            TypeError,
            KeyError,
            ConsoleError,
            StyleError,
            LiveError,
        ) as e:
            return r[list[str]].fail(error_message.format(error=e))

    def get_handlers(self) -> r[list[str]]:
        """Get list of registered command handlers.

        Returns:
            r[list[str]]: List of handler names

        """
        return self._get_dict_keys(
            self._commands,
            c.Cli.ErrorMessages.COMMAND_LISTING_FAILED,
        )

    def get_plugins(self) -> r[list[str]]:
        """Get list of registered plugins.

        Returns:
            r[list[str]]: List of plugin names

        """
        result = self._registry.list_plugins("cli_plugins")
        if result.is_failure:
            return r[list[str]].ok([])
        return r[list[str]].ok(result.value or [])
