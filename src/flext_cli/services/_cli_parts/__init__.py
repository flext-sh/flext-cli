# AUTO-GENERATED FILE — Regenerate with: make gen
"""Cli Parts package."""

from __future__ import annotations

import typing as _t

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if _t.TYPE_CHECKING:
    from flext_cli.services._cli_parts.flextclicli_part_05 import (
        FlextCliCli as FlextCliCli,
    )
_LAZY_IMPORTS = build_lazy_import_map(
    {
        ".flextclicli_part_05": ("FlextCliCli",),
    },
)


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, publish_all=False)
