"""FLEXT CLI - CLI-specific functionality extending flext-core.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

CLI-specific functionality extending flext-core with command-line interface patterns,
authentication, configuration management, and CLI-specific utilities.

Architecture:
    Foundation: Constants, types, exceptions, protocols
    Core: Models, services, context, configuration
    Application: Commands, API functions, authentication, debug
    Infrastructure: Client, formatters, adapters, utilities
    Support: Decorators, helpers, output management

Key Components:
    FlextCliConfig: CLI configuration management with environment variables
    FlextCliContext: Execution context and session management
    FlextCliModels: CLI-specific domain models
    FlextCliServices: CLI service layer with health checks
    FlextCliApi: API client for CLI operations
    FlextCliAuth: Authentication and session management
    FlextCliFormatters: Output formatting and display utilities
    FlextCliDebug: Debug utilities and diagnostics

Examples:
    CLI configuration:
    >>> from flext_cli import FlextCliConfig
    >>> config = FlextCliConfig()
    >>> config.setup_cli()

    Authentication:
    >>> from flext_cli import auth_login
    >>> result = auth_login("username", "password")

    API operations:
    >>> from flext_cli import FlextApiClient
    >>> client = FlextApiClient()
    >>> response = client.get("/api/status")

Notes:
    - All CLI operations should use FlextResult[T] for error handling
    - Configuration is managed through FlextCliConfig
    - Authentication state is maintained in FlextCliContext
    - Follow Clean Architecture patterns with layered imports
    - Leverage flext-core foundation for common functionality

"""

from __future__ import annotations

# =============================================================================
# FOUNDATION LAYER - Import first, no dependencies on other modules
# =============================================================================

from flext_cli.__version__ import *
from flext_cli.constants import *
from flext_cli.typings import *
from flext_cli.exceptions import *
from flext_cli.protocols import *

# =============================================================================
# CORE LAYER - Depends only on Foundation layer
# =============================================================================

from flext_cli.models import *
from flext_cli.core import *
from flext_cli.context import *
from flext_cli.config import *

# =============================================================================
# APPLICATION LAYER - Depends on Core + Foundation layers
# =============================================================================

from flext_cli.cmd import *
from flext_cli.auth import *
from flext_cli.api_functions import *
from flext_cli.commands_debug import *
from flext_cli.debug import *

# =============================================================================
# INFRASTRUCTURE LAYER - Depends on Application + Core + Foundation
# =============================================================================

from flext_cli.client import *
from flext_cli.api import *
from flext_cli.formatters import *
from flext_cli.formatter_adapter import *
from flext_cli.output_adapter import *
from flext_cli.services import *

# =============================================================================
# SUPPORT LAYER - Depends on layers as needed, imported last
# =============================================================================

from flext_cli.decorators import *
from flext_cli.helpers import *
from flext_cli.cli_utils import *
from flext_cli.utils_core import *
from flext_cli.utils_output import *

# =============================================================================
# CLI ENTRY POINT - Main CLI functionality
# =============================================================================

from flext_cli.cli import *

# =============================================================================
# CONSOLIDATED EXPORTS - Combine all __all__ from modules
# =============================================================================

# Combine all __all__ exports from imported modules
import flext_cli.__version__ as _version
import flext_cli.api as _api
import flext_cli.api_functions as _api_functions
import flext_cli.auth as _auth
import flext_cli.cli as _cli
import flext_cli.cli_auth as _cli_auth
import flext_cli.cli_utils as _cli_utils
import flext_cli.client as _client
import flext_cli.cmd as _cmd
import flext_cli.commands_debug as _commands_debug
import flext_cli.config as _config
import flext_cli.constants as _constants
import flext_cli.context as _context
import flext_cli.core as _core
import flext_cli.debug as _debug
import flext_cli.decorators as _decorators
import flext_cli.exceptions as _exceptions
import flext_cli.formatter_adapter as _formatter_adapter
import flext_cli.formatters as _formatters
import flext_cli.helpers as _helpers
import flext_cli.models as _models
import flext_cli.output_adapter as _output_adapter
import flext_cli.protocols as _protocols
import flext_cli.services as _services
import flext_cli.typings as _typings
import flext_cli.utils_core as _utils_core
import flext_cli.utils_output as _utils_output

# Collect all __all__ exports from imported modules
_temp_exports: list[str] = []

for module in [
    _version,
    _constants,
    _typings,
    _exceptions,
    _protocols,
    _models,
    _core,
    _context,
    _config,
    _cmd,
    _auth,
    _cli_auth,
    _api_functions,
    _debug,
    _commands_debug,
    _client,
    _api,
    _formatters,
    _formatter_adapter,
    _output_adapter,
    _services,
    _decorators,
    _helpers,
    _cli_utils,
    _utils_core,
    _utils_output,
    _cli,
]:
    if hasattr(module, "__all__"):
        _temp_exports.extend(module.__all__)

# Remove duplicates and sort for consistent exports - build complete list first
_seen: set[str] = set()
_final_exports: list[str] = []
for item in _temp_exports:
    if item not in _seen:
        _seen.add(item)
        _final_exports.append(item)
_final_exports.sort()

# Define __all__ as literal list for linter compatibility
# This dynamic assignment is necessary for aggregating module exports
__all__: list[str] = _final_exports  # pyright: ignore[reportUnsupportedDunderAll] # noqa: PLE0605
