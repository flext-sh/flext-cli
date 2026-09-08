"""Public configuration facade for Flext CLI."""

from __future__ import annotations

from ._config import FlextCliConfig, config

__all__: tuple[str, ...] = ("FlextCliConfig", "config")
