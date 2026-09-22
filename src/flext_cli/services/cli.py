"""FLEXT CLI - Unified Typer abstraction service.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli import m, s

from ._cli_parts.flextclicli_part_05 import FlextCliCli as FlextCliCliPart05


class FlextCliCli(s[m.Cli.RuntimeStatus], FlextCliCliPart05):
    """Public facade for FlextCliCli."""


__all__: list[str] = ["FlextCliCli"]
