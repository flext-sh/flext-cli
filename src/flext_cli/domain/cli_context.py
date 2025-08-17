"""CLI domain context.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field

from pydantic import BaseModel, ConfigDict, Field
from rich.console import Console


class CLIContext(BaseModel):
    """CLI execution context carrying state across commands (Pydantic)."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    config: object | None = Field(default=None)
    settings: object | None = Field(default=None)
    console: Console | None = Field(default=None)

    # Derived flags (also used directly by some tests when config is missing)
    debug: bool = Field(default=False)
    quiet: bool = Field(default=False)
    verbose: bool = Field(default=False)

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
            return bool(cfg.debug)
        return bool(self.debug)

    @property
    def is_quiet(self) -> bool:
        cfg = self.config
        if cfg is not None and hasattr(cfg, "quiet"):
            return bool(cfg.quiet)
        return bool(self.quiet)

    @property
    def is_verbose(self) -> bool:
        cfg = self.config
        if cfg is not None and hasattr(cfg, "verbose"):
            return bool(cfg.verbose)
        return bool(self.verbose)

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
class CLIExecutionContext:
    """Extended context for command execution (lightweight dataclass)."""

    command_name: str | None = None
    command_args: dict[str, object] = field(default_factory=dict)
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
def create_cli_context(**kwargs: object) -> CLIContext:
    """Create a CLI context with optional parameters."""
    config = kwargs.get("config")
    console_param = kwargs.get("console")
    console = console_param if isinstance(console_param, Console) else Console()
    settings = kwargs.get("settings")
    debug = bool(kwargs.get("debug"))
    quiet = bool(kwargs.get("quiet"))
    verbose = bool(kwargs.get("verbose"))
    return CLIContext(
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
) -> CLIExecutionContext:
    """Create an execution context for a specific command."""
    # Extract and cast specific fields with correct types
    kwargs.get("config", {})
    kwargs.get("environment", {})
    session_id = kwargs.get("session_id")
    user_id = kwargs.get("user_id")
    kwargs.get("debug", False)
    kwargs.get("verbose", False)
    command_args = kwargs.get("command_args", {})
    execution_id = kwargs.get("execution_id")
    start_time = kwargs.get("start_time")

    return CLIExecutionContext(
        command_name=command_name,
        command_args=command_args if isinstance(command_args, dict) else {},
        execution_id=str(execution_id) if execution_id is not None else None,
        start_time=float(start_time)
        if start_time is not None and (isinstance(start_time, (int, float, str)))
        else None,
        session_id=str(session_id) if session_id is not None else None,
        user_id=str(user_id) if user_id is not None else None,
    )
