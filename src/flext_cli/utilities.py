"""FLEXT CLI Utilities - Reusable helpers and utilities for CLI operations.

Provides CLI-specific utility functions building on flext-core FlextUtilities,
eliminating code duplication across modules following SOLID and DRY principles.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import os
import sys
import types
from collections.abc import Callable, Iterable, Mapping, Sequence
from enum import StrEnum
from functools import cache, wraps
from pathlib import Path
from typing import Annotated, TypeIs, Union, cast, get_args, get_origin, get_type_hints

from flext_core import FlextResult, FlextTypes, FlextUtilities
from pydantic import BeforeValidator, ConfigDict, ValidationError, validate_call

from flext_cli.constants import FlextCliConstants
from flext_cli.typings import FlextCliTypes

# Type aliases for complex callable types
type TypingCallable[P, R] = Callable[..., R]


class FlextCliUtilities(FlextUtilities):
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
    # BASE UTILITIES - Direct delegation to flext-core FlextUtilities
    # =========================================================================
    # All data mapping operations delegate directly to FlextUtilities.DataMapper
    # CliJsonValue and ParameterValueType are structurally compatible JSON types
    # Simple helpers provide type casting from ParameterValueType to CliJsonValue
    # =========================================================================

    class DataMapper:
        """Direct delegation to FlextUtilities.DataMapper with CliJsonValue casting.

        These helpers eliminate wrapper overhead by directly using FlextUtilities.DataMapper
        and casting results to CLI-specific types. All conversion logic is in flext-core.
        """

        @staticmethod
        def convert_to_json_value(
            value: FlextTypes.ParameterValueType,
        ) -> FlextCliTypes.CliJsonValue:
            """Convert value to CliJsonValue using flext-core DataMapper.

            Args:
                value: Value to convert (any JSON-compatible type)

            Returns:
                FlextCliTypes.CliJsonValue: CLI-compatible JSON value

            """
            # Use flext-core directly - FlextTypes.GeneralValueType and CliJsonValue are structurally identical
            return cast(
                "FlextCliTypes.CliJsonValue",
                FlextUtilities.DataMapper.convert_to_json_value(value),
            )

        @staticmethod
        def convert_dict_to_json(
            data: Mapping[str, FlextTypes.ParameterValueType],
        ) -> FlextCliTypes.CliJsonDict:
            """Convert mapping to CliJsonDict using flext-core DataMapper.

            Args:
                data: Source mapping with any values

            Returns:
                FlextCliTypes.CliJsonDict: Dictionary with CLI-compatible JSON values

            """
            # Use flext-core directly - convert_dict_to_json returns dict[str, FlextTypes.GeneralValueType]
            # which is structurally compatible with CliJsonDict
            result = FlextUtilities.DataMapper.convert_dict_to_json(dict(data))
            # Cast to CliJsonDict - types are structurally compatible
            return cast("FlextCliTypes.CliJsonDict", result)

        @staticmethod
        def convert_list_to_json(
            data: list[FlextTypes.ParameterValueType]
            | Sequence[FlextTypes.ParameterValueType],
        ) -> list[FlextCliTypes.CliJsonDict]:
            """Convert list to list of CliJsonDict using flext-core DataMapper.

            Args:
                data: Source list of dict-like items

            Returns:
                list[FlextCliTypes.CliJsonDict]: List of CLI-compatible JSON dictionaries

            """
            # Use flext-core directly - convert_list_to_json expects list[object]
            data_list: list[FlextTypes.ParameterValueType] = (
                list(data) if isinstance(data, Sequence) else [data]
            )
            result = FlextUtilities.DataMapper.convert_list_to_json(
                cast("list[object]", data_list)
            )
            # Cast to list[CliJsonDict] - types are structurally compatible
            return cast("list[FlextCliTypes.CliJsonDict]", result)

    class TypeConversion:
        """Simple type conversion helpers using flext-core DataMapper directly.

        These helpers provide convenient methods for converting object types
        to CliJsonValue types using flext-core conversion logic.
        """

        @staticmethod
        def normalize_to_cli_json_value(
            value: object,
        ) -> FlextCliTypes.CliJsonValue:
            """Convert any value to CliJsonValue with proper type narrowing.

            Args:
                value: Object value to convert

            Returns:
                FlextCliTypes.CliJsonValue: Properly typed JSON-compatible value

            """
            # Convert object to FlextTypes.GeneralValueType first, then to CliJsonValue
            general_value = FlextUtilities.DataMapper.convert_to_json_value(
                cast("FlextTypes.ParameterValueType", value)
            )
            return cast("FlextCliTypes.CliJsonValue", general_value)

        @staticmethod
        def normalize_dict_to_cli_json_dict(
            data: dict[str, object] | Mapping[str, object],
        ) -> FlextCliTypes.CliJsonDict:
            """Convert dict to CliJsonDict with proper type narrowing.

            Args:
                data: Dictionary or mapping to convert

            Returns:
                FlextCliTypes.CliJsonDict: Properly typed JSON dictionary

            """
            # Use flext-core DataMapper directly
            result = FlextUtilities.DataMapper.convert_dict_to_json(
                cast("dict[str, FlextTypes.ParameterValueType]", dict(data))
            )
            return cast("FlextCliTypes.CliJsonDict", result)

        @staticmethod
        def normalize_list_to_cli_json_list(
            data: list[object] | Sequence[object],
        ) -> list[FlextCliTypes.CliJsonValue]:
            """Convert list to list[CliJsonValue] with proper type narrowing.

            Args:
                data: List or sequence to convert

            Returns:
                list[FlextCliTypes.CliJsonValue]: Properly typed JSON list

            """
            # Convert each item using flext-core DataMapper
            return [
                FlextCliUtilities.TypeConversion.normalize_to_cli_json_value(item)
                for item in data
            ]

    # =========================================================================
    # CLI VALIDATION - CLI-specific validation helpers
    # =========================================================================

    class CliValidation:
        """CLI-specific validation operations.

        Eliminates code duplication in models.py validate_business_rules methods.
        All validators return FlextResult[bool] for railway pattern composition.

        """

        @staticmethod
        def validate_field_not_empty(
            field_value: FlextTypes.ParameterValueType | None,
            field_display_name: str,
        ) -> FlextResult[bool]:
            """Validate that a field is not empty.

            Delegates to FlextUtilities.Validation.validate_required_string().

            Args:
                field_value: Value to validate
                field_display_name: Display name for error messages

            Returns:
                FlextResult[bool]: True if not empty, failure with error message otherwise

            Example:
                >>> result = FlextCliUtilities.CliValidation.validate_field_not_empty(
                ...     command_line, "Command line"
                ... )
                >>> if result.is_failure:
                ...     print(result.error)

            """
            # Use FlextUtilities.Validation.validate_required_string
            if not isinstance(field_value, str):
                return FlextResult[bool].fail(
                    FlextCliConstants.MixinsValidationMessages.FIELD_CANNOT_BE_EMPTY.format(
                        field_name=field_display_name,
                    ),
                )
            try:
                # validate_required_string returns str or raises ValueError
                _ = FlextUtilities.Validation.validate_required_string(
                    field_value,
                    field_display_name,
                )
                return FlextResult[bool].ok(True)
            except ValueError as e:
                return FlextResult[bool].fail(str(e))

        @staticmethod
        def validate_field_in_list(
            field_value: str | float | None,
            *,
            valid_values: list[str],
            field_name: str,
        ) -> FlextResult[bool]:
            """Validate that a field value is in a list of valid values.

            Delegates to FlextUtilities.Validation.validate_choice().

            Args:
                field_value: Value to validate
                valid_values: List of valid values
                field_name: Field name for error messages

            Returns:
                FlextResult[bool]: True if in list, failure with error message otherwise

            Example:
                >>> result = FlextCliUtilities.CliValidation.validate_field_in_list(
                ...     status,
                ...     [
                ...         FlextCliConstants.CommandStatus.PENDING.value,
                ...         FlextCliConstants.CommandStatus.RUNNING.value,
                ...         FlextCliConstants.CommandStatus.COMPLETED.value,
                ...     ],
                ...     "status",
                ... )
                >>> if result.is_failure:
                ...     print(result.error)

            """
            if not isinstance(field_value, str):
                return FlextResult[bool].fail(
                    FlextCliConstants.MixinsValidationMessages.INVALID_ENUM_VALUE.format(
                        field_name=field_name,
                        valid_values=valid_values,
                    ),
                )
            # Use FlextUtilities.Validation.validate_choice
            result = FlextUtilities.Validation.validate_choice(
                field_value,
                set(valid_values),
                field_name,
                case_sensitive=True,
            )
            # Convert FlextResult[str] to FlextResult[bool]
            if result.is_success:
                return FlextResult[bool].ok(True)
            return FlextResult[bool].fail(result.error or "Validation failed")

        @staticmethod
        def validate_command_status(status: str) -> FlextResult[bool]:
            """Validate command status against known valid statuses.

            Args:
                status: Command status to validate

            Returns:
                FlextResult[bool]: True if valid, failure otherwise

            """
            return FlextCliUtilities.CliValidation.validate_field_in_list(
                status,
                valid_values=FlextCliConstants.COMMAND_STATUSES_LIST,
                field_name="status",
            )

        @staticmethod
        def validate_debug_level(level: str) -> FlextResult[bool]:
            """Validate debug level against known valid levels.

            Args:
                level: Debug level to validate

            Returns:
                FlextResult[bool]: True if valid, failure otherwise

            """
            return FlextCliUtilities.CliValidation.validate_field_in_list(
                level,
                valid_values=FlextCliConstants.DEBUG_LEVELS_LIST,
                field_name="level",
            )

        @staticmethod
        def validate_output_format(format_type: str) -> FlextResult[str]:
            """Validate and normalize output format type.

            Validates format against list of supported output formats and
            returns normalized lowercase format string.

            Uses FlextUtilitiesValidation.validate_choice() internally.

            Args:
                format_type: Output format to validate (json, yaml, table, csv, plain)

            Returns:
                FlextResult[str]: Normalized lowercase format if valid, error otherwise

            Example:
                >>> result = FlextCliUtilities.CliValidation.validate_output_format(
                ...     "JSON"
                ... )
                >>> if result.is_success:
                ...     format = result.unwrap()  # "json"

            """
            format_lower = format_type.lower()
            # Use FlextUtilities.Validation.validate_choice for validation
            result = FlextUtilities.Validation.validate_choice(
                format_lower,
                set(FlextCliConstants.OUTPUT_FORMATS_LIST),
                "Output format",
                case_sensitive=False,
            )
            if result.is_success:
                return FlextResult[str].ok(format_lower)
            return result

        @staticmethod
        def validate_string_not_empty(
            value: str | None,
            error_message: str,
        ) -> FlextResult[bool]:
            """Validate that a value is a non-empty string.

            Delegates to FlextUtilities.Validation.validate_required_string().

            Args:
                value: Value to validate
                error_message: Error message to return on failure (used if value is not a string)

            Returns:
                FlextResult[bool]: True if non-empty string, failure otherwise

            Example:
                >>> result = FlextCliUtilities.CliValidation.validate_string_not_empty(
                ...     name, "Name must be a string"
                ... )
                >>> if result.is_failure:
                ...     return result

            """
            if not isinstance(value, str):
                return FlextResult[bool].fail(error_message)
            try:
                # validate_required_string returns str or raises ValueError
                _ = FlextUtilities.Validation.validate_required_string(
                    value,
                    "Value",
                )
                return FlextResult[bool].ok(True)
            except ValueError:
                # Use custom error_message if validation fails (for backward compatibility)
                return FlextResult[bool].fail(error_message)

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
            # Validate environment variables explicitly - no fallback
            pytest_test = os.environ.get(
                FlextCliConstants.EnvironmentConstants.PYTEST_CURRENT_TEST,
            )
            underscore_value = os.environ.get(
                FlextCliConstants.EnvironmentConstants.UNDERSCORE,
                "",
            )
            ci_value = os.environ.get(FlextCliConstants.EnvironmentConstants.CI)
            return (
                pytest_test is not None
                or (
                    FlextCliConstants.EnvironmentConstants.PYTEST
                    in underscore_value.lower()
                )
                or ci_value == FlextCliConstants.EnvironmentConstants.CI_TRUE_VALUE
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
                    + FlextCliConstants.CmdMessages.CONFIG_DIR_EXISTS,
                )
            else:
                results.append(
                    FlextCliConstants.Symbols.FAILURE_MARK
                    + FlextCliConstants.CmdMessages.CONFIG_DIR_MISSING,
                )

            # Check subdirectories using constants
            for subdir in FlextCliConstants.Subdirectories.STANDARD_SUBDIRS:
                path = flext_dir / subdir
                if path.exists():
                    results.append(
                        FlextCliConstants.CmdMessages.SUBDIR_EXISTS.format(
                            symbol=FlextCliConstants.Symbols.SUCCESS_MARK,
                            subdir=subdir,
                        ),
                    )
                else:
                    results.append(
                        FlextCliConstants.CmdMessages.SUBDIR_MISSING.format(
                            symbol=FlextCliConstants.Symbols.FAILURE_MARK,
                            subdir=subdir,
                        ),
                    )

            return results

        @staticmethod
        def get_config_info() -> FlextCliTypes.CliJsonDict:
            """Get FLEXT CLI configuration information.

            Returns comprehensive configuration information including:
            - Configuration directory path
            - Existence status
            - Read/write permissions
            - Current timestamp

            Returns:
                FlextCliTypes.CliJsonDict: Configuration information dictionary

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
                FlextCliConstants.DictKeys.TIMESTAMP: FlextUtilities.Generators.generate_iso_timestamp(),
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
                ...     if FlextCliUtilities.FileOps.is_file_not_found_error(
                ...         result.error
                ...     ):
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
                return FlextCliUtilities.TypeNormalizer.normalize_union_type(annotation)

            # typing.Union type (traditional typing.Union[X, Y])
            if origin is Union:
                return FlextCliUtilities.TypeNormalizer.normalize_union_type(annotation)

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
                        origin,
                        "__getitem__",
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
                    non_none_args[0],
                )

            # If multiple types, recursively normalize and combine
            if len(non_none_args) > 1:
                # Recursively normalize all inner types
                normalized_non_none_list = []
                for arg in non_none_args:
                    normalized = FlextCliUtilities.TypeNormalizer.normalize_annotation(
                        arg,
                    )
                    if normalized is not None:
                        normalized_non_none_list.append(normalized)

                if not normalized_non_none_list:
                    return None

                # Combine using helper function
                return FlextCliUtilities.TypeNormalizer.combine_types_with_union(
                    normalized_non_none_list,
                    include_none=has_none,
                )

            # Edge case: only None (shouldn't happen normally)
            return annotation

        @staticmethod
        def combine_types_with_union(
            types_list: list[type | types.UnionType],
            *,
            include_none: bool = False,
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

        # ═══════════════════════════════════════════════════════════════════
        # NESTED CLASS: Enum Utilities
        # ═══════════════════════════════════════════════════════════════════

        class Enum:
            """Utilities para trabalhar com StrEnum de forma type-safe.

            FILOSOFIA:
            ──────────
            - TypeIs para narrowing que funciona em if/else
            - Métodos genéricos que aceitam QUALQUER StrEnum
            - Caching para performance em validações frequentes
            - Integração direta com Pydantic BeforeValidator
            """

            # ─────────────────────────────────────────────────────────────
            # TYPEIS FACTORIES: Gera funções TypeIs para qualquer StrEnum
            # ─────────────────────────────────────────────────────────────

            @staticmethod
            def is_member[E: StrEnum](enum_cls: type[E], value: object) -> TypeIs[E]:
                """TypeIs genérico para qualquer StrEnum.

                VANTAGEM sobre TypeGuard:
                - Narrowing funciona em AMBAS branches (if/else)
                - Type checker entende que no 'else' NÃO é E

                Exemplo:
                    if FlextCliUtilities.Enum.is_member(Status, value):
                        # value: Status
                        process_status(value)
                    else:
                        # value: str (narrowed corretamente!)
                        handle_invalid(value)
                """
                if isinstance(value, enum_cls):
                    return True
                if isinstance(value, str):
                    return value in enum_cls._value2member_map_
                return False

            @staticmethod
            def is_subset[E: StrEnum](
                enum_cls: type[E],
                valid_members: frozenset[E],
                value: object,
            ) -> TypeIs[E]:
                """TypeIs para subset de um StrEnum.

                Exemplo:
                    ACTIVE_STATES = frozenset({Status.ACTIVE, Status.PENDING})

                    if FlextCliUtilities.Enum.is_subset(Status, ACTIVE_STATES, value):
                        # value: Status (e sabemos que é ACTIVE ou PENDING)
                        process_active(value)
                """
                if isinstance(value, enum_cls) and value in valid_members:
                    return True
                if isinstance(value, str):
                    try:
                        member = enum_cls(value)
                        return member in valid_members
                    except ValueError:
                        return False
                return False

            # ─────────────────────────────────────────────────────────────
            # CONVERSÃO: String → StrEnum (type-safe)
            # ─────────────────────────────────────────────────────────────

            @staticmethod
            def parse[E: StrEnum](enum_cls: type[E], value: str | E) -> FlextResult[E]:
                """Converte string para StrEnum com FlextResult.

                Exemplo:
                    result = FlextCliUtilities.Enum.parse(Status, "active")
                    if result.is_success:
                        status: Status = result.value
                """
                if isinstance(value, enum_cls):
                    return FlextResult.ok(value)
                try:
                    return FlextResult.ok(enum_cls(value))
                except ValueError:
                    valid = ", ".join(m.value for m in enum_cls)
                    return FlextResult.fail(
                        f"Invalid {enum_cls.__name__}: '{value}'. Valid: {valid}"
                    )

            @staticmethod
            def parse_or_default[E: StrEnum](
                enum_cls: type[E],
                value: str | E | None,
                default: E,
            ) -> E:
                """Converte com fallback para default (nunca falha).

                Exemplo:
                    status = FlextCliUtilities.Enum.parse_or_default(
                        Status, user_input, Status.PENDING
                    )
                """
                if value is None:
                    return default
                if isinstance(value, enum_cls):
                    return value
                try:
                    return enum_cls(value)
                except ValueError:
                    return default

            # ─────────────────────────────────────────────────────────────
            # PYDANTIC VALIDATORS: BeforeValidator factories
            # ─────────────────────────────────────────────────────────────

            @staticmethod
            def coerce_validator[E: StrEnum](
                enum_cls: type[E],
            ) -> type:  # Actually returns a callable, but type hints are complex
                """Cria BeforeValidator para coerção automática no Pydantic.

                PADRÃO RECOMENDADO para campos Pydantic:

                Exemplo:
                    from pydantic import BaseModel
                    from typing import Annotated

                    # Cria o tipo anotado uma vez
                    CoercedStatus = Annotated[
                        Status,
                        BeforeValidator(FlextCliUtilities.Enum.coerce_validator(Status))
                    ]

                    class MyModel(BaseModel):
                        status: CoercedStatus  # Aceita "active" ou Status.ACTIVE
                """

                def _coerce(value: object) -> E:
                    if isinstance(value, enum_cls):
                        return value
                    if isinstance(value, str):
                        try:
                            return enum_cls(value)
                        except ValueError:
                            pass
                    msg = f"Invalid {enum_cls.__name__}: {value!r}"
                    raise ValueError(msg)

                return _coerce

            @staticmethod
            def coerce_by_name_validator[E: StrEnum](
                enum_cls: type[E],
            ) -> type:
                """BeforeValidator que aceita nome OU valor do enum.

                Aceita:
                    - "ACTIVE" (nome do membro)
                    - "active" (valor do membro)
                    - Status.ACTIVE (membro direto)

                Exemplo:
                    StatusByName = Annotated[
                        Status,
                        BeforeValidator(FlextCliUtilities.Enum.coerce_by_name_validator(Status))
                    ]
                """

                def _coerce(value: object) -> E:
                    if isinstance(value, enum_cls):
                        return value
                    if isinstance(value, str):
                        # Tenta por nome primeiro
                        if value in enum_cls.__members__:
                            return enum_cls[value]
                        # Depois por valor
                        try:
                            return enum_cls(value)
                        except ValueError:
                            pass
                    msg = f"Invalid {enum_cls.__name__}: {value!r}"
                    raise ValueError(msg)

                return _coerce

            # ─────────────────────────────────────────────────────────────
            # METADATA: Informações sobre StrEnums
            # ─────────────────────────────────────────────────────────────

            @staticmethod
            @cache
            def values[E: StrEnum](enum_cls: type[E]) -> frozenset[str]:
                """Retorna frozenset dos valores (cached para performance)."""
                return frozenset(m.value for m in enum_cls)

            @staticmethod
            @cache
            def names[E: StrEnum](enum_cls: type[E]) -> frozenset[str]:
                """Retorna frozenset dos nomes dos membros (cached)."""
                return frozenset(enum_cls.__members__.keys())

            @staticmethod
            @cache
            def members[E: StrEnum](enum_cls: type[E]) -> frozenset[E]:
                """Retorna frozenset dos membros (cached)."""
                return frozenset(enum_cls)

        # ═══════════════════════════════════════════════════════════════════
        # NESTED CLASS: Collection Utilities
        # ═══════════════════════════════════════════════════════════════════

        class Collection:
            """Utilities para conversão de coleções com StrEnums.

            PADRÕES collections.abc:
            ────────────────────────
            - Sequence[E] para listas imutáveis
            - Mapping[str, E] para dicts imutáveis
            - Iterable[E] para qualquer iterável
            """

            # ─────────────────────────────────────────────────────────────
            # LIST CONVERSIONS
            # ─────────────────────────────────────────────────────────────

            @staticmethod
            def parse_sequence[E: StrEnum](
                enum_cls: type[E],
                values: Iterable[str | E],
            ) -> FlextResult[tuple[E, ...]]:
                """Converte sequência de strings para tuple de StrEnum.

                Exemplo:
                    result = FlextCliUtilities.Collection.parse_sequence(
                        Status, ["active", "pending"]
                    )
                    if result.is_success:
                        statuses: tuple[Status, ...] = result.value
                """
                parsed: list[E] = []
                errors: list[str] = []

                for idx, val in enumerate(values):
                    if isinstance(val, enum_cls):
                        parsed.append(val)
                    else:
                        try:
                            parsed.append(enum_cls(val))
                        except ValueError:
                            errors.append(f"[{idx}]: '{val}'")

                if errors:
                    return FlextResult.fail(
                        f"Invalid {enum_cls.__name__} values: {', '.join(errors)}"
                    )
                return FlextResult.ok(tuple(parsed))

            @staticmethod
            def coerce_list_validator[E: StrEnum](
                enum_cls: type[E],
            ) -> type:
                """BeforeValidator para lista de StrEnums.

                Exemplo:
                    StatusList = Annotated[
                        list[Status],
                        BeforeValidator(FlextCliUtilities.Collection.coerce_list_validator(Status))
                    ]

                    class MyModel(BaseModel):
                        statuses: StatusList  # Aceita ["active", "pending"]
                """

                def _coerce(value: object) -> list[E]:
                    if not isinstance(value, (list, tuple, set, frozenset)):
                        msg = f"Expected sequence, got {type(value).__name__}"
                        raise TypeError(msg)

                    result: list[E] = []
                    for idx, item in enumerate(value):
                        if isinstance(item, enum_cls):
                            result.append(item)
                        elif isinstance(item, str):
                            try:
                                result.append(enum_cls(item))
                            except ValueError as err:
                                msg = (
                                    f"Invalid {enum_cls.__name__} at [{idx}]: {item!r}"
                                )
                                raise ValueError(msg) from err
                        else:
                            msg = f"Expected str at [{idx}], got {type(item).__name__}"
                            raise TypeError(msg)
                    return result

                return _coerce

            # ─────────────────────────────────────────────────────────────
            # DICT CONVERSIONS
            # ─────────────────────────────────────────────────────────────

            @staticmethod
            def parse_mapping[E: StrEnum](
                enum_cls: type[E],
                mapping: Mapping[str, str | E],
            ) -> FlextResult[dict[str, E]]:
                """Converte Mapping com valores string para dict com StrEnum.

                Exemplo:
                    result = FlextCliUtilities.Collection.parse_mapping(
                        Status, {"user1": "active", "user2": "pending"}
                    )
                """
                parsed: dict[str, E] = {}
                errors: list[str] = []

                for key, val in mapping.items():
                    if isinstance(val, enum_cls):
                        parsed[key] = val
                    else:
                        try:
                            parsed[key] = enum_cls(val)
                        except ValueError:
                            errors.append(f"'{key}': '{val}'")

                if errors:
                    return FlextResult.fail(
                        f"Invalid {enum_cls.__name__} values: {', '.join(errors)}"
                    )
                return FlextResult.ok(parsed)

            @staticmethod
            def coerce_dict_validator[E: StrEnum](
                enum_cls: type[E],
            ) -> type:
                """BeforeValidator para dict com valores StrEnum.

                Exemplo:
                    StatusDict = Annotated[
                        dict[str, Status],
                        BeforeValidator(FlextCliUtilities.Collection.coerce_dict_validator(Status))
                    ]
                """

                def _coerce(value: object) -> dict[str, E]:
                    if not isinstance(value, dict):
                        msg = f"Expected dict, got {type(value).__name__}"
                        raise TypeError(msg)

                    result: dict[str, E] = {}
                    for key, val in value.items():
                        if isinstance(val, enum_cls):
                            result[key] = val
                        elif isinstance(val, str):
                            try:
                                result[key] = enum_cls(val)
                            except ValueError as err:
                                msg = f"Invalid {enum_cls.__name__} at '{key}': {val!r}"
                                raise ValueError(msg) from err
                        else:
                            msg = f"Expected str at '{key}', got {type(val).__name__}"
                            raise TypeError(msg)
                    return result

                return _coerce

        # ═══════════════════════════════════════════════════════════════════
        # NESTED CLASS: Args Utilities
        # ═══════════════════════════════════════════════════════════════════

        class Args:
            """@validated, parse_kwargs - ZERO boilerplate de validação."""

            @staticmethod
            def validated[P, R](func: type) -> type:  # Actually returns a callable
                """Decorator com validate_call - aceita str OU enum, converte auto."""
                return validate_call(
                    config=ConfigDict(
                        arbitrary_types_allowed=True, use_enum_values=False
                    ),
                    validate_return=False,
                )(func)

            @staticmethod
            def validated_with_result[P, R](func: type) -> type:
                """ValidationError → FlextResult.fail()."""

                @wraps(func)
                def wrapper(*args: P.args, **kwargs: P.kwargs) -> FlextResult[R]:
                    try:
                        return validate_call(
                            config=ConfigDict(arbitrary_types_allowed=True),
                            validate_return=False,
                        )(func)(*args, **kwargs)
                    except ValidationError as e:
                        return FlextResult.fail(str(e))

                return wrapper

            @staticmethod
            def parse_kwargs[E: StrEnum](
                kwargs: Mapping[str, object], enum_fields: Mapping[str, type[E]]
            ) -> FlextResult[dict[str, object]]:
                """Parse kwargs converting string enum values to enum instances."""
                parsed, errors = dict(kwargs), []
                for field, enum_cls in enum_fields.items():
                    if field in parsed and isinstance(parsed[field], str):
                        try:
                            parsed[field] = enum_cls(parsed[field])
                        except ValueError:
                            errors.append(f"{field}: '{parsed[field]}'")
                return (
                    FlextResult.fail(f"Invalid: {errors}")
                    if errors
                    else FlextResult.ok(parsed)
                )

            @staticmethod
            def get_enum_params(func: type) -> dict[str, type[StrEnum]]:
                """Extrai parâmetros StrEnum da signature."""
                try:
                    hints = get_type_hints(func)
                    return {
                        n: h
                        for n, h in hints.items()
                        if n != "return"
                        and isinstance(h, type)
                        and issubclass(h, StrEnum)
                    }
                except Exception:
                    return {}

        # ═══════════════════════════════════════════════════════════════════
        # NESTED CLASS: Model Utilities
        # ═══════════════════════════════════════════════════════════════════

        class Model:
            """from_dict, merge_defaults, update - ZERO try/except."""

            @staticmethod
            def from_dict[M](
                model_cls: type[M], data: Mapping[str, object], *, strict: bool = False
            ) -> FlextResult[M]:
                """Create model from dict with FlextResult."""
                try:
                    return FlextResult.ok(model_cls.model_validate(data, strict=strict))
                except Exception as e:
                    return FlextResult.fail(f"Validation failed: {e}")

            @staticmethod
            def merge_defaults[M](
                model_cls: type[M],
                defaults: Mapping[str, object],
                overrides: Mapping[str, object],
            ) -> FlextResult[M]:
                """Merge defaults with overrides and create model."""
                return FlextCliUtilities.Model.from_dict(
                    model_cls, {**defaults, **overrides}
                )

            @staticmethod
            def update[M](instance: M, **updates: object) -> FlextResult[M]:
                """Update model with new values."""
                try:
                    current = instance.model_dump()
                    current.update(updates)
                    return FlextResult.ok(type(instance).model_validate(current))
                except Exception as e:
                    return FlextResult.fail(f"Update failed: {e}")

        # ═══════════════════════════════════════════════════════════════════
        # NESTED CLASS: Pydantic Type Factories
        # ═══════════════════════════════════════════════════════════════════

        class Pydantic:
            """Fábricas de Annotated types."""

            @staticmethod
            def coerced_enum[E: StrEnum](enum_cls: type[E]) -> type:
                """Retorna tipo Annotated para StrEnum com coerção."""
                return Annotated[
                    enum_cls,
                    BeforeValidator(FlextCliUtilities.Enum.coerce_validator(enum_cls)),
                ]


# Note: Aliases moved to avoid circular imports
# Use FlextCliModels.CliModelConverter and FlextCliModels.CliModelDecorators directly


__all__ = [
    "FlextCliUtilities",
]
