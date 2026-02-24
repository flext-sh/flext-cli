"""Public exports for flext-cli with enforced framework isolation.

Expõe `FlextCli`, os serviços de domínio e utilidades respeitando a regra de
isolamento: Typer/Click permanecem em `cli.py`, enquanto Rich/Tabulate ficam em
`formatters.py` e `services/tables.py`. Utilize esses exports de alto nível
para preservar o comportamento suportado pelo projeto.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import d, e, h, r
from flext_core.mixins import x

from flext_cli.__version__ import __version__, __version_info__
from flext_cli.api import FlextCli
from flext_cli.app_base import FlextCliAppBase
from flext_cli.base import FlextCliServiceBase, s
from flext_cli.cli import FlextCliCli
from flext_cli.cli_params import FlextCliCommonParams
from flext_cli.command_builder import FlextCommandBuilder
from flext_cli.commands import FlextCliCommands
from flext_cli.constants import FlextCliConstants, c
from flext_cli.context import FlextCliContext
from flext_cli.debug import FlextCliDebug
from flext_cli.file_tools import FlextCliFileTools
from flext_cli.formatters import FlextCliFormatters
from flext_cli.middleware import (
    FlextMiddleware,
    LoggingMiddleware,
    RetryMiddleware,
    ValidationMiddleware,
    compose_middleware,
)
from flext_cli.mixins import FlextCliMixins
from flext_cli.models import FlextCliModels, m
from flext_cli.option_groups import FlextOptionGroup
from flext_cli.protocols import FlextCliProtocols

# Service exports (used by tests)
from flext_cli.services.cmd import FlextCliCmd
from flext_cli.services.core import FlextCliCore
from flext_cli.services.output import FlextCliOutput
from flext_cli.services.prompts import FlextCliPrompts
from flext_cli.services.tables import FlextCliTables
from flext_cli.settings import FlextCliSettings
from flext_cli.typings import FlextCliTypes, t
from flext_cli.utilities import FlextCliUtilities, u

__all__ = [
    "FlextCli",
    "FlextCliAppBase",
    "FlextCliCli",
    "FlextCliCmd",
    "FlextCliCommands",
    "FlextCliCommonParams",
    "FlextCliConstants",
    "FlextCliContext",
    "FlextCliCore",
    "FlextCliDebug",
    "FlextCliFileTools",
    "FlextCliFormatters",
    "FlextCliMixins",
    "FlextCliModels",
    "FlextCliOutput",
    "FlextCliPrompts",
    "FlextCliProtocols",
    "FlextCliServiceBase",
    "FlextCliSettings",
    "FlextCliTables",
    "FlextCliTypes",
    "FlextCliUtilities",
    "FlextCommandBuilder",
    "FlextMiddleware",
    "FlextOptionGroup",
    "LoggingMiddleware",
    "RetryMiddleware",
    "ValidationMiddleware",
    "__version__",
    "__version_info__",
    "c",
    "compose_middleware",
    "d",
    "e",
    "h",
    "m",
    "r",
    "s",
    "t",
    "u",
    "x",
]
