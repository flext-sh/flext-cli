"""FLEXT CLI - Typer/Click Abstraction Layer.

This is the ONLY file in the entire FLEXT ecosystem allowed to import Typer/Click.
All CLI framework functionality is exposed through this unified interface.

Implementation: Uses Typer as the backend framework. Since Typer is built on Click,
it generates Click-compatible commands internally.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations


class FlextCliCli:
    """Unified Typer/Click abstraction marker for the FLEXT CLI ecosystem.

    Container and logger are provided by FlextMixins via MRO.
    """


__all__ = ["FlextCliCli"]
