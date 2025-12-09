"""FLEXT CLI Utilities - Reusable helpers and utilities for CLI operations.

Provides CLI-specific utility functions building on flext-core u,
eliminating code duplication across modules following SOLID and DRY principles.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import inspect
import os
import sys
import types
from collections.abc import Callable, Iterable, Mapping
from datetime import UTC, datetime
from enum import StrEnum
from functools import wraps
from pathlib import Path
from typing import (
    Annotated,
    Self,
    TypeGuard,
    Union,
    get_args,
    get_origin,
    get_type_hints,
    overload,
)

from flext_core import r, u as u_core
from flext_core.result import FlextResult
from flext_core.typings import P as CORE_P, R
from pydantic import (
    BaseModel,
    BeforeValidator,
    ConfigDict,
    ValidationError,
    validate_call,
)

from flext_cli.constants import c
from flext_cli.protocols import p
from flext_cli.typings import t


class FlextCliUtilities(u_core):
    """FLEXT CLI Utilities - Centralized helpers eliminating code duplication.

    Business Rules:
    ---------------
    1. All utility methods MUST be static (no instance state)
    2. All operations MUST return r[T] for error handling
    3. Field validation MUST enforce business rules (trace requires debug)
    4. Type normalization MUST preserve type safety (no Any types)
    5. Common patterns MUST be consolidated here (DRY principle)
    6. CLI-specific helpers MUST extend flext-core u
    7. All validators MUST use Pydantic validators when applicable
    8. Type conversion MUST handle Python 3.13+ patterns (PEP 695, UnionType)

    Architecture Implications:
    ---------------------------
    - Single source of truth eliminates code duplication across modules
    - Static methods ensure thread safety and no side effects
    - Railway-Oriented Programming via r for composable error handling
    - Type normalization enables Typer compatibility without type loss
    - Validation helpers enforce business rules consistently

    Audit Implications:
    -------------------
    - Validation failures MUST be logged with field name and value (no sensitive data)
    - Type conversion operations SHOULD be logged for debugging
    - Business rule violations MUST return clear error messages
    - Utility operations MUST not modify input data (immutable operations)

    **PURPOSE**: Single source of truth for CLI utility operations.
    Builds on uore and adds CLI-specific helpers.

    **ARCHITECTURE LAYER**: Application Layer (Layer 3)
    - Extends flext-core ucific functionality
    - Pure static methods (no state) for thread safety
    - r[T] railway pattern for all fallible operations

    **ZERO DUPLICATION**: All common helpers consolidated here:
    - Field validation (eliminate duplicates in models.py)
    - Type normalization for Typer compatibility (from type_u.py)
    - Common patterns used across multiple modules

    **CORE NAMESPACES**:
    1. **CliValidation**: CLI-specific field and business rule validation
    2. **TypeNormalizer**: Type annotation normalization for Typer
    3. **Base Utilities**: Access to all uy

    **DESIGN PATTERNS**:
    - DRY: Single source for all common operations
    - SOLID: Single responsibility per namespace
    - Railway Pattern: All operations return r[T]
    - Static Methods: Thread-safe, no state

    """

    class Cli:
        """CLI-specific utilities extending u_core.

        Provides CLI-specific operations and wrappers for flext-core utilities.
        All nested classes and methods are organized within this namespace.
        """

        # =========================================================================
        # BASE UTILITIES - Use u wrappers needed
        # =========================================================================
        # All data mapping operations use uirectly
        # Use t.GeneralValueType and t.Json.JsonDict directly
        # Wrappers for validate/convert to maintain compatibility
        # =========================================================================

        @staticmethod
        def validate[T](
            value: T,
            *validators: p.ValidatorSpec,  # ValidatorSpec from flext-core protocols
            mode: str = "all",
            fail_fast: bool = True,
            collect_errors: bool = False,
            field_name: str | None = None,
        ) -> r[T]:
            """Validate value using flext-core Validation.validate.

            Wrapper for u_core.Validation.validate() to maintain compatibility.
            """
            result = u_core.Validation.validate(
                value,
                *validators,
                mode=mode,
                fail_fast=fail_fast,
                collect_errors=collect_errors,
                field_name=field_name,
            )
            # Convert RuntimeResult to FlextResult (r[T])
            return (
                r[T].ok(result.value)
                if result.is_success
                else r[T].fail(result.error or "")
            )

        @staticmethod
        def convert[T](
            value: t.GeneralValueType, target_type: type[T], default: T
        ) -> T:
            """Convert value using flext-core Parser.convert.

            Wrapper for u_core.Parser.convert() to maintain compatibility.
            """
            return u_core.Parser.convert(value, target_type, default)

        @staticmethod
        def filter[T](
            items: list[T] | tuple[T, ...],
            predicate: Callable[[T], bool],
        ) -> list[T]:
            """Filter items using flext-core Collection.filter.

            Wrapper for u_core.Collection.filter() to maintain compatibility.
            Simplified to list/tuple only for type safety.
            """
            # Type narrowing: predicate needs Callable[..., bool] for flext-core
            if not callable(predicate):
                msg = "predicate must be callable"
                raise TypeError(msg)
            # Use predicate directly - items is list[T] | tuple[T, ...], so items are T
            # predicate accepts T, so direct call is type-safe
            # No wrapper needed - use predicate directly with proper type narrowing
            return u_core.Collection.filter(items, predicate)

        @staticmethod
        def process[T, R](
            items: T | list[T] | tuple[T, ...] | dict[str, T] | Mapping[str, T],
            processor: Callable[[T], R] | Callable[[str, T], R],
            *,
            on_error: str = "skip",
        ) -> r[list[R] | dict[str, R]]:
            """Process items using flext-core Collection.process.

            Wrapper for u_core.Collection.process() to maintain compatibility.
            Returns r[list[R] | dict[str, R]] as per flext-core signature.
            """
            result = u_core.Collection.process(items, processor, on_error=on_error)
            # Convert RuntimeResult to FlextResult (r[T])
            return (
                r[list[R] | dict[str, R]].ok(result.value)
                if result.is_success
                else r[list[R] | dict[str, R]].fail(result.error or "")
            )

        @overload
        @staticmethod
        def get(
            data: Mapping[str, t.GeneralValueType] | t.GeneralValueType,
            key: str,
            *,
            default: str = ...,
        ) -> str: ...

        @overload
        @staticmethod
        def get[T](
            data: t.GeneralValueType, key: str, *, default: list[T]
        ) -> list[T]: ...

        @overload
        @staticmethod
        def get[T](
            data: t.GeneralValueType, key: str, *, default: T | None = ...
        ) -> T | None: ...

        @staticmethod
        def get[T](
            data: Mapping[str, t.GeneralValueType] | t.GeneralValueType,
            key: str,
            *,
            default: T | None = None,
        ) -> T | None:
            """Get value from mapping using flext-core Mapper.get.

            Wrapper for u_core.Mapper.get() to maintain compatibility.
            """
            return u_core.mapper().get(data, key, default=default)

        @staticmethod
        def extract[T](
            data: object,
            path: str,
            *,
            default: T | None = None,
            required: bool = False,
            separator: str = ".",
        ) -> r[T | None]:
            """Extract value from mapping using flext-core Mapper.extract.

            Wrapper for u_core.mapper().extract() to maintain compatibility.
            """
            result = u_core.mapper().extract(
                data,
                path,
                default=default,
                required=required,
                separator=separator,
            )
            # Convert RuntimeResult to FlextResult (r[T | None])
            return (
                r[T | None].ok(result.value)
                if result.is_success
                else r[T | None].fail(result.error or "")
            )

        @staticmethod
        def find[T](
            items: list[T] | tuple[T, ...],
            predicate: Callable[[T], bool],
        ) -> T | None:
            """Find first item matching predicate using flext-core Collection.find.

            Wrapper for u_core.Collection.find() to maintain compatibility.
            """
            if not callable(predicate):
                msg = "predicate must be callable"
                raise TypeError(msg)
            # Use predicate directly - items is list[T] | tuple[T, ...], so items are T
            # predicate accepts T, so direct call is type-safe
            # No wrapper needed - use predicate directly with proper type narrowing
            return u_core.Collection.find(items, predicate)

        @staticmethod
        def validate_required_string(
            value: str,
            *,
            context: str = "Value",
        ) -> None:
            """Validate that string is non-empty, raising ValueError if invalid.

            Business Rule:
            --------------
            Validates that a string is non-empty using u.validate.
            Raises ValueError for compatibility with existing code.
            """
            # Use Cli.CliValidation.v_empty which wraps Validation.validate
            result = FlextCliUtilities.Cli.CliValidation.v_empty(value, name=context)
            if result.is_failure:
                raise ValueError(result.error or f"{context} cannot be empty")

        @overload
        @staticmethod
        def map[T, R](
            items: r[T],
            mapper: Callable[[T], R],
            *,
            default_error: str = "Operation failed",
        ) -> r[R]: ...

        @overload
        @staticmethod
        def map[T, R](
            items: list[T] | tuple[T, ...],
            mapper: Callable[[T], R],
        ) -> list[R]: ...

        @overload
        @staticmethod
        def map[T, R](
            items: set[T] | frozenset[T],
            mapper: Callable[[T], R],
        ) -> set[R] | frozenset[R]: ...

        @overload
        @staticmethod
        def map[T, R](
            items: dict[str, T] | Mapping[str, T],
            mapper: Callable[[str, T], R],
        ) -> dict[str, R]: ...

        @staticmethod
        def map[T, R](
            items: T
            | list[T]
            | tuple[T, ...]
            | set[T]
            | frozenset[T]
            | dict[str, T]
            | Mapping[str, T]
            | r[T],
            mapper: Callable[[T], R] | Callable[[str, T], R],
            *,
            default_error: str = "Operation failed",
        ) -> list[R] | set[R] | frozenset[R] | dict[str, R] | r[R]:
            """Map items using flext-core Collection.map.

            Wrapper for u_core.Collection.map() to maintain compatibility.
            """
            if not callable(mapper):
                msg = "mapper must be callable"
                raise TypeError(msg)
            # Type narrowing: mapper needs proper type for flext-core overloads
            # Use signature inspection to identify mapper type at runtime
            sig = inspect.signature(mapper)
            param_count = len(sig.parameters)

            # Type guards for mapper type narrowing
            # Constants for parameter count validation
            single_param_count = 1
            dict_param_count = 2

            def is_single_param_mapper(
                _m: Callable[[T], R] | Callable[[str, T], R],
            ) -> TypeGuard[Callable[[T], R]]:
                """Type guard: mapper accepts 1 parameter -> Callable[[T], R]."""
                return param_count == single_param_count

            def is_dict_mapper(
                _m: Callable[[T], R] | Callable[[str, T], R],
            ) -> TypeGuard[Callable[[str, T], R]]:
                """Type guard: mapper accepts 2 parameters -> Callable[[str, T], R]."""
                return param_count == dict_param_count

            # Type narrowing based on items type and mapper signature
            # Dispatch to appropriate u_core.Collection.map overload based on items type
            if isinstance(items, r):
                # For r[T], mapper must be Callable[[T], R] with 1 parameter
                if not is_single_param_mapper(mapper):
                    msg = "mapper for r[T] must accept 1 parameter"
                    raise TypeError(msg)
                # Type guard confirms mapper is Callable[[T], R]
                result = u_core.Collection.map(
                    items,
                    mapper,
                    default_error=default_error,
                )
                # Convert RuntimeResult to FlextResult (r[R])
                return (
                    r[R].ok(result.value)
                    if result.is_success
                    else r[R].fail(result.error or "")
                )
            if isinstance(items, (dict, Mapping)):
                # For dict, mapper must be Callable[[str, T], R] with 2 parameters
                if not is_dict_mapper(mapper):
                    msg = "mapper for dict must accept 2 parameters (str, T)"
                    raise TypeError(msg)
                # Type guard confirms mapper is Callable[[str, T], R]
                return u_core.Collection.map(items, mapper)
            # For list, tuple, set, frozenset - mapper must be Callable[[T], R] with 1 parameter
            if not is_single_param_mapper(mapper):
                msg = "mapper for sequences must accept 1 parameter"
                raise TypeError(msg)
            # Type guard confirms mapper is Callable[[T], R]
            if isinstance(items, (list, tuple)):
                return u_core.Collection.map(items, mapper)
            if isinstance(items, (set, frozenset)):
                return u_core.Collection.map(items, mapper)
            # Single value case - wrap in list
            return u_core.Collection.map([items], mapper)

        @staticmethod
        def build(
            value: t.GeneralValueType,
            *,
            ops: t.Types.ConfigurationDict | None = None,
            on_error: str = "fail",
        ) -> t.GeneralValueType:
            """Build value using flext-core Mapper.build.

            Wrapper for u_core.mapper().build() to maintain compatibility.
            Uses GeneralValueType from lower layer instead of object.
            """
            result = u_core.mapper().build(value, ops=ops, on_error=on_error)
            # Type narrowing: build() returns T | object, but we know T is GeneralValueType
            # Verify result is GeneralValueType compatible
            if isinstance(
                result, (str, int, float, bool, type(None), dict, list, tuple)
            ):
                return result
            # Fallback: convert to string if not GeneralValueType compatible
            return str(result)

        @staticmethod
        def parse[T](
            value: object,
            target: type[T],
            default: T | None = None,
            *,
            strict: bool = False,
            coerce: bool = True,
            case_insensitive: bool = False,
            default_factory: Callable[[], T] | None = None,
            field_name: str | None = None,
        ) -> r[T]:
            """Parse value using flext-core Parser.parse.

            Wrapper for u_core.Parser.parse() to maintain compatibility.
            Accepts default as positional argument for backward compatibility.
            """
            result = u_core.Parser.parse(
                value,
                target,
                strict=strict,
                coerce=coerce,
                case_insensitive=case_insensitive,
                default=default,
                default_factory=default_factory,
                field_name=field_name,
            )
            # Type narrowing: result is r[T], so result.value is T when success
            # FlextResult implements p.Result structurally, so use directly
            return (
                r[T].ok(result.value)
                if result.is_success
                else r[T].fail(result.error or "")
            )

        # =========================================================================
        # CLI VALIDATION - CLI-specific validation helpers
        # =========================================================================

        class CliValidation(u_core.Validation):
            """CLI-specific validation operations extending u_core.Validation via inheritance.

            Eliminates code duplication in models.py validate_business_rules methods.
            All validators return r[bool] for railway pattern composition.
            Exposes all flext-core Validation methods through inheritance hierarchy.

            Provides V class inheriting from Validation.String for compatibility.
            """

            # Inherit from Validation.String for compatibility with u.V.string.non_empty pattern
            class V(u_core.Validation.String):
                """String validation utilities - inherits from u_core.Validation.String."""

            class VBuilder:
                """Fluent builder for CLI validation (mnemonic: 'V' = Validate).

                Advanced DSL pattern for composable validation rules.
                Enables fluent chaining: v(val).name("x").non_empty().in_([...]).build()

                Example:
                    >>> result = (
                    ...     CliValidation.VBuilder(val)
                    ...     .name("status")
                    ...     .non_empty()
                    ...     .in_(["a", "b"])
                    ...     .build()
                    ... )
                    >>> if result.is_success:
                    ...     print("Valid!")

                """

                def __init__(self, val: t.GeneralValueType | None) -> None:
                    """Initialize builder with value to validate."""
                    self._val = val
                    self._name = "field"
                    self._empty = True
                    self._in_list: list[str] | None = None
                    self._eq: str | None = None
                    self._msg = ""

                def name(self, name: str) -> Self:
                    """Set field name for error messages."""
                    self._name = name
                    return self

                def non_empty(self) -> Self:
                    """Require non-empty value."""
                    self._empty = False
                    return self

                def in_(self, choices: list[str]) -> Self:
                    """Validate value is in choices list."""
                    self._in_list = choices
                    return self

                def eq(self, expected: str) -> Self:
                    """Validate value equals expected."""
                    self._eq = expected
                    return self

                def msg(self, message: str) -> Self:
                    """Set custom error message."""
                    self._msg = message
                    return self

                def build(self) -> r[bool]:
                    """Execute validation and return result."""
                    return FlextCliUtilities.Cli.CliValidation.v(
                        self._val,
                        name=self._name,
                        empty=self._empty,
                        in_list=self._in_list,
                        eq=self._eq,
                        msg=self._msg,
                    )

            @staticmethod
            def v(
                val: t.GeneralValueType | None,
                *,
                name: str = "field",
                empty: bool = True,
                in_list: list[str] | None = None,
                eq: str | None = None,
                msg: str = "",
            ) -> r[bool]:
                """Generic validator with builder pattern (mnemonic: 'v' = validate).

                Parametrized validation reducing code duplication.
                Combines multiple validation rules in single call.

                Args:
                    val: Value to validate
                    name: Field name for error messages
                    empty: If False, allow empty values
                    in_list: If provided, validate value is in this list
                    eq: If provided, validate value equals this
                    msg: Custom error message (optional)

                Returns:
                    r[bool]: True if valid, failure otherwise

                Example:
                    >>> # Validate not empty
                    >>> CliValidation.v(value, name="status", empty=False)
                    >>> # Validate in list
                    >>> CliValidation.v(value, name="status", in_list=["a", "b"])
                    >>> # Validate equals
                    >>> CliValidation.v(value, name="status", eq="active")

                """
                # Empty check
                if not empty and (
                    val is None
                    or (
                        u_core.Guards.is_type(val, str)
                        and not u_core.Guards.is_string_non_empty(val)
                    )
                ):
                    return r[bool].fail(
                        msg
                        or c.Cli.MixinsValidationMessages.FIELD_CANNOT_BE_EMPTY.format(
                            field_name=name,
                        ),
                    )
                # In-list check
                if in_list is not None:
                    val_str = FlextCliUtilities.Cli.convert(val, str, "")
                    if val_str not in set(in_list):
                        # Use SESSION_STATUS_INVALID for session_status,
                        # INVALID_ENUM_VALUE for others
                        if name == "session_status":
                            error_msg = c.Cli.MixinsValidationMessages.SESSION_STATUS_INVALID.format(
                                current_status=val_str,
                                valid_states=in_list,
                            )
                        else:
                            error_msg = c.Cli.MixinsValidationMessages.INVALID_ENUM_VALUE.format(
                                field_name=name,
                                valid_values=in_list,
                            )
                        return r[bool].fail(msg or error_msg)
                # Equality check
                if eq is not None:
                    val_str = FlextCliUtilities.Cli.convert(val, str, "")
                    if val_str != eq:
                        return r[bool].fail(
                            msg
                            or c.Cli.MixinsValidationMessages.COMMAND_STATE_INVALID.format(
                                operation=name,
                                current_status=val_str,
                                required_status=eq,
                            ),
                        )
                return r[bool].ok(True)

            @staticmethod
            def v_in(
                val: str | float | None,
                *,
                valid: list[str],
                name: str = "field",
            ) -> r[bool]:
                """Validate value in collection (mnemonic: 'v_in' = validate in).

                Shortcut for v(..., in_list=...).

                """
                return FlextCliUtilities.Cli.CliValidation.v(
                    val,
                    name=name,
                    empty=False,
                    in_list=valid,
                )

            @staticmethod
            def v_eq(
                val: str,
                *,
                eq: str,
                name: str = "field",
            ) -> r[bool]:
                """Validate equality (mnemonic: 'v_eq' = validate equals).

                Shortcut for v(..., eq=...).

                """
                return FlextCliUtilities.Cli.CliValidation.v(val, name=name, eq=eq)

            @staticmethod
            def v_empty(
                val: t.GeneralValueType | None,
                *,
                name: str = "field",
            ) -> r[bool]:
                """Validate field not empty (mnemonic: 'v_empty' = validate empty).

                Direct validation without recursion - handles None, empty strings, and non-string types.
                Non-string values are considered non-empty (valid).

                Args:
                    val: Value to validate
                    name: Field name for errors

                Returns:
                    r[bool]: True if not empty, failure otherwise

                """
                # Direct validation: check if value is empty (avoid recursion)
                if val is None:
                    return r[bool].fail(
                        c.Cli.MixinsValidationMessages.FIELD_CANNOT_BE_EMPTY.format(
                            field_name=name,
                        ),
                    )
                if u_core.Guards.is_type(
                    val, str
                ) and not u_core.Guards.is_string_non_empty(val):
                    return r[bool].fail(
                        c.Cli.MixinsValidationMessages.FIELD_CANNOT_BE_EMPTY.format(
                            field_name=name,
                        ),
                    )
                # Non-string values are considered non-empty (valid)
                return r[bool].ok(True)

            @staticmethod
            def validate_field_in_list(
                field_value: str | float | None,
                *,
                valid_values: list[str],
                field_name: str,
            ) -> r[bool]:
                """Validate that a field value is in a list of valid values.

                Delegates to v_in() for consistency.

                Args:
                    field_value: Value to validate
                    valid_values: List of valid values
                    field_name: Field name for error messages

                Returns:
                    r[bool]: True if in list, failure with error message otherwise

                Example:
                    >>> result = u.CliValidation.validate_field_in_list(
                    ...     status,
                    ...     [
                    ...         c.Cli.CommandStatus.PENDING.value,
                    ...         c.Cli.CommandStatus.RUNNING.value,
                    ...         c.Cli.CommandStatus.COMPLETED.value,
                    ...     ],
                    ...     "status",
                    ... )
                    >>> if result.is_failure:
                    ...     print(result.error)

                """
                return FlextCliUtilities.Cli.CliValidation.v_in(
                    field_value,
                    valid=valid_values,
                    name=field_name,
                )

            @staticmethod
            def v_status(status: str) -> r[bool]:
                """Validate command status (mnemonic: 'v_status').

                Shortcut: v_choice(status, choices=COMMAND_STATUSES_LIST, name="status")

                """
                return FlextCliUtilities.Cli.CliValidation.v_choice(
                    status,
                    choices=c.Cli.ValidationLists.COMMAND_STATUSES,
                    name="status",
                )

            @staticmethod
            def v_level(level: str) -> r[bool]:
                """Validate debug level (mnemonic: 'v_level').

                Shortcut: v_choice(level, choices=DEBUG_LEVELS_LIST, name="level")

                """
                return FlextCliUtilities.Cli.CliValidation.v_choice(
                    level,
                    choices=c.Cli.ValidationLists.DEBUG_LEVELS,
                    name="level",
                )

            @staticmethod
            def v_format(format_type: str) -> r[str]:
                """Validate output format (mnemonic: 'v_format').

                Validates and normalizes format string.

                Args:
                    format_type: Format to validate

                Returns:
                    r[str]: Normalized lowercase format if valid

                """
                format_str = FlextCliUtilities.Cli.convert(format_type, str, "").lower()
                result = FlextCliUtilities.Cli.CliValidation.v_choice(
                    format_str,
                    choices=c.Cli.ValidationLists.OUTPUT_FORMATS,
                    name="format",
                )
                if result.is_failure:
                    return r[str].fail(
                        c.Cli.ErrorMessages.INVALID_OUTPUT_FORMAT.format(
                            format=format_type,
                        ),
                    )
                return r[str].ok(format_str)

            @staticmethod
            def v_choice(
                val: str,
                *,
                choices: list[str],
                name: str = "field",
            ) -> r[bool]:
                """Generic choice validator (mnemonic: 'v_choice' = validate choice).

                Replaces specialized validators: validate_command_status, validate_debug_level,
                validate_session_state, validate_output_format.

                Args:
                    val: Value to validate
                    choices: Valid choices list
                    name: Field name for errors

                Returns:
                    r[bool]: True if in choices, failure otherwise

                Example:
                    >>> result = CliValidation.v_choice(
                    ...     "active", choices=["active", "pending"], name="status"
                    ... )
                    >>> # Replaces: validate_command_status("active")

                """
                return FlextCliUtilities.Cli.CliValidation.v_in(
                    val, valid=choices, name=name
                )

            @staticmethod
            def v_state(
                current: str,
                *,
                required: str | None = None,
                valid: list[str] | None = None,
                name: str = "state",
            ) -> r[bool]:
                """Validate state (mnemonic: 'v_state').

                Generic state validator - validates equality OR membership.

                Args:
                    current: Current state value
                    required: Required state (equality check)
                    valid: Valid states list (membership check)
                    name: Field name for errors

                Returns:
                    r[bool]: True if valid, failure otherwise

                """
                if required is not None:
                    return FlextCliUtilities.Cli.CliValidation.v_eq(
                        current,
                        eq=required,
                        name=name,
                    )
                if valid is not None:
                    return FlextCliUtilities.Cli.CliValidation.v_in(
                        current,
                        valid=valid,
                        name=name,
                    )
                return r[bool].fail(f"{name}: no validation criteria provided")

            @staticmethod
            def v_session(
                current: str,
                *,
                valid: list[str],
            ) -> r[bool]:
                """Validate session state (mnemonic: 'v_session').

                Shortcut: v_state(current, valid=valid, name="session_status")

                """
                return FlextCliUtilities.Cli.CliValidation.v_state(
                    current,
                    valid=valid,
                    name="session_status",
                )

            @staticmethod
            def v_step(step: t.Json.JsonDict | None) -> r[bool]:
                """Validate pipeline step (mnemonic: 'v_step').

                Args:
                    step: Pipeline step dict to validate

                Returns:
                    r[bool]: True if valid, failure otherwise

                """
                if step is None:
                    return r[bool].fail(
                        c.Cli.MixinsValidationMessages.PIPELINE_STEP_EMPTY,
                    )

                field_name = c.Cli.MixinsFieldNames.PIPELINE_STEP_NAME
                if field_name not in step:
                    return r[bool].fail(
                        c.Cli.MixinsValidationMessages.PIPELINE_STEP_NO_NAME,
                    )

                step_name = step[field_name]
                return (
                    FlextCliUtilities.Cli.CliValidation.VBuilder(step_name)
                    .name("Pipeline step name")
                    .non_empty()
                    .msg(c.Cli.MixinsValidationMessages.PIPELINE_STEP_NAME_EMPTY)
                    .build()
                )

            @staticmethod
            def v_req(
                data: t.Json.JsonDict | None,
                *,
                fields: list[str],
            ) -> r[bool]:
                """Validate required fields (mnemonic: 'v_req' = validate required).

                Generic validator for required fields in dict.

                Args:
                    data: Dict to validate
                    fields: Required field names

                Returns:
                    r[bool]: True if all fields present, failure otherwise

                """
                if data is None:
                    return r[bool].fail(
                        c.Cli.MixinsValidationMessages.CONFIG_MISSING_FIELDS.format(
                            missing_fields=fields,
                        ),
                    )
                missing = u_core.Collection.filter(fields, lambda f: f not in data)
                if missing:
                    return r[bool].fail(
                        c.Cli.MixinsValidationMessages.CONFIG_MISSING_FIELDS.format(
                            missing_fields=missing,
                        ),
                    )
                return r[bool].ok(True)

            @staticmethod
            def v_type(
                val: t.GeneralValueType | None,
                *,
                types: tuple[type, ...],
                name: str = "field",
            ) -> r[bool]:
                """Validate type (mnemonic: 'v_type').

                Args:
                    val: Value to validate
                    types: Allowed types
                    name: Field name for errors

                Returns:
                    r[bool]: True if type matches, failure otherwise

                """
                if val is None:
                    return r[bool].fail(f"{name} cannot be None")
                if isinstance(val, types):
                    return r[bool].ok(True)
                type_names = ", ".join(t.__name__ for t in types)
                return r[bool].fail(
                    f"{name} must be {type_names}, got {type(val).__name__}",
                )

            @staticmethod
            def v_conv(
                val: object,
            ) -> r[t.GeneralValueType]:
                """Convert and validate (mnemonic: 'v_conv').

                Converts value to GeneralValueType.

                Args:
                    val: Value to convert

                Returns:
                    r[GeneralValueType]: Converted value

                """
                if val is None:
                    return r[t.GeneralValueType].ok(None)
                if isinstance(val, (str, int, float, bool, dict, list)):
                    return r[t.GeneralValueType].ok(val)
                return r[t.GeneralValueType].ok(str(val))

            @staticmethod
            def v_config(
                config: t.Json.JsonDict | None,
                *,
                fields: list[str],
            ) -> r[bool]:
                """Validate configuration (mnemonic: 'v_config').

                Shortcut: v_req(config, fields=fields)

                """
                return FlextCliUtilities.Cli.CliValidation.v_req(config, fields=fields)

            @staticmethod
            def get_valid_output_formats() -> tuple[str, ...]:
                """Get valid output format values.

                Returns a sorted tuple of valid output formats from ValidationMappings.
                Migrated from constants.py to maintain DRY principle.
                """
                return tuple(sorted(c.Cli.ValidationMappings.OUTPUT_FORMAT_SET))

            @staticmethod
            def get_valid_command_statuses() -> tuple[str, ...]:
                """Get valid command status values.

                Returns a sorted tuple of valid command statuses from ValidationMappings.
                Migrated from constants.py to maintain DRY principle.
                """
                return tuple(sorted(c.Cli.ValidationMappings.COMMAND_STATUS_SET))

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
                    >>> if u.Environment.is_test_environment():
                    ...     # Skip interactive prompts in tests
                    ...     pass

                """
                # Validate environment variables explicitly - no fallback
                pytest_test = u_core.mapper().get(
                    os.environ,
                    c.Cli.EnvironmentConstants.PYTEST_CURRENT_TEST,
                )
                underscore_value = os.environ.get(
                    c.Cli.EnvironmentConstants.UNDERSCORE,
                    "",
                )
                ci_value = os.environ.get(c.Cli.EnvironmentConstants.CI)
                return (
                    pytest_test is not None
                    or (c.Cli.EnvironmentConstants.PYTEST in underscore_value.lower())
                    or ci_value == c.Cli.EnvironmentConstants.CI_TRUE_VALUE
                )

        # =========================================================================
        # CONFIG OPS - Configuration operations
        # =========================================================================

        class ConfigOps:
            """Configuration operations and path management.

            Provides utilities for configuration directory management,
            validation, and information retrieval.

            Advanced builder patterns:
            - paths() - Generic path builder (mnemonic: "paths")
            - check() - Generic path checker (mnemonic: "check")
            - info() - Generic info builder (mnemonic: "info")

            """

            @staticmethod
            def paths(
                base: Path,
                *subdirs: str,
            ) -> list[str]:
                """Generic path builder (mnemonic: 'paths').

                Builds list of paths from base + subdirs.

                Args:
                    base: Base path
                    subdirs: Subdirectory names

                Returns:
                    list[str]: List of path strings

                """
                return [str(base)] + [str(base / subdir) for subdir in subdirs]

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
                    >>> paths = u.ConfigOps.get_config_paths()
                    >>> for path in paths:
                    ...     print(path)

                """
                home = Path.home()
                flext_dir = home / c.Cli.Paths.FLEXT_DIR_NAME
                return FlextCliUtilities.Cli.ConfigOps.paths(
                    flext_dir,
                    c.Cli.DictKeys.CONFIG,
                    c.Cli.Subdirectories.CACHE,
                    c.Cli.Subdirectories.LOGS,
                    c.Cli.DictKeys.TOKEN,
                    c.Cli.Subdirectories.REFRESH_TOKEN,
                )

            @staticmethod
            def check(
                base: Path,
                *,
                name: str = "config",
                subdirs: list[str] | None = None,
            ) -> list[str]:
                """Generic path checker (mnemonic: 'check').

                Checks existence of base path and subdirs, returns formatted results.

                Args:
                    base: Base path to check
                    name: Name for messages
                    subdirs: Optional subdirectories to check

                Returns:
                    list[str]: Validation results with marks

                """
                results: list[str] = []
                ok = c.Cli.Symbols.SUCCESS_MARK
                fail = c.Cli.Symbols.FAILURE_MARK

                # Check base
                if base.exists():
                    results.append(ok + f" {name} directory exists")
                else:
                    results.append(fail + f" {name} directory missing")

                # Check subdirs
                if subdirs:
                    for subdir in subdirs:
                        path = base / subdir
                        if path.exists():
                            results.append(
                                c.Cli.CmdMessages.SUBDIR_EXISTS.format(
                                    symbol=ok,
                                    subdir=subdir,
                                ),
                            )
                        else:
                            results.append(
                                c.Cli.CmdMessages.SUBDIR_MISSING.format(
                                    symbol=fail,
                                    subdir=subdir,
                                ),
                            )

                return results

            @staticmethod
            def validate_config_structure() -> list[str]:
                """Validate FLEXT CLI configuration directory structure.

                Delegates to check() for consistency.

                Returns:
                    list[str]: Validation results with check marks for each check

                Example:
                    >>> results = u.ConfigOps.validate_config_structure()
                    >>> for result in results:
                    ...     print(result)
                    [OK] Configuration directory exists
                    [OK] config/ subdirectory exists
                    ...

                """
                home = Path.home()
                flext_dir = home / c.Cli.Paths.FLEXT_DIR_NAME
                return FlextCliUtilities.Cli.ConfigOps.check(
                    flext_dir,
                    name="Configuration",
                    subdirs=c.Cli.Subdirectories.STANDARD_SUBDIRS,
                )

            @staticmethod
            def info(
                path: Path,
                *,
                dir_key: str = c.Cli.DictKeys.CONFIG_DIR,
                exists_key: str = c.Cli.DictKeys.CONFIG_EXISTS,
                readable_key: str = c.Cli.DictKeys.CONFIG_READABLE,
                writable_key: str = c.Cli.DictKeys.CONFIG_WRITABLE,
            ) -> t.Json.JsonDict:
                """Generic info builder (mnemonic: 'info').

                Builds dict with path info (exists, readable, writable, timestamp).

                Args:
                    path: Path to get info for
                    dir_key: Key for directory path
                    exists_key: Key for existence status
                    readable_key: Key for readable status
                    writable_key: Key for writable status

                Returns:
                    t.Json.JsonDict: Info dictionary

                """
                exists = path.exists()
                return {
                    dir_key: str(path),
                    exists_key: exists,
                    readable_key: exists and os.access(path, os.R_OK),
                    writable_key: exists and os.access(path, os.W_OK),
                    c.Cli.DictKeys.TIMESTAMP: datetime.now(UTC).isoformat(),
                }

            @staticmethod
            def get_config_info() -> t.Json.JsonDict:
                """Get FLEXT CLI configuration information.

                Delegates to info() for consistency.

                Returns:
                    t.Json.JsonDict: Configuration information dictionary

                Example:
                    >>> info = u.ConfigOps.get_config_info()
                    >>> print(f"Config dir: {info['config_dir']}")
                    >>> print(f"Exists: {info['exists']}")

                """
                home = Path.home()
                flext_dir = home / c.Cli.Paths.FLEXT_DIR_NAME
                return FlextCliUtilities.Cli.ConfigOps.info(flext_dir)

        # =========================================================================
        # FILE OPS - File operation helpers
        # =========================================================================

        class FileOps:
            """File operation helpers for error detection and common patterns.

            CLI-specific file operations (FileOps does not exist in flext-core).
            Provides utilities for file-related operations including error detection
            and pattern matching. All methods are static for stateless operation.

            Advanced patterns:
            - matches() - Generic pattern matcher (mnemonic: "matches")
            - is_file_not_found_error() - File not found detector

            """

            # File not found patterns for error detection
            FILE_NOT_FOUND_PATTERNS: tuple[str, ...] = (
                "not found",
                "no such file",
                "does not exist",
                "errno 2",
                "cannot open",
            )

            @staticmethod
            def matches(
                msg: str,
                *patterns: str,
            ) -> bool:
                """Generic pattern matcher (mnemonic: 'matches').

                Checks if message matches any pattern (case-insensitive substring match).

                Args:
                    msg: Message to check
                    patterns: Patterns to match against

                Returns:
                    bool: True if any pattern matches (case-insensitive substring)

                """
                msg_lower = msg.lower()
                return any(pattern.lower() in msg_lower for pattern in patterns)

            @staticmethod
            def is_file_not_found_error(error_msg: str) -> bool:
                """Check if an error message indicates a file-not-found error.

                Delegates to matches() for consistency.

                Args:
                    error_msg: Error message string to check

                Returns:
                    bool: True if error message indicates file not found, False otherwise

                """
                return FlextCliUtilities.Cli.FileOps.matches(
                    error_msg,
                    *FlextCliUtilities.Cli.FileOps.FILE_NOT_FOUND_PATTERNS,
                )

        # =========================================================================
        # TYPE NORMALIZER - Typer compatibility (from type_u.py)
        # =========================================================================

        class TypeNormalizer:
            """Type annotation normalization for Typer compatibility.

            CLI-specific type normalization extending flext-core patterns.
            Converts modern Python 3.10+ union syntax to Typer-compatible forms.
            Eliminates all code from type_u.py by consolidating here.

            **PURPOSE**: Typer does not support modern union syntax (Path | None).
            This normalizes annotations to Union/Optional forms transparently.

            Note: TypeNormalizer is CLI-specific and does not exist in flext-core.
            Nested classes (Enum, Collection) inherit from u_core directly.

            """

            @staticmethod
            def normalize_annotation(
                annotation: type | types.UnionType | None,
            ) -> type | types.UnionType | None:
                """Normalize type annotations for Typer compatibility.

                Converts modern Python 3.10+ union syntax (Path | None) to typing-compatible
                forms (Optional[Path] or Union[...]) that Typer can process.

                Handles:
                - Modern union syntax: Path | None -> Optional[Path]
                - Complex unions: str | int | None -> Union[str, int, None]
                - Nested generics: list[str] | None -> Optional[list[str]]
                - Already-normalized types: Optional[Path] -> unchanged
                - Non-union types: str -> unchanged

                Args:
                    annotation: Type annotation to normalize

                Returns:
                    Normalized annotation compatible with Typer

                Example:
                    >>> from pathlib import Path
                    >>> normalized = u.TypeNormalizer.normalize_annotation(Path | None)
                    >>> # Result: Optional[Path] (Typer-compatible)

                """
                if annotation is None:
                    return annotation

                # Check if this is a modern union type (Python 3.10+: X | Y syntax)
                origin = get_origin(annotation)

                # Python 3.10+ union type using | operator
                if sys.version_info >= (3, 10) and origin is types.UnionType:
                    return FlextCliUtilities.Cli.TypeNormalizer.normalize_union_type(
                        annotation
                    )

                # typing.Union type (traditional typing.Union[X, Y])
                if origin is Union:
                    return FlextCliUtilities.Cli.TypeNormalizer.normalize_union_type(
                        annotation
                    )

                # For generic types, recursively normalize inner types
                if origin is not None and hasattr(annotation, "__args__"):
                    args = get_args(annotation)
                    if args:
                        normalized_args = tuple(
                            FlextCliUtilities.Cli.TypeNormalizer.normalize_annotation(
                                arg
                            )
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

                # Handle single non-None type cases
                if len(non_none_args) == 1:
                    inner_type = non_none_args[0]
                    normalized_inner = (
                        FlextCliUtilities.Cli.TypeNormalizer.normalize_annotation(
                            inner_type
                        )
                    )
                    if normalized_inner is None:
                        return None
                    # If has None, create Optional[T], otherwise return normalized type
                    return (
                        normalized_inner | types.NoneType
                        if has_none
                        else normalized_inner
                    )

                # Handle multiple types case
                if len(non_none_args) > 1:
                    # Recursively normalize all inner types
                    normalized_non_none_list = [
                        normalized
                        for arg in non_none_args
                        if (
                            normalized
                            := FlextCliUtilities.Cli.TypeNormalizer.normalize_annotation(
                                arg
                            )
                        )
                        is not None
                    ]

                    if not normalized_non_none_list:
                        return None

                    # Combine using helper function
                    return (
                        FlextCliUtilities.Cli.TypeNormalizer.combine_types_with_union(
                            normalized_non_none_list,
                            include_none=has_none,
                        )
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
                for type_item in types_list[1:]:
                    result_type |= type_item

                # Add None if needed
                if include_none:
                    result_type |= types.NoneType

                return result_type

            # ═══════════════════════════════════════════════════════════════════
            # NESTED CLASS: Enum Utilities
            # ═══════════════════════════════════════════════════════════════════

            class Enum:
                """Enum utilities wrapper providing FlextResult conversion.

                Wraps u_core.Enum methods to convert RuntimeResult to FlextResult.
                Does NOT inherit to avoid type signature conflicts.
                Provides CLI-specific enum operations with GeneralValueType compatibility.

                DESIGN PRINCIPLES:
                ------------------
                - TypeIs for narrowing that works in if/else
                - Generic methods that accept ANY StrEnum
                - Caching for performance in frequent validations
                - Direct integration with Pydantic BeforeValidator
                """

                # -------------------------------------------------------------
                # TYPEIS FACTORIES: Generate TypeIs functions for any StrEnum
                # -------------------------------------------------------------
                # is_member and is_subset are inherited from u_core.Enum
                # No need to redefine - inheritance exposes them correctly

                # -------------------------------------------------------------
                # CONVERSION: String -> StrEnum (type-safe)
                # -------------------------------------------------------------

                @staticmethod
                def try_parse[E: StrEnum](
                    enum_cls: type[E],
                    value: str | E,
                ) -> E | None:
                    """Try parse enum value (mnemonic: 'try_parse').

                    Delegates to u.Enum.parse() and extracts value if successful.

                    Returns enum member or None if invalid.

                    """
                    result = u.Enum.parse(enum_cls, value)
                    return result.value if result.is_success else None

                @staticmethod
                def parse[E: StrEnum](enum_cls: type[E], value: str | E) -> r[E]:
                    """Parse string to StrEnum with r (mnemonic: 'parse').

                    Delegates to u.Enum.parse() for consistency.

                    Example:
                        result = u.TypeNormalizer.Enum.parse(Status, "active")
                        if result.is_success:
                            status: Status = result.value

                    """
                    result = u.Enum.parse(enum_cls, value)
                    # Convert RuntimeResult to FlextResult (r[E])
                    return (
                        r[E].ok(result.value)
                        if result.is_success
                        else r[E].fail(result.error or "")
                    )

                @staticmethod
                def parse_or_default[E: StrEnum](
                    enum_cls: type[E],
                    value: str | E | None,
                    default: E,
                ) -> E:
                    """Parse with default fallback (mnemonic: 'parse_or_default').

                    Delegates to u.Enum.parse_or_default() for consistency.

                    Never fails - returns default if parsing fails.

                    Example:
                        status = u.TypeNormalizer.Enum.parse_or_default(
                            Status, user_input, Status.PENDING
                        )

                    """
                    return u.Enum.parse_or_default(enum_cls, value, default)

                # -------------------------------------------------------------
                # PYDANTIC VALIDATORS: BeforeValidator factories
                # -------------------------------------------------------------

                @staticmethod
                def coerce_impl[E: StrEnum](
                    enum_cls: type[E],
                    value: t.GeneralValueType,
                    *,
                    by_name: bool = False,
                ) -> E:
                    """Coerce implementation (mnemonic: 'coerce_impl').

                    CLI-specific helper that extends u.Enum with by_name support.
                    Uses u.Enum.coerce_validator() or u.Enum.coerce_by_name_validator() internally.

                    Args:
                        enum_cls: Enum class
                        value: Value to coerce
                        by_name: If True, try by name first

                    Returns:
                        Enum member

                    Raises:
                        ValueError: If coercion fails

                    """
                    if isinstance(value, enum_cls):
                        return value
                    if isinstance(value, str):
                        if by_name:
                            # Use coerce_by_name_validator for name-first matching
                            validator = u.Enum.coerce_by_name_validator(enum_cls)
                            return validator(value)
                        # Use standard coerce_validator
                        validator = u.Enum.coerce_validator(enum_cls)
                        return validator(value)
                    enum_name = getattr(enum_cls, "__name__", "Enum")
                    msg = f"Invalid {enum_name}: {value!r}"
                    raise ValueError(msg)

                @staticmethod
                def coerce_validator[E: StrEnum](
                    enum_cls: type[E],
                ) -> Callable[[t.GeneralValueType], E]:
                    """Create BeforeValidator for Pydantic coercion (mnemonic: 'coerce_validator').

                    RECOMMENDED PATTERN for Pydantic fields:

                    Example:
                        CoercedStatus = Annotated[
                            Status,
                            BeforeValidator(u.TypeNormalizer.Enum.coerce_validator(Status))
                        ]

                    """
                    return (
                        lambda v: FlextCliUtilities.Cli.TypeNormalizer.Enum.coerce_impl(
                            enum_cls,
                            v,
                            by_name=False,
                        )
                    )

                @staticmethod
                def coerce_by_name_validator[E: StrEnum](
                    enum_cls: type[E],
                ) -> Callable[[t.GeneralValueType], E]:
                    """BeforeValidator accepting name OR value (mnemonic: 'coerce_by_name_validator').

                    Accepts: "ACTIVE" (name), "active" (value), Status.ACTIVE (member).

                    """
                    return (
                        lambda v: FlextCliUtilities.Cli.TypeNormalizer.Enum.coerce_impl(
                            enum_cls,
                            v,
                            by_name=True,
                        )
                    )

                # -------------------------------------------------------------
                # METADATA: Information about StrEnums
                # -------------------------------------------------------------

                @staticmethod
                def values[E: StrEnum](enum_cls: type[E]) -> frozenset[str]:
                    """Return frozenset of values (cached for performance).

                    Delegates to u.Enum.values() for consistency.

                    """
                    return u.Enum.values(enum_cls)

                @staticmethod
                def names[E: StrEnum](enum_cls: type[E]) -> frozenset[str]:
                    """Return frozenset of member names (cached).

                    Delegates to u.Enum.names() for consistency.

                    """
                    return u.Enum.names(enum_cls)

                @staticmethod
                def members[E: StrEnum](enum_cls: type[E]) -> frozenset[E]:
                    """Return frozenset of members (cached).

                    Delegates to u.Enum.members() for consistency.

                    """
                    return u.Enum.members(enum_cls)

            # ═══════════════════════════════════════════════════════════════════
            # NESTED CLASS: Collection Utilities
            # ═══════════════════════════════════════════════════════════════════

            class Collection:
                """Collection utilities extending u_core.Collection via inheritance.

                Exposes all flext-core Collection methods through inheritance hierarchy.
                Adds CLI-specific collection operations with GeneralValueType compatibility.

                PADRÕES collections.abc:
                ------------------------
                - Sequence[E] para listas imutáveis
                - Mapping[str, E] para dicts imutáveis
                - Iterable[E] para qualquer iterável
                """

                # -------------------------------------------------------------
                # LIST CONVERSIONS
                # -------------------------------------------------------------

                @staticmethod
                def parse_sequence[E: StrEnum](
                    enum_cls: type[E],
                    values: Iterable[str | E],
                ) -> r[tuple[E, ...]]:
                    """Parse sequence to tuple of StrEnum (mnemonic: 'parse_sequence').

                    Delegates to u.Collection.parse_sequence() for consistency.

                    Example:
                        result = u.Collection.parse_sequence(
                            Status, ["active", "pending"]
                        )
                        if result.is_success:
                            statuses: tuple[Status, ...] = result.value

                    """
                    result = u.Collection.parse_sequence(enum_cls, values)
                    # Convert RuntimeResult to FlextResult (r[tuple[E, ...]])
                    return (
                        r[tuple[E, ...]].ok(result.value)
                        if result.is_success
                        else r[tuple[E, ...]].fail(result.error or "")
                    )

                @staticmethod
                def coerce_list_validator[E: StrEnum](
                    enum_cls: type[E],
                ) -> Callable[[t.GeneralValueType], list[E]]:
                    """BeforeValidator for list of StrEnums (mnemonic: 'coerce_list_validator').

                    Example:
                        StatusList = Annotated[
                            list[Status],
                            BeforeValidator(u.Collection.coerce_list_validator(Status))
                        ]

                    """

                    def _coerce(value: t.GeneralValueType) -> list[E]:
                        if not isinstance(value, (list, tuple, set, frozenset)):
                            msg = f"Expected sequence, got {type(value).__name__}"
                            raise TypeError(msg)

                        result: list[E] = []
                        for item in value:
                            # Type narrowing: item must be str | E for enum parsing
                            if isinstance(item, enum_cls):
                                result.append(item)
                            elif isinstance(item, str):
                                parsed_result = u.Enum.parse(enum_cls, item)
                                if parsed_result.is_failure:
                                    enum_name = getattr(enum_cls, "__name__", "Enum")
                                    msg = f"Invalid {enum_name}: {item!r}"
                                    raise ValueError(msg)
                                result.append(parsed_result.value)
                            else:
                                enum_name = getattr(enum_cls, "__name__", "Enum")
                                msg = f"Invalid {enum_name}: expected str or {enum_name}, got {type(item).__name__}"
                                raise TypeError(msg)
                        return result

                    return _coerce

                # -------------------------------------------------------------
                # DICT CONVERSIONS
                # -------------------------------------------------------------

                @staticmethod
                def parse_mapping[E: StrEnum](
                    enum_cls: type[E],
                    mapping: Mapping[str, str | E],
                ) -> r[dict[str, E]]:
                    """Parse mapping to dict with StrEnum values (mnemonic: 'parse_mapping').

                    Delegates to u.Collection.parse_mapping() for consistency.

                    Example:
                        result = u.Collection.parse_mapping(
                            Status, {"user1": "active", "user2": "pending"}
                        )

                    """
                    result = u.Collection.parse_mapping(enum_cls, mapping)
                    # Convert RuntimeResult to FlextResult (r[dict[str, E]])
                    return (
                        r[dict[str, E]].ok(result.value)
                        if result.is_success
                        else r[dict[str, E]].fail(result.error or "")
                    )

                @staticmethod
                def coerce_dict_validator[E: StrEnum](
                    enum_cls: type[E],
                ) -> Callable[[t.GeneralValueType], dict[str, E]]:
                    """BeforeValidator for dict with StrEnum values (mnemonic: 'coerce_dict_validator').

                    Example:
                        StatusDict = Annotated[
                            dict[str, Status],
                            BeforeValidator(u.Collection.coerce_dict_validator(Status))
                        ]

                    """

                    def _coerce(value: t.GeneralValueType) -> dict[str, E]:
                        if not isinstance(value, dict):
                            msg = f"Expected dict, got {type(value).__name__}"
                            raise TypeError(msg)

                        result: dict[str, E] = {}
                        for k, v in value.items():
                            # Type narrowing: v must be str | E for enum parsing
                            if isinstance(v, enum_cls):
                                result[k] = v
                            elif isinstance(v, str):
                                parsed_result = u.Enum.parse(enum_cls, v)
                                if parsed_result.is_failure:
                                    enum_name = getattr(enum_cls, "__name__", "Enum")
                                    msg = f"Invalid {enum_name} at '{k}': {v!r}"
                                    raise ValueError(msg)
                                result[k] = parsed_result.value
                            else:
                                enum_name = getattr(enum_cls, "__name__", "Enum")
                                msg = f"Invalid {enum_name} at '{k}': expected str or {enum_name}, got {type(v).__name__}"
                                raise TypeError(msg)
                        return result

                    return _coerce

                # ---------------------------------------------------------
                # COLLECTION SEARCH AND MAPPING
                # ---------------------------------------------------------

                @staticmethod
                def find(
                    iterable: Iterable[t.GeneralValueType],
                    predicate: Callable[[t.GeneralValueType], bool] | None = None,
                ) -> t.GeneralValueType | None:
                    """Find first element matching predicate.

                    Accepts any iterable and returns first element where predicate is True.
                    """
                    if predicate is None:
                        return None
                    # Direct implementation to avoid type system issues
                    for item in iterable:
                        if predicate(item):
                            return item
                    return None

                @staticmethod
                def map(
                    iterable: Iterable[t.GeneralValueType],
                    mapper: Callable[[t.GeneralValueType], t.GeneralValueType]
                    | None = None,
                ) -> list[t.GeneralValueType]:
                    """Map function over iterable.

                    Applies mapper function to each item in iterable.
                    """
                    if mapper is None:
                        return list(iterable)
                    return [mapper(item) for item in iterable]

            # ═══════════════════════════════════════════════════════════════════
            # NESTED CLASS: Args Utilities
            # ═══════════════════════════════════════════════════════════════════

            class Args:
                """Args utilities extending u_core.Args via inheritance.

                Exposes all flext-core Args methods through inheritance hierarchy.
                Adds CLI-specific args operations with GeneralValueType compatibility.
                """

                @staticmethod
                def validated[**P, R](func: Callable[P, R]) -> Callable[P, R]:
                    """Decorator with validate_call - accepts str or enum, auto-converts."""
                    return validate_call(
                        config=ConfigDict(
                            arbitrary_types_allowed=True,
                            use_enum_values=False,
                        ),
                        validate_return=False,
                    )(func)

                @staticmethod
                def validated_with_result(
                    func: Callable[CORE_P, Union[FlextResult[R], r[R]]],
                ) -> Callable[CORE_P, Union[FlextResult[R], r[R]]]:
                    """ValidationError -> r.fail().

                    Overrides u_core.Args.validated_with_result with exact signature match.

                    Note: Mypy reports override incompatibility due to TypeVar resolution
                    in ResultType alias (Union[FlextResult[R], r[R]]), but the signature
                    is functionally correct. ResultType is defined as Union[FlextResult[R], r[R]]
                    in the supertype, so this is an exact match.
                    """
                    validated_func = validate_call(
                        config=ConfigDict(arbitrary_types_allowed=True),
                        validate_return=False,
                    )(func)

                    @wraps(func)
                    def wrapper(
                        *args: CORE_P.args, **kwargs: CORE_P.kwargs
                    ) -> Union[FlextResult[R], r[R]]:
                        try:
                            return validated_func(*args, **kwargs)
                        except ValidationError as e:
                            return r.fail(str(e))

                    return wrapper

                @staticmethod
                def validated_with_auto_result[**P, R](
                    func: Callable[P, R | r[R]],
                ) -> Callable[P, r[R]]:
                    """ValidationError -> r.fail() with auto-wrap.

                    Extended version that accepts functions returning R or r[R]
                    and always returns r[R] for railway pattern compatibility.

                    Business Rule:
                    --------------
                    Wraps a function with Pydantic validate_call and converts
                    ValidationError to r.fail(). Accepts functions returning R
                    or r[R] and always returns r[R] for railway pattern compatibility.

                    This is a NEW method (not override) to avoid bad-override issues
                    while providing extended functionality beyond parent class.

                    Audit Implications:
                    --------------------
                    - All validation errors are captured and returned as
                    r failures
                    - Original function signature is preserved for type checking
                    - Runtime validation ensures data integrity before execution
                    - Result is wrapped in r[R] if function returns R, otherwise
                    returns r[R] directly
                    """
                    validated_func = validate_call(
                        config=ConfigDict(arbitrary_types_allowed=True),
                        validate_return=False,
                    )(func)

                    @wraps(func)
                    def wrapper(*args: P.args, **kwargs: P.kwargs) -> r[R]:
                        try:
                            validated_result = validated_func(*args, **kwargs)
                            # Type narrowing: validated_func returns r[R] per signature
                            # But runtime may return R if func was R | r[R], so we handle both
                            if isinstance(validated_result, r):
                                return validated_result
                            # Runtime type narrowing: if not r[R], it's R, wrap it
                            # validated_result is R at this point (after isinstance check)
                            return r.ok(validated_result)
                        except ValidationError as e:
                            return r.fail(str(e))

                    return wrapper

                @staticmethod
                def _validate_flexible_value(
                    value: t.GeneralValueType,
                ) -> t.FlexibleValue:
                    """Validate and convert GeneralValueType to FlexibleValue.

                    FlexibleValue = ScalarValue | Sequence[ScalarValue] | Mapping[str, ScalarValue]
                    This function validates that value is compatible with FlexibleValue.
                    """
                    # ScalarValue types
                    if isinstance(value, (str, int, float, bool, type(None))):
                        return value
                    # Sequence[ScalarValue] - validate all items are ScalarValue
                    if isinstance(value, (list, tuple)):
                        if all(
                            isinstance(item, (str, int, float, bool, type(None)))
                            for item in value
                        ):
                            return value
                        msg = "Sequence values must all be ScalarValue"
                        raise TypeError(msg)
                    # Mapping[str, ScalarValue] - validate all values are ScalarValue
                    if isinstance(value, dict):
                        if all(
                            isinstance(v, (str, int, float, bool, type(None)))
                            for v in value.values()
                        ):
                            return value
                        msg = "Mapping values must all be ScalarValue"
                        raise TypeError(msg)
                    msg = f"Value must be ScalarValue, Sequence[ScalarValue], or Mapping[str, ScalarValue], got {type(value).__name__}"
                    raise TypeError(msg)

                @staticmethod
                def parse_kwargs[E: StrEnum](
                    kwargs: Mapping[str, t.FlexibleValue],
                    enum_fields: Mapping[str, type[E]],
                ) -> r[dict[str, t.FlexibleValue]]:
                    """Parse kwargs converting string enum values (mnemonic: 'parse_kwargs').

                    Returns JsonDict since parsed values are JSON-compatible.

                    """
                    # Convert to dict and normalize values
                    parsed: dict[str, t.FlexibleValue] = u_core.mapper().to_dict(kwargs)
                    for k, v in parsed.items():
                        if isinstance(v, dict):
                            # Type cast: dict[str, FlexibleValue] is compatible with dict[str, GeneralValueType]
                            # FlexibleValue is a subset of GeneralValueType
                            if not isinstance(v, dict):
                                msg = "v must be dict"
                                raise TypeError(msg)
                            v_dict: dict[str, t.GeneralValueType] = v
                            t_result = u.transform(v_dict, to_json=True)
                            if t_result.is_success:
                                # Use .value directly instead of deprecated .unwrap()
                                # Type narrowing: value is ConfigurationDict (dict[str, GeneralValueType])
                                # transform returns ConfigurationDict, but FlexibleValue needs Mapping[str, ScalarValue]
                                # ConfigurationDict is dict[str, GeneralValueType] which includes dict[str, JsonValue]
                                # JsonValue is ScalarValue, so this is compatible at runtime
                                # Type narrowing: validate that value is compatible with FlexibleValue
                                transformed_value = t_result.value
                                # Runtime validation: transformed_value is dict[str, GeneralValueType]
                                # FlexibleValue = ScalarValue | Sequence[ScalarValue] | Mapping[str, ScalarValue]
                                # dict[str, ScalarValue] is Mapping[str, ScalarValue], so it's compatible
                                # Type narrowing: validate all values are ScalarValue-compatible
                                if not isinstance(transformed_value, dict):
                                    msg = "transformed value must be dict"
                                    raise TypeError(msg)
                                # Validate all dict values are ScalarValue (str, int, float, bool, None)
                                # This ensures dict[str, ScalarValue] which is Mapping[str, ScalarValue] = FlexibleValue
                                if not all(
                                    isinstance(v, (str, int, float, bool, type(None)))
                                    for v in transformed_value.values()
                                ):
                                    msg = "dict values must all be ScalarValue (str, int, float, bool, None)"
                                    raise TypeError(msg)
                                # Type narrowing: validated dict is dict[str, ScalarValue] = Mapping[str, ScalarValue] = FlexibleValue
                                # Create validated dict with explicit type annotation for type narrowing
                                validated_dict: dict[
                                    str, str | int | float | bool | None
                                ] = {}
                                for key, val in transformed_value.items():
                                    if not isinstance(key, str):
                                        msg = "dict keys must be strings"
                                        raise TypeError(msg)
                                    if isinstance(
                                        val, (str, int, float, bool, type(None))
                                    ):
                                        validated_dict[key] = val
                                # Type narrowing: validated_dict is dict[str, ScalarValue] = Mapping[str, ScalarValue] = FlexibleValue
                                parsed[k] = validated_dict

                    # Convert enum fields using try_parse
                    errors: list[str] = []
                    for k, enum_cls in enum_fields.items():
                        if k in parsed:
                            parsed_val = parsed[k]
                            # Only parse if it's a string
                            if isinstance(parsed_val, str):
                                enum_result = u.Enum.parse(enum_cls, parsed_val)
                                enum_val = (
                                    enum_result.value
                                    if enum_result.is_success
                                    else None
                                )
                                if enum_val is not None:
                                    parsed[k] = (
                                        enum_val.value
                                        if hasattr(enum_val, "value")
                                        else str(enum_val)
                                    )
                                else:
                                    errors.append(f"{k}: '{parsed_val}'")

                    if errors:
                        return r.fail(f"Invalid: {errors}")
                    return r.ok(parsed)

                @staticmethod
                def get_enum_params(
                    func: u_core.Args._CallableWithHints,
                ) -> dict[str, type[StrEnum]]:
                    """Extract StrEnum parameters from function signature."""
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
                """Model utilities extending u_core.Model via inheritance.

                Exposes all flext-core Model methods through inheritance hierarchy.
                Adds CLI-specific model operations with GeneralValueType compatibility.
                """

                @staticmethod
                def from_dict[M: BaseModel](
                    model_cls: type[M],
                    data: Mapping[str, t.FlexibleValue],
                    *,
                    strict: bool = False,
                ) -> r[M]:
                    """Create model from dict with r.

                    Overrides u_core.Model.from_dict() with FlexibleValue compatibility.
                    Delegates to parent method for consistency.

                    Business Rule:
                    --------------
                    Converts a Mapping to a Pydantic model instance using
                    model_validate. The model_cls must be a subclass of
                    FlextModels (which extends BaseModel).

                    Audit Implications:
                    --------------------
                    - All model creation goes through Pydantic validation
                    - Invalid data returns r.fail() with error message
                    - Strict mode enforces exact type matching (no coercion)
                    """
                    result = u_core.Model.from_dict(model_cls, data, strict=strict)
                    # Convert RuntimeResult to FlextResult (r[M])
                    return (
                        r[M].ok(result.value)
                        if result.is_success
                        else r[M].fail(result.error or "")
                    )

                @staticmethod
                def merge_defaults[M: BaseModel](
                    model_cls: type[M],
                    defaults: Mapping[str, t.FlexibleValue],
                    overrides: Mapping[str, t.FlexibleValue],
                ) -> r[M]:
                    """Merge defaults with overrides and create model (mnemonic: 'merge_defaults').

                    Overrides u_core.Model.merge_defaults() with FlexibleValue compatibility.
                    Delegates to parent method for consistency.

                    """
                    result = u_core.Model.merge_defaults(
                        model_cls,
                        defaults,
                        overrides,
                    )
                    # Convert RuntimeResult to FlextResult (r[M])
                    return (
                        r[M].ok(result.value)
                        if result.is_success
                        else r[M].fail(result.error or "")
                    )

                @staticmethod
                def update[M: BaseModel](
                    instance: M,
                    **updates: t.FlexibleValue,
                ) -> r[M]:
                    """Update model with new values (mnemonic: 'update').

                    Overrides u_core.Model.update() with FlexibleValue compatibility.
                    Delegates to parent method for consistency.

                    """
                    result = u_core.Model.update(instance, **updates)
                    # Convert RuntimeResult to FlextResult (r[M])
                    return (
                        r[M].ok(result.value)
                        if result.is_success
                        else r[M].fail(result.error or "")
                    )

            # ═══════════════════════════════════════════════════════════════════
            # NESTED CLASS: Pydantic Type Factories
            # ═══════════════════════════════════════════════════════════════════

            class Pydantic:
                """Annotated type factories.

                Provides factory methods for creating Annotated types with validators.
                """

                @staticmethod
                def coerced_enum[E: StrEnum](
                    enum_cls: type[E],
                ) -> object:
                    """Create Annotated type for StrEnum coercion (mnemonic: 'coerced_enum').

                    Returns Annotated[E, BeforeValidator] wrapped type for Pydantic validation.
                    """
                    validator = (
                        FlextCliUtilities.Cli.TypeNormalizer.Enum.coerce_validator(
                            enum_cls
                        )
                    )
                    # Return Annotated type with validator
                    return Annotated[enum_cls, BeforeValidator(validator)]


u = FlextCliUtilities

__all__ = [
    "FlextCliUtilities",
    "u",
]
