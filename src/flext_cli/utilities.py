"""FLEXT CLI Utilities - Unified class following FLEXT architecture patterns.

Single FlextCliUtilities class consolidating all utility functions and validation helpers.
Follows FLEXT unified class pattern - one class per module extending flext-core.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import csv
import hashlib
import ipaddress
import json
import math
import re
import secrets
import string
import time
import uuid
from collections.abc import Awaitable, Callable, Sequence
from datetime import UTC, datetime
from io import StringIO
from pathlib import Path
from typing import cast, override
from urllib.parse import urlparse

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

    @override
    def __init__(self) -> None:
        """Initialize FlextCliUtilities service."""
        super().__init__()
        self._container = FlextContainer.get_global()
        self._logger = FlextLogger(__name__)

    @override
    def execute(self) -> FlextResult[dict[str, object]]:
        """Execute the main domain service operation.

        Returns:
            FlextResult[dict[str, object]]: Service status and capabilities.

        """
        return FlextResult[dict[str, object]].ok({
            "status": FlextCliConstants.OPERATIONAL,
            "service": "flext-cli-utilities",
            "capabilities": [
                "validation",
                "formatting",
                "conversion",
                "parsing",
                "generation",
            ],
        })

    def parse_timestamp(self, timestamp_str: str) -> FlextResult[datetime]:
        """Parse timestamp string to datetime object."""
        try:
            # Try ISO format first
            if "T" in timestamp_str and "Z" in timestamp_str:
                dt = datetime.fromisoformat(timestamp_str)
                return FlextResult[datetime].ok(dt)

            # Try ISO format without Z
            if "T" in timestamp_str:
                dt = datetime.fromisoformat(timestamp_str)
                return FlextResult[datetime].ok(dt)

            # Try standard format with UTC timezone
            dt = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S").replace(
                tzinfo=UTC
            )
            return FlextResult[datetime].ok(dt)
        except Exception as e:
            return FlextResult[datetime].fail(f"Timestamp parsing failed: {e}")

    def extract_numbers_from_string(self, text: str) -> FlextResult[list[float]]:
        """Extract all numbers from a string."""
        try:
            # Find all numbers including decimals
            pattern = r"-?\d+\.?\d*"
            matches = re.findall(pattern, text)
            numbers = [float(match) for match in matches if match]
            return FlextResult[list[float]].ok(numbers)
        except Exception as e:
            return FlextResult[list[float]].fail(f"Failed to extract numbers: {e}")

    def add_time_to_timestamp(
        self, timestamp: float, seconds: int = 0
    ) -> FlextResult[str]:
        """Add time to timestamp and return as string."""
        try:
            new_timestamp = timestamp + seconds
            # Convert to ISO format string
            dt = datetime.fromtimestamp(new_timestamp, tz=UTC)
            iso_string = dt.isoformat()
            return FlextResult[str].ok(iso_string)
        except Exception as e:
            return FlextResult[str].fail(f"Failed to add time to timestamp: {e}")

    def extract_domain_from_url(self, url: str) -> FlextResult[str]:
        """Extract domain from URL."""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc
            if not domain:
                return FlextResult[str].fail("No domain found in URL")

            # Remove port if present
            if ":" in domain:
                domain = domain.split(":")[0]

            return FlextResult[str].ok(domain)
        except Exception as e:
            return FlextResult[str].fail(f"Failed to extract domain: {e}")

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
                validated_data = data
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
    def validate_data(
        data: dict[str, str | int | float] | None,
        validator: Callable[[dict[str, str | int | float] | None], bool] | None,
    ) -> FlextResult[bool]:
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
        items: Sequence[dict[str, str | int | float] | None],
        processor: Callable[
            [dict[str, str | int | float] | None], dict[str, str | int | float] | None
        ]
        | FlextResult[dict[str, str | int | float] | None],
        batch_size: int = 10,
        *,
        fail_fast: bool = True,
    ) -> FlextResult[list[dict[str, str | int | float] | None]]:
        """Process items in batches using railway composition patterns.

        Args:
            items: Items to process
            processor: Function to process each item
            batch_size: Number of items per batch
            fail_fast: Whether to stop on first failure

        Returns:
            FlextResult with all processed items or first error

        """
        try:
            results: list[dict[str, str | int | float] | None] = []

            # Process items in batches using railway pattern
            for i in range(0, len(items), batch_size):
                batch = items[i : i + batch_size]

                for item in batch:
                    if callable(processor):
                        result = processor(item)
                        if hasattr(result, "is_failure") and getattr(
                            result, "is_failure", False
                        ):
                            if fail_fast:
                                return FlextResult[
                                    list[dict[str, str | int | float] | None]
                                ].fail(
                                    getattr(result, "error", "Batch processing failed")
                                    or "Batch processing failed"
                                )
                            continue
                        processed_item = (
                            result
                            if not hasattr(result, "value")
                            else getattr(result, "value", result)
                        )
                    else:
                        # processor is a FlextResult
                        result = processor
                        if result.is_failure:
                            if fail_fast:
                                return FlextResult[
                                    list[dict[str, str | int | float] | None]
                                ].fail(
                                    getattr(result, "error", "Batch processing failed")
                                    or "Batch processing failed"
                                )
                            continue
                        processed_item = getattr(result, "value", result)

                    results.append(processed_item)

            return FlextResult[list[dict[str, str | int | float] | None]].ok(results)

        except Exception as e:
            return FlextResult[list[dict[str, str | int | float] | None]].fail(
                f"Batch processing failed: {e}"
            )

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

        @override
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

    # String utility methods
    def slugify_string(self, text: str) -> FlextResult[str]:
        """Convert string to URL-friendly slug."""
        try:
            # Convert to lowercase and replace spaces with hyphens
            slug = re.sub(r"[^a-zA-Z0-9\s-]", "", text.lower())
            slug = re.sub(r"\s+", "-", slug.strip())
            return FlextResult[str].ok(slug)
        except Exception as e:
            return FlextResult[str].fail(f"Slugify failed: {e}")

    def camel_case_to_snake_case(self, text: str) -> FlextResult[str]:
        """Convert camelCase to snake_case."""
        try:
            # Insert underscore before uppercase letters that follow lowercase letters or digits
            snake = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", text)
            return FlextResult[str].ok(snake.lower())
        except Exception as e:
            return FlextResult[str].fail(f"Case conversion failed: {e}")

    def snake_case_to_camel_case(self, text: str) -> FlextResult[str]:
        """Convert snake_case to camelCase."""
        try:
            components = text.split("_")
            if not components:
                return FlextResult[str].ok("")
            camel = components[0].lower() + "".join(
                word.capitalize() for word in components[1:]
            )
            return FlextResult[str].ok(camel)
        except Exception as e:
            return FlextResult[str].fail(f"Case conversion failed: {e}")

    def truncate_string(
        self, text: str, max_length: int, suffix: str = "..."
    ) -> FlextResult[str]:
        """Truncate string to specified length with suffix."""
        try:
            if len(text) <= max_length:
                return FlextResult[str].ok(text)
            truncated = text[: max_length - len(suffix)] + suffix
            return FlextResult[str].ok(truncated)
        except Exception as e:
            return FlextResult[str].fail(f"Truncation failed: {e}")

    def remove_special_characters(self, text: str) -> FlextResult[str]:
        """Remove special characters from string."""
        try:
            cleaned = re.sub(r"[^a-zA-Z0-9\s]", "", text)
            return FlextResult[str].ok(cleaned)
        except Exception as e:
            return FlextResult[str].fail(f"Character removal failed: {e}")

    def validate_email(self, email: str) -> FlextResult[bool]:
        """Validate email address format."""
        try:
            if not email or not isinstance(email, str):
                return FlextResult[bool].ok(False)

            # Check for consecutive dots
            if ".." in email:
                return FlextResult[bool].ok(False)

            pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
            is_valid = bool(re.match(pattern, email))
            return FlextResult[bool].ok(is_valid)
        except Exception as e:
            return FlextResult[bool].fail(f"Email validation failed: {e}")

    def validate_url(self, url: str) -> FlextResult[bool]:
        """Validate URL format."""
        try:
            pattern = r"^https?://[^\s/$.?#].[^\s]*$"
            is_valid = bool(re.match(pattern, url))
            return FlextResult[bool].ok(is_valid)
        except Exception as e:
            return FlextResult[bool].fail(f"URL validation failed: {e}")

    def validate_phone_number(self, phone: str) -> FlextResult[bool]:
        """Validate phone number format."""
        try:
            if not phone or not isinstance(phone, str):
                return FlextResult[bool].ok(False)

            # Remove all non-digit characters except + at the beginning
            cleaned = re.sub(r"[^\d+]", "", phone)

            # Check if it starts with + and has 10-15 digits
            if cleaned.startswith("+"):
                digits = cleaned[1:]
                if (
                    len(digits)
                    >= FlextCliConstants.PhoneValidation.MIN_INTERNATIONAL_DIGITS
                    and len(digits)
                    <= FlextCliConstants.PhoneValidation.MAX_INTERNATIONAL_DIGITS
                ):
                    return FlextResult[bool].ok(True)

            # Check if it has exactly 10 digits (US format)
            if (
                len(cleaned) == FlextCliConstants.PhoneValidation.US_PHONE_DIGITS
                and cleaned.isdigit()
            ):
                return FlextResult[bool].ok(True)

            return FlextResult[bool].ok(False)
        except Exception as e:
            return FlextResult[bool].fail(f"Phone validation failed: {e}")

    def validate_ip_address(self, ip: str) -> FlextResult[bool]:
        """Validate IP address format."""
        try:
            ipaddress.ip_address(ip)
            return FlextResult[bool].ok(True)
        except ValueError:
            return FlextResult[bool].ok(False)
        except Exception as e:
            return FlextResult[bool].fail(f"IP validation failed: {e}")

    def is_valid_ipv4(self, ip: str) -> FlextResult[bool]:
        """Validate IPv4 address."""
        try:
            ipaddress.IPv4Address(ip)
            return FlextResult[bool].ok(True)
        except ValueError:
            return FlextResult[bool].ok(False)
        except Exception as e:
            return FlextResult[bool].fail(f"IPv4 validation failed: {e}")

    def is_valid_ipv6(self, ip: str) -> FlextResult[bool]:
        """Validate IPv6 address."""
        try:
            ipaddress.IPv6Address(ip)
            return FlextResult[bool].ok(True)
        except ValueError:
            return FlextResult[bool].ok(False)
        except Exception as e:
            return FlextResult[bool].fail(f"IPv6 validation failed: {e}")

    def format_timestamp(
        self, timestamp: float, format_str: str = "%Y-%m-%dT%H:%M:%SZ"
    ) -> FlextResult[str]:
        """Format timestamp to string."""
        try:
            # Use UTC time instead of local time
            formatted = time.strftime(format_str, time.gmtime(timestamp))
            return FlextResult[str].ok(formatted)
        except Exception as e:
            return FlextResult[str].fail(f"Timestamp formatting failed: {e}")

    def parse_timestamp_to_float(
        self, timestamp_str: str, format_str: str = "%Y-%m-%d %H:%M:%S"
    ) -> FlextResult[float]:
        """Parse timestamp string to float."""
        try:
            parsed = time.mktime(time.strptime(timestamp_str, format_str))
            return FlextResult[float].ok(parsed)
        except Exception as e:
            return FlextResult[float].fail(f"Timestamp parsing failed: {e}")

    def get_timestamp_difference(
        self, timestamp1: float, timestamp2: float
    ) -> FlextResult[float]:
        """Get difference between two timestamps."""
        try:
            difference = abs(timestamp1 - timestamp2)
            return FlextResult[float].ok(difference)
        except Exception as e:
            return FlextResult[float].fail(
                f"Timestamp difference calculation failed: {e}"
            )

    def convert_bytes_to_human_readable(self, bytes_value: float) -> FlextResult[str]:
        """Convert bytes to human readable format."""
        try:
            bytes_per_unit = 1024.0
            for unit in ["B", "KB", "MB", "GB", "TB"]:
                if bytes_value < bytes_per_unit:
                    return FlextResult[str].ok(f"{bytes_value:.1f} {unit}")
                bytes_value /= bytes_per_unit
            return FlextResult[str].ok(f"{bytes_value:.1f} PB")
        except Exception as e:
            return FlextResult[str].fail(f"Bytes conversion failed: {e}")

    def convert_human_readable_to_bytes(self, human_readable: str) -> FlextResult[int]:
        """Convert human readable format to bytes."""
        try:
            units = {"B": 1, "KB": 1024, "MB": 1024**2, "GB": 1024**3, "TB": 1024**4}
            match = re.match(r"(\d+(?:\.\d+)?)\s*([A-Z]+)", human_readable.upper())
            if not match:
                return FlextResult[int].fail("Invalid format")

            value, unit = match.groups()
            if unit not in units:
                return FlextResult[int].fail("Invalid unit")

            bytes_value = int(float(value) * units[unit])
            return FlextResult[int].ok(bytes_value)
        except Exception as e:
            return FlextResult[int].fail(f"Human readable conversion failed: {e}")

    def hash_string(self, text: str, algorithm: str = "sha256") -> FlextResult[str]:
        """Hash string using specified algorithm."""
        try:
            if algorithm.lower() == "sha256":
                hash_obj = hashlib.sha256()
            elif algorithm.lower() == "sha512":
                hash_obj = hashlib.sha512()
            else:
                return FlextResult[str].fail(
                    f"Unsupported algorithm: {algorithm}. Only SHA256 and SHA512 are supported for security reasons."
                )

            hash_obj.update(text.encode("utf-8"))
            return FlextResult[str].ok(hash_obj.hexdigest())
        except Exception as e:
            return FlextResult[str].fail(f"Hash calculation failed: {e}")

    def normalize_path(self, path: str) -> FlextResult[str]:
        """Normalize file path."""
        try:
            normalized = Path(path).resolve()
            return FlextResult[str].ok(str(normalized))
        except Exception as e:
            return FlextResult[str].fail(f"Path normalization failed: {e}")

    def get_file_extension(self, filename: str) -> FlextResult[str]:
        """Get file extension."""
        try:
            extension = Path(filename).suffix.lstrip(".")
            return FlextResult[str].ok(extension)
        except Exception as e:
            return FlextResult[str].fail(f"Extension extraction failed: {e}")

    def get_file_name_without_extension(self, filename: str) -> FlextResult[str]:
        """Get filename without extension."""
        try:
            name = Path(filename).stem
            return FlextResult[str].ok(name)
        except Exception as e:
            return FlextResult[str].fail(f"Name extraction failed: {e}")

    def generate_uuid(self) -> FlextResult[str]:
        """Generate UUID string."""
        try:
            return FlextResult[str].ok(str(uuid.uuid4()))
        except Exception as e:
            return FlextResult[str].fail(f"UUID generation failed: {e}")

    def generate_random_string(self, length: int = 10) -> FlextResult[str]:
        """Generate random string."""
        try:
            chars = string.ascii_letters + string.digits
            random_str = "".join(secrets.choice(chars) for _ in range(length))
            return FlextResult[str].ok(random_str)
        except Exception as e:
            return FlextResult[str].fail(f"Random string generation failed: {e}")

    def encrypt_string(self, text: str, key: str = "default") -> FlextResult[str]:
        """Encrypt string (simple implementation)."""
        try:
            # Simple XOR encryption for demonstration
            encrypted = "".join(
                chr(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(text)
            )
            return FlextResult[str].ok(encrypted)
        except Exception as e:
            return FlextResult[str].fail(f"Encryption failed: {e}")

    def decrypt_string(
        self, encrypted_text: str, key: str = "default"
    ) -> FlextResult[str]:
        """Decrypt string (simple implementation)."""
        try:
            # Simple XOR decryption for demonstration
            decrypted = "".join(
                chr(ord(c) ^ ord(key[i % len(key)]))
                for i, c in enumerate(encrypted_text)
            )
            return FlextResult[str].ok(decrypted)
        except Exception as e:
            return FlextResult[str].fail(f"Decryption failed: {e}")

    def convert_temperature(
        self, value: float, from_unit: str, to_unit: str
    ) -> FlextResult[float]:
        """Convert temperature between units."""
        try:
            from_unit = from_unit.lower()
            to_unit = to_unit.lower()

            # Convert to Celsius first
            if from_unit in {"f", "fahrenheit"}:
                celsius = (value - 32) * 5 / 9
            elif from_unit in {"k", "kelvin"}:
                celsius = value - 273.15
            elif from_unit in {"c", "celsius"}:
                celsius = value
            else:
                return FlextResult[float].fail(f"Unsupported from_unit: {from_unit}")

            # Convert from Celsius to target unit
            if to_unit in {"f", "fahrenheit"}:
                result = celsius * 9 / 5 + 32
            elif to_unit in {"k", "kelvin"}:
                result = celsius + 273.15
            elif to_unit in {"c", "celsius"}:
                result = celsius
            else:
                return FlextResult[float].fail(f"Unsupported to_unit: {to_unit}")

            return FlextResult[float].ok(result)
        except Exception as e:
            return FlextResult[float].fail(f"Temperature conversion failed: {e}")

    def convert_currency(
        self, amount: float, from_currency: str, to_currency: str
    ) -> FlextResult[float]:
        """Convert currency (mock implementation)."""
        try:
            # Mock conversion rates
            rates = {"USD": 1.0, "EUR": 0.85, "GBP": 0.73, "JPY": 110.0}
            usd_amount = amount / rates.get(from_currency.upper(), 1.0)
            result = usd_amount * rates.get(to_currency.upper(), 1.0)
            return FlextResult[float].ok(result)
        except Exception as e:
            return FlextResult[float].fail(f"Currency conversion failed: {e}")

    def calculate_distance(
        self, lat1: float, lon1: float, lat2: float, lon2: float
    ) -> FlextResult[float]:
        """Calculate distance between two coordinates (Haversine formula)."""
        try:
            earth_radius_km = 6371  # Earth's radius in kilometers

            dlat = math.radians(lat2 - lat1)
            dlon = math.radians(lon2 - lon1)

            a = math.sin(dlat / 2) * math.sin(dlat / 2) + math.cos(
                math.radians(lat1)
            ) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) * math.sin(dlon / 2)

            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
            distance = earth_radius_km * c

            return FlextResult[float].ok(distance)
        except Exception as e:
            return FlextResult[float].fail(f"Distance calculation failed: {e}")

    def calculate_percentage(self, value: float, total: float) -> FlextResult[float]:
        """Calculate percentage."""
        try:
            if total == 0:
                return FlextResult[float].fail(
                    "Cannot calculate percentage with zero total"
                )
            percentage = (value / total) * 100
            return FlextResult[float].ok(percentage)
        except Exception as e:
            return FlextResult[float].fail(f"Percentage calculation failed: {e}")

    def round_to_decimal_places(
        self, value: float, places: int = 2
    ) -> FlextResult[float]:
        """Round number to specified decimal places."""
        try:
            rounded = round(value, places)
            return FlextResult[float].ok(rounded)
        except Exception as e:
            return FlextResult[float].fail(f"Rounding failed: {e}")

    def join_paths(self, *paths: str) -> FlextResult[str]:
        """Join multiple path components."""
        try:
            joined = Path(*paths)
            return FlextResult[str].ok(str(joined))
        except Exception as e:
            return FlextResult[str].fail(f"Path joining failed: {e}")

    async def execute_async(self) -> FlextResult[dict[str, object]]:
        """Execute utilities service operation asynchronously."""
        return FlextResult[dict[str, object]].ok({
            "status": "operational",
            "service": "flext-cli-utilities",
            "timestamp": datetime.now(UTC).isoformat(),
            "version": "2.0.0",
        })


__all__ = ["FlextCliUtilities"]
