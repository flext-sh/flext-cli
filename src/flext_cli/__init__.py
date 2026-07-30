# @generated AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Cli package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

from .__version__ import __author__ as __author__
from .__version__ import __author_email__ as __author_email__
from .__version__ import __description__ as __description__
from .__version__ import __license__ as __license__
from .__version__ import __title__ as __title__
from .__version__ import __url__ as __url__
from .__version__ import __version__ as __version__
from .__version__ import __version_info__ as __version_info__

if TYPE_CHECKING:
    from flext_core import d as d
    from flext_core import e as e
    from flext_core import h as h
    from flext_core import r as r
    from flext_core import x as x

    from ._config import FlextCliConfig as FlextCliConfig
    from ._config import config as config
    from ._settings import settings as settings
    from .api import FlextCli as FlextCli
    from .api import cli as cli
    from .base import FlextCliServiceBase as FlextCliServiceBase

    s: type[FlextCliServiceBase]
    from .constants import FlextCliConstants as FlextCliConstants

    c: type[FlextCliConstants]
    from .models import FlextCliModels as FlextCliModels

    m: type[FlextCliModels]
    from .protocols import FlextCliProtocols as FlextCliProtocols

    p: type[FlextCliProtocols]
    from .settings import FlextCliSettings as FlextCliSettings
    from .typings import FlextCliTypes as FlextCliTypes

    t: type[FlextCliTypes]
    from .utilities import FlextCliUtilities as FlextCliUtilities

    u: type[FlextCliUtilities]

_LAZY_MODULES: dict[str, tuple[str, ...]] = {
    "._config": ("FlextCliConfig", "config"),
    "._settings": ("settings",),
    ".api": ("FlextCli", "cli"),
    ".base": ("FlextCliServiceBase", "s"),
    ".constants": ("FlextCliConstants", "c"),
    ".models": ("FlextCliModels", "m"),
    ".protocols": ("FlextCliProtocols", "p"),
    ".settings": ("FlextCliSettings",),
    ".typings": ("FlextCliTypes", "t"),
    ".utilities": ("FlextCliUtilities", "u"),
    "flext_core": ("d", "e", "h", "r", "x"),
}


_LAZY_ALIAS_GROUPS: dict[str, tuple[tuple[str, str], ...]] = {}


_LAZY_IMPORTS = build_lazy_import_map(
    _LAZY_MODULES, alias_groups=_LAZY_ALIAS_GROUPS, sort_keys=False
)

_PUBLIC_EXPORTS: tuple[str, ...] = (
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

__all__: tuple[str, ...] = tuple(_PUBLIC_EXPORTS)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)
