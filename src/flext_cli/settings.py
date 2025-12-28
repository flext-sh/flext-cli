"""FLEXT CLI Configuration Module.

**MODULE**: FlextCliSettings - Enterprise CLI configuration management.
**SCOPE**: Pydantic 2 settings, environment variables, terminal detection, output formatting,
          singleton pattern, functional validation, railway-oriented error handling.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import importlib
import json
import os
import shutil
from collections.abc import Mapping
from pathlib import Path
from typing import Annotated, ClassVar, Self

import yaml
from flext_core import (
    FlextContainer,
    FlextLogger as l_core,
    FlextSettings,
    r,
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
from flext_cli.typings import t
from flext_cli.utilities import FlextCliUtilities, u

logger = l_core(__name__)


@FlextSettings.auto_register("cli")
class FlextCliSettings(FlextSettings):
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
    - Auto-registration enables namespace access via FlextSettings.get_global_instance().cli
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

    This class uses FlextSettings.AutoConfig for automatic:
    - Singleton pattern (thread-safe)
    - Namespace registration (accessible via config.cli)
    - Test reset capability (_reset_instance)

    Implements p.ConfigProvider through structural subtyping.

    Follows standardized pattern:
    - Extends FlextSettings.AutoConfig (BaseModel) for nested config pattern
    - Flat class structure with all fields at top level
    - All defaults from FlextCliConstants
    - SecretStr for sensitive data
    - Uses FlextSettings namespace features for configuration management

    **Usage**:
        # Get singleton instance
        config = FlextCliSettings.get_instance()

        # Or via FlextSettings namespace
        from flext_core import FlextSettings
        config = FlextSettings.get_global_instance()
        cli_config = config.cli

    - Uses Python 3.13 + Pydantic 2 features
    """

    # Use FlextSettings.resolve_env_file() to ensure all FLEXT configs use same .env
    model_config = SettingsConfigDict(
        env_prefix="FLEXT_CLI_",
        env_file=FlextSettings.resolve_env_file(),
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
            default=FlextCliConstants.Cli.CliDefaults.DEFAULT_PROFILE,
            description="CLI profile to use for configuration",
        )
    )

    # Python 3.13+ best practice: Use Literal string for default consistency
    # Pydantic 2 accepts Literal strings in Literal-typed fields
    output_format: FlextCliConstants.Cli.OutputFormatLiteral = Field(
        default="table",  # Use Literal string for Literal type
        description="Default output format for CLI commands",
    )

    no_color: bool = Field(
        default=FlextCliConstants.Cli.CliDefaults.DEFAULT_NO_COLOR,
        description="Disable colored output in CLI",
    )

    config_dir: Path = Field(
        default_factory=lambda: (
            Path.home() / FlextCliConstants.Cli.Paths.FLEXT_DIR_NAME
        ),
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
        default_factory=lambda: (
            Path.home()
            / FlextCliConstants.Cli.Paths.FLEXT_DIR_NAME
            / FlextCliConstants.Cli.Paths.TOKEN_FILE_NAME
        ),
        description="Path to authentication token file",
    )

    refresh_token_file: Path = Field(
        default_factory=lambda: (
            Path.home()
            / FlextCliConstants.Cli.Paths.FLEXT_DIR_NAME
            / FlextCliConstants.Cli.Paths.REFRESH_TOKEN_FILE_NAME
        ),
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
        default=FlextCliConstants.Cli.CliDefaults.DEFAULT_VERBOSE,
        description="Enable verbose CLI output",
    )

    version: str = Field(
        default=FlextCliConstants.Cli.CliDefaults.DEFAULT_VERSION,
        description="Application version",
    )
    quiet: bool = Field(
        default=FlextCliConstants.Cli.CliDefaults.DEFAULT_QUIET,
        description="Enable quiet mode",
    )
    interactive: bool = Field(
        default=FlextCliConstants.Cli.CliDefaults.DEFAULT_INTERACTIVE,
        description="Enable interactive mode",
    )
    environment: str = Field(
        default="development",
        description="Deployment environment",
    )

    max_width: int = Field(
        default=FlextCliConstants.Cli.CliDefaults.DEFAULT_MAX_WIDTH,
        ge=FlextCliConstants.Cli.ValidationLimits.MIN_MAX_WIDTH,
        le=FlextCliConstants.Cli.ValidationLimits.MAX_MAX_WIDTH,
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
    log_verbosity: str = Field(  # Must match FlextSettings.log_verbosity type
        default=FlextCliConstants.Cli.LogVerbosity.DETAILED.value,  # Python 3.13+ best practice: Use Enum value
        description="Logging verbosity (compact, detailed, full)",
    )

    cli_log_level: str = Field(
        default="info",  # Default log level
        description="CLI-specific logging level",
    )

    cli_log_verbosity: str = Field(
        default="detailed",
        description="CLI-specific logging verbosity",
    )

    log_file: str | None = Field(
        default=None,
        description="Optional log file path for persistent logging",
    )

    console_enabled: bool = Field(
        default=FlextCliConstants.Cli.Logging.CONSOLE_ENABLED,
        description="Enable console logging output",
    )

    def _ensure_config_directory(self) -> r[Path]:
        """Ensure config directory exists with proper error handling."""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            return r.ok(self.config_dir)
        except (PermissionError, OSError) as e:
            error_msg = (
                FlextCliConstants.Cli.ErrorMessages.CANNOT_ACCESS_CONFIG_DIR.format(
                    config_dir=self.config_dir,
                    error=e,
                )
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
            # Convert config object to t.GeneralValueType-compatible dict for context
            # Use FlextCliUtilities.transform for JSON conversion
            transform_result = FlextCliUtilities.transform(
                self.model_dump(),
                to_json=True,
            )
            config_dict = (
                transform_result.value
                if transform_result.is_success
                else self.model_dump()
            )
            _ = context.set("cli_config", config_dict)
            # Computed fields return values directly - convert to t.GeneralValueType
            _ = context.set("cli_auto_output_format", str(self.auto_output_format))
            _ = context.set("cli_auto_color_support", bool(self.auto_color_support))
            _ = context.set("cli_auto_verbosity", str(self.auto_verbosity))
            _ = context.set("cli_optimal_table_format", str(self.optimal_table_format))
            return r[bool].ok(True)
        except Exception as e:
            logger.debug(
                "Context not available during config initialization",
                error=str(e),
            )
            return r[bool].ok(True)

    def _register_in_container(self) -> r[bool]:
        """Register configuration in FlextContainer for dependency injection."""
        try:
            container = FlextContainer()
            if not container.has_service("flext_cli_config"):
                # FlextCliSettings extends FlextSettings (BaseModel)
                # Use model_dump() to get dict representation for container
                config_dict = self.model_dump()
                _ = container.with_service("flext_cli_config", config_dict)
            return r[bool].ok(True)
        except Exception as e:
            logger.debug(
                "Container not available during config initialization",
                error=str(e),
            )
            return r[bool].ok(True)

    # Pydantic 2 field validators for boolean environment variables
    @field_validator(
        "debug",
        "verbose",
        "quiet",
        "interactive",
        "console_enabled",
        mode="before",
    )
    @classmethod
    def parse_bool_env_vars(cls, v: t.GeneralValueType) -> bool:
        """Parse boolean environment variables correctly from strings."""
        # Use FlextCliUtilities.Cli.parse for type-safe boolean conversion
        if isinstance(v, bool):
            return v
        # Simple boolean parsing for environment variables
        if isinstance(v, str):
            return v.lower() in {"true", "1", "yes", "on"}
        return bool(v)

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
            str: Optimal output format (table, json, plain, etFlextCliConstants.Cli.)

        """

        # Functional terminal capability detection
        def detect_interactive_mode() -> r[bool]:
            """Detect if output is interactive (not piped)."""
            is_interactive = os.isatty(1)  # STDOUT_FD = 1
            return r.ok(is_interactive)

        def get_terminal_width() -> r[int]:
            """Get terminal width - fast-fail on error."""
            try:
                terminal_size = shutil.get_terminal_size()
                return r.ok(terminal_size.columns)
            except Exception as e:
                return r[int].fail(f"Failed to get terminal width: {e}")

        def determine_format(
            width: int,
            *,
            is_interactive: bool,
            has_color: bool,
        ) -> str:
            """Determine optimal format based on capabilities."""
            # Non-interactive always uses JSON
            if not is_interactive:
                return FlextCliConstants.Cli.OutputFormats.JSON.value

            # Narrow terminals use plain format
            min_terminal_width = 80
            if width < min_terminal_width:
                return FlextCliConstants.Cli.OutputFormats.PLAIN.value

            # Color terminals use table format
            if has_color:
                return FlextCliConstants.Cli.OutputFormats.TABLE.value

            # Default to JSON for non-color interactive terminals
            return FlextCliConstants.Cli.OutputFormats.JSON.value

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
                    width=capabilities[1] if len(capabilities) > 1 else 80,
                    is_interactive=capabilities[0] if len(capabilities) >= 1 else False,
                    has_color=bool(self.auto_color_support),
                ),
            )
        )
        if result.is_success:
            # determine_format returns str
            return result.value
        # Fast-fail: return error format on failure
        return FlextCliConstants.Cli.OutputFormats.JSON.value

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
        def determine_verbosity(*, verbose: bool = False, quiet: bool = False) -> str:
            """Determine verbosity level based on flags."""
            match (verbose, quiet):
                case (True, _):  # Verbose takes precedence
                    return FlextCliConstants.Cli.CliGlobalDefaults.DEFAULT_VERBOSITY
                case (_, True):  # Quiet overrides normal
                    return FlextCliConstants.Cli.CliGlobalDefaults.QUIET_VERBOSITY
                case _:  # Default case
                    return FlextCliConstants.Cli.CliGlobalDefaults.NORMAL_VERBOSITY

        result = r.ok((self.verbose, self.quiet)).map(
            lambda flags: determine_verbosity(verbose=flags[0], quiet=flags[1]),
        )
        if result.is_success:
            # map_to_verbosity returns str
            return result.value
        # Fast-fail: return normal verbosity on failure
        return FlextCliConstants.Cli.CliGlobalDefaults.NORMAL_VERBOSITY

    @computed_field
    def optimal_table_format(self) -> str:
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
            min_terminal_width = 80
            medium_terminal_width = 120
            if width < min_terminal_width:
                return "simple"
            if width < medium_terminal_width:
                return "github"
            return "grid"

        # Railway pattern: get width then select format
        result = get_terminal_width().map(select_table_format)
        if result.is_success:
            # select_table_format returns str
            return result.value
        # Fast-fail: return simple format on failure
        return FlextCliConstants.Cli.TableFormats.SIMPLE

    # CLI-specific methods

    @staticmethod
    def validate_output_format_result(value: str) -> r[str]:
        """Validate output format (delegates to utilities).

        Args:
            value: Output format to validate

        Returns:
            r[str]: Validated format or error with details

        """
        # Validate output format
        valid_formats = u.Cli.CliValidation.get_valid_output_formats()
        if value in valid_formats:
            return r.ok(value)
        return r.fail(
            f"Invalid format '{value}'. Valid formats: {', '.join(valid_formats)}",
        )

    @classmethod
    def load_from_config_file(cls, config_file: Path) -> r[FlextCliSettings]:
        """Load configuration from file with proper error handling."""
        try:
            if not config_file.exists():
                return r[FlextCliSettings].fail(
                    FlextCliConstants.Cli.ErrorMessages.CONFIG_FILE_NOT_FOUND.format(
                        file=config_file,
                    ),
                )

            # Load based on file extension
            if config_file.suffix.lower() == ".json":
                with config_file.open(
                    "r",
                    encoding="utf-8",
                ) as f:
                    data = json.load(f)
            elif config_file.suffix.lower() in {".yaml", ".yml"}:
                with config_file.open(
                    "r",
                    encoding="utf-8",
                ) as f:
                    data = yaml.safe_load(f)
            else:
                return r[FlextCliSettings].fail(
                    FlextCliConstants.Cli.ErrorMessages.UNSUPPORTED_CONFIG_FORMAT.format(
                        suffix=config_file.suffix,
                    ),
                )

            # Create config instance directly with loaded data
            config = cls(**data)
            return r[FlextCliSettings].ok(config)

        except Exception as e:
            return r[FlextCliSettings].fail(
                FlextCliConstants.Cli.ErrorMessages.FAILED_LOAD_CONFIG_FROM_FILE.format(
                    file=config_file,
                    error=e,
                ),
            )

    def execute_service(self) -> r[Mapping[str, t.GeneralValueType]]:
        """Execute config as service operation.

        Pydantic 2 Modernization:
            - Uses ConfigServiceExecutionResult model internally
            - Serializes to dict for API compatibility
            - Type-safe with field validation

        """
        # Convert to JSON-compatible dict using model_dump() and Mapper
        # Handles Path→str, primitives as-is, nested dicts/lists, and other types via str()
        config_dict_raw = self.model_dump()
        # Use FlextCliUtilities.transform for JSON conversion
        transform_result = FlextCliUtilities.transform(config_dict_raw, to_json=True)
        config_dict = transform_result.map_or(config_dict_raw)
        result_dict: dict[str, t.GeneralValueType] = {
            "status": FlextCliConstants.Cli.ServiceStatus.OPERATIONAL.value,
            "service": FlextCliConstants.Cli.CliGlobalDefaults.DEFAULT_SERVICE_NAME,
            "timestamp": FlextCliUtilities.generate("timestamp"),
            "version": FlextCliConstants.Cli.CliGlobalDefaults.DEFAULT_VERSION_STRING,
            "config": config_dict,
        }
        return r[dict[str, t.GeneralValueType]].ok(result_dict)

    def update_from_cli_args(self, **kwargs: t.GeneralValueType) -> r[bool]:
        """Update configuration from CLI arguments with validation.

        Allows CLI commands to override configuration values dynamically.
        All updates are validated against Pydantic field validators.

        Args:
            **kwargs: Configuration key-value pairs to update

        Returns:
            r[bool]: True if update succeeded, failure on error

        Example:
            >>> config = FlextCliSettings()
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
            # Filter dict items using dict comprehension (FlextCliUtilities.filter only works with lists/tuples)
            valid_updates: dict[str, t.GeneralValueType] = {
                k: v
                for k, v in kwargs.items()
                if k in model_fields and k not in computed_fields
            }

            # Apply updates using FlextCliUtilities.process
            def apply_update(k: str, v: t.GeneralValueType) -> None:
                """Apply single update."""
                if k not in computed_fields:
                    setattr(self, k, v)

            _ = FlextCliUtilities.Cli.process_mapping(
                valid_updates,
                processor=apply_update,
                on_error="skip",
            )

            # Re-validate entire model to ensure consistency
            # Exclude computed fields from dump to avoid validation issues
            dump_data = self.model_dump(exclude=computed_fields)
            _ = self.model_validate(dump_data)

            return r[bool].ok(True)

        except Exception as e:
            return r[bool].fail(
                FlextCliConstants.Cli.ErrorMessages.CLI_ARGS_UPDATE_FAILED.format(
                    error=e,
                ),
            )

    def validate_cli_overrides(
        self,
        **overrides: t.GeneralValueType,
    ) -> r[dict[str, t.GeneralValueType]]:
        """Validate CLI overrides without applying them.

        Useful for checking if CLI arguments are valid before applying.

        Args:
            **overrides: Configuration overrides to validate

        Returns:
            r[dict[str, t.GeneralValueType]]: Valid overrides or validation errors

        Example:
            >>> config = FlextCliSettings()
            >>> result = config.validate_cli_overrides(
            ...     output_format="json", max_width=120
            ... )
            >>> if result.is_success:
            ...     config.update_from_cli_args(**result.value)

        """
        try:
            # Use mutable dict for building, then convert to JsonDict for return
            # Use t.GeneralValueType for compatibility (JsonValue is subset)
            # Filter dict items using dict comprehension (FlextCliUtilities.filter only works with lists/tuples)
            valid_overrides: dict[str, t.GeneralValueType] = {
                k: v for k, v in overrides.items() if hasattr(self, k)
            }

            # Validate each override value using FlextCliUtilities.process
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
                    # Convert value to t.GeneralValueType for type safety
                    if isinstance(v, dict):
                        transform_result = FlextCliUtilities.transform(v, to_json=True)
                        json_value: t.GeneralValueType = transform_result.map_or(v)
                    else:
                        json_value = v
                    valid_overrides[k] = json_value
                except Exception as e:
                    errors.append(
                        FlextCliConstants.Cli.ErrorMessages.INVALID_VALUE_FOR_FIELD.format(
                            field=k,
                            error=e,
                        ),
                    )

            FlextCliUtilities.Cli.process_mapping(
                overrides,
                processor=validate_value,
                on_error="collect",
            )

            if errors:
                return r[dict[str, t.GeneralValueType]].fail(
                    FlextCliConstants.Cli.ErrorMessages.VALIDATION_ERRORS.format(
                        errors="; ".join(errors),
                    ),
                )

            # Convert mutable dict to JsonDict (Mapping) for return type
            # t.GeneralValueType dict is compatible with JsonDict
            json_dict: dict[str, t.GeneralValueType] = dict(valid_overrides)
            return r[dict[str, t.GeneralValueType]].ok(json_dict)

        except Exception as e:
            return r[dict[str, t.GeneralValueType]].fail(f"Validation failed: {e}")

    # Protocol-compliant methods for CliConfigProvider
    def load_config(self) -> r[Mapping[str, t.GeneralValueType]]:
        """Load CLI configuration - implements CliConfigProvider protocol.

        Returns:
            r[dict[str, t.GeneralValueType]]: Configuration data or error

        """
        try:
            # Convert model to dictionary format using model_dump()
            # FlextCliUtilities.Mapper handles all type conversions automatically
            config_dict_raw = self.model_dump()
            # Use FlextCliUtilities.transform for JSON conversion
            transform_result = FlextCliUtilities.transform(
                config_dict_raw,
                to_json=True,
            )
            config_dict = (
                transform_result.value
                if transform_result.is_success
                else config_dict_raw
            )
            return r[Mapping[str, t.GeneralValueType]].ok(config_dict)
        except Exception as e:
            return r[Mapping[str, t.GeneralValueType]].fail(
                FlextCliConstants.Cli.ErrorMessages.CONFIG_LOAD_FAILED_MSG.format(
                    error=e,
                ),
            )

    def save_config(
        self,
        config: dict[str, t.GeneralValueType],
    ) -> r[bool]:
        """Save CLI configuration - implements CliConfigProvider protocol.

        Args:
            config: Configuration data to save

        Returns:
            r[bool]: True if save succeeded, failure on error

        """
        try:
            # Update model fields with provided config data using FlextCliUtilities.process
            def apply_config(k: str, v: t.GeneralValueType) -> None:
                """Apply single config value."""
                if hasattr(self, k):
                    setattr(self, k, v)

            FlextCliUtilities.Cli.process_mapping(
                config,
                processor=apply_config,
                on_error="skip",
            )

            # Validate the updated configuration
            _ = self.model_validate(self.model_dump())
            return r[bool].ok(True)
        except Exception as e:
            return r[bool].fail(
                FlextCliConstants.Cli.ErrorMessages.CONFIG_SAVE_FAILED_MSG.format(
                    error=e,
                ),
            )

    _instance: ClassVar[FlextCliSettings | None] = None

    @classmethod
    def get_instance(cls) -> FlextCliSettings:
        """Get singleton instance of FlextCliSettings.

        Returns:
            Singleton instance of FlextCliSettings

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
