"""FLEXT CLI Utilities - Reusable helpers and utilities for CLI operations.

Provides CLI-specific utility functions building on flext-core u,
eliminating code duplication across modules following SOLID and DRY principles.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import os
import sys
import types
from collections.abc import Callable, Iterable, Mapping
from enum import StrEnum
from functools import wraps
from pathlib import Path
from typing import (
    Annotated,
    Self,
    TypeGuard,
    Union,
    cast,
    get_args,
    get_origin,
    get_type_hints,
)

from flext_core import (
    FlextConstants,
    FlextDecorators,
    FlextExceptions,
    FlextHandlers,
    FlextMixins,
    FlextModels,
    FlextProtocols,
    FlextService,
    r,
    t,
    u,
)
from flext_core.utilities import FlextUtilities
from pydantic import (
    BaseModel,
    BeforeValidator,
    ConfigDict,
    ValidationError,
    validate_call,
)

from flext_cli.constants import FlextCliConstants

# Aliases for static method calls and type references
# Use u.* for FlextUtilities static methods
# Use t.* for FlextTypes type references
# Use c.* for FlextConstants constants
# Use m.* for FlextModels model references
# Use p.* for FlextProtocols protocol references
# Use r.* for r methods
# Use e.* for FlextExceptions
# Use d.* for FlextDecorators decorators
# Use s.* for FlextService service base
# Use x.* for FlextMixins mixins
# Use h.* for FlextHandlers handlers
# u is already imported from flext_core
# t is already imported from flext_core
c = FlextConstants
m = FlextModels
p = FlextProtocols
e = FlextExceptions
d = FlextDecorators
s = FlextService
x = FlextMixins
h = FlextHandlers

# Removed unused type alias - use Callable directly


class FlextCliUtilities(FlextUtilities):
    """FLEXT CLI Utilities - Centralized helpers eliminating code duplication.

    Business Rules:
    ───────────────
    1. All utility methods MUST be static (no instance state)
    2. All operations MUST return r[T] for error handling
    3. Field validation MUST enforce business rules (trace requires debug)
    4. Type normalization MUST preserve type safety (no Any types)
    5. Common patterns MUST be consolidated here (DRY principle)
    6. CLI-specific helpers MUST extend flext-core u
    7. All validators MUST use Pydantic validators when applicable
    8. Type conversion MUST handle Python 3.13+ patterns (PEP 695, UnionType)

    Architecture Implications:
    ───────────────────────────
    - Single source of truth eliminates code duplication across modules
    - Static methods ensure thread safety and no side effects
    - Railway-Oriented Programming via r for composable error handling
    - Type normalization enables Typer compatibility without type loss
    - Validation helpers enforce business rules consistently

    Audit Implications:
    ───────────────────
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

    # =========================================================================
    # BASE UTILITIES - Use u wrappers needed
    # =========================================================================
    # All data mapping operations use uirectly
    # Use t.GeneralValueType and t.JsonDict directly
    # No wrappers - direct API usage from flext-core
    # =========================================================================

    # =========================================================================
    # CLI VALIDATION - CLI-specific validation helpers
    # =========================================================================

    class CliValidation:
        """CLI-specific validation operations.

        Eliminates code duplication in models.py validate_business_rules methods.
        All validators return r[bool] for railway pattern composition.

        Advanced builder/DSL patterns for parametrized validation:
        - v() - Generic validator with builder pattern (combines multiple rules)
        - v_in() - Validate value in collection (mnemonic: "validate in")
        - v_eq() - Validate equality (mnemonic: "validate equals")
        - v_req() - Validate required fields in dict (mnemonic: "validate required")
        - v_type() - Validate type (mnemonic: "validate type")
        - v_conv() - Convert and validate (mnemonic: "validate convert")
        - v_choice() - Generic choice validator (replaces specialized validators)

        """

        class VBuilder:
            """Fluent builder for CLI validation (mnemonic: 'V' = Validate).

            Advanced DSL pattern for composable validation rules.
            Enables fluent chaining: v(val).name("x").non_empty().in_([...]).build()

            Example:
                >>> result = CliValidation.VBuilder(val).name("status").non_empty().in_(["a", "b"]).build()
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
                return FlextCliUtilities.CliValidation.v(
                    self._val,
                    name=self._name,
                    empty=self._empty,
                    in_list=self._in_list,
                    eq=self._eq,
                    msg=self._msg,
                )

        @staticmethod
        def v(  # noqa: PLR0913
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
            if not empty:
                v_result = u.validate(val, u.V.string.non_empty, field_name=name)
                if v_result.is_failure:
                    return r[bool].fail(
                        msg
                        or v_result.error
                        or FlextCliConstants.MixinsValidationMessages.FIELD_CANNOT_BE_EMPTY.format(
                            field_name=name,
                        ),
                    )
            # In-list check
            if in_list is not None:
                val_str = u.convert(val, str, "")
                if val_str not in set(in_list):
                    return r[bool].fail(
                        msg
                        or FlextCliConstants.MixinsValidationMessages.INVALID_ENUM_VALUE.format(
                            field_name=name,
                            valid_values=in_list,
                        ),
                    )
            # Equality check
            if eq is not None:
                val_str = u.convert(val, str, "")
                if val_str != eq:
                    return r[bool].fail(
                        msg
                        or FlextCliConstants.MixinsValidationMessages.COMMAND_STATE_INVALID.format(
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
            return FlextCliUtilities.CliValidation.v(
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
            return FlextCliUtilities.CliValidation.v(val, name=name, eq=eq)

        @staticmethod
        def v_empty(
            val: t.GeneralValueType | None,
            *,
            name: str = "field",
        ) -> r[bool]:
            """Validate field not empty (mnemonic: 'v_empty' = validate empty).

            Shortcut: v(val).name(name).non_empty().build()

            Args:
                val: Value to validate
                name: Field name for errors

            Returns:
                r[bool]: True if not empty, failure otherwise

            """
            return FlextCliUtilities.CliValidation.VBuilder(val).name(name).non_empty().build()

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
            return FlextCliUtilities.CliValidation.v_in(
                field_value,
                valid=valid_values,
                name=field_name,
            )

        @staticmethod
        def v_status(status: str) -> r[bool]:
            """Validate command status (mnemonic: 'v_status').

            Shortcut: v_choice(status, choices=COMMAND_STATUSES_LIST, name="status")

            """
            return FlextCliUtilities.CliValidation.v_choice(
                status,
                choices=FlextCliConstants.COMMAND_STATUSES_LIST,
                name="status",
            )

        @staticmethod
        def v_level(level: str) -> r[bool]:
            """Validate debug level (mnemonic: 'v_level').

            Shortcut: v_choice(level, choices=DEBUG_LEVELS_LIST, name="level")

            """
            return FlextCliUtilities.CliValidation.v_choice(
                level,
                choices=FlextCliConstants.DEBUG_LEVELS_LIST,
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
            format_str = u.convert(format_type, str, "").lower()
            result = FlextCliUtilities.CliValidation.v_choice(
                format_str,
                choices=FlextCliConstants.OUTPUT_FORMATS_LIST,
                name="format",
            )
            if result.is_failure:
                return r[str].fail(
                    FlextCliConstants.ErrorMessages.INVALID_OUTPUT_FORMAT.format(
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
                >>> result = CliValidation.v_choice("active", choices=["active", "pending"], name="status")
                >>> # Replaces: validate_command_status("active")

            """
            return FlextCliUtilities.CliValidation.v_in(val, valid=choices, name=name)

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
                return FlextCliUtilities.CliValidation.v_eq(current, eq=required, name=name)
            if valid is not None:
                return FlextCliUtilities.CliValidation.v_in(current, valid=valid, name=name)
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
            return FlextCliUtilities.CliValidation.v_state(current, valid=valid, name="session_status")

        @staticmethod
        def v_step(step: t.JsonDict | None) -> r[bool]:
            """Validate pipeline step (mnemonic: 'v_step').

            Args:
                step: Pipeline step dict to validate

            Returns:
                r[bool]: True if valid, failure otherwise

            """
            if step is None:
                return r[bool].fail(
                    FlextCliConstants.MixinsValidationMessages.PIPELINE_STEP_EMPTY,
                )

            field_name = FlextCliConstants.MixinsFieldNames.PIPELINE_STEP_NAME
            if field_name not in step:
                return r[bool].fail(
                    FlextCliConstants.MixinsValidationMessages.PIPELINE_STEP_NO_NAME,
                )

            step_name = step[field_name]
            return FlextCliUtilities.CliValidation.VBuilder(step_name).name(
                "Pipeline step name"
            ).non_empty().msg(
                FlextCliConstants.MixinsValidationMessages.PIPELINE_STEP_NAME_EMPTY
            ).build()

        @staticmethod
        def v_req(
            data: t.JsonDict | None,
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
                    FlextCliConstants.MixinsValidationMessages.CONFIG_MISSING_FIELDS.format(
                        missing_fields=fields,
                    ),
                )
            missing = u.filter(fields, lambda f: f not in data)
            if missing:
                return r[bool].fail(
                    FlextCliConstants.MixinsValidationMessages.CONFIG_MISSING_FIELDS.format(
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
            return r[bool].fail(f"{name} must be {type_names}, got {type(val).__name__}")

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
            config: t.JsonDict | None,
            *,
            fields: list[str],
        ) -> r[bool]:
            """Validate configuration (mnemonic: 'v_config').

            Shortcut: v_req(config, fields=fields)

            """
            return FlextCliUtilities.CliValidation.v_req(config, fields=fields)

        # ═══════════════════════════════════════════════════════════════════
        # COMPATIBILITY ALIASES - Maintain backward compatibility
        # ═══════════════════════════════════════════════════════════════════

        @staticmethod
        def validate_field_not_empty(
            field_value: t.GeneralValueType | None,
            field_display_name: str,
        ) -> r[bool]:
            """Compatibility alias for v_empty()."""
            return FlextCliUtilities.CliValidation.v_empty(field_value, name=field_display_name)

        @staticmethod
        def validate_command_status(status: str) -> r[bool]:
            """Compatibility alias for v_status()."""
            return FlextCliUtilities.CliValidation.v_status(status)

        @staticmethod
        def validate_debug_level(level: str) -> r[bool]:
            """Compatibility alias for v_level()."""
            return FlextCliUtilities.CliValidation.v_level(level)

        @staticmethod
        def validate_output_format(format_type: str) -> r[str]:
            """Compatibility alias for v_format()."""
            return FlextCliUtilities.CliValidation.v_format(format_type)

        @staticmethod
        def validate_string_not_empty(
            value: str | None,
            error_message: str,
        ) -> r[bool]:
            """Compatibility alias for v_empty()."""
            result = FlextCliUtilities.CliValidation.v_empty(value, name="Value")
            if result.is_failure:
                return r[bool].fail(error_message)
            return result

        @staticmethod
        def validate_str_enum_value(
            enum_class: type[StrEnum],
            value: str,
        ) -> StrEnum | None:
            """Compatibility alias - delegates to u.Enum.try_parse()."""
            result = u.Enum.parse(enum_class, value)
            return result.value if result.is_success else None

        @staticmethod
        def validate_command_execution_state(
            current_status: str,
            required_status: str,
            operation: str,
        ) -> r[bool]:
            """Compatibility alias for v_state()."""
            return FlextCliUtilities.CliValidation.v_state(
                current_status, required=required_status, name=operation
            )

        @staticmethod
        def validate_session_state(
            current_status: str,
            valid_states: list[str],
        ) -> r[bool]:
            """Compatibility alias for v_session()."""
            return FlextCliUtilities.CliValidation.v_session(current_status, valid=valid_states)

        @staticmethod
        def validate_pipeline_step(step: t.JsonDict | None) -> r[bool]:
            """Compatibility alias for v_step()."""
            return FlextCliUtilities.CliValidation.v_step(step)

        @staticmethod
        def validate_configuration_consistency(
            config_data: t.JsonDict | None,
            required_fields: list[str],
        ) -> r[bool]:
            """Compatibility alias for v_config()."""
            return FlextCliUtilities.CliValidation.v_config(config_data, fields=required_fields)

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
                >>> paths = FlextCliUtilities.ConfigOps.get_config_paths()
                >>> for path in paths:
                ...     print(path)

            """
            home = Path.home()
            flext_dir = home / FlextCliConstants.FLEXT_DIR_NAME
            return FlextCliUtilities.ConfigOps.paths(
                flext_dir,
                FlextCliConstants.DictKeys.CONFIG,
                FlextCliConstants.Subdirectories.CACHE,
                FlextCliConstants.Subdirectories.LOGS,
                FlextCliConstants.DictKeys.TOKEN,
                FlextCliConstants.Subdirectories.REFRESH_TOKEN,
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
            ok = FlextCliConstants.Symbols.SUCCESS_MARK
            fail = FlextCliConstants.Symbols.FAILURE_MARK

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
                            FlextCliConstants.CmdMessages.SUBDIR_EXISTS.format(
                                symbol=ok,
                                subdir=subdir,
                            ),
                        )
                    else:
                        results.append(
                            FlextCliConstants.CmdMessages.SUBDIR_MISSING.format(
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
                list[str]: Validation results with ✓/✗ marks for each check

            Example:
                >>> results = FlextCliUtilities.ConfigOps.validate_config_structure()
                >>> for result in results:
                ...     print(result)
                ✓ Configuration directory exists
                ✓ config/ subdirectory exists
                ...

            """
            home = Path.home()
            flext_dir = home / FlextCliConstants.FLEXT_DIR_NAME
            return FlextCliUtilities.ConfigOps.check(
                flext_dir,
                name="Configuration",
                subdirs=FlextCliConstants.Subdirectories.STANDARD_SUBDIRS,
            )

        @staticmethod
        def info(
            path: Path,
            *,
            dir_key: str = FlextCliConstants.DictKeys.CONFIG_DIR,
            exists_key: str = FlextCliConstants.DictKeys.CONFIG_EXISTS,
            readable_key: str = FlextCliConstants.DictKeys.CONFIG_READABLE,
            writable_key: str = FlextCliConstants.DictKeys.CONFIG_WRITABLE,
        ) -> t.JsonDict:
            """Generic info builder (mnemonic: 'info').

            Builds dict with path info (exists, readable, writable, timestamp).

            Args:
                path: Path to get info for
                dir_key: Key for directory path
                exists_key: Key for existence status
                readable_key: Key for readable status
                writable_key: Key for writable status

            Returns:
                t.JsonDict: Info dictionary

            """
            exists = path.exists()
            return {
                dir_key: str(path),
                exists_key: exists,
                readable_key: exists and os.access(path, os.R_OK),
                writable_key: exists and os.access(path, os.W_OK),
                FlextCliConstants.DictKeys.TIMESTAMP: u.generate("timestamp"),
            }

        @staticmethod
        def get_config_info() -> t.JsonDict:
            """Get FLEXT CLI configuration information.

            Delegates to info() for consistency.

            Returns:
                t.JsonDict: Configuration information dictionary

            Example:
                >>> info = FlextCliUtilities.ConfigOps.get_config_info()
                >>> print(f"Config dir: {info['config_dir']}")
                >>> print(f"Exists: {info['exists']}")

            """
            home = Path.home()
            flext_dir = home / FlextCliConstants.FLEXT_DIR_NAME
            return FlextCliUtilities.ConfigOps.info(flext_dir)

    # =========================================================================
    # FILE OPS - File operation helpers
    # =========================================================================

    class FileOps:
        """File operation helpers for error detection and common patterns.

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
        )

        @staticmethod
        def matches(
            msg: str,
            *patterns: str,
        ) -> bool:
            """Generic pattern matcher (mnemonic: 'matches').

            Checks if message matches any pattern (case-insensitive).

            Args:
                msg: Message to check
                patterns: Patterns to match against

            Returns:
                bool: True if any pattern matches

            """
            return any(u.normalize(msg, p) for p in patterns)

        @staticmethod
        def is_file_not_found_error(error_msg: str) -> bool:
            """Check if an error message indicates a file-not-found error.

            Delegates to matches() for consistency.

            Args:
                error_msg: Error message string to check

            Returns:
                bool: True if error message indicates file not found, False otherwise

            """
            return FlextCliUtilities.FileOps.matches(
                error_msg,
                *FlextCliUtilities.FileOps.FILE_NOT_FOUND_PATTERNS,
            )

    # =========================================================================
    # TYPE NORMALIZER - Typer compatibility (from type_u.py)
    # =========================================================================

    class TypeNormalizer:
        """Type annotation normalization for Typer compatibility.

        Converts modern Python 3.10+ union syntax to Typer-compatible forms.
        Eliminates all code from type_u.py by consolidating here.

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

            # Handle single non-None type cases
            if len(non_none_args) == 1:
                inner_type = non_none_args[0]
                normalized_inner = (
                    FlextCliUtilities.TypeNormalizer.normalize_annotation(inner_type)
                )
                if normalized_inner is None:
                    return None
                # If has None, create Optional[T], otherwise return normalized type
                return (
                    normalized_inner | types.NoneType if has_none else normalized_inner
                )

            # Handle multiple types case
            if len(non_none_args) > 1:
                # Recursively normalize all inner types
                normalized_non_none_list = [
                    normalized
                    for arg in non_none_args
                    if (
                        normalized
                        := FlextCliUtilities.TypeNormalizer.normalize_annotation(arg)
                    )
                    is not None
                ]

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
            def is_member[E: StrEnum](
                enum_cls: type[E], value: t.GeneralValueType
            ) -> TypeGuard[E]:
                """TypeGuard genérico para qualquer StrEnum.

                Delegates to u.Enum.is_member() for consistency.

                Verifica se value é um membro válido do enum_cls.

                Exemplo:
                    if FlextCliUtilities.TypeNormalizer.Enum.is_member(Status, value):
                        # value: Status
                        process_status(value)
                    else:
                        # value: GeneralValueType (narrowed corretamente!)
                        handle_invalid(value)
                """
                return u.Enum.is_member(enum_cls, value)

            @staticmethod
            def is_subset[E: StrEnum](
                enum_cls: type[E],
                valid_members: frozenset[E],
                value: t.GeneralValueType,
            ) -> TypeGuard[E]:
                """TypeGuard para subset de um StrEnum.

                Delegates to u.Enum.is_subset() for consistency.

                Verifica se value é um membro válido do enum_cls e está no subset valid_members.

                Exemplo:
                    ACTIVE_STATES = frozenset({Status.ACTIVE, Status.PENDING})

                    if FlextCliUtilities.TypeNormalizer.Enum.is_subset(Status, ACTIVE_STATES, value):
                        # value: Status (e sabemos que é ACTIVE ou PENDING)
                        process_active(value)
                """
                return u.Enum.is_subset(enum_cls, valid_members, value)

            # ─────────────────────────────────────────────────────────────
            # CONVERSÃO: String → StrEnum (type-safe)
            # ─────────────────────────────────────────────────────────────

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

                Exemplo:
                    result = FlextCliUtilities.TypeNormalizer.Enum.parse(Status, "active")
                    if result.is_success:
                        status: Status = result.value

                """
                return u.Enum.parse(enum_cls, value)

            @staticmethod
            def parse_or_default[E: StrEnum](
                enum_cls: type[E],
                value: str | E | None,
                default: E,
            ) -> E:
                """Parse with default fallback (mnemonic: 'parse_or_default').

                Delegates to u.Enum.parse_or_default() for consistency.

                Never fails - returns default if parsing fails.

                Exemplo:
                    status = FlextCliUtilities.TypeNormalizer.Enum.parse_or_default(
                        Status, user_input, Status.PENDING
                    )

                """
                return u.Enum.parse_or_default(enum_cls, value, default)

            # ─────────────────────────────────────────────────────────────
            # PYDANTIC VALIDATORS: BeforeValidator factories
            # ─────────────────────────────────────────────────────────────

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

                PADRÃO RECOMENDADO para campos Pydantic:

                Exemplo:
                    CoercedStatus = Annotated[
                        Status,
                        BeforeValidator(FlextCliUtilities.TypeNormalizer.Enum.coerce_validator(Status))
                    ]

                """
                return lambda v: FlextCliUtilities.TypeNormalizer.Enum.coerce_impl(
                    enum_cls, v, by_name=False
                )

            @staticmethod
            def coerce_by_name_validator[E: StrEnum](
                enum_cls: type[E],
            ) -> Callable[[t.GeneralValueType], E]:
                """BeforeValidator accepting name OR value (mnemonic: 'coerce_by_name_validator').

                Aceita: "ACTIVE" (nome), "active" (valor), Status.ACTIVE (membro).

                """
                return lambda v: FlextCliUtilities.TypeNormalizer.Enum.coerce_impl(
                    enum_cls, v, by_name=True
                )

            # ─────────────────────────────────────────────────────────────
            # METADATA: Informações sobre StrEnums
            # ─────────────────────────────────────────────────────────────

            @staticmethod
            def values[E: StrEnum](enum_cls: type[E]) -> frozenset[str]:
                """Retorna frozenset dos valores (cached para performance).

                Delegates to u.Enum.values() for consistency.

                """
                return u.Enum.values(enum_cls)

            @staticmethod
            def names[E: StrEnum](enum_cls: type[E]) -> frozenset[str]:
                """Retorna frozenset dos nomes dos membros (cached).

                Delegates to u.Enum.names() for consistency.

                """
                return u.Enum.names(enum_cls)

            @staticmethod
            def members[E: StrEnum](enum_cls: type[E]) -> frozenset[E]:
                """Retorna frozenset dos membros (cached).

                Delegates to u.Enum.members() for consistency.

                """
                return u.Enum.members(enum_cls)

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
            ) -> r[tuple[E, ...]]:
                """Parse sequence to tuple of StrEnum (mnemonic: 'parse_sequence').

                Delegates to u.Collection.parse_sequence() for consistency.

                Exemplo:
                    result = FlextCliUtilities.Collection.parse_sequence(
                        Status, ["active", "pending"]
                    )
                    if result.is_success:
                        statuses: tuple[Status, ...] = result.value

                """
                return u.Collection.parse_sequence(enum_cls, values)

            @staticmethod
            def coerce_list_validator[E: StrEnum](
                enum_cls: type[E],
            ) -> Callable[[t.GeneralValueType], list[E]]:
                """BeforeValidator for list of StrEnums (mnemonic: 'coerce_list_validator').

                Exemplo:
                    StatusList = Annotated[
                        list[Status],
                        BeforeValidator(FlextCliUtilities.Collection.coerce_list_validator(Status))
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

            # ─────────────────────────────────────────────────────────────
            # DICT CONVERSIONS
            # ─────────────────────────────────────────────────────────────

            @staticmethod
            def parse_mapping[E: StrEnum](
                enum_cls: type[E],
                mapping: Mapping[str, str | E],
            ) -> r[dict[str, E]]:
                """Parse mapping to dict with StrEnum values (mnemonic: 'parse_mapping').

                Delegates to u.Collection.parse_mapping() for consistency.

                Exemplo:
                    result = FlextCliUtilities.Collection.parse_mapping(
                        Status, {"user1": "active", "user2": "pending"}
                    )

                """
                return u.Collection.parse_mapping(enum_cls, mapping)

            @staticmethod
            def coerce_dict_validator[E: StrEnum](
                enum_cls: type[E],
            ) -> Callable[[t.GeneralValueType], dict[str, E]]:
                """BeforeValidator for dict with StrEnum values (mnemonic: 'coerce_dict_validator').

                Exemplo:
                    StatusDict = Annotated[
                        dict[str, Status],
                        BeforeValidator(FlextCliUtilities.Collection.coerce_dict_validator(Status))
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

        # ═══════════════════════════════════════════════════════════════════
        # NESTED CLASS: Args Utilities
        # ═══════════════════════════════════════════════════════════════════

        class Args:
            """@validated, parse_kwargs - ZERO boilerplate de validação."""

            @staticmethod
            def validated[**P, R](func: Callable[P, R]) -> Callable[P, R]:
                """Decorator com validate_call - aceita str OU enum, converte auto."""
                return validate_call(
                    config=ConfigDict(
                        arbitrary_types_allowed=True, use_enum_values=False
                    ),
                    validate_return=False,
                )(func)

            @staticmethod
            def validated_with_result[**P, R](
                func: Callable[P, R],
            ) -> Callable[P, r[R]]:
                """ValidationError → r.fail().

                Business Rule:
                ──────────────
                Wraps a function with Pydantic validate_call and converts
                ValidationError to r.fail(). Preserves original
                function signature using ParamSpec for type safety.

                Audit Implications:
                ───────────────────
                - All validation errors are captured and returned as
                  r failures
                - Original function signature is preserved for type checking
                - Runtime validation ensures data integrity before execution
                """
                validated_func = validate_call(
                    config=ConfigDict(arbitrary_types_allowed=True),
                    validate_return=False,
                )(func)

                @wraps(func)
                def wrapper(*args: P.args, **kwargs: P.kwargs) -> r[R]:
                    try:
                        result: R = validated_func(*args, **kwargs)
                        return r.ok(result)
                    except ValidationError as e:
                        return r.fail(str(e))

                return wrapper

            @staticmethod
            def parse_kwargs[E: StrEnum](
                kwargs: Mapping[str, t.GeneralValueType],
                enum_fields: Mapping[str, type[E]],
            ) -> r[t.JsonDict]:
                """Parse kwargs converting string enum values (mnemonic: 'parse_kwargs').

                Returns JsonDict since parsed values are JSON-compatible.

                """
                # Convert to dict and normalize values
                parsed: dict[str, t.GeneralValueType] = dict(kwargs)
                for k, v in parsed.items():
                    if isinstance(v, dict):
                        t_result = u.transform(v, to_json=True)
                        if t_result.is_success:
                            parsed[k] = t_result.unwrap()

                # Convert enum fields using try_parse
                errors: list[str] = []
                for k, enum_cls in enum_fields.items():
                    if k in parsed:
                        parsed_val = parsed[k]
                        # Only parse if it's a string
                        if isinstance(parsed_val, str):
                            enum_result = u.Enum.parse(enum_cls, parsed_val)
                            enum_val = enum_result.value if enum_result.is_success else None
                            if enum_val is not None:
                                parsed[k] = enum_val.value if hasattr(enum_val, "value") else str(enum_val)
                            else:
                                errors.append(f"{k}: '{parsed_val}'")

                if errors:
                    return r.fail(f"Invalid: {errors}")
                return r.ok(parsed)

            @staticmethod
            def get_enum_params(
                func: Callable[..., t.GeneralValueType],
            ) -> dict[str, type[StrEnum]]:
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
            def from_dict[M: type[FlextModels]](
                model_cls: type[M],
                data: Mapping[str, t.GeneralValueType],
                *,
                strict: bool = False,
            ) -> r[M]:
                """Create model from dict with r.

                Delegates to u.Model.from_dict() for consistency.
                Converts GeneralValueType to FlexibleValue for compatibility.

                Business Rule:
                ──────────────
                Converts a Mapping to a Pydantic model instance using
                model_validate. The model_cls must be a subclass of
                FlextModels (which extends BaseModel).

                Audit Implications:
                ───────────────────
                - All model creation goes through Pydantic validation
                - Invalid data returns r.fail() with error message
                - Strict mode enforces exact type matching (no coercion)
                """
                # Convert GeneralValueType to FlexibleValue for u.Model compatibility
                flexible_data: dict[str, t.FlexibleValue] = {}
                for k, v in data.items():
                    # GeneralValueType is compatible with FlexibleValue
                    flexible_data[k] = cast("t.FlexibleValue", v)
                # Cast model_cls to BaseModel type for u.Model compatibility
                base_model_cls = cast("type[BaseModel]", model_cls)
                result = u.Model.from_dict(base_model_cls, flexible_data, strict=strict)
                return cast("r[M]", result)

            @staticmethod
            def merge_defaults[M: type[FlextModels]](
                model_cls: type[M],
                defaults: Mapping[str, t.GeneralValueType],
                overrides: Mapping[str, t.GeneralValueType],
            ) -> r[M]:
                """Merge defaults with overrides and create model (mnemonic: 'merge_defaults').

                Delegates to u.Model.merge_defaults() for consistency.
                Converts GeneralValueType to FlexibleValue for compatibility.

                """
                # Convert GeneralValueType to FlexibleValue for u.Model compatibility
                flexible_defaults: dict[str, t.FlexibleValue] = {
                    k: cast("t.FlexibleValue", v) for k, v in defaults.items()
                }
                flexible_overrides: dict[str, t.FlexibleValue] = {
                    k: cast("t.FlexibleValue", v) for k, v in overrides.items()
                }
                # Cast model_cls to BaseModel type for u.Model compatibility
                base_model_cls = cast("type[BaseModel]", model_cls)
                result = u.Model.merge_defaults(base_model_cls, flexible_defaults, flexible_overrides)
                return cast("r[M]", result)

            @staticmethod
            def update[M](instance: M, **updates: t.GeneralValueType) -> r[M]:
                """Update model with new values (mnemonic: 'update').

                Delegates to u.Model.update() for consistency.
                Converts GeneralValueType to FlexibleValue for compatibility.

                """
                # Convert GeneralValueType to FlexibleValue for u.Model compatibility
                flexible_updates: dict[str, t.FlexibleValue] = {
                    k: cast("t.FlexibleValue", v) for k, v in updates.items()
                }
                # Cast instance to BaseModel for u.Model compatibility
                base_instance = cast("BaseModel", instance)
                result = u.Model.update(base_instance, **flexible_updates)
                return cast("r[M]", result)

        # ═══════════════════════════════════════════════════════════════════
        # NESTED CLASS: Pydantic Type Factories
        # ═══════════════════════════════════════════════════════════════════

        class Pydantic:
            """Fábricas de Annotated types."""

            @staticmethod
            def coerced_enum[E: StrEnum](
                enum_cls: type[E],
            ) -> type[Annotated[E, BeforeValidator]]:
                """Create Annotated type for StrEnum coercion (mnemonic: 'coerced_enum')."""
                validator = FlextCliUtilities.TypeNormalizer.Enum.coerce_validator(enum_cls)
                return Annotated[enum_cls, BeforeValidator(validator)]


# Note: Aliases moved to avoid circular imports
# Use FlextCliModels.CliModelConverter and FlextCliModels.CliModelDecorators directly


__all__ = [
    "FlextCliUtilities",
]
