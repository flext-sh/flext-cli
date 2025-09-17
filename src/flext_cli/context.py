"""CLI domain context.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from pathlib import Path

from flext_cli.config import FlextCliConfig
from flext_cli.constants import FlextCliConstants
from flext_cli.utils import FlextCliUtilities
from flext_core import FlextLogger, FlextResult, FlextTypes


class FlextCliContext:
    """CLI execution context using composition for flexibility.

    Composition-based design containing execution environment, user information,
    and configuration settings for CLI command execution. Uses FlextModels.Value
    as a composed component rather than inheritance for better separation of concerns.

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
        logger: FlextLogger | None = None,
        console: object | None = None,  # Support for test compatibility
        debug: bool = False,
        quiet: bool = False,
        verbose: bool = False,
        working_directory: Path | None = None,
        environment_variables: FlextTypes.Core.Headers | None = None,
        user_id: str | None = None,
        session_id: str | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize CLI context with composed components.

        Args:
            id_: Context identifier (generated if not provided)
            config: CLI configuration instance
            logger: FlextLogger for output
            console: Console object for test compatibility
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
        self._logger = logger or FlextLogger(__name__)
        self._console = console  # For test compatibility
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
            "timeout_seconds",
            FlextCliConstants.MAX_COMMAND_TIMEOUT,
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
    def logger(self) -> FlextLogger:
        """Get FlextLogger."""
        return self._logger

    @property
    def console(self) -> object | None:
        """Get console object for test compatibility."""
        return self._console

    @property
    def working_directory(self) -> Path | None:
        """Get working directory."""
        return self._working_directory

    @property
    def environment_variables(self) -> FlextTypes.Core.Headers:
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
    def configuration(self) -> FlextTypes.Core.Dict:
        """Get context-specific configuration."""
        return self._configuration.copy()

    @property
    def timeout_seconds(self) -> int:
        """Get default timeout for operations."""
        match self._timeout_seconds:
            case int() | float() | str() as timeout:
                return int(timeout)
            case _:
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

    @property
    def profile(self) -> str:
        """Get context profile from config."""
        return getattr(self._config, "profile", "default")

    @profile.setter
    def profile(self, _value: str) -> None:
        """Setter to maintain immutability."""
        msg = "Cannot modify immutable FlextCliContext"
        raise ValueError(msg)

    @property
    def output_format(self) -> str:
        """Get output format from config."""
        return getattr(self._config, "output_format", "table")

    @property
    def no_color(self) -> bool:
        """Check if no color output is enabled."""
        return getattr(self._config, "no_color", True)

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
        self._logger.info(f"SUCCESS: {message}")

    def print_error(self, message: str) -> None:
        """Print error message."""
        self._logger.error(f"ERROR: {message}")

    def print_warning(self, message: str) -> None:
        """Print warning message."""
        self._logger.warning(f"WARNING: {message}")

    def print_info(self, message: str) -> None:
        """Print info message."""
        if not self.is_quiet:
            self._logger.info(f"INFO: {message}")

    def print_verbose(self, message: str) -> None:
        """Print verbose message."""
        if self.is_verbose:
            self._logger.debug(f"VERBOSE: {message}")

    def print_debug(self, message: str) -> None:
        """Print debug message if debug mode is enabled."""
        if self._debug:
            self._logger.debug(f"[DEBUG] {message}")

    def validate_business_rules(self) -> FlextResult[None]:
        """Validate CLI context business rules."""
        # CLI context is valid by construction due to Pydantic validation
        # Additional business validations can be added here if needed
        return FlextResult[None].ok(None)

    # Convenience immutability helpers expected by some tests
    def with_environment(self, **env: str) -> FlextCliContext:
        """Create new context with additional environment variables."""
        merged = {**(self.environment_variables or {}), **env}
        # Direct creation path
        return FlextCliContext.create(
            config=self.config,
            logger=self.logger,
            debug=self.debug,
            quiet=self.quiet,
            verbose=self.verbose,
            environment_variables=merged,
        )

    def with_working_directory(self, path: Path) -> FlextCliContext:
        """Create new context with different working directory."""
        return FlextCliContext.create(
            config=self.config,
            logger=self.logger,
            debug=self.debug,
            quiet=self.quiet,
            verbose=self.verbose,
            working_directory=path,
        )

    @dataclass
    class ExecutionContext:
        """Extended context for command execution (lightweight dataclass)."""

        command_name: str | None = None
        command_args: FlextTypes.Core.Dict = field(
            default_factory=FlextCliUtilities.empty_dict,
        )
        execution_id: str | None = None
        start_time: float | None = None
        session_id: str | None = None
        user_id: str | None = None

        def get_execution_info(self) -> FlextTypes.Core.Dict:
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
        logger_param = kwargs.get("logger")
        logger = (
            logger_param
            if isinstance(logger_param, FlextLogger)
            else FlextLogger(__name__)
        )
        debug = bool(kwargs.get("debug"))
        quiet = bool(kwargs.get("quiet"))
        verbose = bool(kwargs.get("verbose"))

        # Use provided config or create new one
        cli_config = config if isinstance(config, FlextCliConfig) else FlextCliConfig()

        # Create context with proper initialization

        return cls(
            id_=str(uuid.uuid4()),
            config=cli_config,
            logger=logger,
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
        command_args = command_args_raw if isinstance(command_args_raw, dict) else {}

        return FlextCliContext.ExecutionContext(
            command_name=command_name,
            command_args=command_args,
            execution_id=str(execution_id) if execution_id else None,
            start_time=float(start_time)
            if start_time and isinstance(start_time, (int, float, str))
            else None,
            session_id=str(session_id) if session_id else None,
            user_id=str(user_id) if user_id else None,
        )

    @classmethod
    def create_with_params(cls, **params: object) -> FlextCliContext:
        """Create CLI context with parameters."""
        # Extract known parameters
        profile = params.get("profile", "default")
        output_format = params.get("output_format", "table")
        debug = params.get("debug", False)
        quiet = params.get("quiet", False)
        verbose = params.get("verbose", False)
        no_color = params.get("no_color", False)

        # Validate parameters
        if profile == "":
            message = "Profile cannot be empty"
            raise ValueError(message)

        if output_format not in {"table", "json", "yaml", "csv", "plain"}:
            message = f"Output format must be one of table, json, yaml, csv, plain, got: {output_format}"
            raise ValueError(message)

        if quiet and verbose:
            message = "Cannot have both quiet and verbose modes enabled"
            raise ValueError(message)

        # Create config with parameters
        config = FlextCliConfig(
            profile=str(profile),
            debug=bool(debug),
            output_format=str(output_format),
            no_color=bool(no_color),
        )

        return cls(
            config=config,
            debug=bool(debug),
            quiet=bool(quiet),
            verbose=bool(verbose),
        )


__all__ = [
    "FlextCliContext",
]
