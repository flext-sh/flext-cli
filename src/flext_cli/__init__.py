"""FLEXT CLI - Production-ready CLI Foundation.

Enterprise-grade command line interface built on flext-core with direct
imports, standardized architecture, and production-ready patterns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli.__main__ import main
from flext_cli.__version__ import __version__

__author__ = "FLEXT Team"
from flext_cli.api import FlextCliApi
from flext_cli.auth import FlextCliAuth
from flext_cli.cli import FlextCli
from flext_cli.cmd import FlextCliCmd
from flext_cli.commands import FlextCliCommands
from flext_cli.config import FlextCliConfig
from flext_cli.constants import FlextCliConstants
from flext_cli.containers import FlextCliContainers
from flext_cli.context import FlextCliContext
from flext_cli.core import FlextCliService
from flext_cli.debug import FlextCliDebug
from flext_cli.exceptions import FlextCliError, FlextCliExceptions
from flext_cli.file_tools import FlextCliFileTools
from flext_cli.handlers import FlextCliHandlers
from flext_cli.logging_setup import FlextCliLoggingSetup
from flext_cli.mixins import FlextCliMixins
from flext_cli.models import FlextCliModels
from flext_cli.output import FlextCliOutput
from flext_cli.processors import FlextCliProcessors
from flext_cli.prompts import FlextCliPrompts
from flext_cli.protocols import FlextCliProtocols
from flext_cli.typings import FlextCliTypes
from flext_cli.utilities import FlextCliUtilities

__all__ = [
    "FlextCli",
    "FlextCliApi",
    "FlextCliAuth",
    "FlextCliCmd",
    "FlextCliCommands",
    "FlextCliConfig",
    "FlextCliConstants",
    "FlextCliContainers",
    "FlextCliContext",
    "FlextCliDebug",
    "FlextCliError",
    "FlextCliExceptions",
    "FlextCliFileTools",
    "FlextCliHandlers",
    "FlextCliLoggingSetup",
    "FlextCliMixins",
    "FlextCliModels",
    "FlextCliOutput",
    "FlextCliProcessors",
    "FlextCliPrompts",
    "FlextCliProtocols",
    "FlextCliService",
    "FlextCliTypes",
    "FlextCliUtilities",
    "__version__",
    "main",
]
