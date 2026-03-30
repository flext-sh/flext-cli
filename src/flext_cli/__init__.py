# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Flext cli package."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING as _TYPE_CHECKING

from flext_core.lazy import install_lazy_exports, merge_lazy_imports

if _TYPE_CHECKING:
    from flext_core import d, e, h, r, x

    from flext_cli.__version__ import *
    from flext_cli._models import *
    from flext_cli.api import *
    from flext_cli.base import *
    from flext_cli.constants import *
    from flext_cli.models import *
    from flext_cli.protocols import *
    from flext_cli.services import *
    from flext_cli.settings import *
    from flext_cli.typings import *
    from flext_cli.utilities import *

_LAZY_IMPORTS: Mapping[str, str | Sequence[str]] = merge_lazy_imports(
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
        "__author__": "flext_cli.__version__",
        "__author_email__": "flext_cli.__version__",
        "__description__": "flext_cli.__version__",
        "__license__": "flext_cli.__version__",
        "__title__": "flext_cli.__version__",
        "__url__": "flext_cli.__version__",
        "__version__": "flext_cli.__version__",
        "__version_info__": "flext_cli.__version__",
        "_models": "flext_cli._models",
        "api": "flext_cli.api",
        "base": "flext_cli.base",
        "c": ("flext_cli.constants", "FlextCliConstants"),
        "cli": "flext_cli.api",
        "constants": "flext_cli.constants",
        "d": "flext_core",
        "e": "flext_core",
        "h": "flext_core",
        "logger": "flext_cli.settings",
        "m": ("flext_cli.models", "FlextCliModels"),
        "models": "flext_cli.models",
        "p": ("flext_cli.protocols", "FlextCliProtocols"),
        "protocols": "flext_cli.protocols",
        "r": "flext_core",
        "s": "flext_cli.base",
        "services": "flext_cli.services",
        "settings": "flext_cli.settings",
        "t": ("flext_cli.typings", "FlextCliTypes"),
        "typings": "flext_cli.typings",
        "u": ("flext_cli.utilities", "FlextCliUtilities"),
        "utilities": "flext_cli.utilities",
        "x": "flext_core",
    },
)


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
