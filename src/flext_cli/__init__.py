"""FLEXT CLI - Production-ready CLI Foundation.

Enterprise-grade command line interface built on flext-core with direct
imports, standardized architecture, and production-ready patterns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli.api import FlextCli
from flext_cli.auth import FlextCliAuth
from flext_cli.cli import FlextCliCli
from flext_cli.cmd import FlextCliCmd
from flext_cli.commands import FlextCliCommands
from flext_cli.config import FlextCliConfig
from flext_cli.constants import FlextCliConstants
from flext_cli.context import FlextCliContext
from flext_cli.core import FlextCliCore
from flext_cli.debug import FlextCliDebug
from flext_cli.exceptions import FlextCliExceptions
from flext_cli.file_tools import FlextCliFileTools
from flext_cli.formatters import FlextCliFormatters
from flext_cli.handlers import FlextCliHandlers
from flext_cli.main import FlextCliMain
from flext_cli.mixins import FlextCliMixins
from flext_cli.models import FlextCliModels
from flext_cli.output import FlextCliOutput
from flext_cli.performance import FlextCliPerformance
from flext_cli.plugins import FlextCliPlugins
from flext_cli.processors import FlextCliProcessors
from flext_cli.prompts import FlextCliPrompts
from flext_cli.protocols import FlextCliProtocols
from flext_cli.shell import FlextCliShell
from flext_cli.tables import FlextCliTables
from flext_cli.testing import FlextCliTesting
from flext_cli.typer_cli import FlextCliTyper
from flext_cli.typings import FlextCliTypes
from flext_cli.version import VERSION, FlextCliVersion

# Standard Python package metadata
__version__: str = FlextCliConstants.VERSION
__version_info__: tuple[int | str, ...] = VERSION.version_info

__all__ = [
    "VERSION",
    "FlextCli",
    "FlextCliAuth",
    "FlextCliCli",
    "FlextCliCmd",
    "FlextCliCommands",
    "FlextCliConfig",
    "FlextCliConstants",
    "FlextCliContext",
    "FlextCliCore",
    "FlextCliDebug",
    "FlextCliExceptions",
    "FlextCliFileTools",
    "FlextCliFormatters",
    "FlextCliHandlers",
    "FlextCliMain",
    "FlextCliMixins",
    "FlextCliModels",
    "FlextCliOutput",
    "FlextCliPerformance",
    "FlextCliPlugins",
    "FlextCliProcessors",
    "FlextCliPrompts",
    "FlextCliProtocols",
    "FlextCliShell",
    "FlextCliTables",
    "FlextCliTesting",
    "FlextCliTyper",
    "FlextCliTypes",
    "FlextCliVersion",
    "__version__",
    "__version_info__",
]
