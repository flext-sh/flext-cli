"""FLEXT CLI - CLI Foundation Library.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

# ruff: noqa: F403
# Import all from each module following flext-core pattern
from flext_cli.__version__ import *
from flext_cli.api import *
from flext_cli.application_commands import *
from flext_cli.cli import *
from flext_cli.cli_auth import *
from flext_cli.cli_config import *
from flext_cli.cli_mixins import *
from flext_cli.cli_types import *
from flext_cli.cli_utils import *
from flext_cli.client import *
from flext_cli.commands_auth import *
from flext_cli.commands_config import *
from flext_cli.commands_debug import *
from flext_cli.config import *
from flext_cli.config_hierarchical import *
from flext_cli.legacy import *
from flext_cli.constants import *
from flext_cli.context import *
from flext_cli.core import *
from flext_cli.core_implementations import *
from flext_cli.decorators import *
from flext_cli.ecosystem_integration import *
from flext_cli.entities import *
from flext_cli.exceptions import *
from flext_cli.flext_api_integration import *
from flext_cli.flext_cli import *
from flext_cli.formatters import *
from flext_cli.foundation import *
from flext_cli.helpers import *
from flext_cli.mixins import *
from flext_cli.models import *
from flext_cli.providers import *
from flext_cli.service_implementations import *
from flext_cli.service_protocols import *

# Import services with explicit handling to avoid class conflicts
from flext_cli import services as _services

# Re-export services classes with explicit names to avoid MyPy conflicts
BasicFlextCliCommandService = _services.BasicFlextCliCommandService
BasicFlextCliSessionService = _services.BasicFlextCliSessionService
from flext_cli.simple_api import *

# Import utilities (avoid duplicated imports)
from flext_cli.flext_cli_utilities import *
from flext_cli.utils_auth import *
from flext_cli.utils_core import *
from flext_cli.utils_output import *

# Note: __all__ is constructed dynamically at runtime from imported modules
# This pattern is necessary for library aggregation but causes pyright warnings
__all__: list[str] = []
