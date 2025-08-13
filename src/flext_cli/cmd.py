"""Top-level short-name commands aggregator."""

from __future__ import annotations

from flext_cli.cli_auth import auth
from flext_cli.cmd_config import config
from flext_cli.cmd_debug import debug_cmd as debug

__all__ = ["auth", "config", "debug"]
