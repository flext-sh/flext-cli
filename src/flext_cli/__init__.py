# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Cli package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from flext_core import (
        build_lazy_import_map,
        cleanup_submodule_namespace,
        core,
        d,
        e,
        h,
        install_lazy_exports,
        lazy,
        lazy_getattr,
        lazy_member,
        merge_lazy_imports,
        normalize_lazy_imports,
        r,
        resolve_lazy_members,
        x,
    )

    from flext_cli.__version__ import (
        FlextCliVersion,
        __author__,
        __author_email__,
        __description__,
        __license__,
        __title__,
        __url__,
        __version__,
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
    from flext_cli.services.cli import FlextCliCli
    from flext_cli.typings import FlextCliTypes, t
    from flext_cli.utilities import FlextCliUtilities, FlextCliUtilitiesCli, u


__all__: tuple[str, ...] = (
    "FlextCli",
    "FlextCliCli",
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
    "build_lazy_import_map",
    "c",
    "cleanup_submodule_namespace",
    "cli",
    "config",
    "core",
    "d",
    "e",
    "h",
    "install_lazy_exports",
    "lazy",
    "lazy_getattr",
    "lazy_member",
    "m",
    "main",
    "merge_lazy_imports",
    "normalize_lazy_imports",
    "p",
    "r",
    "resolve_lazy_members",
    "s",
    "settings",
    "t",
    "u",
    "x",
)

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType({
        "FlextCli": ".api",
        "FlextCliCli": ".services.cli",
        "FlextCliConfig": "._config",
        "FlextCliConstants": ".constants",
        "FlextCliModels": ".models",
        "FlextCliProtocols": ".protocols",
        "FlextCliServiceBase": ".base",
        "FlextCliSettings": "._settings",
        "FlextCliTypes": ".typings",
        "FlextCliUtilities": ".utilities",
        "FlextCliUtilitiesCli": "._utilities.cli_namespace",
        "FlextCliVersion": ".__version__",
        "__author__": ".__version__",
        "__author_email__": ".__version__",
        "__description__": ".__version__",
        "__license__": ".__version__",
        "__title__": ".__version__",
        "__url__": ".__version__",
        "__version_info__": ".__version__",
        "build_lazy_import_map": "flext_core",
        "c": ".constants",
        "cleanup_submodule_namespace": "flext_core",
        "cli": ".api",
        "config": "._config",
        "core": "flext_core",
        "d": "flext_core",
        "e": "flext_core",
        "h": "flext_core",
        "install_lazy_exports": "flext_core",
        "lazy": "flext_core",
        "lazy_getattr": "flext_core",
        "lazy_member": "flext_core",
        "m": ".models",
        "main": ".cli",
        "merge_lazy_imports": "flext_core",
        "normalize_lazy_imports": "flext_core",
        "p": ".protocols",
        "r": "flext_core",
        "resolve_lazy_members": "flext_core",
        "s": ".base",
        "settings": "._settings",
        "t": ".typings",
        "u": ".utilities",
        "x": "flext_core",
    }),
    public_exports=__all__,
)

if not TYPE_CHECKING:
    from flext_cli.__version__ import __version__
