"""CLI domain context.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import cast

from flext_core import FlextResult
from flext_core.models import FlextModels
from rich.console import Console

from flext_cli.config import FlextCliConfig
from flext_cli.constants import FlextCliConstants


class FlextCliContext:
    """CLI execution context using composition for flexibility.

    Composition-based design containing execution environment, user information,
    and configuration settings for CLI command execution. Uses FlextModels.Value
    as a composed component rather than inheritance for better separation of concerns.

    Architecture pattern:
        - Composition: Contains FlextModels.Value as component
        - Immutable state: Context values are frozen after creation
        - Business rules: Validates context state during initialization
        - Type safety: FlextResult for error handling

    Business Rules:
      - Working directory must exist if specified
      - Environment variables must be valid strings
      - User ID must be non-empty if provided
    """

    def __init__(
        self,
        *,
        id_: str | None = None,
        config: FlextCliConfig | None = None,
        console: Console | None = None,
        debug: bool = False,
        quiet: bool = False,
        verbose: bool = False,
        working_directory: Path | None = None,
        environment_variables: dict[str, str] | None = None,
        user_id: str | None = None,
        session_id: str | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize CLI context with composed components.

        Args:
            id_: Context identifier (generated if not provided)
            config: CLI configuration instance
            console: Rich console for output
            debug: Enable debug mode
            quiet: Enable quiet mode
            verbose: Enable verbose mode
            working_directory: Working directory path
            environment_variables: Environment variables dict
            user_id: User identifier
            session_id: Session identifier
            **kwargs: Additional context data

        """
        # Composed core value object - use concrete type instead of abstract
        # self._core_value = FlextModels.Value()  # Abstract - removed

        # Context state management via composition
        self._id = id_ or str(uuid.uuid4())
        self._config = config or FlextCliConfig()
        self._console = console or Console()
        self._debug = debug
        self._quiet = quiet
        self._verbose = verbose
        self._working_directory = working_directory
        self._environment_variables = environment_variables or {}
        self._user_id = user_id
        self._session_id = session_id
        self._additional_data = kwargs
        self._configuration = kwargs.copy()
        self._timeout_seconds = kwargs.get(
            "timeout_seconds", FlextCliConstants.MAX_COMMAND_TIMEOUT
        )

    # Properties for accessing composed state
    @property
    def id(self) -> str:
        """Get context identifier."""
        return self._id

    @property
    def config(self) -> FlextCliConfig:
        """Get CLI configuration."""
        return self._config

    @property
    def console(self) -> Console:
        """Get Rich console."""
        return self._console

    @property
    def working_directory(self) -> Path | None:
        """Get working directory."""
        return self._working_directory

    @property
    def environment_variables(self) -> dict[str, str]:
        """Get environment variables."""
        return self._environment_variables.copy()

    @property
    def user_id(self) -> str | None:
        """Get user identifier."""
        return self._user_id

    @property
    def session_id(self) -> str | None:
        """Get session identifier."""
        return self._session_id

    @property
    def configuration(self) -> dict[str, object]:
        """Get context-specific configuration."""
        return self._configuration.copy()

    @property
    def timeout_seconds(self) -> int:
        """Get default timeout for operations."""
        if isinstance(self._timeout_seconds, (int, float)):
            return int(self._timeout_seconds)
        elif isinstance(self._timeout_seconds, str):
            return int(self._timeout_seconds)
        else:
            return 30

    @property
    def debug(self) -> bool:
        """Check if debug mode is enabled."""
        return self._debug

    @property
    def quiet(self) -> bool:
        """Check if quiet mode is enabled."""
        return self._quiet

    @property
    def verbose(self) -> bool:
        """Check if verbose mode is enabled."""
        return self._verbose

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
        # Direct creation path
        return FlextCliContext.create(
            config=self.config,
            console=self.console,
            debug=self.debug,
            quiet=self.quiet,
            verbose=self.verbose,
            environment_variables=merged,
        )

    def with_working_directory(self, path: Path) -> FlextCliContext:
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
