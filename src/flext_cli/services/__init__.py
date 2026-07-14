# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Cli.services package."""

from __future__ import annotations

from typing import TYPE_CHECKING

# mro-i6nq.10: The package consumes its manifest's public-export contract.
from flext_cli.services.__unit__ import (
    CHILD_MODULE_PATHS as _CHILD_MODULE_PATHS,
    EXCLUDED_LAZY_NAMES as _EXCLUDED_LAZY_NAMES,
    PUBLIC_EXPORTS as _PUBLIC_EXPORTS,
)
from flext_core.lazy import (
    build_lazy_import_map,
    install_lazy_exports,
    merge_lazy_imports,
)

if TYPE_CHECKING:
    from flext_cli.services import _cli_parts as _cli_parts
    from flext_cli.services.auth import FlextCliAuth as FlextCliAuth
    from flext_cli.services.cli import FlextCliCli as FlextCliCli
    from flext_cli.services.cli_params import (
        FlextCliCommonParams as FlextCliCommonParams,
    )
    from flext_cli.services.cmd import FlextCliCmd as FlextCliCmd
    from flext_cli.services.file_tools import FlextCliFileTools as FlextCliFileTools
    from flext_cli.services.formatters import FlextCliFormatters as FlextCliFormatters
    from flext_cli.services.output import FlextCliOutput as FlextCliOutput
    from flext_cli.services.pipeline import FlextCliPipeline as FlextCliPipeline
    from flext_cli.services.prompts import FlextCliPrompts as FlextCliPrompts
    from flext_cli.services.rules import FlextCliRules as FlextCliRules
    from flext_cli.services.runtime import FlextCliRuntime as FlextCliRuntime
    from flext_cli.services.tables import FlextCliTables as FlextCliTables
    from flext_cli.services.xlsx import FlextCliXlsx as FlextCliXlsx
    from flext_cli.services.yaml_model import FlextCliYamlModel as FlextCliYamlModel

    # mro-i6nq.10: Static declaration mirrors the installer-owned runtime binding.
    __all__: tuple[str, ...]


_LAZY_IMPORTS = merge_lazy_imports(
    _CHILD_MODULE_PATHS,
    build_lazy_import_map(
        _LAZY_MODULES, alias_groups=_LAZY_ALIAS_GROUPS, sort_keys=False
    ),
    exclude_names=_EXCLUDED_LAZY_NAMES,
    module_name=__name__,
)


# mro-i6nq.10: The installer publishes __all__ from the manifest's literal ABI.
install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=_PUBLIC_EXPORTS)
