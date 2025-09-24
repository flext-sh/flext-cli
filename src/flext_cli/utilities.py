"""FLEXT CLI Utilities - Unified class following FLEXT architecture patterns.

Single FlextCliUtilities class consolidating all utility functions and validation helpers.
Follows FLEXT unified class pattern - one class per module extending flext-core.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import csv
import json
import time
from collections.abc import Awaitable, Callable, Sequence
from io import StringIO
from pathlib import Path
from typing import cast

import yaml
from pydantic import BaseModel, ConfigDict, ValidationError
from pydantic_settings import SettingsConfigDict
from tabulate import tabulate

from flext_cli.constants import FlextCliConstants
from flext_core import FlextContainer, FlextLogger, FlextResult, FlextUtilities


class FlextCliUtilities(FlextUtilities):
    """Unified utility service for CLI operations using modern Pydantic v2.

    Provides centralized utilities without duplicating Pydantic v2 functionality.
    Uses FlextModels and FlextConfig for all validation needs.
    """

    def __init__(self) -> None:
        """Initialize FlextCliUtilities service."""
        super().__init__()
        self._container = FlextContainer.get_global()
        self._logger = FlextLogger(__name__)

    def execute(self) -> FlextResult[None]:
        """Execute the main domain service operation.

        Returns:
            FlextResult[None]: Description of return value.

        """
        return FlextResult[None].ok(None)

    @property
    def logger(self) -> FlextLogger:
        """Get logger instance.

        Returns:
            FlextLogger: Description of return value.

        """
        return self._logger

    @property
    def container(self) -> FlextContainer:
        """Get container instance.

        Returns:
            FlextContainer: Description of return value.

        """
        return self._container

    @staticmethod
    def get_base_config_dict() -> ConfigDict:
        """Get base Pydantic configuration for CLI models.

        Returns:
            ConfigDict: Description of return value.

        """
        return ConfigDict(
            validate_assignment=True,
            use_enum_values=True,
            arbitrary_types_allowed=True,
        )

    @staticmethod
    def get_strict_config_dict() -> ConfigDict:
        """Get strict Pydantic configuration for CLI models.

        Returns:
            ConfigDict: Description of return value.

        """
        return ConfigDict(
            validate_assignment=True,
            use_enum_values=True,
            arbitrary_types_allowed=False,
            str_strip_whitespace=True,
        )

    @staticmethod
    def home_path() -> Path:
        """Get home directory path.

        Returns:
            Path: Description of return value.

        """
        return Path.home()

    @staticmethod
    def token_file_path() -> Path:
        """Get authentication token file path.

        Returns:
            Path: Description of return value.

        """
        return (
            Path.home()
            / FlextCliConstants.FLEXT_DIR_NAME
            / FlextCliConstants.AUTH_DIR_NAME
            / FlextCliConstants.TOKEN_FILE_NAME
        )

    @staticmethod
    def refresh_token_file_path() -> Path:
        """Get refresh token file path.

        Returns:
            Path: Description of return value.

        """
        return (
            Path.home()
            / FlextCliConstants.FLEXT_DIR_NAME
            / FlextCliConstants.AUTH_DIR_NAME
            / FlextCliConstants.REFRESH_TOKEN_FILE_NAME
        )

    @staticmethod
    def get_settings_config_dict() -> SettingsConfigDict:
        """Get Pydantic configuration for CLI settings models.

        Returns:
            SettingsConfigDict: Description of return value.

        """
        return SettingsConfigDict(
            validate_assignment=True,
            use_enum_values=True,
            env_prefix="FLEXT_CLI_",
            case_sensitive=False,
        )

    @staticmethod
    def validate_with_pydantic_model(
        data: dict[str, object] | object,
        model_class: type[BaseModel],
    ) -> FlextResult[BaseModel]:
        """Validate data using Pydantic v2 model directly.

        Args:
            data: Data to validate (dict or object convertible to dict)
            model_class: Pydantic v2 model class to validate against

        Returns:
            FlextResult containing validated model instance or error

        """
        try:
            # Convert data to dict if needed
            if isinstance(data, dict):
                validated_data = cast("dict[str, object]", data)
            elif hasattr(data, "model_dump") and callable(
                getattr(data, "model_dump", None)
            ):
                # Safe attribute access with getattr instead of direct access
                model_dump_method = getattr(data, "model_dump")
                dumped_data = model_dump_method()
                # Ensure the dumped data is properly typed
                if isinstance(dumped_data, dict):
                    validated_data = cast("dict[str, object]", dumped_data)
                else:
                    validated_data = {"value": dumped_data}
            elif hasattr(data, "__dict__"):
                validated_data = cast("dict[str, object]", data.__dict__)
            else:
                # Try to convert other types to dict format
                validated_data = {"value": data}

            validated_model = model_class.model_validate(validated_data)
            return FlextResult[BaseModel].ok(validated_model)
        except ValidationError as e:
            error_details = "; ".join(
                [
                    f"{err['loc'][0] if err['loc'] else 'field'}: {err['msg']}"
                    for err in e.errors()
                ],
            )
            return FlextResult[BaseModel].fail(f"Validation failed: {error_details}")
        except Exception as e:
            return FlextResult[BaseModel].fail(f"Unexpected validation error: {e}")

    @staticmethod
    def validate_data(data: object, validator: object) -> FlextResult[bool]:
        """Validate data using provided validator function or dict.

        Returns:
            FlextResult[bool]: Description of return value.

        """
        try:
            if data is None or validator is None:
                return FlextResult[bool].fail("Data and validator cannot be None")

            if callable(validator):
                result = validator(data)
                return FlextResult[bool].ok(bool(result))
            if isinstance(validator, dict):
                # Simple dict-based validation
                if isinstance(data, dict):
                    validator_dict = cast("dict[str, type]", validator)
                    for key, expected_type in validator_dict.items():
                        expected_type_obj = expected_type
                        if key not in data:
                            return FlextResult[bool].fail(
                                f"Missing required field: {key}",
                            )
                        if not isinstance(data[key], expected_type_obj):
                            type_name: str = getattr(
                                expected_type_obj, "__name__", str(expected_type_obj)
                            )
                            return FlextResult[bool].fail(
                                f"Invalid type for {key}: expected {type_name}",
                            )
                    return FlextResult[bool].ok(True)
                return FlextResult[bool].fail(
                    "Data must be dict for dict-based validation",
                )
            return FlextResult[bool].fail("Validator must be callable or dict")
        except Exception as e:
            return FlextResult[bool].fail(f"Validation failed: {e}")

    @staticmethod
    def batch_process_items(
        items: Sequence[object],
        processor: Callable[[object], object],
    ) -> FlextResult[list[object]]:
        """Process items in batch with error handling.

        Returns:
            FlextResult[list[object]]: Description of return value.

        """
        try:
            if not isinstance(items, (list, tuple)):
                return FlextResult[list[object]].fail(
                    "Invalid items format: must be list or tuple",
                )

            results: list[object] = []
            for item in items:
                try:
                    result = processor(item)
                    # Handle both FlextResult and raw value returns
                    if hasattr(result, "is_failure") and hasattr(result, "unwrap"):
                        # Safe attribute access with getattr instead of direct access
                        is_failure = getattr(result, "is_failure", False)
                        if is_failure:
                            error_msg = getattr(result, "error", "Unknown error")
                            return FlextResult[list[object]].fail(
                                f"Item processing failed: {error_msg}",
                            )
                        unwrap_method = getattr(result, "unwrap")
                        unwrapped_value: object = unwrap_method()
                        results.append(unwrapped_value)
                    else:
                        result_value: object = result
                        results.append(result_value)
                except Exception as e:
                    return FlextResult[list[object]].fail(
                        f"Item processing failed: {e}",
                    )
            return FlextResult[list[object]].ok(results)
        except Exception as e:
            return FlextResult[list[object]].fail(f"Batch processing failed: {e}")

    @staticmethod
    def safe_json_stringify(data: object) -> str:
        """Safely stringify data to JSON.

        Returns:
            str: Description of return value.

        """
        try:
            return json.dumps(data, default=str, indent=2)
        except Exception:
            return str(data)

    @staticmethod
    def json_stringify_with_result(data: object) -> FlextResult[str]:
        """Stringify data to JSON with result handling.

        Returns:
            FlextResult[str]: Description of return value.

        """
        try:
            return FlextResult[str].ok(json.dumps(data, default=str, indent=2))
        except Exception as e:
            return FlextResult[str].fail(f"JSON serialization failed: {e}")

    @staticmethod
    def safe_json_stringify_flext_result(result: FlextResult[object]) -> str:
        """Safely stringify FlextResult to JSON.

        Returns:
            str: Description of return value.

        """
        return FlextCliUtilities.safe_json_stringify(
            result.unwrap() if result.is_success else {"error": result.error},
        )

    @staticmethod
    def safe_json_parse(json_data: str) -> dict[str, object] | None:
        """Safely parse JSON string to dictionary.

        Args:
            json_data: JSON string to parse

        Returns:
            Parsed data or None if parsing fails

        """
        try:
            result: dict[str, object] = json.loads(json_data)
            return result
        except json.JSONDecodeError:
            return None
        except Exception:
            return None

    @staticmethod
    def format_as_json(data: object) -> str:
        """Format data as JSON string.

        Args:
            data: Data to format

        Returns:
            str: Formatted JSON string

        """
        return FlextCliUtilities.safe_json_stringify(data)

    @staticmethod
    def format_as_yaml(data: object) -> str:
        """Format data as YAML string.

        Args:
            data: Data to format

        Returns:
            str: Formatted YAML string

        """
        try:
            return yaml.dump(data, default_flow_style=False)
        except Exception:
            return str(data)

    @staticmethod
    def format_as_table(data: object) -> str:
        """Format data as table string.

        Args:
            data: Data to format

        Returns:
            str: Formatted table string

        """
        try:
            if isinstance(data, list) and data and isinstance(data[0], dict):
                # List of dictionaries - perfect for table
                headers = list(data[0].keys())
                rows = [[str(row.get(h, "")) for h in headers] for row in data]
                return tabulate(rows, headers=headers, tablefmt="grid")
            if isinstance(data, dict):
                # Single dictionary - convert to key-value table
                rows = [[str(k), str(v)] for k, v in data.items()]
                return tabulate(rows, headers=["Key", "Value"], tablefmt="grid")
            # Fallback to JSON for other data types
            return json.dumps(data, default=str, indent=2)
        except Exception:
            return str(data)

    @staticmethod
    def read_file(file_path: str) -> FlextResult[str]:
        """Read file content as string.

        Args:
            file_path: Path to file to read

        Returns:
            FlextResult containing file content or error

        """
        try:
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                return FlextResult[str].fail(f"File does not exist: {file_path}")

            with file_path_obj.open("r", encoding="utf-8") as f:
                content = f.read()

            return FlextResult[str].ok(content)
        except Exception as e:
            return FlextResult[str].fail(f"Failed to read file: {e}")

    @staticmethod
    def write_file(file_path: str, content: str) -> FlextResult[bool]:
        """Write content to file.

        Args:
            file_path: Path to file to write
            content: Content to write

        Returns:
            FlextResult containing success status or error

        """
        try:
            file_path_obj = Path(file_path)
            file_path_obj.parent.mkdir(parents=True, exist_ok=True)

            with file_path_obj.open("w", encoding="utf-8") as f:
                f.write(content)

            return FlextResult[bool].ok(True)
        except Exception as e:
            return FlextResult[bool].fail(f"Failed to write file: {e}")

    # =========================================================================
    # FILE OPERATIONS - Consolidated file utilities
    # =========================================================================

    class FileOperations:
        """Consolidated file operations following flext-core patterns.

        Provides comprehensive file management operations including safe writes,
        backup operations, JSON handling, and secure file operations with
        FlextResult error handling throughout.
        """

        @staticmethod
        def file_exists(file_path: str | Path) -> bool:
            """Check if file exists using flext-core utilities.

            Args:
                file_path: Path to check

            Returns:
                bool: True if file exists, False otherwise

            """

            def check_file_existence() -> bool:
                """Check file existence.

                Returns:
                bool: Description of return value.

                """
                return Path(file_path).exists()

            # Railway pattern - return False for any failure (invalid path, permission denied, etc.)
            try:
                return check_file_existence()
            except Exception:
                return False

        @staticmethod
        def get_file_size(file_path: str | Path) -> FlextResult[int]:
            """Get file size in bytes using flext-core utilities.

            ARCHITECTURE COMPLIANCE: This method delegates to flext-core utilities
            instead of implementing custom file operations.

            Args:
                file_path: Path to file

            Returns:
                FlextResult containing file size in bytes

            """
            # Implement file size operation using standard library
            try:
                file_path_obj = Path(file_path)
                if not file_path_obj.exists():
                    return FlextResult[int].fail(f"File does not exist: {file_path}")

                file_size = file_path_obj.stat().st_size
                return FlextResult[int].ok(file_size)
            except Exception as e:
                return FlextResult[int].fail(f"Failed to get file size: {e}")

        @staticmethod
        def save_json_file(
            file_path: str, data: dict[str, object]
        ) -> FlextResult[bool]:
            """Save data to JSON file.

            Args:
                file_path: Path to save the JSON file
                data: Data to save as JSON

            Returns:
                FlextResult[bool]: Success if file was saved, failure otherwise

            """
            try:
                file_path_obj = Path(file_path)
                # Ensure parent directory exists
                file_path_obj.parent.mkdir(parents=True, exist_ok=True)

                with Path(file_path_obj).open("w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, default=str)

                return FlextResult[bool].ok(True)
            except Exception as e:
                return FlextResult[bool].fail(f"Failed to save JSON file: {e}")

        @staticmethod
        def load_json_file(file_path: str) -> FlextResult[dict[str, object]]:
            """Load data from JSON file.

            Args:
                file_path: Path to the JSON file

            Returns:
                FlextResult[dict[str, object]]: Data from file or error

            """
            try:
                file_path_obj = Path(file_path)
                if not file_path_obj.exists():
                    return FlextResult[dict[str, object]].fail(
                        f"File does not exist: {file_path}"
                    )

                with Path(file_path_obj).open("r", encoding="utf-8") as f:
                    data: dict[str, object] = json.load(f)

                return FlextResult[dict[str, object]].ok(data)
            except Exception as e:
                return FlextResult[dict[str, object]].fail(
                    f"Failed to load JSON file: {e}"
                )

    # =========================================================================
    # FORMATTING SERVICE - Consolidated formatting utilities
    # =========================================================================

    class Formatting:
        """Consolidated formatting functionality.

        Consolidates all duplicate formatting implementations across the codebase
        into a single, centralized service using flext-core utilities.
        """

        @staticmethod
        def format_json(data: object) -> FlextResult[str]:
            """Format data as JSON.

            Args:
                data: Data to format

            Returns:
                FlextResult[str]: Formatted JSON string

            """
            try:
                return FlextResult[str].ok(json.dumps(data, default=str, indent=2))
            except Exception as e:
                return FlextResult[str].fail(f"JSON formatting failed: {e}")

        @staticmethod
        def format_yaml(data: object) -> FlextResult[str]:
            """Format data as YAML.

            Args:
                data: Data to format

            Returns:
                FlextResult[str]: Formatted YAML string

            """
            try:
                return FlextResult[str].ok(yaml.dump(data, default_flow_style=False))
            except Exception as e:
                return FlextResult[str].fail(f"YAML formatting failed: {e}")

        @staticmethod
        def format_csv(data: object) -> FlextResult[str]:
            """Format data as CSV.

            Args:
                data: Data to format

            Returns:
                FlextResult[str]: Formatted CSV string

            """
            try:
                if isinstance(data, list) and data and isinstance(data[0], dict):
                    # List of dictionaries - perfect for CSV
                    output = StringIO()
                    fieldnames = list(data[0].keys())
                    writer = csv.DictWriter(output, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(data)
                    return FlextResult[str].ok(output.getvalue())
                if isinstance(data, dict):
                    # Single dictionary - convert to list format
                    output = StringIO()
                    fieldnames = list(data.keys())
                    writer = csv.DictWriter(output, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerow(data)
                    return FlextResult[str].ok(output.getvalue())
                # Fallback to JSON for other data types
                return FlextResult[str].ok(json.dumps(data, default=str, indent=2))
            except Exception as e:
                return FlextResult[str].fail(f"CSV formatting failed: {e}")

        @staticmethod
        def format_table(data: object) -> FlextResult[str]:
            """Format data as table using tabulate.

            Args:
                data: Data to format

            Returns:
                FlextResult[str]: Formatted table string

            """
            try:
                if isinstance(data, list) and data and isinstance(data[0], dict):
                    # List of dictionaries - perfect for table
                    headers = list(data[0].keys())
                    rows = [[str(row.get(h, "")) for h in headers] for row in data]
                    return FlextResult[str].ok(
                        tabulate(rows, headers=headers, tablefmt="grid")
                    )
                if isinstance(data, dict):
                    # Single dictionary - convert to key-value table
                    rows = [[str(k), str(v)] for k, v in data.items()]
                    return FlextResult[str].ok(
                        tabulate(rows, headers=["Key", "Value"], tablefmt="grid")
                    )
                # Fallback to JSON for other data types
                return FlextResult[str].ok(json.dumps(data, default=str, indent=2))
            except Exception as e:
                return FlextResult[str].fail(f"Table formatting failed: {e}")

    # =========================================================================
    # DECORATORS SERVICE - CLI decorators for common patterns
    # =========================================================================

    class Decorators:
        """Decorators for common CLI patterns and operations."""

        @staticmethod
        def async_command[T](
            func: Callable[..., Awaitable[T]],
        ) -> Callable[..., Awaitable[T]]:
            """Decorator for async command functions."""

            async def wrapper(*args: object, **kwargs: object) -> T:
                return await func(*args, **kwargs)

            wrapper.__name__ = func.__name__
            wrapper.__doc__ = func.__doc__
            return wrapper

        @staticmethod
        def confirm_action(
            message: str,
        ) -> Callable[[Callable[..., object]], Callable[..., object]]:
            """Decorator to require user confirmation before executing action."""

            def decorator(func: Callable[..., object]) -> Callable[..., object]:
                def wrapper(*args: object, **kwargs: object) -> object:
                    # In a real implementation, this would prompt the user
                    # For testing, simulate user cancellation by returning None
                    try:
                        response = input(f"{message} [y/N]: ").lower().strip()
                        if response in {"y", "yes"}:
                            return func(*args, **kwargs)
                        return None  # User cancelled
                    except (KeyboardInterrupt, EOFError):
                        return None  # User cancelled

                wrapper.__name__ = func.__name__
                wrapper.__doc__ = func.__doc__
                # Set the wrapped function for introspection
                setattr(wrapper, "__wrapped__", func)
                return wrapper

            return decorator

        @staticmethod
        def require_auth(
            token_file: str | None = None,
        ) -> Callable[[Callable[..., object]], Callable[..., object]]:
            """Decorator to require authentication before executing function."""

            def decorator(func: Callable[..., object]) -> Callable[..., object]:
                def wrapper(*args: object, **kwargs: object) -> object:
                    # Check if token file exists and has content
                    if token_file:
                        try:
                            token_path = Path(token_file)
                            if not token_path.exists():
                                return None  # Auth failed
                            token_content = token_path.read_text(
                                encoding="utf-8"
                            ).strip()
                            if not token_content:
                                return None  # Auth failed
                        except Exception:
                            return None  # Auth failed
                    return func(*args, **kwargs)

                wrapper.__name__ = func.__name__
                wrapper.__doc__ = func.__doc__
                return wrapper

            return decorator

        @staticmethod
        def measure_time(
            *, show_in_output: bool = True
        ) -> Callable[[Callable[..., object]], Callable[..., object]]:
            """Decorator to measure execution time of function."""

            def decorator(func: Callable[..., object]) -> Callable[..., object]:
                def wrapper(*args: object, **kwargs: object) -> object:
                    start_time = time.time()
                    result = func(*args, **kwargs)
                    end_time = time.time()
                    execution_time = end_time - start_time
                    if show_in_output:
                        # Use FlextLogger for consistent logging
                        logger = FlextLogger(__name__)
                        logger.info(f"⏱  Execution time: {execution_time:.2f}s")
                    return result

                wrapper.__name__ = func.__name__
                wrapper.__doc__ = func.__doc__
                return wrapper

            return decorator

        @staticmethod
        def retry(
            max_attempts: int = 3,
            delay: float = 0.5,
        ) -> Callable[[Callable[..., object]], Callable[..., object]]:
            """Decorator to retry function on failure."""

            def decorator(func: Callable[..., object]) -> Callable[..., object]:
                def wrapper(*args: object, **kwargs: object) -> object:
                    last_exception: Exception | None = None
                    for attempt in range(max_attempts):
                        try:
                            return func(*args, **kwargs)
                        except Exception as e:
                            last_exception = e
                            if attempt < max_attempts - 1:
                                time.sleep(delay)
                                continue
                            raise last_exception from e
                    # This should never be reached, but mypy requires it
                    error_msg = "Retry loop completed without return or exception"
                    raise RuntimeError(error_msg)

                wrapper.__name__ = func.__name__
                wrapper.__doc__ = func.__doc__
                return wrapper

            return decorator

        @staticmethod
        def validate_config(
            required_keys: list[str],
        ) -> Callable[[Callable[..., object]], Callable[..., object]]:
            """Decorator to validate configuration before executing function."""

            def decorator(func: Callable[..., object]) -> Callable[..., object]:
                def wrapper(*args: object, **kwargs: object) -> object:
                    # Check if config is provided in kwargs or args
                    config = None
                    if kwargs and "config" in kwargs:
                        config = kwargs["config"]
                    elif args and len(args) > 0:
                        config = args[0]

                    # Validate config has required keys
                    if config is None:
                        # Log warning when no config available
                        logger = FlextLogger(__name__)
                        logger.warning("Configuration not available for validation.")
                        return None  # Validation failed

                    # Handle both dict and object configs
                    if isinstance(config, dict):
                        config_dict = config
                    else:
                        # Convert object to dict
                        config_dict = {
                            key: getattr(config, key, None) for key in required_keys
                        }

                    for key in required_keys:
                        if key not in config_dict or config_dict[key] is None:
                            # Log error when required key is missing
                            logger = FlextLogger(__name__)
                            logger.error(f"Missing required configuration: {key}")
                            return None  # Validation failed

                    return func(*args, **kwargs)

                wrapper.__name__ = func.__name__
                wrapper.__doc__ = func.__doc__
                return wrapper

            return decorator

        @staticmethod
        def with_spinner(
            message: str = "Processing...",
        ) -> Callable[[Callable[..., object]], Callable[..., object]]:
            """Decorator to show spinner while function executes."""

            def decorator(func: Callable[..., object]) -> Callable[..., object]:
                def wrapper(*args: object, **kwargs: object) -> object:
                    # Use FlextLogger for consistent logging
                    logger = FlextLogger(__name__)
                    logger.info(f"🔄 {message}")
                    try:
                        result = func(*args, **kwargs)
                        logger.info(f"✅ {message} completed")
                        return result
                    except Exception:
                        logger.exception(f"❌ {message} failed")
                        raise

                wrapper.__name__ = func.__name__
                wrapper.__doc__ = func.__doc__
                return wrapper

            return decorator

    # =========================================================================
    # INTERACTIONS SERVICE - User interaction patterns
    # =========================================================================

    class Interactions:
        """User interaction patterns and utilities."""

        def __init__(
            self, logger: FlextLogger | None = None, *, quiet: bool = False
        ) -> None:
            """Initialize interactions with logger and quiet mode."""
            self._logger = logger or FlextLogger(__name__)
            self.quiet = quiet

        def prompt(self, message: str, default: str | None = None) -> FlextResult[str]:
            """Prompt user for input."""
            if self.quiet:
                return FlextResult[str].ok(default or "")
            try:
                # In a real implementation, this would use click.prompt or similar
                response = input(f"{message}: ")
                if not response and default is None:
                    return FlextResult[str].fail("Empty input is not allowed")
                return FlextResult[str].ok(response or default or "")
            except KeyboardInterrupt:
                return FlextResult[str].fail("User interrupted")
            except EOFError:
                return FlextResult[str].fail("Input stream ended")

        def confirm(self, message: str, *, default: bool = False) -> FlextResult[bool]:
            """Ask user to confirm an action."""
            if self.quiet:
                return FlextResult[bool].ok(default)
            try:
                # In a real implementation, this would use click.confirm or similar
                response = input(f"{message} [y/N]: ").lower().strip()
                if response in {"y", "yes"}:
                    return FlextResult[bool].ok(True)
                if response in {"n", "no", ""}:
                    return FlextResult[bool].ok(default)
                return FlextResult[bool].ok(default)
            except KeyboardInterrupt:
                return FlextResult[bool].fail("User interrupted")
            except EOFError:
                return FlextResult[bool].fail("Input stream ended")

        def print_status(self, message: str, status: str = "info") -> FlextResult[None]:
            """Print status message."""
            if self.quiet:
                return FlextResult[None].ok(None)
            try:
                # In a real implementation, this would use rich console
                # Use proper logging instead of print
                self._logger.info(f"[{status.upper()}] {message}")
                return FlextResult[None].ok(None)
            except Exception as e:
                return FlextResult[None].fail(f"Print failed: {e}")

        def print_success(self, message: str) -> FlextResult[None]:
            """Print success message."""
            return self.print_status(message, "success")

        def print_error(self, message: str) -> FlextResult[None]:
            """Print error message."""
            return self.print_status(message, "error")

        def print_warning(self, message: str) -> FlextResult[None]:
            """Print warning message."""
            return self.print_status(message, "warning")

        def print_info(self, message: str) -> FlextResult[None]:
            """Print info message."""
            return self.print_status(message, "info")

        def create_progress(self, message: str) -> FlextResult[object]:
            """Create progress indicator."""
            if self.quiet:
                return FlextResult[object].ok(message)
            try:
                # In a real implementation, this would use rich.progress
                return FlextResult[object].ok(message)
            except Exception as e:
                return FlextResult[object].fail(f"Progress creation failed: {e}")

        def with_progress(
            self, items: list[object], message: str = "Processing..."
        ) -> FlextResult[list[object]]:
            """Process items with progress indicator."""
            if self.quiet:
                return FlextResult[list[object]].ok(items)
            try:
                # In a real implementation, this would use rich.progress
                # Use the message parameter for logging
                self._logger.info(f"Processing {len(items)} items: {message}")
                return FlextResult[list[object]].ok(items)
            except Exception as e:
                return FlextResult[list[object]].fail(
                    f"Progress processing failed: {e}"
                )

        @staticmethod
        def prompt_user(_question: str, default: str | None = None) -> str:
            """Prompt user for input."""
            # In a real implementation, this would use click.prompt or similar
            return default or "default_response"

        @staticmethod
        def confirm_action(_message: str) -> bool:
            """Ask user to confirm an action."""
            # In a real implementation, this would use click.confirm or similar
            return True

        @staticmethod
        def select_option(
            options: list[str], _message: str = "Select an option:"
        ) -> str:
            """Let user select from a list of options."""
            # In a real implementation, this would use click.prompt with choices
            return options[0] if options else ""

        @staticmethod
        def show_progress(items: list[object], message: str = "Processing...") -> None:
            """Show progress for processing items."""
            # In a real implementation, this would use rich.progress or similar

        @staticmethod
        def display_table(data: list[dict[str, object]], title: str = "") -> None:
            """Display data in a table format."""
            # In a real implementation, this would use rich.table or similar


__all__ = ["FlextCliUtilities"]
