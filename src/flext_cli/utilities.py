"""FLEXT CLI Utilities - Reusable helpers and utilities for CLI operations.

Provides CLI-specific utility functions building on flext-core FlextUtilities,
eliminating code duplication across modules following SOLID and DRY principles.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

import os
import sys
import types
from datetime import UTC, datetime
from pathlib import Path
from typing import Final, Union, get_args, get_origin

from flext_core import FlextResult, FlextTypes, FlextUtilities

from flext_cli.constants import FlextCliConstants


class FlextCliUtilities:
    """FLEXT CLI Utilities - Centralized helpers eliminating code duplication.

    **PURPOSE**: Single source of truth for CLI utility operations.
    Builds on FlextUtilities from flext-core and adds CLI-specific helpers.

    **ARCHITECTURE LAYER**: Application Layer (Layer 3)
    - Extends flext-core FlextUtilities with CLI-specific functionality
    - Pure static methods (no state) for thread safety
    - FlextResult[T] railway pattern for all fallible operations

    **ZERO DUPLICATION**: All common helpers consolidated here:
    - Field validation (eliminate duplicates in models.py)
    - Type normalization for Typer compatibility (from type_utils.py)
    - Common patterns used across multiple modules

    **CORE NAMESPACES**:
    1. **CliValidation**: CLI-specific field and business rule validation
    2. **TypeNormalizer**: Type annotation normalization for Typer
    3. **Base Utilities**: Access to all FlextUtilities functionality

    **DESIGN PATTERNS**:
    - DRY: Single source for all common operations
    - SOLID: Single responsibility per namespace
    - Railway Pattern: All operations return FlextResult[T]
    - Static Methods: Thread-safe, no state

    """

    # =========================================================================
    # BASE UTILITIES - Delegate to flext-core FlextUtilities
    # =========================================================================

    # Expose all FlextUtilities namespaces for convenience
    Cache: Final = FlextUtilities.Cache
    Validation: Final = FlextUtilities.Validation
    TypeGuards: Final = FlextUtilities.TypeGuards
    Generators: Final = FlextUtilities.Generators
    TextProcessor: Final = FlextUtilities.TextProcessor
    Reliability: Final = FlextUtilities.Reliability
    TypeChecker: Final = FlextUtilities.TypeChecker
    Configuration: Final = FlextUtilities.Configuration
    StringParser: Final = FlextUtilities.StringParser
    DataMapper: Final = FlextUtilities.DataMapper

    # =========================================================================
    # CLI VALIDATION - CLI-specific validation helpers
    # =========================================================================

    class CliValidation:
        """CLI-specific validation operations.

        Eliminates code duplication in models.py validate_business_rules methods.
        All validators return FlextResult[None] for railway pattern composition.

        """

        @staticmethod
        def validate_field_not_empty(
            field_value: object,
            field_display_name: str,
        ) -> FlextResult[None]:
            """Validate that a field is not empty.

            Generic helper eliminating code duplication in validate_business_rules.

            Args:
                field_value: Value to validate
                field_display_name: Display name for error messages

            Returns:
                FlextResult[None]: Success if not empty, failure with error message

            Example:
                >>> result = FlextCliUtilities.CliValidation.validate_field_not_empty(
                ...     command_line, "Command line"
                ... )
                >>> if result.is_failure:
                ...     print(result.error)

            """
            if not field_value or not str(field_value).strip():
                return FlextResult[None].fail(
                    FlextCliConstants.MixinsValidationMessages.FIELD_CANNOT_BE_EMPTY.format(
                        field_name=field_display_name
                    )
                )
            return FlextResult[None].ok(None)

        @staticmethod
        def validate_field_in_list(
            field_value: object,
            valid_values: list[str],
            field_name: str,
        ) -> FlextResult[None]:
            """Validate that a field value is in a list of valid values.

            Generic helper eliminating code duplication in validate_business_rules.

            Args:
                field_value: Value to validate
                valid_values: List of valid values
                field_name: Field name for error messages

            Returns:
                FlextResult[None]: Success if in list, failure with error message

            Example:
                >>> result = FlextCliUtilities.CliValidation.validate_field_in_list(
                ...     status, ["pending", "running", "completed"], "status"
                ... )
                >>> if result.is_failure:
                ...     print(result.error)

            """
            if field_value not in valid_values:
                return FlextResult[None].fail(
                    FlextCliConstants.MixinsValidationMessages.INVALID_ENUM_VALUE.format(
                        field_name=field_name,
                        valid_values=valid_values,
                    )
                )
            return FlextResult[None].ok(None)

        @staticmethod
        def validate_command_status(status: str) -> FlextResult[None]:
            """Validate command status against known valid statuses.

            Args:
                status: Command status to validate

            Returns:
                FlextResult[None]: Success if valid, failure otherwise

            """
            return FlextCliUtilities.CliValidation.validate_field_in_list(
                status,
                FlextCliConstants.COMMAND_STATUSES_LIST,
                "status",
            )

        @staticmethod
        def validate_debug_level(level: str) -> FlextResult[None]:
            """Validate debug level against known valid levels.

            Args:
                level: Debug level to validate

            Returns:
                FlextResult[None]: Success if valid, failure otherwise

            """
            return FlextCliUtilities.CliValidation.validate_field_in_list(
                level,
                FlextCliConstants.DEBUG_LEVELS_LIST,
                "level",
            )

        @staticmethod
        def validate_output_format(format_type: str) -> FlextResult[str]:
            """Validate and normalize output format type.

            Validates format against list of supported output formats and
            returns normalized lowercase format string.

            Args:
                format_type: Output format to validate (json, yaml, table, csv, plain)

            Returns:
                FlextResult[str]: Normalized lowercase format if valid, error otherwise

            Example:
                >>> result = FlextCliUtilities.CliValidation.validate_output_format("JSON")
                >>> if result.is_success:
                ...     format = result.unwrap()  # "json"

            """
            format_lower = format_type.lower()
            if format_lower not in FlextCliConstants.OUTPUT_FORMATS_LIST:
                return FlextResult[str].fail(
                    FlextCliConstants.ErrorMessages.UNSUPPORTED_FORMAT_TYPE.format(
                        format_type=format_type
                    )
                )
            return FlextResult[str].ok(format_lower)

        @staticmethod
        def validate_string_not_empty(
            value: object, error_message: str
        ) -> FlextResult[None]:
            """Validate that a value is a non-empty string.

            Consolidates repeated pattern: if not X or not isinstance(X, str)
            Found 6 times in context.py.

            Args:
                value: Value to validate
                error_message: Error message to return on failure

            Returns:
                FlextResult[None]: Success if non-empty string, failure otherwise

            Example:
                >>> result = FlextCliUtilities.CliValidation.validate_string_not_empty(
                ...     name, "Name must be a string"
                ... )
                >>> if result.is_failure:
                ...     return result

            """
            if not value or not isinstance(value, str):
                return FlextResult[None].fail(error_message)
            return FlextResult[None].ok(None)

    # =========================================================================
    # ENVIRONMENT - Environment detection and checks
    # =========================================================================

    class Environment:
        """Environment detection and runtime checks.

        Provides utilities for detecting execution environment (test, CI, etc).
        All methods are static for stateless operation.

        """

        @staticmethod
        def is_test_environment() -> bool:
            """Check if running in a test environment.

            Detects test environment by checking:
            - PYTEST_CURRENT_TEST environment variable
            - "pytest" in _ environment variable (pytest runner)
            - CI environment variable (CI/CD pipelines)

            Returns:
                bool: True if in test environment, False otherwise

            Example:
                >>> if FlextCliUtilities.Environment.is_test_environment():
                ...     # Skip interactive prompts in tests
                ...     pass

            """
            return (
                os.environ.get(FlextCliConstants.EnvironmentConstants.PYTEST_CURRENT_TEST)
                is not None
                or FlextCliConstants.EnvironmentConstants.PYTEST
                in os.environ.get(
                    FlextCliConstants.EnvironmentConstants.UNDERSCORE, ""
                ).lower()
                or os.environ.get(FlextCliConstants.EnvironmentConstants.CI)
                == FlextCliConstants.EnvironmentConstants.CI_TRUE_VALUE
            )

    # =========================================================================
    # CONFIG OPS - Configuration operations
    # =========================================================================

    class ConfigOps:
        """Configuration operations and path management.

        Provides utilities for configuration directory management,
        validation, and information retrieval.

        """

        @staticmethod
        def get_config_paths() -> list[str]:
            """Get standard FLEXT CLI configuration paths.

            Returns all standard configuration directory paths including:
            - Main FLEXT directory (~/.flext)
            - Config subdirectory
            - Cache subdirectory
            - Logs subdirectory
            - Token directories

            Returns:
                list[str]: List of configuration path strings

            Example:
                >>> paths = FlextCliUtilities.ConfigOps.get_config_paths()
                >>> for path in paths:
                ...     print(path)

            """
            home = Path.home()
            flext_dir = home / FlextCliConstants.FLEXT_DIR_NAME

            return [
                str(flext_dir),
                str(flext_dir / FlextCliConstants.DictKeys.CONFIG),
                str(flext_dir / FlextCliConstants.Subdirectories.CACHE),
                str(flext_dir / FlextCliConstants.Subdirectories.LOGS),
                str(flext_dir / FlextCliConstants.DictKeys.TOKEN),
                str(flext_dir / FlextCliConstants.Subdirectories.REFRESH_TOKEN),
            ]

        @staticmethod
        def validate_config_structure() -> list[str]:
            """Validate FLEXT CLI configuration directory structure.

            Checks existence of main config directory and all standard subdirectories.
            Returns human-readable validation results with success/failure marks.

            Returns:
                list[str]: Validation results with ✓/✗ marks for each check

            Example:
                >>> results = FlextCliUtilities.ConfigOps.validate_config_structure()
                >>> for result in results:
                ...     print(result)
                ✓ Configuration directory exists
                ✓ config/ subdirectory exists
                ...

            """
            results: list[str] = []
            home = Path.home()
            flext_dir = home / FlextCliConstants.FLEXT_DIR_NAME

            # Check main config directory
            if flext_dir.exists():
                results.append(
                    FlextCliConstants.Symbols.SUCCESS_MARK
                    + FlextCliConstants.CmdMessages.CONFIG_DIR_EXISTS
                )
            else:
                results.append(
                    FlextCliConstants.Symbols.FAILURE_MARK
                    + FlextCliConstants.CmdMessages.CONFIG_DIR_MISSING
                )

            # Check subdirectories using constants
            for subdir in FlextCliConstants.Subdirectories.STANDARD_SUBDIRS:
                path = flext_dir / subdir
                if path.exists():
                    results.append(
                        FlextCliConstants.CmdMessages.SUBDIR_EXISTS.format(
                            symbol=FlextCliConstants.Symbols.SUCCESS_MARK, subdir=subdir
                        )
                    )
                else:
                    results.append(
                        FlextCliConstants.CmdMessages.SUBDIR_MISSING.format(
                            symbol=FlextCliConstants.Symbols.FAILURE_MARK, subdir=subdir
                        )
                    )

            return results

        @staticmethod
        def get_config_info() -> FlextTypes.JsonDict:
            """Get FLEXT CLI configuration information.

            Returns comprehensive configuration information including:
            - Configuration directory path
            - Existence status
            - Read/write permissions
            - Current timestamp

            Returns:
                FlextTypes.JsonDict: Configuration information dictionary

            Example:
                >>> info = FlextCliUtilities.ConfigOps.get_config_info()
                >>> print(f"Config dir: {info['config_dir']}")
                >>> print(f"Exists: {info['exists']}")

            """
            home = Path.home()
            flext_dir = home / FlextCliConstants.FLEXT_DIR_NAME

            return {
                FlextCliConstants.DictKeys.CONFIG_DIR: str(flext_dir),
                FlextCliConstants.DictKeys.CONFIG_EXISTS: flext_dir.exists(),
                FlextCliConstants.DictKeys.CONFIG_READABLE: flext_dir.exists()
                and os.access(flext_dir, os.R_OK),
                FlextCliConstants.DictKeys.CONFIG_WRITABLE: flext_dir.exists()
                and os.access(flext_dir, os.W_OK),
                FlextCliConstants.DictKeys.TIMESTAMP: datetime.now(UTC).isoformat(),
            }

    # =========================================================================
    # FILE OPS - File operation helpers
    # =========================================================================

    class FileOps:
        """File operation helpers for error detection and common patterns.

        Provides utilities for file-related operations including error detection
        and pattern matching. All methods are static for stateless operation.

        """

        @staticmethod
        def is_file_not_found_error(error_msg: str) -> bool:
            """Check if an error message indicates a file-not-found error.

            Detects file-not-found errors by checking for common patterns in
            error messages across different operating systems and error types.

            Patterns checked:
            - "not found" (common general pattern)
            - "no such file" (Unix/Linux errno 2)
            - "does not exist" (Windows and Python FileNotFoundError)
            - "errno 2" (explicit errno check)

            Args:
                error_msg: Error message string to check

            Returns:
                bool: True if error message indicates file not found, False otherwise

            Example:
                >>> result = file_tools.read_json_file("missing.json")
                >>> if result.is_failure:
                ...     if FlextCliUtilities.FileOps.is_file_not_found_error(result.error):
                ...         print("File does not exist")
                ...     else:
                ...         print(f"Other error: {result.error}")

            """
            error_lower = error_msg.lower()
            return any(
                pattern in error_lower
                for pattern in [
                    "not found",
                    "no such file",
                    "does not exist",
                    "errno 2",
                ]
            )

    # =========================================================================
    # TYPE NORMALIZER - Typer compatibility (from type_utils.py)
    # =========================================================================

    class TypeNormalizer:
        """Type annotation normalization for Typer compatibility.

        Converts modern Python 3.10+ union syntax to Typer-compatible forms.
        Eliminates all code from type_utils.py by consolidating here.

        **PURPOSE**: Typer does not support modern union syntax (Path | None).
        This normalizes annotations to Union/Optional forms transparently.

        """

        @staticmethod
        def normalize_annotation(
            annotation: type | types.UnionType | None,
        ) -> type | types.UnionType | None:
            """Normalize type annotations for Typer compatibility.

            Converts modern Python 3.10+ union syntax (Path | None) to typing-compatible
            forms (Optional[Path] or Union[...]) that Typer can process.

            Handles:
            - Modern union syntax: Path | None → Optional[Path]
            - Complex unions: str | int | None → Union[str, int, None]
            - Nested generics: list[str] | None → Optional[list[str]]
            - Already-normalized types: Optional[Path] → unchanged
            - Non-union types: str → unchanged

            Args:
                annotation: Type annotation to normalize

            Returns:
                Normalized annotation compatible with Typer

            Example:
                >>> from pathlib import Path
                >>> normalized = FlextCliUtilities.TypeNormalizer.normalize_annotation(
                ...     Path | None
                ... )
                >>> # Result: Optional[Path] (Typer-compatible)

            """
            if annotation is None:
                return annotation

            # Check if this is a modern union type (Python 3.10+: X | Y syntax)
            origin = get_origin(annotation)

            # Python 3.10+ union type using | operator
            if sys.version_info >= (3, 10) and origin is types.UnionType:
                return FlextCliUtilities.TypeNormalizer.normalize_union_type(
                    annotation
                )

            # typing.Union type (traditional typing.Union[X, Y])
            try:
                if origin is Union:
                    return FlextCliUtilities.TypeNormalizer.normalize_union_type(
                        annotation
                    )
            except (ImportError, AttributeError):
                pass

            # For generic types, recursively normalize inner types
            if origin is not None and hasattr(annotation, "__args__"):
                args = get_args(annotation)
                if args:
                    normalized_args = tuple(
                        FlextCliUtilities.TypeNormalizer.normalize_annotation(arg)
                        for arg in args
                    )
                    # Reconstruct the generic type with normalized args
                    # Skip ParamSpec and other special forms that don't support indexing
                    if hasattr(annotation, "__class_getitem__") and hasattr(
                        origin, "__getitem__"
                    ):
                        try:
                            reconstructed: type | types.UnionType = origin[
                                normalized_args
                            ]
                            return reconstructed
                        except (TypeError, AttributeError):
                            pass
                    # Fall back to original if we can't reconstruct
                    return annotation

            return annotation

        @staticmethod
        def normalize_union_type(
            annotation: type | types.UnionType,
        ) -> type | types.UnionType | None:
            """Normalize a union type to Optional or Union form.

            Converts modern union syntax and typing.Union to a form Typer understands.

            Args:
                annotation: Union type annotation

            Returns:
                Normalized annotation, or None if normalization fails

            """
            # Extract union members
            args = get_args(annotation)
            if not args:
                return annotation

            # Check if None is in the union
            has_none = types.NoneType in args
            non_none_args = tuple(arg for arg in args if arg is not types.NoneType)

            # If only one non-None type with None, use Union[T, None]
            if has_none and len(non_none_args) == 1:
                inner_type = non_none_args[0]
                # Recursively normalize the inner type
                normalized_inner = (
                    FlextCliUtilities.TypeNormalizer.normalize_annotation(inner_type)
                )
                if normalized_inner is None:
                    return None
                # Create Optional[T] using pipe operator (Python 3.10+)
                return normalized_inner | types.NoneType

            # If only one non-None type without None, use that type directly
            if not has_none and len(non_none_args) == 1:
                return FlextCliUtilities.TypeNormalizer.normalize_annotation(
                    non_none_args[0]
                )

            # If multiple types, recursively normalize and combine
            if len(non_none_args) > 1:
                # Recursively normalize all inner types
                normalized_non_none_list = []
                for arg in non_none_args:
                    normalized = (
                        FlextCliUtilities.TypeNormalizer.normalize_annotation(arg)
                    )
                    if normalized is not None:
                        normalized_non_none_list.append(normalized)

                if not normalized_non_none_list:
                    return None

                # Combine using helper function
                return FlextCliUtilities.TypeNormalizer.combine_types_with_union(
                    normalized_non_none_list, include_none=has_none
                )

            # Edge case: only None (shouldn't happen normally)
            return annotation

        @staticmethod
        def combine_types_with_union(
            types_list: list[type | types.UnionType], *, include_none: bool = False
        ) -> type | types.UnionType:
            """Combine multiple types using pipe operator to create Union.

            Args:
                types_list: List of types to combine
                include_none: Whether to add None to the union

            Returns:
                Combined union type

            """
            # Start with first type and progressively OR with others
            result_type: type | types.UnionType = types_list[0]
            for t in types_list[1:]:
                result_type |= t

            # Add None if needed
            if include_none:
                result_type |= types.NoneType

            return result_type


__all__ = [
    "FlextCliUtilities",
]
