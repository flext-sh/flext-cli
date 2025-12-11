"""Base class for CLI applications using the FLEXT pattern.

Provides consistent initialization, execution, and error handling for Typer CLIs.
Subclasses define `app_name`, `app_help` and `config_class` and implement
`_register_commands()`.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import inspect
import os
import pathlib
import sys
import traceback
from abc import ABC, abstractmethod
from typing import ClassVar

import typer
from flext_core import FlextLogger as l_core, e, r

from flext_cli.cli import FlextCliCli, UsageError as ClickUsageError
from flext_cli.services.output import FlextCliOutput
from flext_cli.settings import FlextCliSettings


class FlextCliAppBase(ABC):
    """Base class for CLI applications using the FLEXT pattern.

    Fornece inicialização, execução e tratamento de erros consistentes para CLIs
    Typer. Subclasses definem `app_name`, `app_help` e `config_class` e
    implementam `_register_commands()`.
    """

    # ClassVars to override in subclass
    app_name: ClassVar[str]
    app_help: ClassVar[str]
    config_class: ClassVar[type[FlextCliSettings]]

    # Instance attributes
    logger: l_core
    _output: FlextCliOutput
    _cli: FlextCliCli
    _app: typer.Typer
    _config: FlextCliSettings

    def __init__(self) -> None:
        """Initialize CLI with FlextCli infrastructure."""
        super().__init__()
        self.logger = l_core(__name__)
        self._output = FlextCliOutput()
        self._cli = FlextCliCli()
        self._config = self.config_class.get_instance()

        self.logger.debug(
            "CLI configuration loaded",
            app_name=self.app_name,
        )

        # create_app_with_common_params expects FlextCliSettings | None
        # Pass config directly since it's already FlextCliSettings
        self._app = self._cli.create_app_with_common_params(
            name=self.app_name,
            help_text=self.app_help,
            config=self._config,
            add_completion=True,
        )

        try:
            self._register_commands()
        except NameError as ne:
            self._handle_pathlib_annotation_error(ne)

    @abstractmethod
    def _register_commands(self) -> None:
        """Register CLI commands - implement in subclass."""
        ...

    @staticmethod
    def _handle_pathlib_annotation_error(ne: NameError) -> None:
        """Handle Typer annotation issues with pathlib.Path in Python <3.10."""
        if "pathlib" in str(ne):
            l_core.get_logger().warning(
                "Pathlib annotation issue detected during command registration",
                error=str(ne),
                python_version_note=(
                    "Expected in Python <3.10 with Typer annotation issues"
                ),
            )
        else:
            raise ne

    @staticmethod
    def _resolve_cli_args(args: list[str] | None) -> list[str]:
        """Resolve CLI arguments based on environment."""
        if args is None:
            if os.getenv("PYTEST_CURRENT_TEST"):
                return []
            return sys.argv[1:] if len(sys.argv) > 1 else []
        return args

    def execute_cli(self, args: list[str] | None = None) -> r[bool]:
        """Execute the CLI with Railway-pattern error handling."""
        try:
            # Ensure pathlib is available for Typer's annotation evaluation
            sys.modules["pathlib"] = pathlib
            frame = inspect.currentframe()
            if frame and "pathlib" not in frame.f_globals:
                frame.f_globals["pathlib"] = pathlib

            resolved_args = FlextCliAppBase._resolve_cli_args(args)
            # Use standalone_mode=True to ensure Typer handles errors and output
            # When standalone_mode=False, Typer doesn't print errors automatically
            self._app(args=resolved_args, standalone_mode=True)
            return r[bool].ok(True)
        except NameError as name_err:
            if "pathlib" in str(name_err):
                error_msg = f"CLI annotation evaluation error: {name_err!s}"
                self._output.print_error(error_msg)
                return r[bool].fail(error_msg)
            raise
        except SystemExit as sys_exit:
            if sys_exit.code == 0:
                return r[bool].ok(True)
            # SystemExit with non-zero code means failure
            # Typer already printed the error in standalone_mode=True
            return r[bool].fail(f"CLI execution failed with code {sys_exit.code}")
        except Exception as exc:
            if isinstance(exc, ClickUsageError):
                error_msg = f"CLI execution error: {exc!s}"
                self._output.print_error(error_msg)
                return r[bool].fail(error_msg)
            # Business Rule: Exception handling MUST catch all FlextExceptions.BaseError types
            # Architecture: Use FlextExceptions.BaseError for flext-specific exceptions
            # Audit Implication: Proper exception handling ensures error logging and recovery
            if isinstance(
                exc,
                (
                    ValueError,
                    KeyError,
                    AttributeError,
                    TypeError,
                    OSError,
                    RuntimeError,
                    e.BaseError,
                ),
            ):
                tb = traceback.format_exc()
                error_msg = f"CLI execution error: {exc!s}\nTraceback:\n{tb}"
                self._output.print_error(error_msg)
                return r[bool].fail(f"CLI execution error: {exc!s}")
            raise
