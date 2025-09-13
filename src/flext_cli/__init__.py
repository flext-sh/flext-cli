"""FLEXT CLI - API exposure using.

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

# Import aliases and utility functions from dedicated module
from flext_cli.aliases import (
    FlextCliExecutionContext,
    auth,
    config,
    debug,
    get_cli_config,
    handle_service_result,
    login,
    logout,
    status,
)
from flext_cli.api import FlextCliApi
from flext_cli.auth import FlextCliAuth
from flext_cli.cli import (
    auth as auth_cmd,
    cli,
    debug as debug_cmd,
    get_cmd,
    login as login_cmd,
    logout as logout_cmd,
    main,
    status as status_cmd,
)
from flext_cli.cli_bus import FlextCliCommandBusService
from flext_cli.cli_main import FlextCliMain
from flext_cli.client import FlextApiClient
from flext_cli.cmd import FlextCliCmd  # DEPRECATED - use FlextCliCommandBusService
from flext_cli.config import FlextCliConfig
from flext_cli.constants import FlextCliConstants
from flext_cli.context import FlextCliContext
from flext_cli.core import FlextCliService
from flext_cli.data_processing import FlextCliDataProcessing
from flext_cli.debug import FlextCliDebug
from flext_cli.decorators import FlextCliDecorators
from flext_cli.domain_services import FlextCliDomainServices
from flext_cli.exceptions import (
    FlextCliArgumentError,
    FlextCliAuthenticationError,
    FlextCliCommandError,
    FlextCliConfigurationError,
    FlextCliConnectionError,
    FlextCliContextError,
    FlextCliError,
    FlextCliException,
    FlextCliFormatError,
    FlextCliOutputError,
    FlextCliProcessingError,
    FlextCliTimeoutError,
    FlextCliValidationError,
)
from flext_cli.factory import FlextCliFactory
from flext_cli.file_operations import FlextCliFileOperations
from flext_cli.formatters import FlextCliFormatters
from flext_cli.interactions import FlextCliInteractions
from flext_cli.logging_setup import FlextCliLoggingSetup
from flext_cli.models import FlextCliModels
from flext_cli.services import FlextCliServices
from flext_cli.typings import E, F, P, R, T, U, V

__all__ = [
    "E",
    "F",
    "FlextApiClient",
    "FlextCliApi",
    "FlextCliArgumentError",
    "FlextCliAuth",
    "FlextCliAuthenticationError",
    "FlextCliCmd",  # DEPRECATED - use FlextCliCommandBusService
    "FlextCliCommandBusService",  # NEW - proper Command Bus integration
    "FlextCliCommandError",
    "FlextCliConfig",
    "FlextCliConfigurationError",
    "FlextCliConnectionError",
    "FlextCliConstants",
    "FlextCliContext",
    "FlextCliContextError",
    "FlextCliDataProcessing",
    "FlextCliDebug",
    "FlextCliDecorators",
    "FlextCliDomainServices",
    "FlextCliError",
    "FlextCliException",
    "FlextCliExecutionContext",
    "FlextCliFactory",
    "FlextCliFileOperations",
    "FlextCliFormatError",
    "FlextCliFormatters",
    "FlextCliInteractions",
    "FlextCliLoggingSetup",
    "FlextCliMain",
    "FlextCliModels",
    "FlextCliOutputError",
    "FlextCliProcessingError",
    "FlextCliService",
    "FlextCliServices",
    "FlextCliTimeoutError",
    "FlextCliValidationError",
    "P",
    "R",
    "T",
    "U",
    "V",
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
    "auth_cmd",
    "cli",
    "config",
    "debug",
    "debug_cmd",
    "get_cli_config",
    "get_cmd",
    "handle_service_result",
    "login",
    "login_cmd",
    "logout",
    "logout_cmd",
    "main",
    "status",
    "status_cmd",
]
