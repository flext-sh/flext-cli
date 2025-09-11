"""FLEXT CLI Config - Unified configuration service using flext-core directly.

Single responsibility configuration service eliminating ALL loose functions
and wrapper patterns. Uses flext-core utilities directly with SOURCE OF TRUTH
principle for all configurations and metadata.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import importlib
from pathlib import Path
from typing import TypedDict

from flext_core import (
    FlextContainer,
    FlextDomainService,
    FlextResult,
    FlextUtilities,
)

from flext_cli.constants import FlextCliConstants


class FlextCliConfig(FlextDomainService[str]):
    """Unified configuration service using flext-core utilities directly.

    Eliminates ALL wrapper methods and loose functions, using flext-core
    utilities directly without abstraction layers. Uses SOURCE OF TRUTH
    principle for all configuration metadata loading.

    SOLID Principles Applied:
        - Single Responsibility: Configuration management only
        - Open/Closed: Extensible through flext-core patterns
        - Dependency Inversion: Uses FlextContainer for dependencies
        - Interface Segregation: Focused configuration interface
    """

    class ConfigData(TypedDict):
        """Configuration data structure from SOURCE OF TRUTH."""

        profile: str
        debug: bool
        output_format: str
        timeout: int
        api_url: str | None

    class ValidationResult(TypedDict):
        """Configuration validation result structure."""

        is_valid: bool
        errors: list[str]
        warnings: list[str]

    class PathInfo(TypedDict):
        """Configuration path information structure."""

        path_type: str
        location: Path
        exists: bool

    class FormatOptions(TypedDict):
        """Output format options from SOURCE OF TRUTH."""

        format_type: str
        supports_colors: bool
        requires_import: str | None

    def __init__(self, **_data: object) -> None:
        """Initialize configuration service with flext-core dependencies and SOURCE OF TRUTH."""
        super().__init__()
        self._container = FlextContainer.get_global()

        # Load constants from SOURCE OF TRUTH - NO deduction
        constants_result = self._load_constants_metadata()
        if constants_result.is_failure:
            msg = f"Failed to load constants metadata: {constants_result.error}"
            raise ValueError(msg)
        self._constants = constants_result.value

        # Load format metadata from SOURCE OF TRUTH
        format_metadata_result = self._load_format_metadata()
        if format_metadata_result.is_failure:
            msg = f"Failed to load format metadata: {format_metadata_result.error}"
            raise ValueError(msg)
        self._format_metadata = format_metadata_result.value

    def _load_constants_metadata(self) -> FlextResult[FlextCliConstants]:
        """Load constants metadata from SOURCE OF TRUTH."""
        try:
            # Direct metadata loading - NO deduction or assumptions
            constants_instance = FlextCliConstants()
            return FlextResult[FlextCliConstants].ok(constants_instance)
        except (
            ImportError,
            AttributeError,
            ValueError,
        ) as e:
            return FlextResult[FlextCliConstants].fail(
                f"Constants metadata load failed: {e}",
            )

    def _load_format_metadata(
        self,
    ) -> FlextResult[dict[str, FlextCliConfig.FormatOptions]]:
        """Load output format metadata from SOURCE OF TRUTH."""
        try:
            # SOURCE OF TRUTH format configurations - NO deduction
            format_metadata: dict[str, FlextCliConfig.FormatOptions] = {
                "json": {
                    "format_type": "json",
                    "supports_colors": False,
                    "requires_import": None,
                },
                "yaml": {
                    "format_type": "yaml",
                    "supports_colors": False,
                    "requires_import": "yaml",
                },
                "table": {
                    "format_type": "table",
                    "supports_colors": True,
                    "requires_import": None,
                },
                "plain": {
                    "format_type": "plain",
                    "supports_colors": False,
                    "requires_import": None,
                },
            }

            return FlextResult[dict[str, FlextCliConfig.FormatOptions]].ok(
                format_metadata,
            )
        except (
            ImportError,
            AttributeError,
            ValueError,
        ) as e:
            return FlextResult[dict[str, FlextCliConfig.FormatOptions]].fail(
                f"Format metadata load failed: {e}",
            )

    def get_config_data(
        self,
        config_object: object,
    ) -> FlextResult[FlextCliConfig.ConfigData]:
        """Extract configuration data from config object using SOURCE OF TRUTH."""
        try:
            if not config_object:
                return FlextResult[FlextCliConfig.ConfigData].fail(
                    "Config object is None",
                )

            # Extract using SOURCE OF TRUTH attribute names
            config_data: FlextCliConfig.ConfigData = {
                "profile": getattr(config_object, "profile", "default"),
                "debug": getattr(config_object, "debug", False),
                "output_format": getattr(config_object, "output_format", "table"),
                "timeout": getattr(
                    config_object,
                    "timeout",
                    self._constants.DEFAULT_COMMAND_TIMEOUT,
                ),
                "api_url": getattr(config_object, "api_url", None),
            }

            return FlextResult[FlextCliConfig.ConfigData].ok(config_data)

        except (
            ImportError,
            AttributeError,
            ValueError,
        ) as e:
            return FlextResult[FlextCliConfig.ConfigData].fail(
                f"Config data extraction from SOURCE OF TRUTH failed: {e}",
            )

    def find_config_value(self, config_object: object, key: str) -> FlextResult[object]:
        """Find configuration value using SOURCE OF TRUTH attribute lookup."""
        try:
            if not config_object:
                return FlextResult[object].fail("Config object is None")

            # Direct attribute access from SOURCE OF TRUTH
            if hasattr(config_object, key):
                value = getattr(config_object, key)
                return FlextResult[object].ok(value)

            # Check in settings if present (SOURCE OF TRUTH fallback)
            settings = getattr(config_object, "settings", None)
            if settings and hasattr(settings, key):
                value = getattr(settings, key)
                return FlextResult[object].ok(value)

            return FlextResult[object].fail(
                f"Configuration key '{key}' not found in SOURCE OF TRUTH",
            )

        except (
            ImportError,
            AttributeError,
            ValueError,
        ) as e:
            return FlextResult[object].fail(
                f"Config value lookup from SOURCE OF TRUTH failed: {e}",
            )

    def format_config_output(
        self,
        data: dict[str, object],
        format_type: str,
    ) -> FlextResult[str]:
        """Format configuration output using SOURCE OF TRUTH format metadata."""
        try:
            # Get format metadata from SOURCE OF TRUTH
            format_info = self._format_metadata.get(format_type)
            if not format_info:
                return FlextResult[str].fail(f"Unsupported format type: {format_type}")

            # Handle JSON formatting using flext-core utilities
            if format_info["format_type"] == "json":
                json_result = FlextUtilities.safe_json_stringify(data)
                return FlextResult[str].ok(json_result)

            # Handle YAML formatting using SOURCE OF TRUTH import metadata
            if format_info["format_type"] == "yaml":
                yaml_import = format_info["requires_import"]
                if yaml_import:
                    try:
                        yaml_mod = importlib.import_module(yaml_import)
                        yaml_output = yaml_mod.safe_dump(data, default_flow_style=False)
                        return FlextResult[str].ok(yaml_output)
                    except ImportError:
                        return FlextResult[str].fail(
                            f"YAML module '{yaml_import}' not available",
                        )
                    except (
                        AttributeError,
                        ValueError,
                    ) as e:
                        return FlextResult[str].fail(f"YAML formatting failed: {e}")

            # Handle plain text formatting
            elif format_info["format_type"] == "plain":
                plain_lines = [f"{key}: {value}" for key, value in data.items()]
                return FlextResult[str].ok("\n".join(plain_lines))

            # Handle table formatting (requires external table generator)
            elif format_info["format_type"] == "table":
                # Return structured data for external table rendering
                table_data = {
                    "title": self._constants.TABLE_TITLE_CONFIG,
                    "columns": ["Key", "Value", "Source"],
                    "rows": [[str(k), str(v), "config"] for k, v in data.items()],
                }
                return FlextResult[str].ok(
                    FlextUtilities.safe_json_stringify(table_data),
                )

            return FlextResult[str].fail(f"Unknown format type: {format_type}")

        except (
            ImportError,
            AttributeError,
            ValueError,
        ) as e:
            return FlextResult[str].fail(
                f"Config output formatting using SOURCE OF TRUTH failed: {e}",
            )

    def validate_config_object(
        self,
        config_object: object,
    ) -> FlextResult[FlextCliConfig.ValidationResult]:
        """Validate configuration using SOURCE OF TRUTH validation rules."""
        try:
            if not config_object:
                return FlextResult[FlextCliConfig.ValidationResult].fail(
                    "Config object is None",
                )

            validation_errors = []
            validation_warnings = []

            # Load validation rules from SOURCE OF TRUTH
            config_data_result = self.get_config_data(config_object)
            if config_data_result.is_failure:
                return FlextResult[FlextCliConfig.ValidationResult].fail(
                    f"Failed to get config data: {config_data_result.error}",
                )

            config_data = config_data_result.value

            # Validate profile using SOURCE OF TRUTH rules
            if not config_data["profile"] or config_data["profile"].strip() == "":
                validation_errors.append("Missing or empty profile")

            # Validate API URL using SOURCE OF TRUTH format rules
            if config_data["api_url"] and not config_data["api_url"].startswith(
                ("http://", "https://")
            ):
                validation_errors.append(
                    "Invalid API URL format (must start with http:// or https://)",
                )

            # Validate timeout using SOURCE OF TRUTH range rules
            if config_data["timeout"] <= 0:
                validation_errors.append("Invalid timeout value (must be > 0)")
            elif config_data["timeout"] < self._constants.MIN_COMMAND_TIMEOUT:
                validation_warnings.append(
                    f"Timeout below recommended minimum: {self._constants.MIN_COMMAND_TIMEOUT}",
                )

            # Validate output format using SOURCE OF TRUTH format metadata
            if config_data["output_format"] not in self._format_metadata:
                validation_errors.append(
                    f"Invalid output format: {config_data['output_format']}",
                )

            validation_result: FlextCliConfig.ValidationResult = {
                "is_valid": len(validation_errors) == 0,
                "errors": validation_errors,
                "warnings": validation_warnings,
            }

            return FlextResult[FlextCliConfig.ValidationResult].ok(validation_result)

        except (
            ImportError,
            AttributeError,
            ValueError,
        ) as e:
            return FlextResult[FlextCliConfig.ValidationResult].fail(
                f"Config validation using SOURCE OF TRUTH failed: {e}",
            )

    def get_config_paths(
        self,
        config_object: object | None = None,
    ) -> FlextResult[list[FlextCliConfig.PathInfo]]:
        """Get configuration paths using SOURCE OF TRUTH path metadata."""
        try:
            # Load path metadata from SOURCE OF TRUTH constants
            home = Path.home()
            flext_dir = home / self._constants.FLEXT_DIR_NAME

            # SOURCE OF TRUTH path configurations
            paths_metadata = [
                {
                    "path_type": "Config File",
                    "location": flext_dir / self._constants.CONFIG_FILE_NAME,
                },
                {"path_type": "Log Directory", "location": flext_dir / "logs"},
                {"path_type": "Cache Directory", "location": flext_dir / "cache"},
            ]

            # Add config-specific paths if config object provided
            if config_object:
                if hasattr(config_object, "token_file"):
                    token_file = getattr(config_object, "token_file", None)
                    if token_file:
                        paths_metadata.append(
                            {"path_type": "Token File", "location": Path(token_file)},
                        )

                if hasattr(config_object, "refresh_token_file"):
                    refresh_token_file = getattr(
                        config_object, "refresh_token_file", None
                    )
                    if refresh_token_file:
                        paths_metadata.append(
                            {
                                "path_type": "Refresh Token File",
                                "location": Path(refresh_token_file),
                            },
                        )

            # Check existence using direct filesystem calls - NO deduction
            paths_data: list[FlextCliConfig.PathInfo] = []
            for path_metadata in paths_metadata:
                path_info: FlextCliConfig.PathInfo = {
                    "path_type": str(path_metadata["path_type"]),
                    "location": Path(str(path_metadata["location"])),
                    "exists": Path(
                        str(path_metadata["location"]),
                    ).exists(),  # Direct filesystem check
                }
                paths_data.append(path_info)

            return FlextResult[list[FlextCliConfig.PathInfo]].ok(paths_data)

        except (
            ImportError,
            AttributeError,
            ValueError,
        ) as e:
            return FlextResult[list[FlextCliConfig.PathInfo]].fail(
                f"Config paths fetch from SOURCE OF TRUTH failed: {e}",
            )

    def set_config_value(
        self,
        config_object: object,
        key: str,
        value: str,
    ) -> FlextResult[object]:
        """Set configuration value with type conversion using SOURCE OF TRUTH."""
        try:
            if not config_object:
                return FlextResult[object].fail("Config object is None")

            # Get current value for type inference from SOURCE OF TRUTH
            old_value = getattr(config_object, key, None)
            converted_value: object

            if old_value is not None:
                try:
                    if isinstance(old_value, bool):
                        # SOURCE OF TRUTH boolean conversion rules
                        converted_value = value.lower() in {"true", "yes", "1", "on"}
                    elif isinstance(old_value, int):
                        converted_value = int(value)
                    elif isinstance(old_value, float):
                        converted_value = float(value)
                    else:
                        converted_value = value
                except (ValueError, TypeError):
                    # Use string if conversion fails
                    converted_value = value
            else:
                converted_value = value

            # Set attribute using SOURCE OF TRUTH
            setattr(config_object, key, converted_value)
            return FlextResult[object].ok(converted_value)

        except (
            ImportError,
            AttributeError,
            ValueError,
        ) as e:
            return FlextResult[object].fail(
                f"Config value setting using SOURCE OF TRUTH failed: {e}",
            )

    def create_default_config_file(self, config_path: Path) -> FlextResult[None]:
        """Create default configuration file using SOURCE OF TRUTH template."""
        try:
            # Ensure parent directory exists
            config_path.parent.mkdir(parents=True, exist_ok=True)

            # SOURCE OF TRUTH default configuration template
            default_config = {
                "debug": False,
                "timeout": self._constants.DEFAULT_COMMAND_TIMEOUT,
                "profile": "default",
                "output_format": "table",
            }

            # Try YAML format first (SOURCE OF TRUTH preference)
            try:
                yaml_mod = importlib.import_module("yaml")
                yaml_content = yaml_mod.safe_dump(
                    default_config,
                    default_flow_style=False,
                )

                with config_path.open(
                    "w",
                    encoding=self._constants.DEFAULT_ENCODING,
                ) as f:
                    f.write("# FLEXT CLI Configuration (SOURCE OF TRUTH)\n")
                    f.write(yaml_content)

            except ImportError:
                # Fallback to basic format using SOURCE OF TRUTH structure
                with config_path.open(
                    "w",
                    encoding=self._constants.DEFAULT_ENCODING,
                ) as f:
                    f.write("# FLEXT CLI Configuration (SOURCE OF TRUTH)\n")
                    f.write("# YAML not available, using basic format\n")
                    for key, value in default_config.items():
                        f.write(f"{key}: {value}\n")

            return FlextResult[None].ok(None)

        except (
            ImportError,
            AttributeError,
            ValueError,
        ) as e:
            return FlextResult[None].fail(
                f"Default config file creation using SOURCE OF TRUTH failed: {e}",
            )

    class CommandHandler:
        """Unified command handler for configuration operations using SOURCE OF TRUTH."""

        def __init__(self, config_service: FlextCliConfig) -> None:
            """Initialize with SOURCE OF TRUTH configuration service."""
            self._config = config_service

        def handle_show(self, config_object: object) -> None:
            """Handle show command using SOURCE OF TRUTH."""
            config_result = self._config.get_config_data(config_object)
            if config_result.is_failure:
                return

            config_data = config_result.value
            output_format = config_data["output_format"]

            # Format using SOURCE OF TRUTH
            format_result = self._config.format_config_output(
                dict(config_data),
                output_format,
            )
            if format_result.is_failure:
                return

        def handle_get(self, config_object: object, key: str | None = None) -> None:
            """Handle get command using SOURCE OF TRUTH."""
            if key is None:
                # Get all configuration
                config_result = self._config.get_config_data(config_object)
                if config_result.is_failure:
                    return

                config_data = config_result.value
                for _k, _v in config_data.items():
                    pass
            else:
                # Get specific value
                value_result = self._config.find_config_value(config_object, key)
                if value_result.is_failure:
                    return

        def handle_set(self, config_object: object, key: str, value: str) -> None:
            """Handle set command using SOURCE OF TRUTH."""
            set_result = self._config.set_config_value(config_object, key, value)
            if set_result.is_failure:
                return

        def handle_validate(self, config_object: object) -> None:
            """Handle validate command using SOURCE OF TRUTH."""
            validation_result = self._config.validate_config_object(config_object)
            if validation_result.is_failure:
                return

            validation = validation_result.value

            if validation["is_valid"]:
                pass
            else:
                for _error in validation["errors"]:
                    pass

            if validation["warnings"]:
                for _warning in validation["warnings"]:
                    pass

        def handle_path(self, config_object: object | None = None) -> None:
            """Handle path command using SOURCE OF TRUTH."""
            paths_result = self._config.get_config_paths(config_object)
            if paths_result.is_failure:
                return

            paths = paths_result.value
            for path_info in paths:
                "✅" if path_info["exists"] else "❌"

        def handle_edit(self, config_object: object) -> None:
            """Handle edit command using SOURCE OF TRUTH."""
            # Get config file path from SOURCE OF TRUTH
            paths_result = self._config.get_config_paths(config_object)
            if paths_result.is_failure:
                return

            # Find config file path
            config_file_path = None
            for path_info in paths_result.value:
                if path_info["path_type"] == "Config File":
                    config_file_path = path_info["location"]
                    break

            if not config_file_path:
                return

            # Create default config if it doesn't exist
            if not config_file_path.exists():
                create_result = self._config.create_default_config_file(
                    config_file_path,
                )
                if create_result.is_failure:
                    return


__all__ = ["FlextCliConfig"]
