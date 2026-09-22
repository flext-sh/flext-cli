"""Public configuration facade for Flext CLI."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ._config import FlextCliConfig, config

if TYPE_CHECKING:
    from flext_core import t

__all__: t.VariadicTuple[str] = ("FlextCliConfig", "config")
