"""Infrastructure layer for FLEXT CLI."""

from __future__ import annotations

from flext_cli.infrastructure.container import (
    get_container,
    get_service,
    register_service,
    register_singleton,
)

__all__ = [
    "get_container",
    "get_service",
    "register_service",
    "register_singleton",
]
