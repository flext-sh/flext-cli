"""CLI configuration module."""

from __future__ import annotations

# Re-export from main config module for backward compatibility
from flext_cli.config import CLIConfig, CLIOutputFormat, CLISettings

__all__ = ["CLIConfig", "CLIOutputFormat", "CLISettings"]
