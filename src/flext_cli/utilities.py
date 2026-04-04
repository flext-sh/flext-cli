"""FLEXT CLI utility facade and CLI-specific helpers."""

from __future__ import annotations

import inspect
import logging
import os
import types
from collections.abc import Callable, Mapping, MutableMapping, MutableSequence
from datetime import UTC, datetime
from pathlib import Path
from typing import (
    ClassVar,
    Literal,
    Union,
    get_args,
    get_origin,
)

from pydantic import (
    BaseModel,
    TypeAdapter,
    ValidationError,
)
from pydantic.fields import FieldInfo
from typer.models import OptionInfo

from flext_cli import c, m, p, r, t
from flext_cli._utilities.json import FlextCliUtilitiesJson
from flext_cli._utilities.toml import FlextCliUtilitiesToml
from flext_cli._utilities.yaml import FlextCliUtilitiesYaml
from flext_core import FlextLogger, FlextUtilities

_logger = FlextLogger(__name__)


class FlextCliUtilities(FlextUtilities):
    """Main utilities class for the Flext CLI."""

    class Cli(FlextCliUtilitiesJson, FlextCliUtilitiesToml, FlextCliUtilitiesYaml):
        """Command line interface specific utilities."""

        @staticmethod
        def default_for_type_kind(
            type_kind: Literal["str", "bool", "dict"],
            default: t.Cli.JsonValue | None,
        ) -> str | bool | Mapping[str, t.Cli.JsonValue] | None:
            """Default value for type_kind. Centralized (no polymorphic branches at call sites)."""
            if type_kind == "str":
                return default if isinstance(default, str) else None
            if type_kind == "bool":
                return default if isinstance(default, bool) else False
            if isinstance(default, Mapping):
                return {
                    str(k): FlextCliUtilities.Cli.normalize_json_value(v)
                    for k, v in default.items()
                }
            return {}

        @staticmethod
        def project_names_from_values(
            *values: str | t.Cli.StrSequence | None,
        ) -> list[str] | None:
            """Normalize repeated or comma-separated CLI selector values."""
            names: list[str] = []
            for value in values:
                if value is None:
                    continue
                raw_values = [value] if isinstance(value, str) else list(value)
                for raw_value in raw_values:
                    names.extend(
                        item.strip() for item in raw_value.split(",") if item.strip()
                    )
            return names or None

        class OptionBuilder:
            """Builder for Typer CLI options from field metadata.

            Constructs typer.Option instances from field_name and registry configuration.
            NOT a Pydantic model - this is a utility builder class.
            """

            def __init__(
                self,
                field_name: str,
                registry: Mapping[str, Mapping[str, t.Scalar | t.StrSequence]],
            ) -> None:
                """Initialize builder with field name and registry."""
                super().__init__()
                self.field_name = field_name
                self.registry = registry

            def build(self) -> OptionInfo:
                """Build typer.Option from field metadata."""
                field_meta = self.registry.get(self.field_name, {})
                if not field_meta:
                    msg = "Option registry metadata must support key lookup"
                    raise TypeError(msg)
                help_text = str(field_meta.get("help", ""))
                short_flag = str(field_meta.get("short", ""))
                default_value = field_meta.get("default", ...)

                field_name_override = field_meta.get(
                    c.Cli.CliParamsRegistry.KEY_FIELD_NAME_OVERRIDE,
                )
                cli_param_name: str = (
                    field_name_override
                    if isinstance(field_name_override, str)
                    else self.field_name
                )

                option_args: MutableSequence[str] = [
                    f"--{cli_param_name.replace('_', '-')}"
                ]
                if short_flag:
                    option_args.append(f"-{short_flag}")

                return OptionInfo(
                    default=default_value,
                    param_decls=option_args,
                    help=help_text,
                )

        class CliModelConverter:
            """Converter for Pydantic models to CLI parameters."""

            JSON_VALUE_ADAPTER: ClassVar[TypeAdapter[t.Cli.JsonValue]] = TypeAdapter(
                t.Cli.JsonValue,
            )

            @staticmethod
            def cli_args_to_model[M: BaseModel](
                model_class: type[M],
                cli_args: Mapping[str, t.Cli.JsonValue],
            ) -> r[M]:
                """Convert CLI args dict to a Pydantic model instance.

                Validates the args dict against the model schema and returns
                r[M] wrapping success or validation failure.
                """
                try:
                    instance: M = model_class.model_validate(cli_args)
                    return r.ok(instance)
                except ValidationError as exc:
                    return r[M].fail(
                        f"Validation error for {model_class.__name__}: {exc}",
                    )

            @staticmethod
            def convert_field_value(
                field_value: t.Cli.JsonValue | None,
            ) -> r[t.Cli.JsonValue]:
                """Convert field value to JSON-compatible value."""
                if field_value is None:
                    empty_value: t.Cli.JsonValue = ""
                    return r.ok(empty_value)
                try:
                    json_value: t.Cli.JsonValue = FlextCliUtilities.Cli.CliModelConverter.JSON_VALUE_ADAPTER.validate_python(
                        field_value,
                    )
                    return r.ok(json_value)
                except ValidationError as exc:
                    _logger.debug(
                        "convert_field_value validation fallback",
                        error=exc,
                        exc_info=False,
                    )
                    fallback_value: t.Cli.JsonValue = str(field_value)
                    return r.ok(fallback_value)

        class ModelCommandBuilder[M: BaseModel]:
            """Builder for Typer commands from Pydantic models.

            Creates Typer command functions with automatic parameter extraction from model fields.
            NOT a Pydantic model - this is a utility builder class.
            """

            def __init__(
                self,
                model_class: type[M],
                handler: Callable[[M], t.Cli.JsonValue],
                config: t.Cli.JsonValue | None = None,
            ) -> None:
                """Initialize builder with model class, handler, and optional config."""
                super().__init__()
                self.model_class = model_class
                self.handler = handler
                self.config = config

            @staticmethod
            def _create_real_annotations(
                annotations: Mapping[str, type],
            ) -> Mapping[str, type]:
                """Create real type annotations for Typer flag detection."""

                def process_annotation(_name: str, field_type: type) -> type:
                    origin = get_origin(field_type)
                    is_union = (
                        origin is Union
                        or origin is type(Union)
                        or origin is types.UnionType
                    )
                    if is_union:
                        args = get_args(field_type)
                        non_none = [a for a in args if a is not type(None)]
                        if non_none and non_none[0] is bool:
                            return bool
                        return field_type
                    return field_type

                processed_annotations: Mapping[str, type] = {
                    name: process_annotation(name, field_type)
                    for name, field_type in annotations.items()
                }
                return processed_annotations

            @staticmethod
            def _extract_optional_inner_type(
                field_type: type,
            ) -> tuple[type, bool]:
                """Extract inner type from Optional/Union types.

                Returns (inner_type, is_optional) tuple.
                """
                result_type: type = field_type
                is_optional = False

                origin = get_origin(field_type)
                if origin is None:
                    pass
                elif origin is Literal:
                    result_type = str
                elif type(None) not in get_args(field_type):
                    non_none_types = [
                        arg for arg in get_args(field_type) if arg is not type(None)
                    ]
                    if non_none_types:
                        first_type = non_none_types[0]
                        if get_origin(first_type) is Literal:
                            result_type = str
                        else:
                            result_type = first_type
                    else:
                        result_type = str
                else:
                    is_optional = True
                    non_none_types = [
                        arg for arg in get_args(field_type) if arg is not type(None)
                    ]
                    if not non_none_types or get_origin(non_none_types[0]) is Literal:
                        result_type = str
                    else:
                        result_type = non_none_types[0]

                return result_type, is_optional

            @staticmethod
            def _resolve_type_alias(field_type: type) -> tuple[type, str | None]:
                """Resolve type aliases to Literal and return (resolved_type, origin)."""
                origin = get_origin(field_type)
                if origin is not None:
                    return field_type, str(origin)

                type_value_candidate = getattr(field_type, "__value__", None)
                type_value: str | None = (
                    str(type_value_candidate)
                    if type_value_candidate is not None
                    else None
                )
                if type_value is not None and "Literal" in type_value:
                    return str, "Literal"
                resolved_origin = get_origin(field_type)
                return field_type, str(
                    resolved_origin,
                ) if resolved_origin is not None else None

            def _process_field_metadata(
                self,
                field_name: str,
                field_info: FieldInfo | Mapping[str, t.Cli.JsonValue] | t.Cli.JsonValue,
            ) -> tuple[type, t.Cli.JsonValue | None, bool, bool]:
                """Process field metadata and return type info.

                Returns (field_type, default_value, is_required, has_factory).
                """
                default_value: t.Cli.JsonValue | None = None
                is_required = True
                has_factory = False

                default_attr = (
                    field_info.default if isinstance(field_info, FieldInfo) else None
                )
                if default_attr is not None:
                    default_value = default_attr
                factory_attr = (
                    field_info.default_factory
                    if isinstance(field_info, FieldInfo)
                    else None
                )
                has_factory = callable(factory_attr)
                is_required_fn = (
                    field_info.is_required
                    if isinstance(field_info, FieldInfo)
                    else None
                )
                if callable(is_required_fn):
                    is_required = bool(is_required_fn())

                if self.config is not None:
                    config_value = (
                        getattr(self.config, field_name)
                        if hasattr(self.config, field_name)
                        else None
                    )
                    if config_value is not None:
                        default_value = config_value

                field_type_raw = (
                    field_info.annotation if isinstance(field_info, FieldInfo) else None
                )
                if field_type_raw is None:
                    field_type = (
                        type(default_value) if default_value is not None else str
                    )
                else:
                    field_type, origin = self._resolve_type_alias(field_type_raw)
                    if origin is not None and field_type is not str:
                        field_type, _ = self._extract_optional_inner_type(field_type)

                field_type_typed: type = field_type
                return field_type_typed, default_value, is_required, has_factory

            def build(self) -> p.Cli.CliCommandWrapper:
                """Build Typer command from Pydantic model."""
                narrowed_fields: t.Cli.FieldInfoMapping = getattr(
                    self.model_class,
                    "__pydantic_fields__",
                )
                annotations, defaults, fields_with_factory = self._collect_field_data(
                    narrowed_fields,
                )
                return self._execute_command_wrapper(
                    annotations,
                    defaults,
                    fields_with_factory,
                )

            def _collect_field_data(
                self,
                model_fields: Mapping[str, FieldInfo],
            ) -> tuple[
                Mapping[str, type],
                Mapping[str, t.Cli.JsonValue],
                set[str],
            ]:
                """Collect annotations, defaults and factory fields from model fields."""

                def process_field(
                    field_name: str,
                    field_info: FieldInfo
                    | Mapping[str, t.Cli.JsonValue]
                    | t.Cli.JsonValue,
                ) -> tuple[type, t.Cli.JsonValue | None, bool]:
                    """Process single field and return (type, default, has_factory)."""
                    field_type, default_val, _is_required, has_factory = (
                        self._process_field_metadata(field_name, field_info)
                    )
                    return (
                        field_type,
                        default_val if default_val is not None else None,
                        has_factory,
                    )

                processed_dict: Mapping[
                    str,
                    tuple[type, t.Cli.JsonValue | None, bool],
                ] = {
                    field_name: process_field(field_name, field_info)
                    for field_name, field_info in model_fields.items()
                }
                annotations: MutableMapping[str, type] = {}
                defaults: MutableMapping[str, t.Cli.JsonValue] = {}
                fields_with_factory: set[str] = set()

                for field_name, (
                    field_type,
                    default_val,
                    has_factory,
                ) in processed_dict.items():
                    annotations[field_name] = field_type
                    if has_factory:
                        fields_with_factory.add(field_name)
                    if (
                        field_name not in fields_with_factory
                        and default_val is not None
                    ):
                        defaults[field_name] = default_val

                return annotations, defaults, fields_with_factory

            def _execute_command_wrapper(
                self,
                annotations: Mapping[str, type],
                defaults: Mapping[str, t.Cli.JsonValue],
                fields_with_factory: set[str],
            ) -> p.Cli.CliCommandWrapper:
                required_parameters: MutableSequence[inspect.Parameter] = []
                defaulted_parameters: MutableSequence[inspect.Parameter] = []
                for field_name, field_type in annotations.items():
                    has_default = (
                        field_name in defaults and field_name not in fields_with_factory
                    )
                    default_value = (
                        defaults[field_name] if has_default else inspect.Parameter.empty
                    )
                    parameter = inspect.Parameter(
                        name=field_name,
                        kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
                        default=default_value,
                        annotation=field_type,
                    )
                    if has_default:
                        defaulted_parameters.append(parameter)
                    else:
                        required_parameters.append(parameter)
                signature_parameters = [*required_parameters, *defaulted_parameters]
                command_signature = inspect.Signature(parameters=signature_parameters)

                def command_wrapper(
                    *args: t.Cli.JsonValue,
                    **kwargs: t.Cli.JsonValue,
                ) -> t.Cli.JsonValue:
                    try:
                        bound_arguments = command_signature.bind(*args, **kwargs)
                    except TypeError as ex:
                        msg = f"Invalid command arguments: {ex}"
                        raise RuntimeError(msg) from ex

                    model_instance = self.model_class.model_validate(
                        dict(bound_arguments.arguments),
                    )
                    if self.config is not None:
                        for fn, value in bound_arguments.arguments.items():
                            try:
                                setattr(self.config, fn, value)
                            except (AttributeError, TypeError) as ex:
                                _logger.debug(
                                    "Could not set builder_config.%s",
                                    fn,
                                    error=ex,
                                )
                    if callable(self.handler):
                        return self.handler(model_instance)
                    msg = "builder_handler is not callable"
                    raise RuntimeError(msg)

                real_annotations = self._create_real_annotations(annotations)
                command_wrapper.__annotations__ = dict(real_annotations)

                def typed_wrapper(
                    *args: t.Cli.JsonValue,
                    **kwargs: t.Cli.JsonValue,
                ) -> t.Cli.JsonValue:
                    raw_result = command_wrapper(*args, **kwargs)
                    normalized: r[t.Cli.JsonValue] = (
                        FlextCliUtilities.Cli.CliModelConverter.convert_field_value(
                            raw_result,
                        )
                    )
                    if normalized.is_success:
                        normalized_value: t.Cli.JsonValue = normalized.value
                        return normalized_value
                    return str(raw_result)

                setattr(typed_wrapper, "__signature__", command_signature)
                typed_wrapper.__annotations__ = dict(real_annotations)
                return typed_wrapper

        @staticmethod
        def process_mapping[T, U](
            items: Mapping[str, T],
            processor: Callable[[str, T], U],
            on_error: str = "fail",
        ) -> r[Mapping[str, U]]:
            """Process a mapping of items with error handling."""
            errors: MutableSequence[str] = []
            values: MutableMapping[str, U] = {}
            for key, value in items.items():
                try:
                    values[key] = processor(key, value)
                except c.Cli.CLI_SAFE_EXCEPTIONS as exc:
                    if on_error == "fail":
                        return r[Mapping[str, U]].fail(f"Error processing {key}: {exc}")
                    if on_error == "collect":
                        errors.append(f"{key}: {exc}")
                    else:
                        logging.getLogger(__name__).debug(
                            "process_mapping skip key %s: %s",
                            key,
                            exc,
                            exc_info=False,
                        )
            return (
                r[Mapping[str, U]].fail("; ".join(errors)) if errors else r.ok(values)
            )

        class CliValidation:
            """CLI-specific validation utilities."""

            @staticmethod
            def to_str(value: t.Cli.CliValue) -> str:
                """Convert a value to a string safely."""
                if value is None:
                    return ""
                if isinstance(value, str):
                    return value
                return str(value)

            @staticmethod
            def v(
                val: t.Cli.CliValue,
                *,
                name: str = "field",
                empty: bool = True,
                in_list: t.StrSequence | None = None,
                eq: str | None = None,
                msg: str = "",
            ) -> r[bool]:
                """Validate a value against various criteria."""
                if not empty:
                    check = FlextCliUtilities.Cli.CliValidation.v_empty(val, name=name)
                    if check.is_failure:
                        return r[bool].fail(msg or check.error or "")
                if in_list is not None:
                    val_str = FlextCliUtilities.Cli.CliValidation.to_str(val)
                    if val_str not in set(in_list):
                        err = (
                            c.Cli.MixinsValidationMessages.SESSION_STATUS_INVALID.format(
                                current_status=val_str,
                                valid_states=in_list,
                            )
                            if name == "session_status"
                            else c.Cli.MixinsValidationMessages.INVALID_ENUM_VALUE.format(
                                field_name=name,
                                valid_values=in_list,
                            )
                        )
                        return r[bool].fail(msg or err)
                if eq is not None:
                    val_str = FlextCliUtilities.Cli.CliValidation.to_str(val)
                    if val_str != eq:
                        err = (
                            c.Cli.MixinsValidationMessages.COMMAND_STATE_INVALID.format(
                                operation=name,
                                current_status=val_str,
                                required_status=eq,
                            )
                        )
                        return r[bool].fail(msg or err)
                    return r.ok(True)
                return r.ok(True)

            @staticmethod
            def v_empty(val: t.Cli.CliValue, *, name: str = "field") -> r[bool]:
                """Validate that a value is not empty."""
                if val is None:
                    return r[bool].fail(
                        c.Cli.MixinsValidationMessages.FIELD_CANNOT_BE_EMPTY.format(
                            field_name=name,
                        ),
                    )
                if isinstance(val, str) and (
                    not FlextUtilities.is_string_non_empty(val)
                ):
                    return r[bool].fail(
                        c.Cli.MixinsValidationMessages.FIELD_CANNOT_BE_EMPTY.format(
                            field_name=name,
                        ),
                    )
                return r.ok(True)

            @staticmethod
            def v_format(format_type: str) -> r[str]:
                """Validate an output format."""
                fmt = str(format_type).lower()
                valid = FlextCliUtilities.Cli.CliValidation.v(
                    fmt,
                    name="format",
                    empty=False,
                    in_list=c.Cli.ValidationLists.OUTPUT_FORMATS,
                )
                if valid.is_success:
                    return r.ok(fmt)
                return r[str].fail(
                    c.Cli.ErrorMessages.INVALID_OUTPUT_FORMAT.format(
                        format=format_type,
                    ),
                )

        class ConfigOps:
            """Configuration operations."""

            @staticmethod
            def get_config_info() -> m.Cli.ConfigSnapshot:
                """Get configuration information."""
                path = Path.home() / c.Cli.Paths.FLEXT_DIR_NAME
                exists = path.exists()
                return m.Cli.ConfigSnapshot(
                    config_dir=str(path),
                    config_exists=exists,
                    config_readable=exists and os.access(path, os.R_OK),
                    config_writable=exists and os.access(path, os.W_OK),
                    timestamp=datetime.now(UTC).isoformat(),
                )

            @staticmethod
            def validate_config_structure() -> t.StrSequence:
                """Validate configuration directory structure."""
                base = Path.home() / c.Cli.Paths.FLEXT_DIR_NAME
                ok = c.Cli.Symbols.SUCCESS_MARK
                fail = c.Cli.Symbols.FAILURE_MARK
                lines = [
                    f"{ok} Configuration directory exists"
                    if base.exists()
                    else f"{fail} Configuration directory missing",
                ]
                for subdir in c.Cli.Subdirectories.STANDARD_SUBDIRS:
                    path = base / subdir
                    lines.append(
                        c.Cli.CmdMessages.SUBDIR_EXISTS.format(symbol=ok, subdir=subdir)
                        if path.exists()
                        else c.Cli.CmdMessages.SUBDIR_MISSING.format(
                            symbol=fail,
                            subdir=subdir,
                        ),
                    )
                return lines

        FILE_NOT_FOUND_PATTERNS: tuple[str, ...] = (
            "not found",
            "no such file",
            "does not exist",
            "errno 2",
            "cannot open",
        )

        @staticmethod
        def is_file_not_found_error(error_msg: str) -> bool:
            """Check if error message indicates file not found."""
            return FlextCliUtilities.Cli.matches(
                error_msg,
                *FlextCliUtilities.Cli.FILE_NOT_FOUND_PATTERNS,
            )

        @staticmethod
        def matches(msg: str, *patterns: str) -> bool:
            """Check if message matches any pattern."""
            text = msg.lower()
            return any(pattern.lower() in text for pattern in patterns)


u = FlextCliUtilities

__all__ = ["FlextCliUtilities", "u"]
