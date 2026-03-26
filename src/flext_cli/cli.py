"""FLEXT CLI - Typer/Click Abstraction Layer.

This is the ONLY file in the entire FLEXT ecosystem allowed to import Typer/Click.
All CLI framework functionality is exposed through this unified interface.

Implementation: Uses Typer as the backend framework. Since Typer is built on Click,
it generates Click-compatible commands internally.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import FlextContainer, FlextLogger

from flext_cli import p


class FlextCliCli:
    """Unified Typer/Click abstraction used by the FLEXT ecosystem."""

    container: p.Container
    logger: p.Logger

    def __init__(self) -> None:
        """Initialize FlextCliCli."""
        super().__init__()
        self.container = FlextContainer.get_global()
        self.logger = FlextLogger(__name__)


__all__ = ["FlextCliCli"]
