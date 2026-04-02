# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Flext cli package."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING as _TYPE_CHECKING

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
from flext_core.lazy import install_lazy_exports, merge_lazy_imports

if _TYPE_CHECKING:
    from flext_cli import (
        _models,
        api,
        base,
        constants,
        models,
        protocols,
        services,
        settings,
        typings,
        utilities,
    )
    from flext_cli._models import FlextCliModelsBase
    from flext_cli.api import FlextCli, cli
    from flext_cli.base import FlextCliServiceBase, s
    from flext_cli.constants import FlextCliConstants, FlextCliConstants as c
    from flext_cli.models import FlextCliModels, FlextCliModels as m
    from flext_cli.protocols import FlextCliProtocols, FlextCliProtocols as p
    from flext_cli.services import (
        FlextCliAuth,
        FlextCliCli,
        FlextCliCmd,
        FlextCliCommands,
        FlextCliCommonParams,
        FlextCliFileTools,
        FlextCliFormatters,
        FlextCliOutput,
        FlextCliPrompts,
        FlextCliTables,
        auth,
        cli_params,
        cmd,
        commands,
        file_tools,
        formatters,
        output,
        prompts,
        tables,
    )
    from flext_cli.settings import FlextCliSettings, logger
    from flext_cli.typings import FlextCliTypes, FlextCliTypes as t
    from flext_cli.utilities import FlextCliUtilities, FlextCliUtilities as u
    from flext_core import FlextTypes
    from flext_core.decorators import FlextDecorators as d
    from flext_core.exceptions import FlextExceptions as e
    from flext_core.handlers import FlextHandlers as h
    from flext_core.mixins import FlextMixins as x
    from flext_core.result import FlextResult as r

_LAZY_IMPORTS: FlextTypes.LazyImportIndex = merge_lazy_imports(
    (
        "flext_cli._models",
        "flext_cli.services",
    ),
    {
        "FlextCli": "flext_cli.api",
        "FlextCliConstants": "flext_cli.constants",
        "FlextCliModels": "flext_cli.models",
        "FlextCliProtocols": "flext_cli.protocols",
        "FlextCliServiceBase": "flext_cli.base",
        "FlextCliSettings": "flext_cli.settings",
        "FlextCliTypes": "flext_cli.typings",
        "FlextCliUtilities": "flext_cli.utilities",
        "_models": "flext_cli._models",
        "api": "flext_cli.api",
        "base": "flext_cli.base",
        "c": ("flext_cli.constants", "FlextCliConstants"),
        "cli": "flext_cli.api",
        "constants": "flext_cli.constants",
        "d": ("flext_core.decorators", "FlextDecorators"),
        "e": ("flext_core.exceptions", "FlextExceptions"),
        "h": ("flext_core.handlers", "FlextHandlers"),
        "logger": "flext_cli.settings",
        "m": ("flext_cli.models", "FlextCliModels"),
        "models": "flext_cli.models",
        "p": ("flext_cli.protocols", "FlextCliProtocols"),
        "protocols": "flext_cli.protocols",
        "r": ("flext_core.result", "FlextResult"),
        "s": "flext_cli.base",
        "services": "flext_cli.services",
        "settings": "flext_cli.settings",
        "t": ("flext_cli.typings", "FlextCliTypes"),
        "typings": "flext_cli.typings",
        "u": ("flext_cli.utilities", "FlextCliUtilities"),
        "utilities": "flext_cli.utilities",
        "x": ("flext_core.mixins", "FlextMixins"),
    },
)


install_lazy_exports(
    __name__,
    globals(),
    _LAZY_IMPORTS,
    [
        "__author__",
        "__author_email__",
        "__description__",
        "__license__",
        "__title__",
        "__url__",
        "__version__",
        "__version_info__",
    ],
)
