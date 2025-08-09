"""FLEXT CLI Hierarchical Configuration - Following docs/patterns/config-cli.md.

This module implements the hierarchical configuration system following the patterns
defined in docs/patterns/config-cli.md with proper precedence order and provider-based
architecture for CLI foundation library usage.

Configuration Hierarchy (Precedence Order):
    1. CLI Arguments      (highest precedence)
    2. Environment Vars
    3. .env Files
    4. Config Files
    5. Constants         (lowest precedence)

Provider-Based Architecture:
    - Pluggable configuration sources with consistent interface
    - Separation of concerns between CLI and configuration
    - Type-safe operations with FlextResult patterns

Integration with FLEXT Foundation:
    - Used by flext-meltano, algar-oud-mig, and other ecosystem projects
    - Provides unified configuration management across CLI implementations
    - Supports both modern and legacy patterns

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import json
import logging
import os
import tomllib
from pathlib import Path
from typing import TYPE_CHECKING, Protocol, runtime_checkable

import yaml
from flext_core import FlextResult

from flext_cli.constants import FlextConfigSemanticConstants
from flext_cli.providers import FlextCliArgsProvider

if TYPE_CHECKING:
    from collections.abc import Callable


@runtime_checkable
class FlextConfigProvider(Protocol):
    """Protocol for configuration providers following docs/patterns/config-cli.md."""

    def get_config(self, key: str, default: object = None) -> FlextResult[object]:
        """Get configuration value from this provider."""

    def get_priority(self) -> int:
        """Get provider priority for hierarchical sorting."""

    def get_all(self) -> dict[str, object]:
        """Get all configuration values from this provider."""


class FlextEnvironmentProvider:
    """Environment variable configuration provider."""

    def __init__(self, prefix: str = "FLEXT_CLI_") -> None:
        self.prefix = prefix

    def get_config(self, key: str, default: object = None) -> FlextResult[object]:
        """Get configuration from environment variables."""
        env_key = f"{self.prefix}{key.upper().replace('.', '_')}"
        value = os.environ.get(env_key, default)
        return FlextResult.ok(value)

    def get_priority(self) -> int:
        """Get provider priority."""
        return FlextConfigSemanticConstants.Hierarchy.ENV_VARS

    def get_all(self) -> dict[str, object]:
        """Get all environment variables with the prefix."""
        result: dict[str, object] = {}
        for key, value in os.environ.items():
            if key.startswith(self.prefix):
                config_key = key[len(self.prefix) :].lower().replace("_", ".")
                result[config_key] = value
        return result


class FlextDotenvProvider:
    """Dotenv file configuration provider."""

    def __init__(self, dotenv_path: Path | None = None) -> None:
        self.dotenv_path = dotenv_path or Path(".env")
        self._config: dict[str, object] = {}
        self._load_dotenv()

    def _load_dotenv(self) -> None:
        """Load .env file if it exists."""
        if not self.dotenv_path.exists():
            return

        try:
            content: str = self.dotenv_path.read_text()
            for content_line in content.splitlines():
                stripped_line: str = content_line.strip()
                if (
                    stripped_line
                    and not stripped_line.startswith("#")
                    and "=" in stripped_line
                ):
                    key, value = stripped_line.split("=", 1)
                    self._config[key.strip()] = value.strip().strip("\"'")
        except Exception as e:
            # Log warning for debugging but continue
            logging.getLogger(__name__).debug(f"Optional .env file parse error: {e}")

    def get_config(self, key: str, default: object = None) -> FlextResult[object]:
        """Get configuration value from .env file."""
        env_key = key.upper().replace(".", "_")
        value: object = self._config.get(env_key, default)
        return FlextResult.ok(value)

    def get_priority(self) -> int:
        """Get provider priority."""
        return FlextConfigSemanticConstants.Hierarchy.ENV_FILES

    def get_all(self) -> dict[str, object]:
        """Get all dotenv configuration."""
        return self._config.copy()


class FlextConfigFileProvider:
    """Configuration file provider supporting JSON, YAML, TOML."""

    def __init__(self, config_path: Path) -> None:
        self.config_path = config_path
        self._config: dict[str, object] = {}
        self._load_config()

    def _load_config(self) -> None:
        """Load configuration file based on extension."""
        if not self.config_path.exists():
            return

        try:
            content: str = self.config_path.read_text()

            if self.config_path.suffix == ".json":
                self._config = json.loads(content)
            elif self.config_path.suffix in {".yaml", ".yml"}:
                self._config = yaml.safe_load(content)
            elif self.config_path.suffix == ".toml":
                self._config = tomllib.loads(content)
        except Exception as e:
            # Log warning for debugging but continue
            logging.getLogger(__name__).debug(f"Optional config file parse error: {e}")

    def get_config(self, key: str, default: object = None) -> FlextResult[object]:
        """Get configuration value using dot notation."""
        keys = key.split(".")
        value: object | None = self._config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return FlextResult.ok(default)

        return FlextResult.ok(value)

    def get_priority(self) -> int:
        """Get provider priority."""
        return FlextConfigSemanticConstants.Hierarchy.CONFIG_FILES

    def get_all(self) -> dict[str, object]:
        """Get all configuration from file."""
        return self._config.copy()


class FlextCLIConfigHierarchical:
    """CLI-specific hierarchical configuration management following docs/patterns/config-cli.md."""

    def __init__(self) -> None:
        self._providers: list[FlextConfigProvider] = []
        self._cache: dict[str, object] = {}
        self._transformers: dict[str, Callable[[object], object]] = {}

    def register_provider(self, provider: FlextConfigProvider) -> FlextResult[None]:
        """Register configuration provider with automatic priority sorting."""
        try:
            # Check for duplicate priorities
            existing_priorities = [p.get_priority() for p in self._providers]
            if provider.get_priority() in existing_priorities:
                return FlextResult.fail(
                    f"Provider with priority {provider.get_priority()} already exists",
                )

            self._providers.append(provider)
            self._providers.sort(key=lambda p: p.get_priority())
            self._cache.clear()

            return FlextResult.ok(None)
        except Exception as e:
            return FlextResult.fail(f"Failed to register provider: {e}")

    def get_config(self, key: str, default: object = None) -> FlextResult[object]:
        """Get configuration value following hierarchical precedence."""
        if key in self._cache:
            return FlextResult.ok(self._cache[key])

        for provider in self._providers:
            result = provider.get_config(key, None)
            if result.success and result.data is not None:
                value = self._apply_transformers(key, result.data)
                self._cache[key] = value
                return FlextResult.ok(value)

        return FlextResult.ok(default)

    def get_all_configs(self) -> dict[str, object]:
        """Get all configuration values merged by precedence."""
        all_configs = {}

        # Apply in reverse priority order (lowest first, highest last)
        for provider in reversed(self._providers):
            if hasattr(provider, "get_all"):
                provider_configs = provider.get_all()
                all_configs.update(provider_configs)

        return all_configs

    def add_transformer(
        self, key: str, transformer: Callable[[object], object]
    ) -> None:
        """Add value transformer for specific configuration key."""
        self._transformers[key] = transformer

    def _apply_transformers(self, key: str, value: object) -> object:
        """Apply registered transformers to configuration value."""
        if key in self._transformers:
            try:
                return self._transformers[key](value)
            except Exception as e:
                # Log transformation failure for debugging
                logging.getLogger(__name__).debug(
                    f"Config transformation failed for {key}: {e}"
                )
        return value

    def clear_cache(self) -> None:
        """Clear configuration cache."""
        self._cache.clear()


def create_default_hierarchy(
    cli_args: dict[str, object] | None = None,
    env_prefix: str = "FLEXT_CLI_",
    dotenv_path: Path | None = None,
    config_path: Path | None = None,
) -> FlextResult[FlextCLIConfigHierarchical]:
    """Create default hierarchical configuration following standard patterns.

    Args:
        cli_args: CLI arguments (highest precedence)
        env_prefix: Environment variable prefix
        dotenv_path: Path to .env file
        config_path: Path to configuration file

    Returns:
        FlextResult[FlextCLIConfigHierarchical]: Configured hierarchy

    Example:
        hierarchy = create_default_hierarchy(
            cli_args={"debug": True},
            env_prefix="MYAPP_"
        ).unwrap()

        debug = hierarchy.get_config("debug").unwrap_or(False)

    """
    try:
        hierarchy = FlextCLIConfigHierarchical()

        # Register providers in priority order

        # CLI arguments (highest priority)
        if cli_args:
            # Use FlextCliArgsProvider to handle CLI arguments
            cli_provider = FlextCliArgsProvider(cli_args)
            result = hierarchy.register_provider(cli_provider)
            if not result.success:
                return FlextResult.fail(
                    result.error or "Failed to register CLI provider"
                )

        # Environment variables
        env_provider = FlextEnvironmentProvider(env_prefix)
        result = hierarchy.register_provider(env_provider)
        if not result.success:
            return FlextResult.fail(
                result.error or "Failed to register environment provider"
            )

        # .env files
        if dotenv_path is None:
            dotenv_path = Path(".env")
        dotenv_provider = FlextDotenvProvider(dotenv_path)
        result = hierarchy.register_provider(dotenv_provider)
        if not result.success:
            return FlextResult.fail(
                result.error or "Failed to register dotenv provider"
            )

        # Configuration files
        if config_path and config_path.exists():
            config_provider = FlextConfigFileProvider(config_path)
            result = hierarchy.register_provider(config_provider)
            if not result.success:
                return FlextResult.fail(
                    result.error or "Failed to register config file provider"
                )

        return FlextResult.ok(hierarchy)

    except Exception as e:
        return FlextResult.fail(f"Failed to create configuration hierarchy: {e}")


__all__ = [
    "FlextCLIConfigHierarchical",
    "FlextConfigFileProvider",
    "FlextConfigProvider",
    "FlextConfigSemanticConstants",
    "FlextDotenvProvider",
    "FlextEnvironmentProvider",
    "create_default_hierarchy",
]
