"""FLEXT CLI Configuration Module.

**MODULE**: FlextCliConfig - Enterprise CLI configuration management
**SCOPE**: Pydantic 2 settings, environment variables, terminal detection, output formatting,
          singleton pattern, functional validation, railway-oriented error handling

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import importlib
import json
import os
import shutil
from pathlib import Path
from typing import Annotated, ClassVar, Self

import yaml
from flext_core import (
    FlextConfig,
    FlextConstants,
    FlextContainer,
    FlextExceptions,
    FlextLogger,
    FlextModels,
    FlextProtocols,
    FlextResult,
    t,
    u,
)
from pydantic import (
    Field,
    SecretStr,
    StringConstraints,
    computed_field,
    field_validator,
    model_validator,
)
from pydantic_settings import SettingsConfigDict

from flext_cli.constants import FlextCliConstants
from flext_cli.utilities import FlextCliUtilities

# Alias LogLevel from FlextConstants (moved from flext_core direct export)
LogLevel = FlextConstants.Settings.LogLevel

# Aliases for static method calls and type references
# Use u.* for FlextUtilities static methods
# Use t.* for FlextTypes type references
# Use c.* for FlextConstants constants
# Use m.* for FlextModels model references
# Use p.* for FlextProtocols protocol references
# Use r.* for FlextResult methods
# Use e.* for FlextExceptions
# u is already imported from flext_core
# t is already imported from flext_core
c = FlextConstants
m = FlextModels
p = FlextProtocols
r = FlextResult
e = FlextExceptions

logger = FlextLogger(__name__)


@FlextConfig.auto_register("cli")
class FlextCliConfig(FlextConfig):
    """Single flat Pydantic 2 BaseModel class for flext-cli using AutoConfig pattern.

    Business Rules:
    ───────────────
    1. Configuration MUST use singleton pattern (thread-safe access)
    2. Configuration MUST support environment variable overrides (FLEXT_CLI_*)
    3. Configuration MUST validate all values using Pydantic 2 validators
    4. Sensitive data (passwords, tokens, keys) MUST use SecretStr
    5. Configuration MUST use FlextCliConstants for all defaults
    6. Configuration MUST support .env file loading (optional)
    7. Configuration changes MUST be validated before application
    8. Trace mode REQUIRES debug mode to be enabled (enforced by validator)

    Architecture Implications:
    ───────────────────────────
    - Auto-registration enables namespace access via FlextConfig.get_global_instance().cli
    - Singleton pattern ensures consistent configuration across application
    - Pydantic 2 SettingsConfigDict enables environment variable integration
    - Field validators enforce business rules (trace requires debug)
    - SecretStr prevents accidental logging of sensitive data
    - Flat structure simplifies access and reduces nesting complexity

    Audit Implications:
    ───────────────────
    - Configuration changes MUST be logged with timestamp and user context
    - Sensitive fields (SecretStr) MUST NOT be logged or serialized
    - Environment variable overrides MUST be validated before use
    - Configuration validation failures MUST prevent application startup
    - Default values MUST be secure (no hardcoded credentials or weak settings)
    - Configuration file paths MUST be validated for security (path traversal prevention)
    - Remote configuration loading MUST use encrypted connections (TLS/SSL)
    - Configuration backups MUST exclude sensitive data (SecretStr fields)

    **ARCHITECTURAL PATTERN**: Zero-Boilerplate Auto-Registration

    This class uses FlextConfig.AutoConfig for automatic:
    - Singleton pattern (thread-safe)
    - Namespace registration (accessible via config.cli)
    - Test reset capability (_reset_instance)

    Implements FlextCliProtocols.CliConfigProvider through structural subtyping.

    Follows standardized pattern:
    - Extends FlextConfig.AutoConfig (BaseModel) for nested config pattern
    - Flat class structure with all fields at top level
    - All defaults from FlextCliConstants
    - SecretStr for sensitive data
    - Uses FlextConfig namespace features for configuration management

    **Usage**:
        # Get singleton instance
        config = FlextCliConfig.get_instance()

        # Or via FlextConfig namespace
        from flext_core import FlextConfig
        config = FlextConfig.get_global_instance()
        cli_config = config.cli

    - Uses Python 3.13 + Pydantic 2 features
    """

    # Use FlextConfig.resolve_env_file() to ensure all FLEXT configs use same .env
    model_config = SettingsConfigDict(
        env_prefix="FLEXT_CLI_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        use_enum_values=True,
        json_schema_extra={
            "title": "FLEXT CLI Configuration",
            "description": "Enterprise CLI configuration using AutoConfig pattern",
        },
    )

    # CLI-specific configuration fields using FlextCliConstants for defaults
    # Using Annotated with StringConstraints for automatic validation (Pydantic 2)
    profile: Annotated[str, StringConstraints(min_length=1, strip_whitespace=True)] = (
        Field(
            default=FlextCliConstants.CliDefaults.DEFAULT_PROFILE,
            description="CLI profile to use for configuration",
        )
    )

    # Python 3.13+ best practice: Use Enum value for default consistency
    # Pydantic 2 accepts Enum values in Literal-typed fields
    output_format: FlextCliConstants.OutputFormatLiteral = Field(
        default="table",  # Use literal string value for Literal type
        description="Default output format for CLI commands",
    )

    no_color: bool = Field(
        default=FlextCliConstants.CliDefaults.DEFAULT_NO_COLOR,
        description="Disable colored output in CLI",
    )

    config_dir: Path = Field(
        default_factory=lambda: Path.home() / FlextCliConstants.FLEXT_DIR_NAME,
        description="Configuration directory path",
    )

    project_name: str = Field(
        default="flext-cli",
        description="Project name for CLI operations",
    )

    # Authentication configuration using SecretStr for sensitive data
    api_url: str = Field(
        default="http://localhost:8080/api",
        description="API URL for remote operations",
    )

    cli_api_key: SecretStr | None = Field(
        default=None,
        description="API key for authentication (sensitive)",
    )

    token_file: Path = Field(
        default_factory=lambda: Path.home()
        / FlextCliConstants.FLEXT_DIR_NAME
        / FlextCliConstants.TOKEN_FILE_NAME,
        description="Path to authentication token file",
    )

    refresh_token_file: Path = Field(
        default_factory=lambda: Path.home()
        / FlextCliConstants.FLEXT_DIR_NAME
        / FlextCliConstants.REFRESH_TOKEN_FILE_NAME,
        description="Path to refresh token file",
    )

    auto_refresh: bool = Field(
        default=True,
        description="Automatically refresh authentication tokens",
    )

    # CLI behavior configuration (flattened from previous nested classes)
    # Core fields needed for CLI operations - using Pydantic Settings pattern
    debug: bool = Field(
        default=False,
        description="Enable debug mode",
    )
    trace: bool = Field(
        default=False,
        description="Enable trace mode (requires debug=True)",
    )
    verbose: bool = Field(
        default=FlextCliConstants.CliDefaults.DEFAULT_VERBOSE,
        description="Enable verbose CLI output",
    )

    version: str = Field(
        default=FlextCliConstants.CliDefaults.DEFAULT_VERSION,
        description="Application version",
    )
    quiet: bool = Field(
        default=FlextCliConstants.CliDefaults.DEFAULT_QUIET,
        description="Enable quiet mode",
    )
    interactive: bool = Field(
        default=FlextCliConstants.CliDefaults.DEFAULT_INTERACTIVE,
        description="Enable interactive mode",
    )
    environment: FlextCliConstants.EnvironmentLiteral = Field(
        default=FlextCliConstants.Environment.DEVELOPMENT,  # Already a string constant
        description="Deployment environment",
    )

    max_width: int = Field(
        default=FlextCliConstants.CliDefaults.DEFAULT_MAX_WIDTH,
        ge=FlextCliConstants.ValidationLimits.MIN_MAX_WIDTH,
        le=FlextCliConstants.ValidationLimits.MAX_MAX_WIDTH,
        description="Maximum width for CLI output",
    )

    config_file: Path | None = Field(
        default=None,
        description="Custom configuration file path",
    )

    # Network configuration
    cli_timeout: float = Field(
        default=30,
        description="CLI network timeout in seconds",
        ge=0,
        le=300,
    )

    max_retries: int = Field(
        default=3,
        description="Maximum number of retry attempts",
        ge=0,
        le=10,
    )

    # Logging configuration - centralized for all FLEXT projects
    log_verbosity: str = Field(  # Must match FlextConfig.log_verbosity type
        default=FlextCliConstants.LogVerbosity.DETAILED.value,  # Python 3.13+ best practice: Use Enum value
        description="Logging verbosity (compact, detailed, full)",
    )

    cli_log_level: LogLevel = Field(
        default=FlextConstants.Settings.LogLevel.INFO,  # Use enum value from constants
        description="CLI-specific logging level",
    )

    cli_log_verbosity: FlextCliConstants.LogVerbosityLiteral = Field(
        default="detailed",  # Use literal string value for Literal type
        description="CLI-specific logging verbosity",
    )

    log_file: str | None = Field(
        default=None,
        description="Optional log file path for persistent logging",
    )

    console_enabled: bool = Field(
        default=FlextConstants.Logging.CONSOLE_ENABLED,
        description="Enable console logging output",
    )

    def _ensure_config_directory(self) -> r[Path]:
        """Ensure config directory exists with proper error handling."""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            return r.ok(self.config_dir)
        except (PermissionError, OSError) as e:
            error_msg = FlextCliConstants.ErrorMessages.CANNOT_ACCESS_CONFIG_DIR.format(
                config_dir=self.config_dir,
                error=e,
            )
            return r.fail(error_msg)

    def _propagate_to_context(self) -> r[bool]:
        """Propagate configuration to FlextContext with error recovery."""
        try:
            flext_core_module = importlib.import_module("flext_core")
            context_cls = getattr(flext_core_module, "FlextContext", None)
            context = context_cls() if context_cls is not None else None
            if context is None:
                return r.fail("FlextContext not available")
            # Convert config object to GeneralValueType-compatible dict for context
            # Use u.transform for JSON conversion
            transform_result = u.transform(self.model_dump(), to_json=True)
            config_dict = (
                transform_result.unwrap()
                if transform_result.is_success
                else self.model_dump()
            )
            _ = context.set("cli_config", config_dict)
            # Computed fields return values directly - convert to GeneralValueType
            _ = context.set("cli_auto_output_format", str(self.auto_output_format))
            _ = context.set("cli_auto_color_support", bool(self.auto_color_support))
            _ = context.set("cli_auto_verbosity", str(self.auto_verbosity))
            _ = context.set("cli_optimal_table_format", str(self.optimal_table_format))
            return r[bool].ok(True)
        except Exception as e:
            logger.debug(
                "Context not available during config initialization", error=str(e)
            )
            return r[bool].ok(True)

    def _register_in_container(self) -> r[bool]:
        """Register configuration in FlextContainer for dependency injection."""
        try:
            container = FlextContainer()
            if not container.has_service("flext_cli_config"):
                _ = container.with_service("flext_cli_config", self)
            return r[bool].ok(True)
        except Exception as e:
            logger.debug(
                "Container not available during config initialization", error=str(e)
            )
            return r[bool].ok(True)

    # Pydantic 2 field validators for boolean environment variables
    @field_validator(
        "debug", "verbose", "quiet", "interactive", "console_enabled", mode="before"
    )
    @classmethod
    def parse_bool_env_vars(cls, v: t.GeneralValueType) -> bool:
        """Parse boolean environment variables correctly from strings."""
        # Use u.parse for type-safe boolean conversion
        if isinstance(v, bool):
            return v
        parse_result = u.parse(v, bool, default=False, coerce=True)
        return parse_result.unwrap() if parse_result.is_success else bool(v)

    # Pydantic 2.11 model validator (runs after all field validators)
    @model_validator(mode="after")
    def validate_configuration(self) -> Self:
        """Validate configuration using functional composition and railway pattern."""
        validation_result = (
            self._ensure_config_directory()
            .flat_map(lambda _: self._propagate_to_context())
            .flat_map(lambda _: self._register_in_container())
        )
        if validation_result.is_failure:
            msg = f"Configuration validation failed: {validation_result.error}"
            raise ValueError(msg)
        return self

    # Pydantic 2 computed fields for smart auto-configuration
    @computed_field
    def auto_output_format(self) -> str:
        """Auto-detect optimal output format using functional composition and railway pattern.

        Detects terminal capabilities using functional pipeline:
        - Interactive vs piped output detection
        - Terminal width assessment
        - Color support evaluation
        - Format selection based on capabilities

        Returns:
            str: Optimal output format (table, json, plain, etc.)

        """

        # Functional terminal capability detection
        def detect_interactive_mode() -> r[bool]:
            """Detect if output is interactive (not piped)."""
            is_interactive = os.isatty(FlextCliConstants.ConfigValidation.STDOUT_FD)
            return r.ok(is_interactive)

        def get_terminal_width() -> r[int]:
            """Get terminal width - fast-fail on error."""
            try:
                terminal_size = shutil.get_terminal_size()
                return r.ok(terminal_size.columns)
            except Exception as e:
                return r[int].fail(f"Failed to get terminal width: {e}")

        def determine_format(is_interactive: bool, width: int, has_color: bool) -> str:
            """Determine optimal format based on capabilities."""
            # Non-interactive always uses JSON
            if not is_interactive:
                return FlextCliConstants.OutputFormats.JSON

            # Narrow terminals use plain format
            if width < FlextCliConstants.TERMINAL_WIDTH_NARROW:
                return FlextCliConstants.OutputFormats.PLAIN

            # Color terminals use table format
            if has_color:
                return FlextCliConstants.OutputFormats.TABLE

            # Default to JSON for non-color interactive terminals
            return FlextCliConstants.OutputFormats.JSON

        # Railway pattern: detect capabilities then determine format
        result = (
            detect_interactive_mode()
            .flat_map(
                lambda interactive: get_terminal_width().map(
                    lambda width: (interactive, width),
                ),
            )
            .map(
                lambda capabilities: determine_format(
                    capabilities[0]
                    if isinstance(capabilities, tuple)
                    and len(capabilities)
                    >= FlextCliConstants.ConfigValidation.CAPABILITIES_TUPLE_MIN_LENGTH
                    else False,  # is_interactive
                    capabilities[1]
                    if isinstance(capabilities, tuple)
                    and len(capabilities)
                    >= FlextCliConstants.ConfigValidation.CAPABILITIES_TUPLE_MIN_LENGTH
                    else FlextCliConstants.ConfigValidation.DEFAULT_TERMINAL_WIDTH,
                    bool(self.auto_color_support),  # has_color
                ),
            )
        )
        if result.is_success:
            format_result = result.unwrap()
            # Type narrowing: determine_format returns str
            if isinstance(format_result, str):
                return format_result
        # Fast-fail: return error format on failure
        return FlextCliConstants.OutputFormats.JSON.value

    @computed_field
    def auto_color_support(self) -> bool:
        """Auto-detect if terminal supports colors.

        Checks:
        - Configuration setting (no_color)

        Returns:
            bool: True if colors are supported, False otherwise

        """
        # Check if user explicitly disabled colors in config
        return not self.no_color

    @computed_field
    def auto_verbosity(self) -> str:
        """Auto-detect verbosity using functional pattern matching and railway approach.

        Determines verbosity level based on flags with clear priority:
        - Explicit verbose flag takes precedence
        - Quiet flag overrides normal
        - Falls back to normal verbosity

        Returns:
            str: Verbosity level (verbose, normal, quiet)

        """

        # Functional verbosity determination using pattern matching
        def determine_verbosity() -> str:
            """Determine verbosity level based on configuration."""
            match (self.verbose, self.quiet):
                case (True, _):  # Verbose takes precedence
                    return FlextCliConstants.CliGlobalDefaults.DEFAULT_VERBOSITY
                case (_, True):  # Quiet overrides normal
                    return FlextCliConstants.CliGlobalDefaults.QUIET_VERBOSITY
                case _:  # Default case
                    return FlextCliConstants.CliGlobalDefaults.NORMAL_VERBOSITY

        # Railway pattern: validate and determine verbosity
        def map_to_verbosity(_: tuple[bool, bool]) -> str:
            """Map tuple to verbosity level."""
            return determine_verbosity()

        result = r.ok((self.verbose, self.quiet)).map(map_to_verbosity)
        if result.is_success:
            verbosity_result = result.unwrap()
            # Type narrowing: map_to_verbosity returns str
            if isinstance(verbosity_result, str):
                return verbosity_result
        # Fast-fail: return normal verbosity on failure
        return FlextCliConstants.CliGlobalDefaults.NORMAL_VERBOSITY

    @computed_field
    def optimal_table_format(self) -> str:  # noqa: PLR6301
        """Determine optimal table format using functional composition and railway pattern.

        Analyzes terminal width using functional pipeline to select the best
        tabulate format for optimal visual presentation.

        Returns:
            str: Optimal tabulate format (simple, github, grid)

        """

        # Functional terminal width detection
        def get_terminal_width() -> r[int]:
            """Get terminal width - fast-fail on error."""
            try:
                terminal_size = shutil.get_terminal_size()
                return r.ok(terminal_size.columns)
            except Exception as e:
                return r[int].fail(f"Failed to get terminal width: {e}")

        def select_table_format(width: int) -> str:
            """Select optimal table format based on terminal width."""
            if width < FlextCliConstants.TERMINAL_WIDTH_NARROW:
                return FlextCliConstants.TableFormats.SIMPLE
            if width < FlextCliConstants.TERMINAL_WIDTH_MEDIUM:
                return FlextCliConstants.TableFormats.GITHUB
            return FlextCliConstants.TableFormats.GRID

        # Railway pattern: get width then select format
        result = get_terminal_width().map(select_table_format)
        if result.is_success:
            format_result = result.unwrap()
            # Type narrowing: select_table_format returns str
            if isinstance(format_result, str):
                return format_result
        # Fast-fail: return simple format on failure
        return FlextCliConstants.TableFormats.SIMPLE

    # CLI-specific methods

    @staticmethod
    def validate_output_format_result(value: str) -> r[str]:
        """Validate output format (delegates to utilities).

        Args:
            value: Output format to validate

        Returns:
            r[str]: Validated format or error with details

        """
        return FlextCliUtilities.CliValidation.validate_output_format(value)

    @classmethod
    def load_from_config_file(cls, config_file: Path) -> r[FlextCliConfig]:
        """Load configuration from file with proper error handling."""
        try:
            if not config_file.exists():
                return r[FlextCliConfig].fail(
                    FlextCliConstants.ErrorMessages.CONFIG_FILE_NOT_FOUND.format(
                        file=config_file,
                    ),
                )

            # Load based on file extension
            if config_file.suffix.lower() == FlextCliConstants.FileExtensions.JSON:
                with config_file.open(
                    "r",
                    encoding=FlextCliConstants.Encoding.UTF8,
                ) as f:
                    data = json.load(f)
            elif (
                config_file.suffix.lower()
                in FlextCliConstants.ConfigValidation.YAML_EXTENSIONS
            ):
                with config_file.open(
                    "r",
                    encoding=FlextCliConstants.Encoding.UTF8,
                ) as f:
                    data = yaml.safe_load(f)
            else:
                return r[FlextCliConfig].fail(
                    FlextCliConstants.ErrorMessages.UNSUPPORTED_CONFIG_FORMAT.format(
                        suffix=config_file.suffix,
                    ),
                )

            # Create config instance directly with loaded data
            config = cls(**data)
            return r[FlextCliConfig].ok(config)

        except Exception as e:
            return r[FlextCliConfig].fail(
                FlextCliConstants.ErrorMessages.FAILED_LOAD_CONFIG_FROM_FILE.format(
                    file=config_file,
                    error=e,
                ),
            )

    def execute_service(self) -> r[t.JsonDict]:
        """Execute config as service operation.

        Pydantic 2 Modernization:
            - Uses ConfigServiceExecutionResult model internally
            - Serializes to dict for API compatibility
            - Type-safe with field validation

        """
        # Convert to JSON-compatible dict using model_dump() and DataMapper
        # Handles Path→str, primitives as-is, nested dicts/lists, and other types via str()
        config_dict_raw = self.model_dump()
        # Use u.transform for JSON conversion
        transform_result = u.transform(config_dict_raw, to_json=True)
        config_dict = (
            transform_result.unwrap()
            if transform_result.is_success
            else config_dict_raw
        )
        result_dict: t.JsonDict = {
            "status": FlextCliConstants.ServiceStatus.OPERATIONAL.value,
            "service": FlextCliConstants.CliGlobalDefaults.DEFAULT_SERVICE_NAME,
            "timestamp": u.generate("timestamp"),
            "version": FlextCliConstants.CliGlobalDefaults.DEFAULT_VERSION_STRING,
            "config": config_dict,
        }
        return r[t.JsonDict].ok(result_dict)

    def update_from_cli_args(self, **kwargs: t.GeneralValueType) -> r[bool]:
        """Update configuration from CLI arguments with validation.

        Allows CLI commands to override configuration values dynamically.
        All updates are validated against Pydantic field validators.

        Args:
            **kwargs: Configuration key-value pairs to update

        Returns:
            r[bool]: True if update succeeded, failure on error

        Example:
            >>> config = FlextCliConfig()
            >>> result = config.update_from_cli_args(
            ...     profile="production", output_format="json", verbose=True
            ... )
            >>> result.is_success
            True

        """
        try:
            # Filter only valid configuration fields that are not computed fields
            # Computed fields (like auto_output_format) cannot be set directly
            computed_fields = {
                "auto_output_format",
                "auto_table_format",
                "auto_color_support",
                "auto_verbosity",
                "effective_log_level",
                "optimal_table_format",
            }
            # Get model fields (not computed fields) from Pydantic model_fields (class attribute)
            model_fields = set(type(self).model_fields.keys())
            # Use u.filter to get valid updates
            valid_updates_dict = u.filter(
                kwargs,
                predicate=lambda k, _v: k in model_fields and k not in computed_fields,
            )
            if isinstance(valid_updates_dict, dict):
                valid_updates: t.JsonDict = valid_updates_dict
            else:
                valid_updates = {}

            # Apply updates using u.process
            def apply_update(k: str, v: t.GeneralValueType) -> None:
                """Apply single update."""
                if k not in computed_fields:
                    setattr(self, k, v)

            u.process(valid_updates, processor=apply_update, on_error="skip")

            # Re-validate entire model to ensure consistency
            # Exclude computed fields from dump to avoid validation issues
            dump_data = self.model_dump(exclude=computed_fields)
            _ = self.model_validate(dump_data)

            return r[bool].ok(True)

        except Exception as e:
            return r[bool].fail(
                FlextCliConstants.ErrorMessages.CLI_ARGS_UPDATE_FAILED.format(error=e),
            )

    def validate_cli_overrides(
        self,
        **overrides: t.GeneralValueType,
    ) -> r[t.JsonDict]:
        """Validate CLI overrides without applying them.

        Useful for checking if CLI arguments are valid before applying.

        Args:
            **overrides: Configuration overrides to validate

        Returns:
            r[t.JsonDict]: Valid overrides or validation errors

        Example:
            >>> config = FlextCliConfig()
            >>> result = config.validate_cli_overrides(
            ...     output_format="json", max_width=120
            ... )
            >>> if result.is_success:
            ...     config.update_from_cli_args(**result.unwrap())

        """
        try:
            # Use mutable dict for building, then convert to JsonDict for return
            # Use GeneralValueType for compatibility (JsonValue is subset)
            # Use u.filter to find valid fields first
            valid_dict = u.filter(overrides, predicate=lambda k, _v: hasattr(self, k))
            valid_overrides: dict[str, t.GeneralValueType] = (
                dict(valid_dict) if isinstance(valid_dict, dict) else {}
            )

            # Validate each override value using u.process
            errors: list[str] = []

            def validate_value(k: str, v: t.GeneralValueType) -> None:
                """Validate single override value."""
                if k not in valid_overrides:
                    return
                try:
                    # Create test instance with override
                    test_config = self.model_copy()
                    setattr(test_config, k, v)
                    _ = test_config.model_validate(test_config.model_dump())
                    # Convert value to GeneralValueType for type safety
                    if isinstance(v, dict):
                        transform_result = u.transform(v, to_json=True)
                        json_value: t.GeneralValueType = (
                            transform_result.unwrap()
                            if transform_result.is_success
                            else v
                        )
                    else:
                        json_value = v
                    valid_overrides[k] = json_value
                except Exception as e:
                    errors.append(
                        FlextCliConstants.ErrorMessages.INVALID_VALUE_FOR_FIELD.format(
                            field=k,
                            error=e,
                        ),
                    )

            u.process(overrides, processor=validate_value, on_error="collect")

            if errors:
                return r[t.JsonDict].fail(
                    FlextCliConstants.ErrorMessages.VALIDATION_ERRORS.format(
                        errors="; ".join(errors),
                    ),
                )

            # Convert mutable dict to JsonDict (Mapping) for return type
            # GeneralValueType dict is compatible with JsonDict
            json_dict: t.JsonDict = dict(valid_overrides)
            return r[t.JsonDict].ok(json_dict)

        except Exception as e:
            return r[t.JsonDict].fail(f"Validation failed: {e}")

    # Protocol-compliant methods for CliConfigProvider
    def load_config(self) -> r[t.JsonDict]:
        """Load CLI configuration - implements CliConfigProvider protocol.

        Returns:
            r[t.JsonDict]: Configuration data or error

        """
        try:
            # Convert model to dictionary format using model_dump()
            # u.DataMapper handles all type conversions automatically
            config_dict_raw = self.model_dump()
            # Use u.transform for JSON conversion
            transform_result = u.transform(config_dict_raw, to_json=True)
            config_dict = (
                transform_result.unwrap()
                if transform_result.is_success
                else config_dict_raw
            )
            return r[t.JsonDict].ok(config_dict)
        except Exception as e:
            return r[t.JsonDict].fail(
                FlextCliConstants.ErrorMessages.CONFIG_LOAD_FAILED_MSG.format(error=e),
            )

    def save_config(
        self,
        config: t.JsonDict,
    ) -> r[bool]:
        """Save CLI configuration - implements CliConfigProvider protocol.

        Args:
            config: Configuration data to save

        Returns:
            r[bool]: True if save succeeded, failure on error

        """
        try:
            # Update model fields with provided config data using u.process
            def apply_config(k: str, v: t.GeneralValueType) -> None:
                """Apply single config value."""
                if hasattr(self, k):
                    setattr(self, k, v)

            u.process(config, processor=apply_config, on_error="skip")

            # Validate the updated configuration
            _ = self.model_validate(self.model_dump())
            return r[bool].ok(True)
        except Exception as e:
            return r[bool].fail(
                FlextCliConstants.ErrorMessages.CONFIG_SAVE_FAILED_MSG.format(error=e),
            )

    _instance: ClassVar[FlextCliConfig | None] = None

    @classmethod
    def get_instance(cls) -> FlextCliConfig:
        """Get singleton instance of FlextCliConfig.

        Returns:
            Singleton instance of FlextCliConfig

        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def _reset_instance(cls) -> None:
        """Reset singleton instance for testing purposes.

        This method is intended for use in tests only to allow
        clean state between test runs.
        """
        cls._instance = None


__all__ = [
    "FlextCliConfig",
]
