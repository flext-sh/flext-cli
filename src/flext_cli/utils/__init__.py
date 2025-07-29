"""FLEXT CLI Utilities - Clean Architecture v0.7.0.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

Utility modules using flext-core patterns exclusively.
No legacy configuration or fallback code.

"""

from __future__ import annotations

# Only export what's needed - clean architecture
from flext_cli.utils.config import CLIConfig, CLISettings, get_config

__all__ = [
    "CLIConfig",
    "CLISettings",
    "get_config",
]
