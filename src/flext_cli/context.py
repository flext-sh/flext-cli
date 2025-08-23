"""CLI domain context.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from typing import cast, override

from flext_core import FlextModel
from pydantic import ConfigDict, Field
from rich.console import Console


class FlextCliContext(FlextModel):
    """CLI execution context carrying state across commands (Pydantic)."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    config: object | None = Field(default=None)
    settings: object | None = Field(default=None)
    console: Console | None = Field(default=None)

    # Derived flags (also used directly by some tests when config is missing)
    debug: bool = Field(default=False)
    quiet: bool = Field(default=False)
    verbose: bool = Field(default=False)

    @override
    def model_post_init(self, __context: object, /) -> None:
        # Provide sensible defaults instead of failing hard. Tests construct this
        # context without explicitly providing config/console.
        if self.console is None:
            self.console = Console()
        # Leave config optional; derived flags already fall back to fields

    # Properties based on config if present, otherwise fall back to fields
    @property
    def is_debug(self) -> bool:
        cfg = self.config
        if cfg is not None and hasattr(cfg, "debug"):
            return bool(getattr(cfg, "debug", False))
        return bool(getattr(self, "debug", False))

    @property
    def is_quiet(self) -> bool:
        cfg = self.config
        if cfg is not None and hasattr(cfg, "quiet"):
            return bool(getattr(cfg, "quiet", False))
        return bool(getattr(self, "quiet", False))

    @property
    def is_verbose(self) -> bool:
        cfg = self.config
        if cfg is not None and hasattr(cfg, "verbose"):
            return bool(getattr(cfg, "verbose", False))
        return bool(getattr(self, "verbose", False))

    # Printing helpers expected by tests
    def print_success(self, message: str) -> None:
        if self.console is None:
            sys.stdout.write(f"[SUCCESS] {message}\n")
            sys.stdout.flush()
        else:
            self.console.print(f"[green][SUCCESS][/green] {message}")

    def print_error(self, message: str) -> None:
        if self.console is None:
            sys.stderr.write(f"[ERROR] {message}\n")
            sys.stderr.flush()
        else:
            self.console.print(f"[red][ERROR][/red] {message}")

    def print_warning(self, message: str) -> None:
        if self.console is None:
            sys.stderr.write(f"[WARNING] {message}\n")
            sys.stderr.flush()
        else:
            self.console.print(f"[yellow][WARNING][/yellow] {message}")

    def print_info(self, message: str) -> None:
        if not self.is_quiet:
            if self.console is None:
                sys.stdout.write(f"[INFO] {message}\n")
                sys.stdout.flush()
            else:
                self.console.print(f"[blue][INFO][/blue] {message}")

    def print_verbose(self, message: str) -> None:
        if self.is_verbose:
            if self.console is None:
                sys.stdout.write(f"[VERBOSE] {message}\n")
                sys.stdout.flush()
            else:
                self.console.print(f"[dim][VERBOSE][/dim] {message}")


@dataclass
class FlextCliExecutionContext:
    """Extended context for command execution (lightweight dataclass)."""

    command_name: str | None = None
    command_args: dict[str, object] = field(
        default_factory=lambda: cast("dict[str, object]", {})
    )
    execution_id: str | None = None
    start_time: float | None = None
    session_id: str | None = None
    user_id: str | None = None

    def get_execution_info(self) -> dict[str, object]:
        """Get execution information."""
        return {
            "command_name": self.command_name,
            "execution_id": self.execution_id,
            "start_time": self.start_time,
            "session_id": self.session_id,
        }


# Factory functions
def create_cli_context(**kwargs: object) -> FlextCliContext:
    """Create a CLI context with optional parameters."""
    config = kwargs.get("config")
    console_param = kwargs.get("console")
    console = console_param if isinstance(console_param, Console) else Console()
    settings = kwargs.get("settings")
    debug = bool(kwargs.get("debug"))
    quiet = bool(kwargs.get("quiet"))
    verbose = bool(kwargs.get("verbose"))
    return FlextCliContext(
        config=config,
        settings=settings,
        console=console,
        debug=debug,
        quiet=quiet,
        verbose=verbose,
    )


def create_execution_context(
    command_name: str,
    **kwargs: object,
) -> FlextCliExecutionContext:
    """Create an execution context for a specific command."""
    # Extract and cast specific fields with correct types
    kwargs.get("config", {})
    kwargs.get("environment", {})
    session_id = kwargs.get("session_id")
    user_id = kwargs.get("user_id")
    kwargs.get("debug", False)
    kwargs.get("verbose", False)
    command_args_raw = kwargs.get("command_args", {})
    execution_id = kwargs.get("execution_id")
    start_time = kwargs.get("start_time")

    # Properly type command_args
    command_args = (
        cast("dict[str, object]", command_args_raw)
        if isinstance(command_args_raw, dict)
        else {}
    )

    return FlextCliExecutionContext(
        command_name=command_name,
        command_args=command_args,
        execution_id=str(execution_id) if execution_id is not None else None,
        start_time=float(start_time)
        if start_time is not None and (isinstance(start_time, (int, float, str)))
        else None,
        session_id=str(session_id) if session_id is not None else None,
        user_id=str(user_id) if user_id is not None else None,
    )
