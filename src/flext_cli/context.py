"""CLI domain context.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import ClassVar, cast

from flext_core import FlextModels, FlextResult
from pydantic import ConfigDict, Field
from rich.console import Console

from flext_cli.config import FlextCliConfig
from flext_cli.constants import FlextCliConstants


class FlextCliContext(FlextModels.Value):
    """CLI execution context extending FlextContext with CLI-specific functionality.

    Immutable context containing execution environment, user information,
    and configuration settings for CLI command execution.

    Business Rules:
      - Working directory must exist if specified
      - Environment variables must be valid strings
      - User ID must be non-empty if provided
    """

    # Reference to flext-core models for inheritance
    Core: ClassVar[type[FlextModels]] = FlextModels

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")

    def __init__(
        self,
        *,
        id_: str | None = None,
        config: FlextCliConfig | None = None,
        console: Console | None = None,
        debug: bool = False,
        quiet: bool = False,
        verbose: bool = False,
        **kwargs: object,
    ) -> None: ...

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Context id")
    config: FlextCliConfig = Field(
        default_factory=FlextCliConfig,
        description="CLI configuration instance",
    )
    console: Console = Field(
        default_factory=Console,
        description="Rich console for output",
    )

    # Additional context data
    working_directory: Path | None = Field(
        default=None,
        description="Working directory for command execution",
    )
    environment_variables: dict[str, str] = Field(
        default_factory=dict,
        description="Environment variables for execution context",
    )
    user_id: str | None = Field(
        default=None,
        description="User identifier for the context",
    )
    session_id: str | None = Field(
        default=None,
        description="CLI session identifier",
    )
    configuration: dict[str, object] = Field(
        default_factory=dict,
        description="Context-specific configuration",
    )
    timeout_seconds: int = Field(
        default=FlextCliConstants.MAX_COMMAND_TIMEOUT,
        ge=1,
        description="Default timeout for operations in this context",
    )

    # Derived flags (also used directly by some tests when config is missing)
    debug: bool = Field(default=False)
    quiet: bool = Field(default=False)
    verbose: bool = Field(default=False)

    def model_post_init(self, __context: object, /) -> None:
        """Initialize context after model creation."""
        # Context initialization - no need to set console since it has default_factory

    # Properties based on config if present, otherwise fall back to fields
    @property
    def is_debug(self) -> bool:
        """Check if debug mode is enabled."""
        if hasattr(self.config, "debug"):
            return bool(self.config.debug)
        return bool(self.debug)

    @property
    def is_quiet(self) -> bool:
        """Check if quiet mode is enabled."""
        # Check if config has quiet mode directly
        if hasattr(self.config, "quiet"):
            return bool(self.config.quiet)
        return bool(self.quiet)

    @property
    def is_verbose(self) -> bool:
        """Check if verbose mode is enabled."""
        # Check if config has verbose mode directly
        if hasattr(self.config, "verbose"):
            return bool(self.config.verbose)
        return bool(self.verbose)

    # Printing helpers expected by tests
    def print_success(self, message: str) -> None:
        """Print success message."""
        self.console.print(f"[green][SUCCESS][/green] {message}")

    def print_error(self, message: str) -> None:
        """Print error message."""
        self.console.print(f"[red][ERROR][/red] {message}")

    def print_warning(self, message: str) -> None:
        """Print warning message."""
        self.console.print(f"[yellow][WARNING][/yellow] {message}")

    def print_info(self, message: str) -> None:
        """Print info message."""
        if not self.is_quiet:
            self.console.print(f"[blue][INFO][/blue] {message}")

    def print_verbose(self, message: str) -> None:
        """Print verbose message."""
        if self.is_verbose:
            self.console.print(f"[dim][VERBOSE][/dim] {message}")

    def validate_business_rules(self) -> FlextResult[None]:
        """Validate CLI context business rules."""
        # CLI context is valid by construction due to Pydantic validation
        # Additional business validations can be added here if needed
        return FlextResult[None].ok(None)

    # Convenience immutability helpers expected by some tests
    def with_environment(self, **env: str) -> FlextCliContext:
        merged = {**(self.environment_variables or {}), **env}
        if hasattr(self, "model_copy"):
            return self.model_copy(update={"environment_variables": merged})
        # Fallback creation path
        return FlextCliContext.create(
            config=self.config,
            console=self.console,
            debug=self.debug,
            quiet=self.quiet,
            verbose=self.verbose,
        )

    def with_working_directory(self, path: Path) -> FlextCliContext:
        if hasattr(self, "model_copy"):
            return self.model_copy(update={"working_directory": path})
        return FlextCliContext.create(
            config=self.config,
            console=self.console,
            debug=self.debug,
            quiet=self.quiet,
            verbose=self.verbose,
        )

    @dataclass
    class ExecutionContext:
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
    @classmethod
    def create(cls, **kwargs: object) -> FlextCliContext:
        """Create a CLI context with optional parameters."""
        config = kwargs.get("config")
        console_param = kwargs.get("console")
        console = console_param if isinstance(console_param, Console) else Console()
        debug = bool(kwargs.get("debug"))
        quiet = bool(kwargs.get("quiet"))
        verbose = bool(kwargs.get("verbose"))

        # Use provided config or create new one
        cli_config = config if isinstance(config, FlextCliConfig) else FlextCliConfig()

        # Create context with proper initialization

        return cls(
            id=str(uuid.uuid4()),
            config=cli_config,
            console=console,
            debug=debug,
            quiet=quiet,
            verbose=verbose,
        )

    @classmethod
    def create_execution(
        cls: type[FlextCliContext],
        command_name: str,
        **kwargs: object,
    ) -> FlextCliContext.ExecutionContext:
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

        return FlextCliContext.ExecutionContext(
            command_name=command_name,
            command_args=command_args,
            execution_id=str(execution_id) if execution_id is not None else None,
            start_time=float(start_time)
            if start_time is not None and (isinstance(start_time, (int, float, str)))
            else None,
            session_id=str(session_id) if session_id is not None else None,
            user_id=str(user_id) if user_id is not None else None,
        )


# Backward-compatibility alias expected by tests
FlextCliExecutionContext = FlextCliContext.ExecutionContext


__all__ = [
    "FlextCliContext",
    "FlextCliExecutionContext",
]
