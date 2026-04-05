"""CLI model command helpers shared through ``u.Cli``."""

from __future__ import annotations

import inspect
import types
from collections.abc import Mapping, MutableMapping, MutableSequence
from typing import ClassVar, Literal, Union, get_args, get_origin

from pydantic import BaseModel
from pydantic.fields import FieldInfo

from flext_cli import p, t
from flext_cli._utilities.json import FlextCliUtilitiesJson
from flext_core import FlextLogger


class FlextCliUtilitiesModelCommandBuilder[M: BaseModel]:
    """Build Typer command wrappers from Pydantic models."""

    _module_logger: ClassVar[FlextLogger] = FlextLogger(__name__)

    def __init__(
        self,
        model_class: type[M],
        handler: t.Cli.JsonModelHandler[M],
        config: t.Cli.JsonValue | None = None,
    ) -> None:
        """Initialize the command builder."""
        super().__init__()
        self.model_class = model_class
        self.handler = handler
        self.config = config

    @staticmethod
    def _create_real_annotations(
        annotations: Mapping[str, type],
    ) -> Mapping[str, type]:
        """Create runtime annotations accepted by Typer."""

        def process_annotation(_name: str, field_type: type) -> type:
            origin = get_origin(field_type)
            is_union = (
                origin is Union or origin is type(Union) or origin is types.UnionType
            )
            if is_union:
                args = get_args(field_type)
                non_none = [arg for arg in args if arg is not type(None)]
                if non_none and non_none[0] is bool:
                    return bool
                return field_type
            return field_type

        return {
            name: process_annotation(name, field_type)
            for name, field_type in annotations.items()
        }

    @staticmethod
    def _extract_optional_inner_type(field_type: type) -> tuple[type, bool]:
        """Extract the effective inner type from optional/union annotations."""
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
                result_type = str if get_origin(first_type) is Literal else first_type
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
        """Resolve type aliases to their runtime Typer-compatible type."""
        origin = get_origin(field_type)
        if origin is not None:
            return field_type, str(origin)

        type_value_candidate = getattr(field_type, "__value__", None)
        type_value: str | None = (
            str(type_value_candidate) if type_value_candidate is not None else None
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
        field_info: t.Cli.FieldMetadataSource,
    ) -> tuple[type, t.Cli.JsonValue | None, bool, bool]:
        """Process field metadata and return type/default info."""
        default_value: t.Cli.JsonValue | None = None
        is_required = True
        has_factory = False

        default_attr = field_info.default if isinstance(field_info, FieldInfo) else None
        if default_attr is not None:
            default_value = default_attr
        factory_attr = (
            field_info.default_factory if isinstance(field_info, FieldInfo) else None
        )
        has_factory = callable(factory_attr)
        is_required_fn = (
            field_info.is_required if isinstance(field_info, FieldInfo) else None
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
            field_type = type(default_value) if default_value is not None else str
        else:
            field_type, origin = self._resolve_type_alias(field_type_raw)
            if origin is not None and field_type is not str:
                field_type, _ = self._extract_optional_inner_type(field_type)

        return field_type, default_value, is_required, has_factory

    def _collect_field_data(
        self,
        model_fields: Mapping[str, FieldInfo],
    ) -> tuple[Mapping[str, type], t.Cli.JsonDefaults, set[str]]:
        """Collect annotations, defaults, and factory fields from model fields."""

        def process_field(
            field_name: str,
            field_info: t.Cli.FieldMetadataSource,
        ) -> tuple[type, t.Cli.JsonValue | None, bool]:
            field_type, default_val, _is_required, has_factory = (
                self._process_field_metadata(field_name, field_info)
            )
            return (
                field_type,
                default_val if default_val is not None else None,
                has_factory,
            )

        processed_dict: Mapping[str, tuple[type, t.Cli.JsonValue | None, bool]] = {
            field_name: process_field(field_name, field_info)
            for field_name, field_info in model_fields.items()
        }
        annotations: MutableMapping[str, type] = {}
        defaults: t.Cli.MutableJsonDefaults = {}
        fields_with_factory: set[str] = set()

        for field_name, (
            field_type,
            default_val,
            has_factory,
        ) in processed_dict.items():
            annotations[field_name] = field_type
            if has_factory:
                fields_with_factory.add(field_name)
            if field_name not in fields_with_factory and default_val is not None:
                defaults[field_name] = default_val

        return annotations, defaults, fields_with_factory

    def _execute_command_wrapper(
        self,
        annotations: Mapping[str, type],
        defaults: t.Cli.JsonDefaults,
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
        command_signature = inspect.Signature(
            parameters=[*required_parameters, *defaulted_parameters],
        )

        def command_wrapper(
            *args: t.RecursiveContainer,
            **kwargs: t.RecursiveContainer,
        ) -> t.RecursiveValue:
            try:
                bound_arguments = command_signature.bind(*args, **kwargs)
            except TypeError as ex:
                msg = f"Invalid command arguments: {ex}"
                raise RuntimeError(msg) from ex

            model_instance = self.model_class.model_validate(
                dict(bound_arguments.arguments),
            )
            if self.config is not None:
                for field_name, value in bound_arguments.arguments.items():
                    try:
                        setattr(self.config, field_name, value)
                    except (AttributeError, TypeError) as ex:
                        FlextCliUtilitiesModelCommandBuilder._module_logger.debug(
                            f"Could not set builder_config.{field_name}",
                            error=str(ex),
                        )
            if callable(self.handler):
                return self.handler(model_instance)
            msg = "builder_handler is not callable"
            raise RuntimeError(msg)

        real_annotations = self._create_real_annotations(annotations)
        command_wrapper.__annotations__ = dict(real_annotations)

        def typed_wrapper(
            *args: t.RecursiveContainer,
            **kwargs: t.RecursiveContainer,
        ) -> t.RecursiveValue:
            raw_result = command_wrapper(*args, **kwargs)
            return FlextCliUtilitiesJson.normalize_json_value(raw_result)

        setattr(typed_wrapper, "__signature__", command_signature)
        typed_wrapper.__annotations__ = dict(real_annotations)
        return typed_wrapper

    def build(self) -> p.Cli.CliCommandWrapper:
        """Build a Typer command wrapper from a Pydantic model."""
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


class FlextCliUtilitiesModelCommands:
    """Model command methods exposed directly on ``u.Cli``."""

    @staticmethod
    def build_model_command[M: BaseModel](
        model_class: type[M],
        handler: t.Cli.JsonModelHandler[M],
        config: t.Cli.JsonValue | None = None,
    ) -> p.Cli.CliCommandWrapper:
        """Build a Typer command wrapper from a model and handler."""
        return FlextCliUtilitiesModelCommandBuilder(
            model_class=model_class,
            handler=handler,
            config=config,
        ).build()


__all__ = [
    "FlextCliUtilitiesModelCommandBuilder",
    "FlextCliUtilitiesModelCommands",
]
