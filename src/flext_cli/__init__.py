"""FLEXT CLI - CLI Foundation (30% functional, targeting 75%).

Current Status: Basic CLI wrapper with authentication and configuration.
Planned: Complete Click/Rich abstraction layer for ecosystem.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli.__version__ import (
    __author__,
    __author_email__,
    __build__,
    __classifiers__,
    __description__,
    __documentation_url__,
    __download_url__,
    __issues_url__,
    __keywords__,
    __license__,
    __long_description__,
    __maintainer__,
    __maintainer_email__,
    __platforms__,
    __python_requires__,
    __release_date__,
    __repository_url__,
    __status__,
    __url__,
    __version__,
    __version_info__,
)
from flext_cli.api import FlextCliApi
from flext_cli.auth import FlextCliAuth

# Clean imports without aliases following FLEXT unified class pattern
from flext_cli.cli import (
    auth,
    cli,
    config,
    debug,
    login,
    logout,
    main,
    status,
)
from flext_cli.cli_bus import FlextCliCommandBusService
from flext_cli.cli_main import FlextCliMain
from flext_cli.client import FlextCliClient
from flext_cli.cmd import FlextCliCmd
from flext_cli.config import FlextCliConfig
from flext_cli.constants import FlextCliConstants
from flext_cli.context import FlextCliContext
from flext_cli.core import FlextCliService
from flext_cli.debug import FlextCliDebug
from flext_cli.decorators import FlextCliDecorators
from flext_cli.domain_services import FlextCliDomainServices
from flext_cli.exceptions import FlextCliError
from flext_cli.file_operations import FlextCliFileOperations
from flext_cli.formatters import FlextCliFormatters
from flext_cli.interactions import FlextCliInteractions
from flext_cli.logging_setup import FlextCliLoggingSetup
from flext_cli.models import FlextCliModels
from flext_cli.protocols import FlextCliProtocols
from flext_cli.utils import FlextCliUtilities
from flext_core import FlextResult

# Clean exports without function aliases - use class methods directly


__all__ = [
    # Core CLI classes - no aliases or compatibility layers
    "FlextCliClient",
    "FlextCliApi",
    "FlextCliAuth",
    "FlextCliCmd",
    "FlextCliCommandBusService",
    "FlextCliConfig",
    "FlextCliConstants",
    "FlextCliContext",
    "FlextCliDebug",
    "FlextCliDecorators",
    "FlextCliDomainServices",
    "FlextCliError",
    "FlextCliFileOperations",
    "FlextCliFormatters",
    "FlextCliInteractions",
    "FlextCliLoggingSetup",
    "FlextCliMain",
    "FlextCliModels",
    "FlextCliProtocols",
    "FlextCliService",
    "FlextCliUtilities",
    "FlextResult",
    "__author__",
    "__author_email__",
    "__build__",
    "__classifiers__",
    "__description__",
    "__documentation_url__",
    "__download_url__",
    "__issues_url__",
    "__keywords__",
    "__license__",
    "__long_description__",
    "__maintainer__",
    "__maintainer_email__",
    "__platforms__",
    "__python_requires__",
    "__release_date__",
    "__repository_url__",
    "__status__",
    "__url__",
    "__version__",
    "__version_info__",
    "auth",
    "cli",
    "config",
    "debug",
    "login",
    "logout",
    "main",
    "status",
]


# ARCHITECTURAL COMPLIANCE: All aliases and compatibility wrappers removed
# Use FlextCliAuth class methods directly instead of loose functions
