"""Core mixins and decorators for the CLI.

Provides small and composable building blocks for CLI classes based on
``FlextResult`` and ``flext_cli.core.helpers`` utilities.
"""

from __future__ import annotations

import time
from collections.abc import Callable, Iterable
from functools import wraps
from pathlib import Path
from typing import ParamSpec, TypeVar

from flext_core import FlextResult
from rich.console import Console
from rich.progress import Progress, track as rich_track

from flext_cli import config_hierarchical
from flext_cli.core.helpers import FlextCliHelper

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

# Exported alias for internal use and in tests
track = rich_track


class FlextCliValidationMixin:
    """Input validation utilities for CLI."""

    def __init__(self) -> None:
        """Initialize the mixin."""
        self._flext_cli_helper = FlextCliHelper()
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
            return FlextResult.fail(f"Validation failed for {key}: {res.error}")
        return res.map(str)

    def _validate_url_input(self, key: str, value: object) -> FlextResult[str]:
        res = self._flext_cli_helper.flext_cli_validate_url(str(value))
        if res.is_failure:
            return FlextResult.fail(f"Validation failed for {key}: {res.error}")
        return res.map(str)

    def _validate_file_input(self, key: str, value: object) -> FlextResult[str]:
        path_res = self._flext_cli_helper.flext_cli_validate_path(
            str(value),
            must_exist=True,
            must_be_file=True,
        )
        if path_res.is_failure:
            return FlextResult.fail(f"Validation failed for {key}: {path_res.error}")
        return path_res.map(str)

    def _validate_path_input(self, key: str, value: object) -> FlextResult[str]:
        path_res = self._flext_cli_helper.flext_cli_validate_path(str(value))
        if path_res.is_failure:
            return FlextResult.fail(f"Validation failed for {key}: {path_res.error}")
        return path_res.map(str)

    def _validate_dir_input(self, key: str, value: object) -> FlextResult[str]:
        path_res = self._flext_cli_helper.flext_cli_validate_path(
            str(value),
            must_exist=True,
            must_be_dir=True,
        )
        if path_res.is_failure:
            return FlextResult.fail(f"Validation failed for {key}: {path_res.error}")
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
                    return FlextResult.fail(
                        f"Validation failed for {key}: {validation_result.error}",
                    )
                output[key] = validation_result.unwrap()
            else:
                return FlextResult.fail(
                    f"Unknown validation type: {vtype} for key {key}",
                )
        return FlextResult.ok(output)

    def flext_cli_require_confirmation(
        self,
        message: str,
        *,
        dangerous: bool = False,
    ) -> FlextResult[bool]:
        """Request user confirmation, with additional emphasis for dangerous actions."""
        prompt = f"[bold red]{message}[/bold red]" if dangerous else message
        res = self._flext_cli_helper.flext_cli_confirm(prompt)
        if res.is_failure:
            return res
        return (
            FlextResult.ok(True)  # noqa: FBT003
            if res.unwrap()
            else FlextResult.fail("Operation cancelled by user")
        )


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
        if result.success:
            self.console.print(f"✓ {result.data}")
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
        return bool(res.unwrap())


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
        """Iterate over items while displaying a simple progress indicator."""
        return list(track(items, description=description, console=self.console))

    def flext_cli_with_progress(self) -> Progress:
        """Create a Rich progress manager configured for the current console."""
        return Progress(console=self.console)


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
                return FlextResult.fail(f"Operation failed: {e}")
            if res.is_failure:
                return FlextResult.fail(res.error or "Unknown error")
            results.append(res.unwrap())
        return FlextResult.ok(results)

    def flext_cli_handle_result(
        self,
        result: FlextResult[object],
        *,
        success_action: Callable[[object], None] | None = None,
        error_action: Callable[[str], None] | None = None,
    ) -> object | None:
        """Encapsulate common logic for handling success/error of results."""
        if result.success:
            if success_action is not None:
                success_action(result.data)
            return result.data
        if error_action is not None and result.error is not None:
            error_action(result.error)
        return None


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
        res = config_hierarchical.create_default_hierarchy(config_path=config_path)
        if res.is_failure:
            return FlextResult.fail(
                "Config loading failed: " + (res.error or "unknown"),
            )
        self._flext_cli_config = res.unwrap()
        return FlextResult.ok(self._flext_cli_config)


class FlextCliAdvancedMixin(
    FlextCliValidationMixin,
    FlextCliInteractiveMixin,
    FlextCliProgressMixin,
    FlextCliResultMixin,
    FlextCliConfigMixin,
):
    """A complete mixin combining validation, UI, progress, results, and config."""

    def __init__(self) -> None:
        """Initialize the mixin."""
        FlextCliValidationMixin.__init__(self)
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
            return FlextResult.fail(valid.error or "Validation failed")
        if dangerous:
            confirm = self.flext_cli_require_confirmation(
                operation_name,
                dangerous=True,
            )
            if confirm.is_failure or not confirm.unwrap():
                return FlextResult.ok("Operation cancelled by user")
        if hasattr(self, "_flext_cli_console") and self._flext_cli_console is not None:
            self._flext_cli_console.print("✓ Validation passed")
        result = operation()
        if result.success and (
            hasattr(self, "_flext_cli_console") and self._flext_cli_console is not None
        ):
            self._flext_cli_console.print("✓ Operation completed")
        return result

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
        show_progress: bool | None = None,
    ) -> FlextResult[object]:
        """Execute a named sequence of steps that transform ``data``."""
        current: object = data
        for name, step in steps:
            if (
                hasattr(self, "_flext_cli_console")
                and self._flext_cli_console is not None
            ) and show_progress:
                self._flext_cli_console.print(f"Processing step: {name}")
            result = step(current)
            if result.is_failure:
                return FlextResult.fail(f"Step '{name}' failed: {result.error}")
            current = result.unwrap()
        return FlextResult.ok(current)

    # File operations helper used by tests
    def flext_cli_handle_file_operations(
        self,
        operations: list[tuple[str, str, Callable[[str], FlextResult[str]]]],
    ) -> FlextResult[list[dict[str, str]]]:
        """Execute operations on files, ensuring existence and safe I/O."""
        results: list[dict[str, str]] = []
        for op_name, path, func in operations:
            p = Path(path)
            if not p.exists():
                return FlextResult.fail(f"File not found: {path}")
            try:
                content = p.read_text(encoding="utf-8")
                res = func(content)
                if res.is_failure:
                    return FlextResult.fail(f"Operation {op_name} failed: {res.error}")
                p.write_text(res.unwrap(), encoding="utf-8")
                results.append({"operation": op_name, "file": path})
            except Exception as e:
                return FlextResult.fail(str(e))
        return FlextResult.ok(results)


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
                        return FlextResult.fail("Validation failed")
            helper = FlextCliHelper()
            if confirm:
                conf = helper.flext_cli_confirm(
                    f"[bold red]{operation_name}[/bold red]"
                    if dangerous
                    else operation_name,
                )
                if conf.is_failure or not conf.unwrap():
                    return FlextResult.ok("Operation cancelled by user")
            try:
                result = func(*args, **kwargs)
                if isinstance(result, FlextResult):
                    return result.map(str)
                return FlextResult.ok(str(result))
            except Exception as e:
                return FlextResult.fail(
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
                        if result.success:
                            return result.map(str)
                        last_error = result.error
                    else:
                        return FlextResult.ok(str(result))
                except Exception as e:
                    last_error = str(e)
                if _attempt < max_attempts:
                    time.sleep(delay)

            return FlextResult.fail(
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
                        return result.map(str)
                    return FlextResult.ok(str(result))
                except Exception as e:
                    return FlextResult.fail(f"Operation failed: {e}")

        return wrapper

    return decorator


# Reexports úteis em testes
FlextCliMixin = FlextCliAdvancedMixin
FlextCliBasicMixin = FlextCliProgressMixin  # conjunto mínimo usado em testes


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
                        return FlextResult.fail(
                            f"Validation failed for {key}: {res.error}",
                        )
                else:
                    return FlextResult.fail("Unknown validation type for " + key)
            try:
                result = func(*args, **kwargs)
                if isinstance(result, FlextResult):
                    return result.map(str)
                return FlextResult.ok(str(result))
            except Exception as e:
                return FlextResult.fail(str(e))

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
                    return value.map(str)
                return FlextResult.ok(str(value))
            except Exception as e:
                prefix = (message + ": ") if message else ""
                return FlextResult.fail(prefix + str(e))

        return wrapper

    return decorator


def flext_cli_require_confirmation(message: str) -> FlextCliDecorator[P, R]:
    """Request confirmation before executing the wrapped function."""

    def decorator(func: FlextDecoratedFunction[P, R]) -> Callable[P, FlextResult[str]]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> FlextResult[str]:
            helper = FlextCliHelper()
            conf = helper.flext_cli_confirm(message)
            if conf.is_failure or not conf.unwrap():
                return FlextResult.ok("Operation cancelled by user")
            result = func(*args, **kwargs)
            if isinstance(result, FlextResult):
                return result.map(str)
            return FlextResult.ok(str(result))

        return wrapper

    return decorator
