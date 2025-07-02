"""FLX CLI - Developer Command Line Interface.

Enterprise command-line interface for the FLX platform with rich interactive features.

Copyright (c) 2025 FLX Team. All rights reserved.
"""

from __future__ import annotations

__version__ = "0.1.0"

from flx_cli.cli import cli
from flx_cli.client import FlxApiClient

__all__ = ["FlxApiClient", "__version__", "cli"]
