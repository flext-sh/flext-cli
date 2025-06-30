"""FLEXT CLI - Developer Command Line Interface.

Enterprise command-line interface for the FLEXT platform with rich interactive features.

Copyright (c) 2025 FLEXT Team. All rights reserved.
"""

from __future__ import annotations

__version__ = "0.1.0"

from flext_cli.cli import cli
from flext_cli.client import FlextApiClient

__all__ = ["cli", "FlextApiClient", "__version__"]
