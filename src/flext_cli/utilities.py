"""FLEXT CLI utility facade and CLI-specific helpers."""
from __future__ import annotations
import os
import types
import typing as pytyping
from collections.abc import Callable, Mapping, Sequence
from datetime import UTC, datetime
from enum import StrEnum
from functools import wraps
from pathlib import Path
from typing import get_args, get_origin
from flext_core import FlextUtilities, r
from pydantic import BaseModel, ConfigDict, ValidationError, validate_call
from flext_cli.constants import c
from flext_cli.typings import CliExecutionMetadata, CliValidationResult, t
class FlextCliUtilities(FlextUtilities):
    class Cli(FlextUtilities):
        @staticmethod
        def process[T, U](
            items: Sequence[T],
            processor: Callable[[T], U],
            *,
            predicate: Callable[[T], bool] | None = None,
            on_error: str = "fail",
            filter_keys: set[str] | None = None,
            exclude_keys: set[str] | None = None,
        ) -> r[list[U]]:
            _ = filter_keys, exclude_keys
            errors: list[str] = []
            values: list[U] = []
            for idx, item in enumerate(items):
                if predicate is not None and not predicate(item):
                    continue
                try:
                    values.append(processor(item))
                except Exception as exc:
                    if on_error == "fail":
                        return r[list[U]].fail(f"Error at index {idx}: {exc}")
                    if on_error == "collect":
                        errors.append(f"[{idx}]: {exc}")
            return (
                r[list[U]].fail("; ".join(errors)) if errors else r[list[U]].ok(values)
            )
        @staticmethod
        def process_mapping[T, U](
            items: Mapping[str, T],
            processor: Callable[[str, T], U],
            on_error: str = "fail",
        ) -> r[dict[str, U]]:
            errors: list[str] = []
            values: dict[str, U] = {}
            for key, value in items.items():
                try:
                    values[key] = processor(key, value)
                except Exception as exc:
                    if on_error == "fail":
                        return r[dict[str, U]].fail(f"Error processing {key}: {exc}")
                    if on_error == "collect":
                        errors.append(f"{key}: {exc}")
            return (
                r[dict[str, U]].fail("; ".join(errors))
                if errors
                else r[dict[str, U]].ok(values)
            )
        @staticmethod
        def validate_required_string(value: str, *, context: str = "Value") -> None:
            checked = FlextCliUtilities.Cli.CliValidation.v_empty(value, name=context)
            if checked.is_failure:
                raise ValueError(checked.error or f"{context} cannot be empty")
        class CliValidation(FlextUtilities.Validation):
            @staticmethod
            def _to_str(value: t.GeneralValueType | None) -> str:
                return (
                    value
                    if isinstance(value, str)
                    else ""
                    if value is None
                    else str(value)
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
                if not empty:
                    check = FlextCliUtilities.Cli.CliValidation.v_empty(val, name=name)
                    if check.is_failure:
                        return r[bool].fail(msg or check.error or "")
                if in_list is not None:
                    val_str = FlextCliUtilities.Cli.CliValidation._to_str(val)
                    if val_str not in set(in_list):
                        err = (
                            c.Cli.MixinsValidationMessages.SESSION_STATUS_INVALID.format(
                                current_status=val_str, valid_states=in_list
                            )
                            if name == "session_status"
                            else c.Cli.MixinsValidationMessages.INVALID_ENUM_VALUE.format(
                                field_name=name, valid_values=in_list
                            )
                        )
                        return r[bool].fail(msg or err)
                if eq is not None:
                    val_str = FlextCliUtilities.Cli.CliValidation._to_str(val)
                    if val_str != eq:
                        err = (
                            c.Cli.MixinsValidationMessages.COMMAND_STATE_INVALID.format(
                                operation=name,
                                current_status=val_str,
                                required_status=eq,
                            )
                        )
                        return r[bool].fail(msg or err)
                return r[bool].ok(True)
            @staticmethod
            def v_empty(
                val: t.GeneralValueType | None, *, name: str = "field"
            ) -> r[bool]:
                if val is None or (
                    isinstance(val, str) and not FlextUtilities.is_string_non_empty(val)
                ):
                    return r[bool].fail(
                        c.Cli.MixinsValidationMessages.FIELD_CANNOT_BE_EMPTY.format(
                            field_name=name
                        )
                    )
                return r[bool].ok(True)
            @staticmethod
            def validate_field_in_list(
                field_value: str | float | None,
                *,
                valid_values: list[str],
                field_name: str,
            ) -> r[bool]:
                return FlextCliUtilities.Cli.CliValidation.v(
                    field_value, name=field_name, empty=False, in_list=valid_values
                )
            @staticmethod
            def v_status(status: str) -> r[bool]:
                return FlextCliUtilities.Cli.CliValidation.v(
                    status,
                    name="status",
                    empty=False,
                    in_list=c.Cli.ValidationLists.COMMAND_STATUSES,
                )
            @staticmethod
            def v_level(level: str) -> r[bool]:
                return FlextCliUtilities.Cli.CliValidation.v(
                    level,
                    name="level",
                    empty=False,
                    in_list=c.Cli.ValidationLists.DEBUG_LEVELS,
                )
            @staticmethod
            def v_format(format_type: str) -> r[str]:
                fmt = str(format_type).lower()
                valid = FlextCliUtilities.Cli.CliValidation.v(
                    fmt,
                    name="format",
                    empty=False,
                    in_list=c.Cli.ValidationLists.OUTPUT_FORMATS,
                )
                return (
                    r[str].ok(fmt)
                    if valid.is_success
                    else r[str].fail(
                        c.Cli.ErrorMessages.INVALID_OUTPUT_FORMAT.format(
                            format=format_type
                        )
                    )
                )
            @staticmethod
            def v_state(
                current: str,
                *,
                required: str | None = None,
                valid: list[str] | None = None,
                name: str = "state",
            ) -> r[bool]:
                if required is not None:
                    return FlextCliUtilities.Cli.CliValidation.v(
                        current, name=name, eq=required
                    )
                if valid is not None:
                    return FlextCliUtilities.Cli.CliValidation.v(
                        current, name=name, in_list=valid, empty=False
                    )
                return r[bool].fail(f"{name}: no validation criteria provided")
            @staticmethod
            def v_session(current: str, *, valid: list[str]) -> r[bool]:
                return FlextCliUtilities.Cli.CliValidation.v_state(
                    current, valid=valid, name="session_status"
                )
            @staticmethod
            def v_req(
                data: dict[str, t.GeneralValueType] | None, *, fields: list[str]
            ) -> r[bool]:
                if data is None:
                    return r[bool].fail(
                        c.Cli.MixinsValidationMessages.CONFIG_MISSING_FIELDS.format(
                            missing_fields=fields
                        )
                    )
                missing = [name for name in fields if name not in data]
                return (
                    r[bool].ok(True)
                    if not missing
                    else r[bool].fail(
                        c.Cli.MixinsValidationMessages.CONFIG_MISSING_FIELDS.format(
                            missing_fields=missing
                        )
                    )
                )
            @staticmethod
            def v_config(
                config: dict[str, t.GeneralValueType] | None, *, fields: list[str]
            ) -> r[bool]:
                return FlextCliUtilities.Cli.CliValidation.v_req(config, fields=fields)
            @staticmethod
            def v_step(step: dict[str, t.GeneralValueType] | None) -> r[bool]:
                if step is None:
                    return r[bool].fail(
                        c.Cli.MixinsValidationMessages.PIPELINE_STEP_EMPTY
                    )
                key = c.Cli.MixinsFieldNames.PIPELINE_STEP_NAME
                if key not in step:
                    return r[bool].fail(
                        c.Cli.MixinsValidationMessages.PIPELINE_STEP_NO_NAME
                    )
                value = step[key]
                if value is None or (isinstance(value, str) and not value.strip()):
                    return r[bool].fail(
                        c.Cli.MixinsValidationMessages.PIPELINE_STEP_NAME_EMPTY
                    )
                return r[bool].ok(True)
            @staticmethod
            def get_valid_output_formats() -> tuple[str, ...]:
                return tuple(sorted(c.Cli.ValidationMappings.OUTPUT_FORMAT_SET))
            @staticmethod
            def get_valid_command_statuses() -> tuple[str, ...]:
                return tuple(sorted(c.Cli.ValidationMappings.COMMAND_STATUS_SET))
        class Environment:
            @staticmethod
            def is_test_environment() -> bool:
                pytest_test = FlextUtilities.get(
                    os.environ, c.Cli.EnvironmentConstants.PYTEST_CURRENT_TEST
                )
                underscore = os.environ.get(c.Cli.EnvironmentConstants.UNDERSCORE, "")
                ci = os.environ.get(c.Cli.EnvironmentConstants.CI)
                return (
                    pytest_test is not None
                    or c.Cli.EnvironmentConstants.PYTEST in underscore.lower()
                    or ci == c.Cli.EnvironmentConstants.CI_TRUE_VALUE
                )
        class ConfigOps:
            @staticmethod
            def get_config_paths() -> list[str]:
                base = Path.home() / c.Cli.Paths.FLEXT_DIR_NAME
                return [
                    str(base),
                    str(base / c.Cli.DictKeys.CONFIG),
                    str(base / c.Cli.Subdirectories.CACHE),
                    str(base / c.Cli.Subdirectories.LOGS),
                    str(base / c.Cli.DictKeys.TOKEN),
                    str(base / c.Cli.Subdirectories.REFRESH_TOKEN),
                ]
            @staticmethod
            def validate_config_structure() -> list[str]:
                base = Path.home() / c.Cli.Paths.FLEXT_DIR_NAME
                ok = c.Cli.Symbols.SUCCESS_MARK
                fail = c.Cli.Symbols.FAILURE_MARK
                lines = [
                    f"{ok} Configuration directory exists"
                    if base.exists()
                    else f"{fail} Configuration directory missing"
                ]
                for subdir in c.Cli.Subdirectories.STANDARD_SUBDIRS:
                    path = base / subdir
                    lines.append(
                        c.Cli.CmdMessages.SUBDIR_EXISTS.format(symbol=ok, subdir=subdir)
                        if path.exists()
                        else c.Cli.CmdMessages.SUBDIR_MISSING.format(
                            symbol=fail, subdir=subdir
                        )
                    )
                return lines
            @staticmethod
            def get_config_info() -> Mapping[str, t.GeneralValueType]:
                path = Path.home() / c.Cli.Paths.FLEXT_DIR_NAME
                exists = path.exists()
                return {
                    c.Cli.DictKeys.CONFIG_DIR: str(path),
                    c.Cli.DictKeys.CONFIG_EXISTS: exists,
                    c.Cli.DictKeys.CONFIG_READABLE: exists and os.access(path, os.R_OK),
                    c.Cli.DictKeys.CONFIG_WRITABLE: exists and os.access(path, os.W_OK),
                    c.Cli.DictKeys.TIMESTAMP: datetime.now(UTC).isoformat(),
                }
        class FileOps:
            FILE_NOT_FOUND_PATTERNS: tuple[str, ...] = (
                "not found",
                "no such file",
                "does not exist",
                "errno 2",
                "cannot open",
            )
            @staticmethod
            def matches(msg: str, *patterns: str) -> bool:
                text = msg.lower()
                return any(pattern.lower() in text for pattern in patterns)
            @staticmethod
            def is_file_not_found_error(error_msg: str) -> bool:
                return FlextCliUtilities.Cli.FileOps.matches(
                    error_msg, *FlextCliUtilities.Cli.FileOps.FILE_NOT_FOUND_PATTERNS
                )
        class TypeNormalizer:
            @staticmethod
            def normalize_annotation(
                annotation: type | types.UnionType | None,
            ) -> type | types.UnionType | None:
                if annotation is None:
                    return None
                origin = get_origin(annotation)
                if origin is types.UnionType or origin is pytyping.Union:
                    return FlextCliUtilities.Cli.TypeNormalizer.normalize_union_type(
                        annotation
                    )
                if origin is not None and hasattr(origin, "__getitem__"):
                    args = get_args(annotation)
                    if args:
                        norm = tuple(
                            FlextCliUtilities.Cli.TypeNormalizer.normalize_annotation(
                                arg
                            )
                            for arg in args
                        )
                        try:
                            return origin[norm]
                        except (TypeError, AttributeError):
                            return annotation
                return annotation
            @staticmethod
            def normalize_union_type(
                annotation: type | types.UnionType,
            ) -> type | types.UnionType | None:
                args = get_args(annotation)
                if not args:
                    return annotation
                has_none = types.NoneType in args
                non_none = [arg for arg in args if arg is not types.NoneType]
                if len(non_none) == 1:
                    inner = FlextCliUtilities.Cli.TypeNormalizer.normalize_annotation(
                        non_none[0]
                    )
                    if inner is None:
                        return None
                    return inner | types.NoneType if has_none else inner
                if len(non_none) > 1:
                    normalized = [
                        item
                        for item in (
                            FlextCliUtilities.Cli.TypeNormalizer.normalize_annotation(
                                arg
                            )
                            for arg in non_none
                        )
                        if item is not None
                    ]
                    if not normalized:
                        return None
                    return (
                        FlextCliUtilities.Cli.TypeNormalizer.combine_types_with_union(
                            normalized, include_none=has_none
                        )
                    )
                return annotation
            @staticmethod
            def combine_types_with_union(
                types_list: list[type | types.UnionType], *, include_none: bool = False
            ) -> type | types.UnionType:
                result: type | types.UnionType = types_list[0]
                for item in types_list[1:]:
                    result |= item
                if include_none:
                    result |= types.NoneType
                return result
            class Args:
                @staticmethod
                def validated_with_result[**P, U](
                    func: Callable[P, r[U]],
                ) -> Callable[P, r[U]]:
                    wrapped = validate_call(
                        config=ConfigDict(arbitrary_types_allowed=True),
                        validate_return=False,
                    )(func)
                    @wraps(func)
                    def call(*args: P.args, **kwargs: P.kwargs) -> r[U]:
                        try:
                            return wrapped(*args, **kwargs)
                        except ValidationError as exc:
                            return r[U].fail(str(exc))
                    return call
                @staticmethod
                def parse_kwargs[E: StrEnum](
                    kwargs: Mapping[str, t.FlexibleValue],
                    enum_fields: Mapping[str, type[E]],
                ) -> r[dict[str, t.FlexibleValue]]:
                    parsed = FlextUtilities.mapper().to_dict(kwargs)
                    errors: list[str] = []
                    for key, enum_cls in enum_fields.items():
                        if key not in parsed:
                            continue
                        value = parsed[key]
                        if isinstance(value, str):
                            parsed_enum = FlextUtilities.Enum.parse(enum_cls, value)
                            if parsed_enum.is_success:
                                parsed[key] = parsed_enum.value.value
                            else:
                                errors.append(f"{key}: '{value}'")
                    return (
                        r[dict[str, t.FlexibleValue]].fail(f"Invalid: {errors}")
                        if errors
                        else r[dict[str, t.FlexibleValue]].ok(parsed)
                    )
            class Model:
                @staticmethod
                def from_dict[M: BaseModel](
                    model_cls: type[M],
                    data: Mapping[str, t.FlexibleValue],
                    *,
                    strict: bool = False,
                ) -> r[M]:
                    result = FlextUtilities.Model.from_dict(
                        model_cls, data, strict=strict
                    )
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
                    result = FlextUtilities.Model.merge_defaults(
                        model_cls, defaults, overrides
                    )
                    return (
                        r[M].ok(result.value)
                        if result.is_success
                        else r[M].fail(result.error or "")
                    )
                @staticmethod
                def update[M: BaseModel](
                    instance: M, **updates: t.FlexibleValue
                ) -> r[M]:
                    result = FlextUtilities.Model.update(instance, **updates)
                    return (
                        r[M].ok(result.value)
                        if result.is_success
                        else r[M].fail(result.error or "")
                    )
            class Pydantic:
                @staticmethod
                def coerced_enum[E: StrEnum](enum_cls: type[E]) -> type[E]:
                    return enum_cls
    TypeNormalizer, Environment, FileOps, ConfigOps, CliValidation = (
        Cli.TypeNormalizer,
        Cli.Environment,
        Cli.FileOps,
        Cli.ConfigOps,
        Cli.CliValidation,
    )
u = FlextCliUtilities
__all__ = ["CliExecutionMetadata", "CliValidationResult", "FlextCliUtilities", "u"]
