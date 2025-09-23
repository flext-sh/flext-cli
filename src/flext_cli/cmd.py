"""FLEXT CLI CMD Module - Unified class following FLEXT architecture patterns.

Single FlextCliCmd class providing CLI command functionality.
Follows FLEXT unified class pattern - one class per module extending flext-core.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import os
from datetime import UTC, datetime
from pathlib import Path

from flext_core import (
    FlextContainer,
    FlextLogger,
    FlextResult,
    FlextService,
)


class FlextCliCmd(FlextService[str]):
    """CMD service extending FlextService from flext-core.

    Provides essential command functionality using flext-core patterns.
    Follows single-responsibility principle with nested helpers.
    """

    def __init__(self) -> None:
        """Initialize command service with flext-core integration."""
        super().__init__()
        self._logger = FlextLogger(__name__)
        self._container = FlextContainer.get_global()

    class _ConfigHelper:
        """Nested helper for configuration operations."""

        @staticmethod
        def get_config_paths() -> list[str]:
            """Get standard configuration paths."""
            home = Path.home()
            flext_dir = home / ".flext"

            return [
                str(flext_dir),
                str(flext_dir / "config"),
                str(flext_dir / "cache"),
                str(flext_dir / "logs"),
                str(flext_dir / "token"),
                str(flext_dir / "refresh_token"),
            ]

        @staticmethod
        def validate_config_structure() -> list[str]:
            """Validate configuration directory structure."""
            results = []
            home = Path.home()
            flext_dir = home / ".flext"

            # Check main config directory
            if flext_dir.exists():
                results.append("✓ Main config directory exists")
            else:
                results.append("✗ Main config directory missing")

            # Check subdirectories
            for subdir in ["config", "cache", "logs"]:
                path = flext_dir / subdir
                if path.exists():
                    results.append(f"✓ {subdir} directory exists")
                else:
                    results.append(f"✗ {subdir} directory missing")

            return results

        @staticmethod
        def get_config_info() -> dict[str, object]:
            """Get configuration information."""
            home = Path.home()
            flext_dir = home / ".flext"

            return {
                "config_dir": str(flext_dir),
                "config_exists": flext_dir.exists(),
                "config_readable": flext_dir.exists() and os.access(flext_dir, os.R_OK),
                "config_writable": flext_dir.exists() and os.access(flext_dir, os.W_OK),
                "timestamp": datetime.now(UTC).isoformat(),
            }

    def execute(self) -> FlextResult[str]:
        """Execute command service - required by FlextService."""
        return FlextResult[str].ok("FlextCliCmd service operational")

    def show_config_paths(self) -> FlextResult[list[str]]:
        """Show configuration paths."""
        try:
            paths = self._ConfigHelper.get_config_paths()
            return FlextResult[list[str]].ok(paths)
        except Exception as e:
            return FlextResult[list[str]].fail(f"Config paths failed: {e}")

    def validate_config(self) -> FlextResult[None]:
        """Validate configuration structure."""
        try:
            results = self._ConfigHelper.validate_config_structure()
            if (
                results
            ):  # If there are results, log them but still return None for compatibility
                self._logger.info(f"Config validation results: {results}")
            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"Config validation failed: {e}")

    def get_config_info(self) -> FlextResult[dict[str, object]]:
        """Get configuration information."""
        try:
            info = self._ConfigHelper.get_config_info()
            return FlextResult[dict[str, object]].ok(info)
        except Exception as e:
            return FlextResult[dict[str, object]].fail(f"Config info failed: {e}")

    def set_config_value(self, key: str, value: str) -> FlextResult[bool]:
        """Set configuration value (placeholder implementation)."""
        try:
            # Placeholder implementation - would integrate with flext_cli_config
            self._logger.info(f"Setting config: {key} = {value}")
            return FlextResult[bool].ok(True)
        except Exception as e:
            return FlextResult[bool].fail(f"Set config failed: {e}")

    def get_config_value(self, key: str) -> FlextResult[dict[str, object]]:
        """Get configuration value (placeholder implementation)."""
        try:
            # Placeholder implementation - would integrate with flext_cli_config
            config_data: dict[str, object] = {
                "key": key,
                "value": f"config_value_for_{key}",
                "timestamp": datetime.now(UTC).isoformat(),
            }
            return FlextResult[dict[str, object]].ok(config_data)
        except Exception as e:
            return FlextResult[dict[str, object]].fail(f"Get config failed: {e}")

    def show_config(self) -> FlextResult[None]:
        """Show current configuration."""
        try:
            info_result = self.get_config_info()
            if info_result.is_failure:
                return FlextResult[None].fail(
                    f"Show config failed: {info_result.error}"
                )

            self._logger.info("Configuration displayed", config=info_result.value)
            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"Show config failed: {e}")

    def edit_config(self) -> FlextResult[str]:
        """Edit configuration (placeholder implementation)."""
        try:
            # Placeholder implementation - would open config editor
            return FlextResult[str].ok("Config editor opened (placeholder)")
        except Exception as e:
            return FlextResult[str].fail(f"Edit config failed: {e}")


__all__ = [
    "FlextCliCmd",
]
