"""FLEXT CLI - CLI Foundation Library.

Simplified CLI library extending flext-core with minimal dependencies.
Focus on what works, avoid reinventing the wheel.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

# Core functionality - use bridge for safe imports
from flext_cli.core_bridge import *

# Simplified models that work
from flext_cli.models_simple import *

# Dependency injection container
from flext_cli.container import *

# Clean Architecture base classes
from flext_cli.architecture import *

# Essential CLI functionality only
from flext_cli.__version__ import __version__
import contextlib

# Only import what exists and works - handle all types of errors gracefully
with contextlib.suppress(ImportError, AttributeError, SyntaxError):
    from flext_cli.config import *

with contextlib.suppress(ImportError, AttributeError, SyntaxError):
    from flext_cli.constants import *

with contextlib.suppress(ImportError, AttributeError, SyntaxError):
    from flext_cli.typings import *

with contextlib.suppress(ImportError, AttributeError, SyntaxError):
    from flext_cli.decorators import *

with contextlib.suppress(ImportError, AttributeError, SyntaxError):
    from flext_cli.utils_core import flext_cli_output_data

with contextlib.suppress(ImportError, AttributeError, SyntaxError):
    from flext_cli.config import get_cli_config

with contextlib.suppress(ImportError, AttributeError, SyntaxError):
    from flext_cli.simple_api import setup_cli

# CLI-specific exports
__all__ = [
    # From core_bridge
    "FlextResult",
    "FlextModels.Entity",
    "FlextModels.EntityId",
    "FlextLogger",
    # From models_simple
    "FlextCliCommand",
    "FlextCliSession",
    "CommandStatus",
    "FlextCliOutputFormat",
    # From container
    "FlextContainer",
    "get_flext_container",
    "flext_service",
    # From decorators
    "cli_handle_keyboard_interrupt",
    "flext_cli_handle_keyboard_interrupt",
    "cli_measure_time",
    # From utils_core
    "flext_cli_output_data",
    # From config
    "get_cli_config",
    # From simple_api
    "setup_cli",
    # Version
    "__version__",
]
