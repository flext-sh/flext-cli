"""FLEXT CLI - Production-ready CLI Foundation.

Enterprise-grade command line interface built on flext-core with direct
imports, standardized architecture, and production-ready patterns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli.__version__ import __version__, __version_info__
from flext_cli.api import FlextCli
from flext_cli.cli import FlextCliCli
from flext_cli.cli_params import FlextCliCommonParams
from flext_cli.cmd import FlextCliCmd
from flext_cli.commands import FlextCliCommands

# FlextCliConfig moved to FlextCliModels.CliConfig
from flext_cli.constants import FlextCliConstants
from flext_cli.context import FlextCliContext
from flext_cli.core import FlextCliCore
from flext_cli.debug import FlextCliDebug
from flext_cli.exceptions import FlextCliExceptions
from flext_cli.file_tools import FlextCliFileTools
from flext_cli.formatters import FlextCliFormatters
from flext_cli.mixins import FlextCliMixins
from flext_cli.models import FlextCliModels
from flext_cli.output import FlextCliOutput
from flext_cli.prompts import FlextCliPrompts
from flext_cli.protocols import FlextCliProtocols
from flext_cli.tables import FlextCliTables
from flext_cli.typings import FlextCliTypes

__all__ = [
    "FlextCli",
    "FlextCliCli",
    "FlextCliCmd",
    "FlextCliCommands",
    "FlextCliCommonParams",
    "FlextCliConfig",
    "FlextCliConstants",
    "FlextCliContext",
    "FlextCliCore",
    "FlextCliDebug",
    "FlextCliExceptions",
    "FlextCliFileTools",
    "FlextCliFormatters",
    "FlextCliMixins",
    "FlextCliModels",
    "FlextCliOutput",
    "FlextCliPrompts",
    "FlextCliProtocols",
    "FlextCliTables",
    "FlextCliTypes",
    "__version__",
    "__version_info__",
]
