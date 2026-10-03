"""FLEXT CLI - Unified Typer abstraction service.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from inspect import Parameter, Signature
from types import GenericAlias
from typing import Never

from flext_cli import c, e, m, p, r, settings, t, u


class FlextCliCli:
    """Implementation part for FlextCliCli."""

    class _ModelCommand[M: t.Cli.ModelLike]:
        """Callable wrapper with explicit signature for Typer introspection.

        Note: __annotations__ uses MutableMapping[str, type] because Typer reads
        it via inspect at runtime. __call__ uses t.Scalar kwargs because Typer
        may pass scalar values or repeated option lists.
        """

        __name__: str
        __signature__: Signature
        _handler: p.Cli.ModelCommandHandler[M]
        _model_cls: t.ModelClass[M]
        _result_border: bool

        def __init__(
            self,
            *,
            handler: p.Cli.ModelCommandHandler[M],
            model_cls: t.ModelClass[M],
            parameters: t.SequenceOf[Parameter],
            result_border: bool,
        ) -> None:
            self.__name__ = getattr(handler, "__name__", model_cls.__name__)
            self.__signature__ = Signature(parameters)
            self._handler = handler
            self._model_cls = model_cls
            self._result_border = result_border

        def __call__(self, **kwargs: t.Cli.CliValue) -> t.JsonValue:
            # Typer passes each option under its parameter (field) name, so an
            # aliased field must validate by name as well as by alias. A result
            # border turns rejected input into ``e.fail_validation`` carrying
            # the ValidationError and exits non-zero; a plain command raises it.
            try:
                model = self._model_cls.model_validate(kwargs, by_name=True)
            except m.ValidationError as exc:
                if not self._result_border:
                    raise
                failure = e.fail_validation(
                    self._model_cls.__name__,
                    error=exc,
                    result_type=r[bool],
                )
                u.Cli.commands_emit_failure_cause(failure)
                FlextCliCli._exit_failure(failure)
            return self._handler(model)

    @staticmethod
    def _exit_failure[TResult: t.Cli.ResultValue](result: p.Result[TResult]) -> Never:
        """Expose a failed Result once at the CLI border and exit non-zero."""
        u.Cli.framework_exit_result(result)
        u.Cli.commands_emit_result_error(result, verbose=settings.cli_verbose)
        u.Cli.framework_exit(c.Cli.EXIT_CODE_FAILURE)

    @classmethod
    def _build_model_parameter(
        cls,
        field_name: str,
        field_info: m.FieldInfo,
        settings: t.Cli.ModelLike | None,
    ) -> t.Pair[Parameter, type | GenericAlias]:
        """Build a keyword-only Typer option from a Pydantic field.

        Returns:
            The resulting ``t.Pair[Parameter, type | GenericAlias]``.

        """
        alias = getattr(field_info, "alias", None)
        cli_name = alias or field_name
        option_name = f"--{cli_name.replace('_', '-')}"
        # Every validation alias is a first-class input name: the CLI exposes
        # the canonical alias plus each string validation_alias choice, so a
        # field migrated between names (e.g. workspace -> repository_root)
        # accepts both spellings instead of stranding one of them.
        extra_option_names: list[str] = []
        validation_alias = getattr(field_info, "validation_alias", None)
        choices = getattr(validation_alias, "choices", None)
        if isinstance(choices, tuple):
            for choice in choices:
                if not isinstance(choice, str):
                    continue
                candidate = f"--{choice.replace('_', '-')}"
                if candidate != option_name and candidate not in extra_option_names:
                    extra_option_names.append(candidate)
        field_annotation = u.Cli.field_annotation(field_name, field_info)
        annotation = u.Cli.resolve_typer_annotation(field_annotation)
        json_annotation = (
            field_annotation if u.Cli.is_json_option(field_annotation) else None
        )
        help_text = getattr(field_info, "description", None) or ""
        if json_annotation is not None:
            help_text = f"{help_text} {c.Cli.CLI_JSON_OPTION_HELP}".strip()
        is_required = field_info.is_required()
        default_value: t.Cli.CliValue | None = (
            None
            if is_required
            else u.Cli.field_default(field_name, field_info, settings)
        )
        option_decls = [option_name, *extra_option_names]
        extra = getattr(field_info, "json_schema_extra", None)
        custom_param_decls: list[str] | None = None
        if isinstance(extra, Mapping):
            declared = extra.get("typer_param_decls")
            if isinstance(declared, Sequence) and not isinstance(declared, str):
                custom_param_decls = [str(item) for item in declared]
        if annotation is bool and isinstance(default_value, bool):
            dashed_name = cli_name.replace("_", "-")
            option_decls = [f"--{dashed_name}/--no-{dashed_name}"]
        if custom_param_decls is not None:
            option_decls = custom_param_decls
        spec = m.Cli.OptionSpec(
            declarations=tuple(option_decls),
            help_text=help_text,
            default=default_value,
            required=is_required,
        )
        return (
            u.Cli.framework_build_parameter(
                field_name,
                annotation,
                spec,
                json_annotation=json_annotation,
            ),
            annotation,
        )


__all__: list[str] = ["FlextCliCli"]
