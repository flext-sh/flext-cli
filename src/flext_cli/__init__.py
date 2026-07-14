# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Cli package."""

from __future__ import annotations

from typing import TYPE_CHECKING

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
from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext_core import d, e, h, r, x

    from ._config import FlextCliConfig, config
    from ._settings import FlextCliSettings, settings
    from .api import FlextCli, cli
    from .base import FlextCliServiceBase, s
    from .constants import FlextCliConstants, FlextCliConstants as c
    from .models import FlextCliModels, FlextCliModels as m
    from .protocols import FlextCliProtocols, FlextCliProtocols as p
    from .typings import FlextCliTypes, FlextCliTypes as t
    from .utilities import FlextCliUtilities, FlextCliUtilities as u

    _ = (
        c,
        FlextCliConstants,
        t,
        FlextCliTypes,
        p,
        FlextCliProtocols,
        m,
        FlextCliModels,
        u,
        FlextCliUtilities,
        d,
        e,
        h,
        r,
        x,
        s,
        FlextCliServiceBase,
        FlextCliConfig,
        config,
        FlextCliSettings,
        settings,
        FlextCli,
        cli,
    )


_LAZY_MODULES: dict[str, tuple[str, ...]] = {
    "._config": ("FlextCliConfig", "config"),
    "._settings": ("FlextCliSettings", "settings"),
    ".api": ("FlextCli", "cli"),
    ".base": ("FlextCliServiceBase", "s"),
    ".constants": ("FlextCliConstants", "c"),
    ".models": ("FlextCliModels", "m"),
    ".protocols": ("FlextCliProtocols", "p"),
    ".typings": ("FlextCliTypes", "t"),
    ".utilities": ("FlextCliUtilities", "u"),
    "flext_core": ("d", "e", "h", "r", "x"),
}


_LAZY_ALIAS_GROUPS: dict[str, tuple[tuple[str, str], ...]] = {}


_LAZY_IMPORTS = build_lazy_import_map(
    _LAZY_MODULES, alias_groups=_LAZY_ALIAS_GROUPS, sort_keys=False
)

_DIRECT_IMPORTS: tuple[str, ...] = (
    "FlextCli",
    "FlextCliConfig",
    "FlextCliConstants",
    "FlextCliModels",
    "FlextCliProtocols",
    "FlextCliServiceBase",
    "FlextCliSettings",
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
    "build_lazy_import_map",
    "c",
    "cli",
    "config",
    "d",
    "e",
    "h",
    "install_lazy_exports",
    "m",
    "p",
    "r",
    "s",
    "settings",
    "t",
    "u",
    "x",
)

__all__: tuple[str, ...] = (
    "FlextCli",
    "FlextCliConfig",
    "FlextCliConstants",
    "FlextCliModels",
    "FlextCliProtocols",
    "FlextCliServiceBase",
    "FlextCliSettings",
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
    "config",
    "d",
    "e",
    "h",
    "m",
    "p",
    "r",
    "s",
    "settings",
    "t",
    "u",
    "x",
)


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)
