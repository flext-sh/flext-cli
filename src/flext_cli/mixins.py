"""Core mixins and decorators for the CLI.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import time
from collections.abc import Callable, Iterable
from functools import wraps
from pathlib import Path
from typing import ParamSpec, TypeVar, override

from flext_core import FlextResult
from rich.console import Console
from rich.progress import Progress, track as rich_track

from flext_cli.config_hierarchical import create_default_hierarchy
from flext_cli.helpers import FlextCliHelper

# Helper types for static annotations
P = ParamSpec("P")
T = TypeVar("T")
R = TypeVar("R")  # For return type of decorated function

FlextDecoratedFunction = Callable[P, R | FlextResult[R]]
FlextCliFunction = Callable[P, FlextResult[str]]
FlextCliDecorator = Callable[
    [FlextDecoratedFunction[P, R]],
    Callable[P, FlextResult[str]],
]


class FlextCliValidationMixin:
    """Input validation utilities for CLI."""

    def __init__(self) -> None:
        """Initialize the mixin."""
        self._flext_cli_helper = FlextCliHelper()
        # Back-compat attribute expected by tests for patching
        self._helper = self._flext_cli_helper
        self._input_validators: dict[str, Callable[[str, object], FlextResult[str]]] = {
            "email": self._validate_email_input,
            "url": self._validate_url_input,
            "file": self._validate_file_input,
            "path": self._validate_path_input,
            "dir": self._validate_dir_input,
        }

    def _validate_email_input(self, key: str, value: object) -> FlextResult[str]:
        res = self._flext_cli_helper.flext_cli_validate_email(str(value))
        if res.is_failure:
            return FlextResult[str].fail(f"Validation failed for {key}: {res.error}")
        return res.map(str)

    def _validate_url_input(self, key: str, value: object) -> FlextResult[str]:
        res = self._flext_cli_helper.flext_cli_validate_url(str(value))
        if res.is_failure:
            return FlextResult[str].fail(f"Validation failed for {key}: {res.error}")
        return res.map(str)

    def _validate_file_input(self, key: str, value: object) -> FlextResult[str]:
        path_res = self._flext_cli_helper.flext_cli_validate_path(
            str(value),
            must_exist=True,
            must_be_file=True,
        )
        if path_res.is_failure:
            return FlextResult[str].fail(
                f"Validation failed for {key}: {path_res.error}"
            )
        return path_res.map(str)

    def _validate_path_input(self, key: str, value: object) -> FlextResult[str]:
        path_res = self._flext_cli_helper.flext_cli_validate_path(str(value))
        if path_res.is_failure:
            return FlextResult[str].fail(
                f"Validation failed for {key}: {path_res.error}"
            )
        return path_res.map(str)

    def _validate_dir_input(self, key: str, value: object) -> FlextResult[str]:
        path_res = self._flext_cli_helper.flext_cli_validate_path(
            str(value),
            must_exist=True,
            must_be_dir=True,
        )
        if path_res.is_failure:
            return FlextResult[str].fail(
                f"Validation failed for {key}: {path_res.error}"
            )
        return path_res.map(str)

    def flext_cli_validate_inputs(
        self,
        inputs: dict[str, tuple[object, str]],
    ) -> FlextResult[dict[str, object]]:
        """Validate a mapping of name -> (value, type) and return normalized values."""
        output: dict[str, object] = {}
        for key, (value, vtype) in inputs.items():
            validator = self._input_validators.get(vtype)
            if validator:
                validation_result = validator(key, value)
                if validation_result.is_failure:
                    return FlextResult[dict[str, object]].fail(
                        f"Validation failed for {key}: {validation_result.error}",
                    )
                output[key] = validation_result.value
            else:
                return FlextResult[dict[str, object]].fail(
                    f"Unknown validation type: {vtype} for key {key}",
                )
        return FlextResult[dict[str, object]].ok(output)

    def flext_cli_require_confirmation(
        self,
        message: str,
        *,
        dangerous: bool = False,
    ) -> FlextResult[bool]:
        """Request user confirmation, with additional emphasis for dangerous actions."""
        prompt = f"[bold red]{message}[/bold red]" if dangerous else message
        # Use back-compat helper attribute if present (tests patch this)
        helper = getattr(self, "_helper", self._flext_cli_helper)
        # Use modern FlextResult pattern following flext-core standards
        confirmation_result = helper.flext_cli_confirm(prompt)
        confirmed = (
            confirmation_result.value if confirmation_result.is_success else False
        )
        if not confirmed:
            return FlextResult[bool].fail("Operation cancelled by user")
        return FlextResult[bool].ok(data=True)


class FlextCliInteractiveMixin:
    """Helpers for console and simple UI interactions."""

    def __init__(self) -> None:
        """Initialize the mixin."""
        self._flext_cli_console: Console | None = None

    @property
    def console(self) -> Console:
        """Return a Rich console, initialized on demand."""
        if self._flext_cli_console is None:
            self._flext_cli_console = Console()
        return self._flext_cli_console

    def flext_cli_print_success(self, message: str) -> None:
        """Print a standardized success message."""
        self.console.print(f"✓ {message}")

    def flext_cli_print_error(self, message: str) -> None:
        """Print a standardized error message."""
        self.console.print(f"✗ {message}")

    def flext_cli_print_warning(self, message: str) -> None:
        """Print a standardized warning."""
        self.console.print(f"⚠ {message}")

    def flext_cli_print_info(self, message: str) -> None:
        """Print a standardized info message."""
        self.console.print(f"i {message}")

    def flext_cli_print_result(self, result: FlextResult[object]) -> None:
        """Print the result of a ``FlextResult`` to the console."""
        if result.is_success:
            self.console.print(f"✓ {result.value}")
        else:
            self.console.print(f"✗ {result.error}")

    def flext_cli_confirm_operation(
        self,
        message: str,
    ) -> bool:
        """Run a simple confirmation flow, returning ``False`` on failure."""
        helper = FlextCliHelper(console=self.console)
        res = helper.flext_cli_confirm(message)
        if res.is_failure:
            self.console.print(f"✗ {res.error}")
            return False
        # Use modern FlextResult pattern following flext-core standards
        return res.value if res.is_success else False


class FlextCliProgressMixin:
    """Progress helpers based on Rich."""

    def __init__(self) -> None:
        """Initialize the mixin."""
        self._flext_cli_console: Console | None = None

    @property
    def console(self) -> Console:
        """Return a Rich console, initialized on demand."""
        if self._flext_cli_console is None:
            self._flext_cli_console = Console()
        return self._flext_cli_console

    def flext_cli_track_progress(
        self,
        items: Iterable[object],
        description: str,
    ) -> list[object]:
        """Iterate over items while displaying a simple progress indicator.

        Uses Rich track function for progress display.
        """
        try:
            # Use Rich track directly with proper signature
            return list(
                rich_track(items, description=description, console=self.console),
            )
        except Exception:
            # Fallback to simple list if Rich track fails
            return list(items)

    def flext_cli_with_progress(self, *args: object) -> Progress:
        """Create a Rich progress manager configured for the current console.

        Args:
            *args: Accepts either (message,) or (total, message) for compatibility.

        """
        # Extract message from args if provided
        message = None
        min_args_for_message = 2

        if len(args) == 1 and isinstance(args[0], str):
            message = args[0]
        elif (
            len(args) >= min_args_for_message
            and len(args) > 1
            and isinstance(args[1], str)
        ):
            message = args[1]
        if message:
            self.console.print(message)
        # Some tests inject a Console mock missing get_time; create Progress with default Console
        try:
            return Progress(console=self.console)
        except Exception:
            from rich.console import Console as _Console

            return Progress(console=_Console())


class FlextCliResultMixin:
    """Utilities for composing and handling ``FlextResult`` pipelines."""

    def flext_cli_chain_results(
        self,
        *operations: Callable[[], FlextResult[object]],
    ) -> FlextResult[list[object]]:
        """Execute operations in a chain, failing on the first error."""
        results: list[object] = []
        for op in operations:
            try:
                res = op()
            except Exception as e:
                return FlextResult[list[object]].fail(f"Operation failed: {e}")
            if res.is_failure:
                return FlextResult[list[object]].fail(res.error or "Unknown error")
            results.append(res.value)
        return FlextResult[list[object]].ok(results)

    def flext_cli_handle_result(
        self,
        result: FlextResult[object],
        *,
        success_action: Callable[[object], None] | None = None,
        error_action: Callable[[str], None] | None = None,
    ) -> object | None:
        """Encapsulate common logic for handling success/error of results."""
        if result.is_success:
            if success_action is not None:
                success_action(result.value)
        elif error_action is not None and result.error is not None:
            error_action(result.error)
        return result.value if result.is_success else None


class FlextCliBasicMixin(FlextCliValidationMixin):
    """Backward-compat basic mixin providing a Console and a helper."""

    def __init__(self) -> None:
        FlextCliValidationMixin.__init__(self)
        self._flext_cli_console: Console | None = None
        self._flext_cli_helper = FlextCliHelper()
        # Back-compat for tests that patch _helper
        self._helper = self._flext_cli_helper

    @property
    def console(self) -> Console:
        if self._flext_cli_console is None:
            self._flext_cli_console = Console()
        return self._flext_cli_console


# FlextCliMixin will be alias to FlextCliAdvancedMixin at end of file


class FlextCliConfigMixin:
    """Configuration loading via config hierarchy facade."""

    def __init__(self) -> None:
        """Initialize the mixin."""
        self._flext_cli_config: dict[str, object] | None = None

    @property
    def config(self) -> dict[str, object] | None:
        """Return the loaded configuration cache."""
        return self._flext_cli_config

    def flext_cli_load_config(
        self,
        config_path: str | None = None,
    ) -> FlextResult[dict[str, object]]:
        """Load default configuration (or custom via path)."""
        res = create_default_hierarchy(config_path=config_path)
        if res.is_failure:
            return FlextResult[dict[str, object]].fail(
                "Config loading failed: " + (res.error or "unknown"),
            )
        self._flext_cli_config = res.value
        return FlextResult[dict[str, object]].ok(self._flext_cli_config)


class FlextCliAdvancedMixin(
    FlextCliBasicMixin,
    FlextCliInteractiveMixin,
    FlextCliProgressMixin,
    FlextCliResultMixin,
    FlextCliConfigMixin,
):
    """A complete mixin combining validation, UI, progress, results, and config."""

    def __init__(self) -> None:
        """Initialize the mixin."""
        FlextCliBasicMixin.__init__(self)
        FlextCliInteractiveMixin.__init__(self)
        FlextCliProgressMixin.__init__(self)
        FlextCliResultMixin.__init__(self)
        FlextCliConfigMixin.__init__(self)

    def flext_cli_execute_with_full_validation(
        self,
        inputs: dict[str, tuple[object, str]],
        operation: Callable[[], FlextResult[str]],
        *,
        operation_name: str = "operation",
        dangerous: bool = False,
    ) -> FlextResult[str]:
        """Execute validation, optional confirmation, and then the provided operation."""
        # Input validation
        valid = self.flext_cli_validate_inputs(inputs)
        if valid.is_failure:
            return FlextResult[str].fail(valid.error or "Validation failed")
        if dangerous:
            confirm = self.flext_cli_require_confirmation(
                operation_name,
                dangerous=True,
            )
            if confirm.is_failure or not confirm.value:
                return FlextResult[str].ok("Operation cancelled by user")
        if hasattr(self, "_flext_cli_console") and self._flext_cli_console is not None:
            self._flext_cli_console.print("✓ Validation passed")
        result = operation()
        if result.is_success and (
            hasattr(self, "_flext_cli_console") and self._flext_cli_console is not None
        ):
            self._flext_cli_console.print("✓ Operation completed")
        return result

    @override
    def flext_cli_require_confirmation(
        self,
        message: str,
        *,
        dangerous: bool = False,
    ) -> FlextResult[bool]:
        """Re-expose confirmation using the base validation implementation."""
        return FlextCliValidationMixin.flext_cli_require_confirmation(
            self,
            message,
            dangerous=dangerous,
        )

    def flext_cli_process_data_workflow(
        self,
        data: object,
        steps: list[tuple[str, Callable[[object], FlextResult[object]]]],
        *,
        show_progress: bool | None = True,
    ) -> FlextResult[object]:
        """Execute a named sequence of steps that transform ``data``."""
        current: object = data
        for name, step in steps:
            if (
                hasattr(self, "_flext_cli_console")
                and self._flext_cli_console is not None
            ) and show_progress:
                self._flext_cli_console.print(f"Processing step: {name}")
            try:
                result = step(current)
            except Exception as e:  # convert exceptions to FlextResult failure
                return FlextResult[object].fail(f"Step '{name}' failed: {e}")
            if result.is_failure:
                return FlextResult[object].fail(f"Step '{name}' failed: {result.error}")
            current = result.value
        return FlextResult[object].ok(current)

    # File operations helper used by tests
    def flext_cli_execute_file_operations(
        self,
        operations: list[tuple[str, str, Callable[[str], FlextResult[str]]]],
        *,
        require_confirmation: bool | None = None,
    ) -> FlextResult[list[str]]:
        """Execute operations on files, ensuring existence and safe I/O.

        Returns a list of operation summaries like "<op>_<file>" to match tests.
        """
        results: list[str] = []
        for op_name, path, func in operations:
            p = Path(path)
            if not p.exists():
                return FlextResult[list[str]].fail(f"File not found: {path}")
            try:
                res = func(str(p))
                if res.is_failure:
                    return FlextResult[list[str]].fail(
                        f"Operation {op_name} failed: {res.error}"
                    )
                # If the operation returns content, write it back; otherwise keep original
                new_content = res.value
                # Write content back to file
                p.write_text(str(new_content), encoding="utf-8")
                results.append(f"{op_name}_{path}")
            except Exception as e:
                return FlextResult[list[str]].fail(str(e))
        return FlextResult[list[str]].ok(results)


# Rebind alias after advanced mixin is available
FlextCliMixin = FlextCliAdvancedMixin


def flext_cli_zero_config(
    operation_name: str,
    *,
    confirm: bool = True,
    validate_inputs: dict[str, str] | None = None,
    dangerous: bool = False,
) -> FlextCliDecorator[P, R]:
    """Apply standard validation and confirmation to a function."""

    def decorator(func: FlextDecoratedFunction[P, R]) -> Callable[P, FlextResult[str]]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> FlextResult[str]:
            if validate_inputs:
                for key, vtype in validate_inputs.items():
                    value = kwargs.get(key)
                    if vtype == "email" and (
                        not isinstance(value, str) or "@" not in value
                    ):
                        return FlextResult[str].fail("Validation failed")
            helper = FlextCliHelper()
            if confirm:
                conf = helper.flext_cli_confirm(
                    f"[bold red]{operation_name}[/bold red]"
                    if dangerous
                    else operation_name,
                )
                if conf.is_failure or not conf.value:
                    return FlextResult[str].ok("Operation cancelled by user")
            try:
                result = func(*args, **kwargs)
                if isinstance(result, FlextResult):
                    if result.is_success:
                        # Handle generic result value safely
                        value_str = "" if result.value is None else str(result.value)
                        return FlextResult[str].ok(value_str)
                    return FlextResult[str].fail(result.error or "Unknown error")
                return FlextResult[str].ok(str(result))
            except Exception as e:
                return FlextResult[str].fail(
                    f"{operation_name.capitalize()} raised exception: {e}",
                )

        return wrapper

    return decorator


def flext_cli_auto_retry(
    *,
    max_attempts: int,
    delay: float,
) -> FlextCliDecorator[P, R]:
    """Rerun a function on failure, with a fixed delay."""

    def decorator(func: FlextDecoratedFunction[P, R]) -> Callable[P, FlextResult[str]]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> FlextResult[str]:
            last_error: str | None = None
            for _attempt in range(1, max_attempts + 1):
                try:
                    result = func(*args, **kwargs)
                    if isinstance(result, FlextResult):
                        if result.is_success:
                            # Convert value to string safely, handling None case
                            return FlextResult[str].ok(
                                "" if result.value is None else str(result.value)
                            )
                        last_error = result.error
                    else:
                        return FlextResult[str].ok(str(result))
                except Exception as e:
                    last_error = str(e)
                if _attempt < max_attempts:
                    time.sleep(delay)

            return FlextResult[str].fail(
                f"Operation failed after {max_attempts} attempts: {last_error}",
            )

        return wrapper

    return decorator


def flext_cli_with_progress(message: str) -> FlextCliDecorator[P, R]:
    """Display a spinner while the wrapped function is executing."""

    def decorator(func: FlextDecoratedFunction[P, R]) -> Callable[P, FlextResult[str]]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> FlextResult[str]:
            console = Console()
            with console.status(message, spinner="dots"):
                try:
                    result = func(*args, **kwargs)
                    if isinstance(result, FlextResult):
                        if result.is_success:
                            # Convert value to string safely, handling None case
                            return FlextResult[str].ok(
                                "" if result.value is None else str(result.value)
                            )
                        return FlextResult[str].fail(result.error or "Unknown error")
                    return FlextResult[str].ok(str(result))
                except Exception as e:
                    return FlextResult[str].fail(f"Operation failed: {e}")

        return wrapper

    return decorator


def flext_cli_auto_validate(**rules: str) -> FlextCliDecorator[P, R]:
    """Validate kwargs based on simple rules.

    Supported rules: "email", "url", "file", "path", "dir".
    """

    def decorator(func: FlextDecoratedFunction[P, R]) -> Callable[P, FlextResult[str]]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> FlextResult[str]:
            helper = FlextCliHelper()
            auto_validators: dict[str, Callable[[object], FlextResult[str]]] = {
                "email": lambda v: helper.flext_cli_validate_email(
                    str(v) if v is not None else "",
                ).map(str),
                "url": lambda v: helper.flext_cli_validate_url(
                    str(v) if v is not None else "",
                ).map(str),
                "file": lambda v: helper.flext_cli_validate_path(
                    str(v) if v is not None else "",
                    must_exist=True,
                    must_be_file=True,
                ).map(str),
                "path": lambda v: helper.flext_cli_validate_path(
                    str(v) if v is not None else "",
                ).map(str),
                "dir": lambda v: helper.flext_cli_validate_path(
                    str(v) if v is not None else "",
                    must_exist=True,
                    must_be_dir=True,
                ).map(str),
            }

            for key, vtype in rules.items():
                value = kwargs.get(key)
                validator = auto_validators.get(vtype)
                if validator:
                    res = validator(value)
                    if res.is_failure:
                        return FlextResult[str].fail(
                            f"Validation failed for {key}: {res.error}",
                        )
                else:
                    return FlextResult[str].fail("Unknown validation type for " + key)
            try:
                result = func(*args, **kwargs)
                if isinstance(result, FlextResult):
                    if result.is_success:
                        # Convert value to string safely, handling None case
                        return FlextResult[str].ok(
                            "" if result.value is None else str(result.value)
                        )
                    return FlextResult[str].fail(result.error or "Unknown error")
                return FlextResult[str].ok(str(result))
            except Exception as e:
                return FlextResult[str].fail(str(e))

        return wrapper

    return decorator


def flext_cli_handle_exceptions(
    message: str | None = None,
) -> FlextCliDecorator[P, R]:
    """Convert exceptions into ``FlextResult`` with an optional message."""

    def decorator(func: FlextDecoratedFunction[P, R]) -> Callable[P, FlextResult[str]]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> FlextResult[str]:
            try:
                value = func(*args, **kwargs)
                if isinstance(value, FlextResult):
                    if value.is_success:
                        # Handle generic result value safely
                        value_str = "" if value.value is None else str(value.value)
                        return FlextResult[str].ok(value_str)
                    return FlextResult[str].fail(value.error or "Unknown error")
                return FlextResult[str].ok(str(value))
            except Exception as e:
                prefix = (message + ": ") if message else ""
                return FlextResult[str].fail(prefix + str(e))

        return wrapper

    return decorator


def flext_cli_require_confirmation(message: str) -> FlextCliDecorator[P, R]:
    """Request confirmation before executing the wrapped function."""

    def decorator(func: FlextDecoratedFunction[P, R]) -> Callable[P, FlextResult[str]]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> FlextResult[str]:
            helper = FlextCliHelper()
            conf = helper.flext_cli_confirm(message)
            if conf.is_failure or not conf.value:
                return FlextResult[str].ok("Operation cancelled by user")
            result = func(*args, **kwargs)
            if isinstance(result, FlextResult):
                if result.is_success:
                    # Handle generic result value safely
                    value_str = "" if result.value is None else str(result.value)
                    return FlextResult[str].ok(value_str)
                return FlextResult[str].fail(result.error or "Unknown error")
            return FlextResult[str].ok(str(result))

        return wrapper

    return decorator


__all__ = [
    "FlextCliDecorator",
    "FlextCliFunction",
    "FlextDecoratedFunction",
    "flext_cli_auto_validate",
    "flext_cli_handle_exceptions",
    "flext_cli_require_confirmation",
    "flext_cli_with_progress",
]
