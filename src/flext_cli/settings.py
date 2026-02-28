"""FLEXT CLI Configuration Module.

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
from typing import Annotated, ClassVar, Self, override

import yaml
from flext_core import (
    FlextContainer,
    FlextLogger,
    FlextSettings,
    r,
)
from pydantic import (
    Field,
    SecretStr,
    StringConstraints,
    ValidationError,
    computed_field,
    field_validator,
    model_validator,
)
from pydantic_settings import SettingsConfigDict

from flext_cli import c, t, u

logger = FlextLogger(__name__)


@FlextSettings.auto_register("cli")
class FlextCliSettings(FlextSettings):
    """Flat Pydantic 2 settings with AutoConfig pattern.

    Singleton, env var overrides (FLEXT_CLI_*), SecretStr for sensitive data.
    Auto-registered as 'cli' namespace via FlextSettings.
    """

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

    profile: Annotated[str, StringConstraints(min_length=1, strip_whitespace=True)] = (
        Field(default=c.Cli.CliDefaults.DEFAULT_PROFILE)
    )
    output_format: c.Cli.OutputFormatLiteral = Field(default="table")
    no_color: bool = Field(default=c.Cli.CliDefaults.DEFAULT_NO_COLOR)
    config_dir: Path = Field(
        default_factory=lambda: Path.home() / c.Cli.Paths.FLEXT_DIR_NAME,
    )
    project_name: str = Field(default="flext-cli")
    api_url: str = Field(default="http://localhost:8080/api")
    cli_api_key: SecretStr | None = Field(default=None)
    token_file: Path = Field(
        default_factory=lambda: (
            Path.home() / c.Cli.Paths.FLEXT_DIR_NAME / c.Cli.Paths.TOKEN_FILE_NAME
        ),
    )
    refresh_token_file: Path = Field(
        default_factory=lambda: (
            Path.home()
            / c.Cli.Paths.FLEXT_DIR_NAME
            / c.Cli.Paths.REFRESH_TOKEN_FILE_NAME
        ),
    )
    auto_refresh: bool = Field(default=True)
    debug: bool = Field(default=False)
    trace: bool = Field(default=False)
    verbose: bool = Field(default=c.Cli.CliDefaults.DEFAULT_VERBOSE)
    version: str = Field(default=c.Cli.CliDefaults.DEFAULT_VERSION)
    quiet: bool = Field(default=c.Cli.CliDefaults.DEFAULT_QUIET)
    interactive: bool = Field(default=c.Cli.CliDefaults.DEFAULT_INTERACTIVE)
    environment: str = Field(default="development")
    max_width: int = Field(
        default=c.Cli.CliDefaults.DEFAULT_MAX_WIDTH,
        ge=c.Cli.ValidationLimits.MIN_MAX_WIDTH,
        le=c.Cli.ValidationLimits.MAX_MAX_WIDTH,
    )
    config_file: Path | None = Field(default=None)
    cli_timeout: float = Field(default=30, ge=0, le=300)
    max_retries: int = Field(default=3, ge=0, le=10)
    log_verbosity: str = Field(default=c.Cli.LogVerbosity.DETAILED.value)
    cli_log_level: str = Field(default="info")
    cli_log_verbosity: str = Field(default="detailed")
    log_file: str | None = Field(default=None)
    console_enabled: bool = Field(default=c.Cli.Logging.CONSOLE_ENABLED)

    def _ensure_config_directory(self) -> r[Path]:
        """Ensure config directory exists with proper error handling."""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            return r.ok(self.config_dir)
        except (PermissionError, OSError) as e:
            error_msg = c.Cli.ErrorMessages.CANNOT_ACCESS_CONFIG_DIR.format(
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
            # Use u.transform for JSON conversion
            transform_result = u.transform(
                self.model_dump(),
                to_json=True,
            )
            config_dict = (
                transform_result.value
                if transform_result.is_success
                else self.model_dump()
            )
            _ = context.set("cli_config", config_dict)
            # Computed fields return values directly - convert to t.JsonValue
            _ = context.set("cli_auto_output_format", str(self.auto_output_format))
            _ = context.set("cli_auto_color_support", bool(self.auto_color_support))
            _ = context.set("cli_auto_verbosity", str(self.auto_verbosity))
            _ = context.set("cli_optimal_table_format", str(self.optimal_table_format))
            return r[bool].ok(value=True)
        except (AttributeError, TypeError, RuntimeError) as e:
            logger.debug(
                "Context not available during config initialization",
                error=str(e),
            )
            return r[bool].ok(value=True)

    def _register_in_container(self) -> r[bool]:
        """Register configuration in FlextContainer for dependency injection."""
        try:
            container = FlextContainer()
            if not container.has_service("flext_cli_config"):
                # FlextCliSettings extends FlextSettings (BaseModel)
                # Use model_dump() to get dict representation for container
                config_dict = self.model_dump()
                _ = container.with_service("flext_cli_config", config_dict)
            return r[bool].ok(value=True)
        except (AttributeError, TypeError, RuntimeError) as e:
            logger.debug(
                "Container not available during config initialization",
                error=str(e),
            )
            return r[bool].ok(value=True)

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
        if v is True or v is False:
            return bool(v)
        normalized = str(v).strip().lower()
        if normalized in {"true", "1", "yes", "on"}:
            return True
        if normalized in {"false", "0", "no", "off", "none", ""}:
            return False
        return bool(v)

    # Pydantic 2.11 model validator (runs after all field validators)
    @override
    @model_validator(mode="after")
    def validate_configuration(self) -> Self:
        """Validate configuration using functional composition and railway pattern."""
        validation_result = (
            self
            ._ensure_config_directory()
            .flat_map(lambda _: self._propagate_to_context())
            .flat_map(lambda _: self._register_in_container())
        )
        if validation_result.is_failure:
            msg = f"Configuration validation failed: {validation_result.error}"
            raise ValueError(msg)
        return self

    @computed_field
    def auto_output_format(self) -> str:
        """Auto-detect optimal output format based on terminal capabilities."""
        fmt = c.Cli.OutputFormats
        try:
            is_interactive = os.isatty(1)
        except (OSError, RuntimeError) as e:
            logger.debug("isatty(1) failed, defaulting to JSON output: %s", e)
            return fmt.JSON.value
        width = self._try_terminal_width()
        if width is None:
            return fmt.JSON.value
        if not is_interactive:
            return fmt.JSON.value
        if width < c.Cli.Terminal.WIDTH_NARROW:
            return fmt.PLAIN.value
        return fmt.TABLE.value if not self.no_color else fmt.JSON.value

    @computed_field
    def auto_color_support(self) -> bool:
        """Auto-detect if terminal supports colors."""
        return not self.no_color

    @computed_field
    def auto_verbosity(self) -> str:
        """Auto-detect verbosity level (verbose > quiet > normal)."""
        gd = c.Cli.CliGlobalDefaults
        if self.verbose:
            return gd.DEFAULT_VERBOSITY
        if self.quiet:
            return gd.QUIET_VERBOSITY
        return gd.NORMAL_VERBOSITY

    @computed_field
    def optimal_table_format(self) -> str:
        """Determine optimal tabulate format based on terminal width."""
        width = self._try_terminal_width()
        if width is None:
            return c.Cli.TableFormats.SIMPLE
        if width < c.Cli.Terminal.WIDTH_NARROW:
            return "simple"
        return "github" if width < c.Cli.Terminal.WIDTH_MEDIUM else "grid"

    @staticmethod
    def _try_terminal_width() -> int | None:
        """Read terminal width safely without leaking exceptions."""
        try:
            return shutil.get_terminal_size().columns
        except OSError as e:
            logger.debug("get_terminal_size failed: %s", e)
            return None

    @staticmethod
    def validate_output_format_result(value: str) -> r[str]:
        """Validate output format."""
        valid_formats = u.Cli.CliValidation.get_valid_output_formats()
        if value in valid_formats:
            return r.ok(value)
        return r.fail(
            f"Invalid format '{value}'. Valid formats: {', '.join(valid_formats)}",
        )

    @classmethod
    def load_from_config_file(cls, config_file: Path) -> r[FlextCliSettings]:
        """Load configuration from JSON/YAML file."""
        em = c.Cli.ErrorMessages
        try:
            if not config_file.exists():
                return r[FlextCliSettings].fail(
                    em.CONFIG_FILE_NOT_FOUND.format(file=config_file),
                )
            suffix = config_file.suffix.lower()
            with config_file.open("r", encoding="utf-8") as f:
                if suffix == ".json":
                    data = json.load(f)
                elif suffix in {".yaml", ".yml"}:
                    data = yaml.safe_load(f)
                else:
                    return r[FlextCliSettings].fail(
                        em.UNSUPPORTED_CONFIG_FORMAT.format(suffix=suffix),
                    )
            return r[FlextCliSettings].ok(cls(**data))
        except (OSError, ValueError, ValidationError, yaml.YAMLError) as e:
            return r[FlextCliSettings].fail(
                em.FAILED_LOAD_CONFIG_FROM_FILE.format(file=config_file, error=e),
            )

    def execute_service(self) -> r[Mapping[str, t.JsonValue]]:
        """Execute config as service operation."""
        config_dict = u.transform(self.model_dump(), to_json=True).map_or(
            self.model_dump(),
        )
        result_dict: dict[str, t.JsonValue] = {
            "status": c.Cli.ServiceStatus.OPERATIONAL.value,
            "service": c.Cli.CliGlobalDefaults.DEFAULT_SERVICE_NAME,
            "timestamp": u.generate("timestamp"),
            "version": c.Cli.CliGlobalDefaults.DEFAULT_VERSION_STRING,
            "config": config_dict,
        }
        return r[Mapping[str, t.JsonValue]].ok(result_dict)

    _COMPUTED: ClassVar[set[str]] = {
        "auto_output_format",
        "auto_table_format",
        "auto_color_support",
        "auto_verbosity",
        "effective_log_level",
        "optimal_table_format",
    }

    def update_from_cli_args(self, **kwargs: t.JsonValue) -> r[bool]:
        """Update configuration from CLI arguments with validation."""
        try:
            model_fields = set(type(self).model_fields.keys())
            valid = {
                k: v
                for k, v in kwargs.items()
                if k in model_fields and k not in self._COMPUTED
            }
            for k, v in valid.items():
                setattr(self, k, v)
            _ = self.model_validate(self.model_dump(exclude=self._COMPUTED))
            return r[bool].ok(value=True)
        except (ValidationError, TypeError, AttributeError) as e:
            return r[bool].fail(
                c.Cli.ErrorMessages.CLI_ARGS_UPDATE_FAILED.format(error=e),
            )

    def validate_cli_overrides(
        self,
        **overrides: t.JsonValue,
    ) -> r[Mapping[str, t.JsonValue]]:
        """Validate CLI overrides without applying them."""
        em = c.Cli.ErrorMessages
        try:
            model_fields = set(type(self).model_fields.keys())
            valid: dict[str, t.JsonValue] = {
                k: v for k, v in overrides.items() if k in model_fields
            }
            errors: list[str] = []
            for k, v in valid.items():
                try:
                    if not hasattr(self, k):
                        msg = f"Unknown field: {k}"
                        raise ValueError(msg)
                    test_cfg = self.model_copy()
                    setattr(test_cfg, k, v)
                    _ = test_cfg.model_validate(test_cfg.model_dump())
                    if isinstance(v, Mapping):
                        valid[k] = u.transform(v, to_json=True).map_or(v)
                    else:
                        valid[k] = v
                except (ValidationError, TypeError, AttributeError, RuntimeError) as e:
                    errors.append(em.INVALID_VALUE_FOR_FIELD.format(field=k, error=e))
            if errors:
                return r[Mapping[str, t.JsonValue]].fail(
                    em.VALIDATION_ERRORS.format(errors="; ".join(errors)),
                )
            return r[Mapping[str, t.JsonValue]].ok(valid)
        except (ValidationError, TypeError, RuntimeError) as e:
            return r[Mapping[str, t.JsonValue]].fail(f"Validation failed: {e}")

    def load_config(self) -> r[Mapping[str, t.JsonValue]]:
        """Load CLI configuration — implements CliConfigProvider protocol."""
        try:
            raw: dict[str, t.JsonValue] = dict(self.model_dump(mode="json"))
            return r[Mapping[str, t.JsonValue]].ok(raw)
        except (ValidationError, TypeError, RuntimeError) as e:
            return r[Mapping[str, t.JsonValue]].fail(
                c.Cli.ErrorMessages.CONFIG_LOAD_FAILED_MSG.format(error=e),
            )

    def save_config(
        self,
        config: FlextCliSettings | Mapping[str, t.JsonValue],
    ) -> r[bool]:
        """Save CLI configuration — implements CliConfigProvider protocol."""
        try:
            to_save = (
                config.model_dump() if isinstance(config, FlextCliSettings) else config
            )
            model_fields = set(type(self).model_fields.keys())
            for k, v in to_save.items():
                if k in model_fields:
                    setattr(self, k, v)
            _ = self.model_validate(self.model_dump())
            return r[bool].ok(value=True)
        except (ValidationError, TypeError, AttributeError) as e:
            return r[bool].fail(
                c.Cli.ErrorMessages.CONFIG_SAVE_FAILED_MSG.format(error=e),
            )

    _instance: ClassVar[FlextCliSettings | None] = None

    @classmethod
    def get_instance(cls) -> FlextCliSettings:
        """Get singleton instance of FlextCliSettings."""
        if cls._instance is None:
            cls._instance = cls()
        instance = cls._instance
        if instance is None:
            msg = "FlextCliSettings instance was not initialized"
            raise RuntimeError(msg)
        return instance

    @override
    @classmethod
    def _reset_instance(cls) -> None:
        """Reset singleton instance for testing."""
        cls._instance = None
        super()._reset_instance()
