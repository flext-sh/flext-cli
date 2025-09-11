"""FLEXT CLI - Direct API exposure using flext-core.

NO WRAPPERS - Direct exposure of flext-core functionality.
Uses SOURCE OF TRUTH principle - no reimplementation.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

# Direct imports - NO WRAPPERS
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

# Core CLI classes - DIRECT EXPOSURE
from flext_cli.api import FlextCliApi
from flext_cli.auth import FlextCliAuth

# Click commands - DIRECT EXPOSURE
from flext_cli.cli import (
    FlextCliMain,
    auth as auth_cmd,
    cli,
    debug as debug_cmd,
    login as login_cmd,
    logout as logout_cmd,
    main,
    status as status_cmd,
)
from flext_cli.client import FlextApiClient
from flext_cli.config import FlextCliConfig
from flext_cli.constants import FlextCliConstants
from flext_cli.context import FlextCliContext, FlextCliExecutionContext
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

# Simple aliases for test compatibility - NO WRAPPERS
auth = auth_cmd
status = status_cmd
login = login_cmd
logout = logout_cmd
debug = debug_cmd
config = FlextCliConfig
FlextCliCmd = FlextCliConfig
handle_service_result = FlextCliDecorators.handle_service_result


def get_cli_config() -> FlextCliConfig:
    """Get CLI config instance - test compatibility."""
    return FlextCliConfig()


__all__ = [
    "E",
    "F",
    "FlextApiClient",
    "FlextCliApi",
    "FlextCliArgumentError",
    "FlextCliAuth",
    "FlextCliAuthenticationError",
    "FlextCliCmd",
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
    "cli",
    "config",
    "debug",
    "get_cli_config",
    "handle_service_result",
    "login",
    "logout",
    "main",
    "status",
]
