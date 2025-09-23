"""FLEXT CLI - Unified facade class for direct CLI access.

Single FlextCli class providing unified access to all CLI functionality.
Follows FLEXT pattern of one class per module with direct access.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli.debug import FlextCliDebug
from flext_cli.flext_cli_api import FlextCliApi
from flext_cli.flext_cli_auth import FlextCliAuth
from flext_cli.flext_cli_formatters import FlextCliFormatters
from flext_cli.flext_cli_main import FlextCliMain
from flext_cli.models import FlextCliModels
from flext_core import FlextService


class FlextCli(FlextService[dict[str, object]]):
    """Unified CLI facade providing direct access to all CLI functionality.

    Single entry point for the FLEXT CLI ecosystem, aggregating all CLI services
    without wrappers or aliases, following FLEXT domain patterns.
    """

    def __init__(self, **data: object) -> None:
        """Initialize unified CLI facade."""
        super().__init__(**data)

        # Direct access to CLI components
        self.api = FlextCliApi()
        self.auth = FlextCliAuth()
        self.config = FlextCliModels.FlextCliConfig()
        self.debug = FlextCliDebug()
        self.formatters = FlextCliFormatters()
        self.main = FlextCliMain()


__all__ = [
    "FlextCli",
]
