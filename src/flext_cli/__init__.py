"""FLEXT CLI - Production-ready CLI Foundation.

Enterprise-grade command line interface built on flext-core with direct
imports, standardized architecture, and production-ready patterns.

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

# CLI Core Components - Reorganized structure following FLEXT standards
from flext_cli.config import FlextCliConfig
from flext_cli.constants import FlextCliConstants
from flext_cli.context import FlextCliContext
from flext_cli.core import FlextCliService
from flext_cli.decorators import FlextCliDecorators

# FlextCliDomainService merged into FlextCliService
from flext_cli.exceptions import FlextCliError, FlextCliExceptions
from flext_cli.flext_cli import FlextCli
from flext_cli.flext_cli_api import FlextCliApi
from flext_cli.flext_cli_auth import FlextCliAuth
from flext_cli.flext_cli_formatters import FlextCliFormatters
from flext_cli.flext_cli_main import FlextCliMain
from flext_cli.logging_setup import FlextCliLoggingSetup
from flext_cli.mixins import FlextCliMixins
from flext_cli.models import FlextCliModels
from flext_cli.typings import FlextCliTypings

_CLI_PROVIDER_AVAILABLE = True


# All available exports
__all__ = [
    # CLI Provider availability indicator
    "_CLI_PROVIDER_AVAILABLE",
    # CLI Core Components
    "FlextCli",
    # CLI Provider APIs
    "FlextCliApi",
    "FlextCliAuth",
    "FlextCliConfig",
    "FlextCliConstants",
    "FlextCliContext",
    "FlextCliDecorators",
    # "FlextCliDomainService", # Merged into FlextCliService
    "FlextCliError",
    "FlextCliExceptions",
    "FlextCliFormatters",
    "FlextCliLoggingSetup",
    "FlextCliMain",
    "FlextCliMixins",
    "FlextCliModels",
    "FlextCliService",
    "FlextCliTypings",
    # Version information
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
]
