# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Cli package."""

from __future__ import annotations

from flext_cli.__version__ import (
    __author__,
    __author_email__,
    __description__,
    __license__,
    __title__,
    __url__,
    __version__,
    __version_info__,
)
from flext_cli._exports import FLEXT_CLI_LAZY_IMPORTS
from flext_core.lazy import install_lazy_exports

_LAZY_IMPORTS = FLEXT_CLI_LAZY_IMPORTS

__all__: tuple[str, ...] = (
    "FlextCli",
    "FlextCliAuth",
    "FlextCliCli",
    "FlextCliCmd",
    "FlextCliCommonParams",
    "FlextCliConstants",
    "FlextCliFileTools",
    "FlextCliFormatters",
    "FlextCliModels",
    "FlextCliOutput",
    "FlextCliPipeline",
    "FlextCliPrompts",
    "FlextCliProtocols",
    "FlextCliRules",
    "FlextCliRuntime",
    "FlextCliServiceBase",
    "FlextCliSettings",
    "FlextCliTables",
    "FlextCliTypes",
    "FlextCliUtilities",
    "__author__",
    "__author_email__",
    "__description__",
    "__license__",
    "__title__",
    "__url__",
    "__version__",
    "__version_info__",
    "c",
    "cli",
    "d",
    "e",
    "h",
    "m",
    "p",
    "r",
    "s",
    "t",
    "u",
    "x",
)


install_lazy_exports(
    __name__,
    globals(),
    _LAZY_IMPORTS,
    public_exports=__all__,
)
