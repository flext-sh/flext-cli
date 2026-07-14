# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Cli.services. Cli Parts package."""

from __future__ import annotations

from typing import TYPE_CHECKING

# mro-i6nq.10: The package consumes its manifest's public-export contract.
from flext_cli.services._cli_parts.__unit__ import PUBLIC_EXPORTS as _PUBLIC_EXPORTS
from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext_cli.services._cli_parts.flextclicli_part_05 import (
        FlextCliCli as FlextCliCli,
    )

    # mro-i6nq.10: Static declaration mirrors the installer-owned runtime binding.
    __all__: tuple[str, ...]


_LAZY_IMPORTS = build_lazy_import_map(
    _LAZY_MODULES, alias_groups=_LAZY_ALIAS_GROUPS, sort_keys=False
)


# mro-i6nq.10: The installer publishes __all__ from the manifest's literal ABI.
install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=_PUBLIC_EXPORTS)
