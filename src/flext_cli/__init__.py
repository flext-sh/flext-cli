# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Cli package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

from flext_cli.__version__ import __version__

if TYPE_CHECKING:
    from flext_core import d, e, h, r, x

    from flext_cli import services as services, vendor as vendor
    from flext_cli.__version__ import (
        FlextCliVersion,
        __author__,
        __author_email__,
        __description__,
        __license__,
        __title__,
        __url__,
        __version_info__,
    )
    from flext_cli._config import FlextCliConfig, config
    from flext_cli._settings import FlextCliSettings, settings
    from flext_cli.api import FlextCli, cli
    from flext_cli.base import FlextCliServiceBase, s
    from flext_cli.cli import main
    from flext_cli.constants import FlextCliConstants, c
    from flext_cli.models import FlextCliModels, m
    from flext_cli.protocols import FlextCliProtocols, p
    from flext_cli.typings import FlextCliTypes, t
    from flext_cli.utilities import FlextCliUtilities, FlextCliUtilitiesCli, u


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
    "FlextCliUtilitiesCli",
    "FlextCliVersion",
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
    "main",
    "p",
    "r",
    "s",
    "services",
    "settings",
    "t",
    "u",
    "vendor",
    "x",
)

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType({
        "FlextCli": ".api",
        "FlextCliConfig": "._config",
        "FlextCliConstants": ".constants",
        "FlextCliModels": ".models",
        "FlextCliProtocols": ".protocols",
        "FlextCliServiceBase": ".base",
        "FlextCliSettings": "._settings",
        "FlextCliTypes": ".typings",
        "FlextCliUtilities": ".utilities",
        "FlextCliUtilitiesCli": ".utilities",
        "FlextCliVersion": ".__version__",
        "__author__": ".__version__",
        "__author_email__": ".__version__",
        "__description__": ".__version__",
        "__license__": ".__version__",
        "__title__": ".__version__",
        "__url__": ".__version__",
        "__version_info__": ".__version__",
        "c": ".constants",
        "cli": ".api",
        "config": "._config",
        "d": "flext_core",
        "e": "flext_core",
        "h": "flext_core",
        "m": ".models",
        "main": ".cli",
        "p": ".protocols",
        "r": "flext_core",
        "s": ".base",
        "services": ".services",
        "settings": "._settings",
        "t": ".typings",
        "u": ".utilities",
        "vendor": ".vendor",
        "x": "flext_core",
    }),
    public_exports=__all__,
)
