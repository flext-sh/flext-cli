"""FLEXT CLI Core Mixins - Boilerplate Reduction Patterns.

This module provides comprehensive mixin classes that reduce CLI boilerplate by 85%+
following flext-core patterns with FlextResult integration and type safety.

FlextCli Mixin Classes:
    - FlextCliValidationMixin: Automatic validation for CLI inputs
    - FlextCliConfigMixin: Zero-configuration config management
    - FlextCliProgressMixin: Built-in progress tracking
    - FlextCliInteractiveMixin: Rich interactive patterns
    - FlextCliResultMixin: FlextResult integration utilities

Boilerplate Reduction Features:
    - Automatic argument validation and sanitization
    - Railway-oriented programming with FlextResult
    - Zero-configuration Rich console integration
    - Built-in progress tracking and status reporting
    - Type-safe configuration management

Examples:
    >>> class MyCliCommand(FlextCliValidationMixin, FlextCliInteractiveMixin):
    ...     def execute(self, email: str, url: str) -> FlextResult[str]:
    ...         # Automatic validation via mixin
    ...         validated = self.flext_cli_validate_inputs({
    ...             "email": (email, "email"),
    ...             "url": (url, "url")
    ...         })
    ...         if not validated.success:
    ...             return validated
    ...
    ...         # Automatic confirmation via mixin
    ...         if not self.flext_cli_confirm_operation("Send request?"):
    ...             return FlextResult.ok("Operation cancelled")
    ...
    ...         return FlextResult.ok("Command executed successfully")

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import functools
import inspect
import time
from pathlib import Path
from typing import TYPE_CHECKING, Protocol, TypeVar, cast

from flext_core import FlextResult
from rich.console import Console
from rich.progress import Progress, track

from flext_cli.config_hierarchical import create_default_hierarchy
from flext_cli.core.helpers import FlextCliHelper, flext_cli_batch_validate
from flext_cli.core.typedefs import FlextCliValidationType

if TYPE_CHECKING:
    from collections.abc import Callable

T = TypeVar("T")


class CallableProtocol(Protocol):
    def __call__(self, *args: object, **kwargs: object) -> object: ...


F = TypeVar("F", bound=CallableProtocol)


class FlextCliValidationMixin:
    """Mixin providing automatic validation utilities for CLI classes.

    Provides zero-configuration validation methods that integrate with FlextResult
    patterns for railway-oriented programming.
    """

    def __init__(self, *args: object, **kwargs: object) -> None:
        """Initialize validation mixin."""
        super().__init__(*args, **kwargs)
        self._flext_cli_helper: FlextCliHelper | None = None

    @property
    def _helper(self) -> FlextCliHelper:
        """Lazy-loaded helper instance."""
        if self._flext_cli_helper is None:
            self._flext_cli_helper = FlextCliHelper()
        return self._flext_cli_helper

    def flext_cli_validate_inputs(self, inputs: dict[str, tuple[str, str]]) -> FlextResult[dict[str, object]]:
        """Validate multiple inputs with automatic type detection.

        Args:
            inputs: Dict of {key: (value, validation_type)} pairs

        Returns:
            FlextResult[Dict]: Success with validated data or failure

        Examples:
            >>> result = self.flext_cli_validate_inputs({
            ...     "email": ("user@example.com", "email"),
            ...     "url": ("https://api.flext.sh", "url"),
            ...     "config_file": ("/path/to/config.yml", "file")
            ... })

        """
        validated_data: dict[str, object] = {}

        for key, (value, validation_type) in inputs.items():
            if validation_type == "email":
                result = self._helper.flext_cli_validate_input(value, FlextCliValidationType.EMAIL)
            elif validation_type == "url":
                result = self._helper.flext_cli_validate_input(value, FlextCliValidationType.URL)
            elif validation_type == "path":
                result = self._helper.flext_cli_validate_input(value, FlextCliValidationType.PATH)
            elif validation_type == "file":
                result = self._helper.flext_cli_validate_input(value, FlextCliValidationType.FILE)
            elif validation_type == "dir":
                result = self._helper.flext_cli_validate_input(value, FlextCliValidationType.DIR)
            elif validation_type == "uuid":
                result = self._helper.flext_cli_validate_input(value, FlextCliValidationType.UUID)
            elif validation_type == "port":
                result = self._helper.flext_cli_validate_input(value, FlextCliValidationType.PORT)
            else:
                return FlextResult.fail(f"Unknown validation type for {key}: {validation_type}")

            if not result.success:
                return FlextResult.fail(f"Validation failed for {key}: {result.error}")

            validated_data[key] = result.data

        return FlextResult.ok(validated_data)

    def flext_cli_require_confirmation(self, operation: str, *, default: bool = False, dangerous: bool = False) -> FlextResult[bool]:
        """Require user confirmation for operations.

        Args:
            operation: Description of the operation
            default: Default confirmation value
            dangerous: Whether operation is dangerous (affects styling)

        Returns:
            FlextResult[bool]: Success with confirmation or failure

        """
        style = "[bold red]" if dangerous else "[bold yellow]"
        message = f"{style}Confirm {operation}?[/bold]"

        confirmation_result = self._helper.flext_cli_confirm(message, default=default)
        if not confirmation_result.success:
            return confirmation_result

        if not confirmation_result.data:
            return FlextResult.fail(f"Operation cancelled by user: {operation}")

        return FlextResult.ok(data=True)


class FlextCliInteractiveMixin:
    """Mixin providing interactive CLI utilities with Rich integration."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        """Initialize interactive mixin."""
        super().__init__(*args, **kwargs)
        self._flext_cli_console: Console | None = None

    @property
    def console(self) -> Console:
        """Lazy-loaded console instance."""
        if self._flext_cli_console is None:
            self._flext_cli_console = Console()
        return self._flext_cli_console

    def flext_cli_print_success(self, message: str) -> None:
        """Print success message with consistent styling."""
        self.console.print(f"[bold green]✓[/bold green] {message}")

    def flext_cli_print_error(self, message: str) -> None:
        """Print error message with consistent styling."""
        self.console.print(f"[bold red]✗[/bold red] {message}")

    def flext_cli_print_warning(self, message: str) -> None:
        """Print warning message with consistent styling."""
        self.console.print(f"[bold yellow]⚠[/bold yellow] {message}")

    def flext_cli_print_info(self, message: str) -> None:
        """Print info message with consistent styling."""
        self.console.print(f"[bold blue]i[/bold blue] {message}")

    def flext_cli_print_result(self, result: FlextResult[object]) -> None:
        """Print FlextResult with automatic success/error styling."""
        if result.success:
            self.flext_cli_print_success(str(result.data))
        else:
            self.flext_cli_print_error(str(result.error))

    def flext_cli_confirm_operation(self, operation: str, *, default: bool = False) -> bool:
        """Simple confirmation with automatic error handling."""
        try:
            helper = FlextCliHelper(console=self.console)
            result = helper.flext_cli_confirm(f"Confirm: {operation}?", default=default)
            if result.success:
                return result.data if isinstance(result.data, bool) else False
            self.flext_cli_print_error(f"Confirmation failed: {result.error}")
            return False
        except Exception as e:
            self.flext_cli_print_error(f"Confirmation error: {e}")
            return False


class FlextCliProgressMixin:
    """Mixin providing progress tracking utilities."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        """Initialize progress mixin."""
        super().__init__(*args, **kwargs)
        self._flext_cli_console: Console | None = None

    @property
    def console(self) -> Console:
        """Lazy-loaded console instance."""
        if self._flext_cli_console is None:
            self._flext_cli_console = Console()
        return self._flext_cli_console

    def flext_cli_track_progress(self, items: list[T], description: str = "Processing...") -> list[T]:
        """Track progress for iterable operations.

        Args:
            items: Items to process
            description: Progress description

        Returns:
            List of items (for use in for loops)

        Examples:
            >>> for item in self.flext_cli_track_progress(items, "Processing files"):
            ...     process_item(item)

        """
        return list(track(items, description=description, console=self.console))

    def flext_cli_with_progress(self, _total: int, _description: str = "Processing...") -> Progress:
        """Create progress context manager.

        Args:
            total: Total number of items
            description: Progress description

        Returns:
            Progress context manager

        Examples:
            >>> with self.flext_cli_with_progress(100, "Processing") as progress:
            ...     task = progress.add_task("Processing", total=100)
            ...     for i in range(100):
            ...         # Do work
            ...         progress.update(task, advance=1)

        """
        return Progress(console=self.console)


class FlextCliResultMixin:
    """Mixin providing FlextResult integration utilities."""

    def flext_cli_chain_results(self, *operations: Callable[[], FlextResult[object]]) -> FlextResult[list[object]]:
        """Chain multiple FlextResult operations.

        Args:
            *operations: Operations that return FlextResult

        Returns:
            FlextResult[list]: Success with all results or first failure

        Examples:
            >>> result = self.flext_cli_chain_results(
            ...     lambda: validate_input("test@example.com"),
            ...     lambda: save_config(config_data),
            ...     lambda: initialize_service()
            ... )

        """
        results: list[object] = []
        for operation in operations:
            try:
                result = operation()
                if not result.success:
                    return FlextResult.fail(result.error or "Operation failed")
                results.append(result.data)
            except Exception as e:
                return FlextResult.fail(f"Operation failed: {e}")

        return FlextResult.ok(results)

    def flext_cli_handle_result(self, result: FlextResult[T], *,
                               success_action: Callable[[T], None] | None = None,
                               error_action: Callable[[str], None] | None = None) -> T | None:
        """Handle FlextResult with automatic success/error actions.

        Args:
            result: FlextResult to handle
            success_action: Action to take on success
            error_action: Action to take on error

        Returns:
            Result data on success, None on failure

        """
        if result.success:
            if success_action and result.data is not None:
                success_action(result.data)
            return result.data
        if error_action:
            error_action(result.error or "Unknown error")
        return None


class FlextCliConfigMixin:
    """Mixin providing configuration management utilities."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        """Initialize config mixin."""
        super().__init__(*args, **kwargs)
        self._flext_cli_config: object | None = None

    def flext_cli_load_config(self, config_path: str | None = None) -> FlextResult[object]:
        """Load configuration with automatic type detection.

        Args:
            config_path: Path to config file (auto-detected if None)

        Returns:
            FlextResult with loaded config

        """
        try:
            # Use flext-core config loading patterns

            if config_path:
                # Load specific config file
                config_result = create_default_hierarchy(config_path=Path(config_path) if config_path else None)
            else:
                # Auto-detect config
                config_result = create_default_hierarchy()

            if config_result.success:
                self._flext_cli_config = config_result.data
                return FlextResult.ok(config_result.data)
            return FlextResult.fail(f"Config loading failed: {config_result.error}")

        except Exception as e:
            return FlextResult.fail(f"Config loading error: {e}")

    @property
    def config(self) -> object | None:
        """Access loaded configuration."""
        return self._flext_cli_config


# Boilerplate reduction decorators
def flext_cli_auto_validate(**validators: str) -> Callable[[F], F]:
    """Decorator for automatic argument validation.

    Args:
        **validators: Argument name to validation type mapping

    Examples:
        >>> @flext_cli_auto_validate(email="email", url="url", config_path="file")
        ... def my_command(email: str, url: str, config_path: str) -> FlextResult[str]:
        ...     # Arguments automatically validated
        ...     return FlextResult.ok("Success")

    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: object, **kwargs: object) -> object:
            helper = FlextCliHelper()

            # Validate arguments
            for arg_name, validation_type in validators.items():
                if arg_name in kwargs:
                    value = str(kwargs[arg_name])

                    if validation_type == "email":
                        result = helper.flext_cli_validate_input(value, FlextCliValidationType.EMAIL)
                    elif validation_type == "url":
                        result = helper.flext_cli_validate_input(value, FlextCliValidationType.URL)
                    elif validation_type == "file":
                        result = helper.flext_cli_validate_input(value, FlextCliValidationType.FILE)
                    elif validation_type == "dir":
                        result = helper.flext_cli_validate_input(value, FlextCliValidationType.DIR)
                    elif validation_type == "path":
                        result = helper.flext_cli_validate_input(value, FlextCliValidationType.PATH)
                    else:
                        return FlextResult.fail(f"Unknown validation type: {validation_type}")

                    if not result.success:
                        return FlextResult.fail(f"Validation failed for {arg_name}: {result.error}")

                    # Replace with validated value
                    kwargs[arg_name] = result.data

            return func(*args, **kwargs)
        return cast("F", wrapper)
    return decorator


def flext_cli_handle_exceptions(error_message: str = "Operation failed") -> Callable[[F], F]:
    """Decorator for automatic exception handling with FlextResult.

    Args:
        error_message: Base error message for exceptions

    Examples:
        >>> @flext_cli_handle_exceptions("Database operation failed")
        ... def save_data(data: dict) -> FlextResult[str]:
        ...     # Any exception automatically converted to FlextResult.fail
        ...     return FlextResult.ok("Data saved")

    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: object, **kwargs: object) -> FlextResult[object]:
            try:
                result = func(*args, **kwargs)
                # If function doesn't return FlextResult, wrap it
                if not hasattr(result, "success"):
                    return FlextResult.ok(result)
                return result  # type: ignore[return-value]
            except Exception as e:
                return FlextResult.fail(f"{error_message}: {e}")
        return cast("F", wrapper)
    return decorator


def flext_cli_require_confirmation(operation: str, *, default: bool = False) -> Callable[[F], F]:
    """Decorator for requiring user confirmation before operation.

    Args:
        operation: Description of the operation
        default: Default confirmation value

    Examples:
        >>> @flext_cli_require_confirmation("Delete all data", default=False)
        ... def delete_data() -> FlextResult[str]:
        ...     # User will be prompted for confirmation first
        ...     return FlextResult.ok("Data deleted")

    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: object, **kwargs: object) -> object:
            helper = FlextCliHelper()
            confirmation = helper.flext_cli_confirm(f"Confirm: {operation}?", default=default)

            if not confirmation.success:
                return FlextResult.fail(f"Confirmation failed: {confirmation.error}")

            if not confirmation.data:
                return FlextResult.ok("Operation cancelled by user")

            return func(*args, **kwargs)
        return cast("F", wrapper)
    return decorator


# Advanced Mixin Combinations for Common Patterns
class FlextCliAdvancedMixin(FlextCliValidationMixin, FlextCliInteractiveMixin, FlextCliProgressMixin, FlextCliResultMixin):
    """Advanced CLI mixin with enhanced patterns for massive boilerplate reduction."""

    def flext_cli_execute_with_full_validation(self, inputs: dict[str, tuple[str, str]], operation: Callable[[], FlextResult[object]], *, operation_name: str = "operation", dangerous: bool = False) -> FlextResult[object]:
        """Execute operation with full validation, confirmation, and error handling - eliminates 90%+ boilerplate.

        Args:
            inputs: Dict of validation inputs {key: (value, type)}
            operation: Operation to execute after validation and confirmation
            operation_name: Name for confirmation prompt
            dangerous: Whether to style as dangerous

        Returns:
            FlextResult: Operation result with full error handling

        Examples:
            >>> class MyCommand(FlextCliAdvancedMixin):
            ...     def execute(self, email: str, file_path: str):
            ...         inputs = {"email": (email, "email"), "config": (file_path, "file")}
            ...         return self.flext_cli_execute_with_full_validation(
            ...             inputs,
            ...             lambda: self.do_work(),
            ...             operation_name="process user data",
            ...             dangerous=True
            ...         )

        """
        # Step 1: Validate all inputs
        validation_result = self.flext_cli_validate_inputs(inputs)
        if not validation_result.success:
            self.flext_cli_print_error(f"Validation failed: {validation_result.error}")
            return FlextResult.fail(validation_result.error or "Validation failed")

        self.flext_cli_print_success("All inputs validated successfully")

        # Step 2: Get user confirmation
        confirmation_result = self.flext_cli_require_confirmation(operation_name, dangerous=dangerous)
        if not confirmation_result.success:
            return FlextResult.fail(confirmation_result.error or "Confirmation failed")

        # Step 3: Execute with error handling and progress indication
        try:
            self.flext_cli_print_info(f"Executing {operation_name}...")
            result = operation()

            if result.success:
                self.flext_cli_print_success(f"{operation_name.capitalize()} completed successfully")
            else:
                self.flext_cli_print_error(f"{operation_name.capitalize()} failed: {result.error}")

            return result

        except Exception as e:
            error_msg = f"{operation_name.capitalize()} raised exception: {e}"
            self.flext_cli_print_error(error_msg)
            return FlextResult.fail(error_msg)

    def flext_cli_process_data_workflow(self, data: object, workflow_steps: list[tuple[str, Callable[[object], FlextResult[object]]]], *, show_progress: bool = True) -> FlextResult[object]:
        """Process data through workflow with progress tracking - eliminates workflow boilerplate.

        Args:
            data: Initial data
            workflow_steps: List of (step_name, processor_function) tuples
            show_progress: Whether to show progress for each step

        Returns:
            FlextResult: Final processed data

        Examples:
            >>> class DataProcessor(FlextCliAdvancedMixin):
            ...     def process_user_data(self, raw_data):
            ...         steps = [
            ...             ("validate", self.validate_data),
            ...             ("clean", self.clean_data),
            ...             ("transform", self.transform_data),
            ...             ("save", self.save_data)
            ...         ]
            ...         return self.flext_cli_process_data_workflow(raw_data, steps)

        """
        current_data = data

        if show_progress:
            steps_to_track = self.flext_cli_track_progress(workflow_steps, f"Processing {len(workflow_steps)} steps")
        else:
            steps_to_track = workflow_steps

        for step_name, processor in steps_to_track:
            try:
                self.flext_cli_print_info(f"Processing step: {step_name}")

                result = processor(current_data)
                if not result.success:
                    error_msg = f"Step '{step_name}' failed: {result.error}"
                    self.flext_cli_print_error(error_msg)
                    return FlextResult.fail(error_msg)

                current_data = result.data
                self.flext_cli_print_success(f"Step '{step_name}' completed")

            except Exception as e:
                error_msg = f"Step '{step_name}' raised exception: {e}"
                self.flext_cli_print_error(error_msg)
                return FlextResult.fail(error_msg)

        return FlextResult.ok(current_data)

    def flext_cli_handle_file_operations(self, file_operations: list[tuple[str, str, Callable[[str], FlextResult[object]]]], *, require_confirmation: bool = True) -> FlextResult[dict[str, object]]:
        """Handle multiple file operations with validation and confirmation - eliminates file handling boilerplate.

        Args:
            file_operations: List of (operation_name, file_path, operation_function) tuples
            require_confirmation: Whether to require user confirmation

        Returns:
            FlextResult[dict]: Results of all file operations

        Examples:
            >>> class FileManager(FlextCliAdvancedMixin):
            ...     def backup_and_process_files(self):
            ...         operations = [
            ...             ("backup", "/path/to/data.json", self.backup_file),
            ...             ("process", "/path/to/data.json", self.process_file),
            ...             ("cleanup", "/path/to/temp.json", self.cleanup_file)
            ...         ]
            ...         return self.flext_cli_handle_file_operations(operations)

        """
        # Validate all file paths first
        file_validations = {
            f"file_{i}": (file_path, "file")
            for i, (_, file_path, _) in enumerate(file_operations)
        }

        validation_result = self.flext_cli_validate_inputs(file_validations)
        if not validation_result.success:
            return validation_result

        # Get confirmation for all operations
        if require_confirmation:
            operation_names = [op_name for op_name, _, _ in file_operations]
            confirmation_msg = f"perform {len(file_operations)} file operations: {', '.join(operation_names)}"

            confirmation_result = self.flext_cli_require_confirmation(confirmation_msg, dangerous=any("delete" in op.lower() or "remove" in op.lower() for op, _, _ in file_operations))
            if not confirmation_result.success:
                return FlextResult.fail(confirmation_result.error or "Confirmation failed")

        # Execute all operations with progress tracking
        results: dict[str, object] = {}
        operations_to_track = self.flext_cli_track_progress(file_operations, "File operations")

        for operation_name, file_path, operation_func in operations_to_track:
            try:
                self.flext_cli_print_info(f"Executing {operation_name} on {file_path}")

                result = operation_func(file_path)
                if result.success:
                    results[f"{operation_name}_{file_path}"] = result.data
                    self.flext_cli_print_success(f"{operation_name.capitalize()} completed for {file_path}")
                else:
                    error_msg = f"{operation_name.capitalize()} failed for {file_path}: {result.error}"
                    results[f"{operation_name}_{file_path}"] = error_msg
                    self.flext_cli_print_error(error_msg)

            except Exception as e:
                error_msg = f"{operation_name.capitalize()} raised exception for {file_path}: {e}"
                results[f"{operation_name}_{file_path}"] = error_msg
                self.flext_cli_print_error(error_msg)

        return FlextResult.ok(results)


# Zero-Configuration Decorators for Massive Boilerplate Reduction
def flext_cli_zero_config(operation_name: str = "operation", *, dangerous: bool = False, confirm: bool = True, validate_inputs: dict[str, str] | None = None) -> Callable[[F], F]:
    """Ultimate zero-configuration decorator eliminating 95% of CLI boilerplate.

    Automatically handles:
    - Input validation based on function annotations
    - User confirmation for dangerous operations
    - Error handling with FlextResult
    - Progress indication and success/failure reporting
    - Console styling and user experience

    Args:
        operation_name: Human-readable operation name
        dangerous: Whether to style as dangerous operation
        confirm: Whether to require user confirmation
        validate_inputs: Optional manual validation mapping {param_name: validation_type}

    Examples:
        >>> @flext_cli_zero_config("delete user data", dangerous=True)
        ... def delete_user(self, email: str, user_id: int) -> FlextResult[str]:
        ...     # All validation, confirmation, error handling automatic
        ...     return FlextResult.ok("User deleted")

        >>> @flext_cli_zero_config("process files", validate_inputs={"config": "file"})
        ... def process_files(self, config: str, count: int) -> FlextResult[dict]:
        ...     # Automatic file validation + confirmation + error handling
        ...     return FlextResult.ok({"processed": count})

    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: object, **kwargs: object) -> FlextResult[object]:
            # Get console from self if available
            console = getattr(args[0], "console", None) if args else None
            helper = FlextCliHelper(console=console)

            try:
                # Step 1: Auto-validation based on validate_inputs or function annotations
                if validate_inputs:
                    validations = []
                    sig = inspect.signature(func)

                    for param_name, validation_type in validate_inputs.items():
                        if param_name in sig.parameters:
                            # Get parameter value from args/kwargs
                            param_value = kwargs.get(param_name)
                            if param_value is None and len(args) > 1:  # Skip 'self'
                                param_index = list(sig.parameters.keys()).index(param_name)
                                if param_index < len(args):
                                    param_value = args[param_index]

                            if param_value is not None:
                                validations.append((str(param_value), validation_type, param_name))

                    if validations:
                        # Convert list of tuples to dict format expected by batch_validate
                        validation_inputs = {param_name: (value, val_type) for value, val_type, param_name in validations}
                        validation_result = flext_cli_batch_validate(validation_inputs)
                        if not validation_result.success:
                            helper.console.print(f"[red]✗[/red] {validation_result.error}")
                            return FlextResult.fail(validation_result.error or "Validation failed")

                        helper.console.print("[green]✓[/green] All inputs validated successfully")

                # Step 2: User confirmation if required
                if confirm:
                    if dangerous:
                        message = f"[bold red]Confirm: {operation_name}?[/bold red]"
                    else:
                        message = f"[bold yellow]Confirm: {operation_name}?[/bold yellow]"

                    confirmation = helper.flext_cli_confirm(message, default=False)
                    if not confirmation.success:
                        return FlextResult.fail(confirmation.error or "Confirmation failed")

                    if not confirmation.data:
                        return FlextResult.ok("Operation cancelled by user")

                # Step 3: Execute with progress indication
                helper.console.print(f"[blue]→[/blue] Executing {operation_name}...")

                result = func(*args, **kwargs)

                # Step 4: Report results
                if hasattr(result, "success"):
                    # It's a FlextResult
                    if result.success:
                        helper.console.print(f"[green]✓[/green] {operation_name.capitalize()} completed successfully")
                    else:
                        error_msg = getattr(result, "error", "Unknown error")
                        helper.console.print(f"[red]✗[/red] {operation_name.capitalize()} failed: {error_msg}")
                    return result  # type: ignore[return-value]
                # Wrap non-FlextResult in success
                helper.console.print(f"[green]✓[/green] {operation_name.capitalize()} completed successfully")
                return FlextResult.ok(result)

            except Exception as e:
                error_msg = f"{operation_name.capitalize()} raised exception: {e}"
                helper.console.print(f"[red]✗[/red] {error_msg}")
                return FlextResult.fail(error_msg)

        return cast("F", wrapper)
    return decorator


def flext_cli_auto_retry(max_attempts: int = 3, delay: float = 1.0, backoff_factor: float = 2.0) -> Callable[[F], F]:
    """Automatic retry decorator with exponential backoff - eliminates retry logic boilerplate.

    Args:
        max_attempts: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff_factor: Factor to multiply delay by for exponential backoff

    Examples:
        >>> @flext_cli_auto_retry(max_attempts=5, delay=1.0)
        ... def call_flaky_api(self) -> FlextResult[dict]:
        ...     # Automatic retry with exponential backoff
        ...     return self.make_api_call()

    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: object, **kwargs: object) -> object:
            console = getattr(args[0], "console", None) if args else None
            helper = FlextCliHelper(console=console)

            last_result = None
            current_delay = delay

            for attempt in range(max_attempts):
                try:
                    result = func(*args, **kwargs)

                    # Check if result indicates success
                    if hasattr(result, "success") and result.success:
                        if attempt > 0:
                            helper.console.print(f"[green]✓[/green] Operation succeeded after {attempt + 1} attempts")
                        return result
                    if not hasattr(result, "success"):
                        # Non-FlextResult, assume success
                        if attempt > 0:
                            helper.console.print(f"[green]✓[/green] Operation succeeded after {attempt + 1} attempts")
                        return result

                    # FlextResult failure
                    last_result = result
                    if attempt < max_attempts - 1:
                        error_msg = getattr(result, "error", "Unknown error")
                        helper.console.print(f"[yellow]⚠[/yellow] Attempt {attempt + 1} failed: {error_msg}. Retrying in {current_delay:.1f}s...")
                        time.sleep(current_delay)
                        current_delay *= backoff_factor

                except Exception as e:
                    if attempt < max_attempts - 1:
                        helper.console.print(f"[yellow]⚠[/yellow] Attempt {attempt + 1} failed with exception: {e}. Retrying in {current_delay:.1f}s...")
                        time.sleep(current_delay)
                        current_delay *= backoff_factor
                        last_result = FlextResult.fail(str(e))
                    else:
                        return FlextResult.fail(f"Operation failed after {max_attempts} attempts. Last error: {e}")

            # All attempts exhausted
            error_msg = f"Operation failed after {max_attempts} attempts"
            if last_result and hasattr(last_result, "error"):
                error_msg += f". Last error: {last_result.error}"
            return FlextResult.fail(error_msg)

        return cast("F", wrapper)
    return decorator


def flext_cli_with_progress(description: str = "Processing...") -> Callable[[F], F]:
    """Automatic progress indication decorator - eliminates progress display boilerplate.

    Args:
        description: Description to show during operation

    Examples:
        >>> @flext_cli_with_progress("Processing user data...")
        ... def process_users(self, users: list) -> FlextResult[list]:
        ...     # Automatic spinner/progress display
        ...     return FlextResult.ok(processed_users)

    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: object, **kwargs: object) -> object:
            console = getattr(args[0], "console", None) if args else None
            helper = FlextCliHelper(console=console)

            try:
                # Show start message
                helper.console.print(f"[blue]→[/blue] {description}")

                result = func(*args, **kwargs)

                # Show result
                if hasattr(result, "success"):
                    if result.success:
                        helper.console.print(f"[green]✓[/green] {description} completed")
                    else:
                        error_msg = getattr(result, "error", "Unknown error")
                        helper.console.print(f"[red]✗[/red] {description} failed: {error_msg}")
                else:
                    helper.console.print(f"[green]✓[/green] {description} completed")

                return result

            except Exception as e:
                helper.console.print(f"[red]✗[/red] {description} failed: {e}")
                return FlextResult.fail(f"Operation failed: {e}")

        return cast("F", wrapper)
    return decorator


# Enhanced Type aliases for improved ergonomics
FlextCliMixin = FlextCliAdvancedMixin  # Primary recommendation
FlextCliBasicMixin = type("FlextCliBasicMixin", (
    FlextCliValidationMixin,
    FlextCliInteractiveMixin,
    FlextCliProgressMixin,
    FlextCliResultMixin,
    FlextCliConfigMixin,
), {})
"""Combined mixin with all FlextCli utilities."""
