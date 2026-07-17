"""Behavioral tests for the public ``cli.model_command`` builder.

Every assertion targets an observable contract of the public API:

* the generated Typer command exposes the option specs a Typer app consumes
  (option names, aliases, custom declarations, bool toggles, resolved
  annotations, and resolved defaults) -- this signature *is* the return
  contract of the builder, not private state; and
* invoking the built command drives the real end-to-end flow: the handler
  receives a validated model built from parsed values, the settings model
  used to seed option defaults is left untouched (invocation never writes
  back into it), and the handler return value flows back to the caller.

No private attribute access, collaborator spying, or patching is used.
"""

from __future__ import annotations

import inspect
from typing import Annotated, ClassVar

import pytest

from flext_cli import cli, m
from tests import c
from tests import p, t
from tests import u
from flext_tests import tm


class TestsFlextCliOptionsUtilsCov:
    """Behavioral coverage for ``cli.model_command`` public behavior."""

    class _StringAnnotationModel(m.BaseModel):
        value: str

    class _OptionalStringAnnotationModel(m.BaseModel):
        value: t.Tests.OptionalStringAlias

    class _UnionAnnotationModel(m.BaseModel):
        value: str | int

    class _ListAnnotationModel(m.BaseModel):
        value: list[str]

    class _TupleAnnotationModel(m.BaseModel):
        value: t.StrSequence

    class _SetAnnotationModel(m.BaseModel):
        value: set[str]

    class _FrozenSetAnnotationModel(m.BaseModel):
        value: frozenset[str]

    class _DictAnnotationModel(m.BaseModel):
        value: dict[str, int]

    class _AnnotatedStringModel(m.BaseModel):
        value: Annotated[str, "meta"]

    class _StringListAliasModel(m.BaseModel):
        value: t.Tests.StringListAlias

    class _AliasOptionsModel(m.BaseModel):
        project_name: str = m.Field(..., alias="project", validate_default=True)

    class _CustomDeclModel(m.BaseModel):
        custom_name: str = m.Field(
            ...,
            json_schema_extra={"typer_param_decls": ["--custom-name", "--projects"]},
            validate_default=True,
        )

    class _BoolToggleModel(m.BaseModel):
        debug: bool = False

    class _GreetModel(m.BaseModel):
        """Simple request model used to exercise command invocation."""

        name: str
        shout: bool = False

    class _OptionsDefaultsModel(m.BaseModel):
        """Model used to exercise field-default normalization paths."""

        name: str = "default-name"
        tags: t.StrSequence = ("a", "b")
        generated: t.StrSequence = m.Field(("gen", "value"), validate_default=True)
        valid_mapping: t.Cli.DefaultMapping = m.Field(
            dict(c.Tests.OPTIONS_FIELD_DEFAULT_VALID_MAPPING), validate_default=True
        )
        invalid_mapping: t.JsonValue = m.Field(
            dict(c.Tests.OPTIONS_FIELD_DEFAULT_INVALID_MAPPING), validate_default=True
        )

    _ANNOTATION_CASES: ClassVar[
        tuple[tuple[t.ModelClass[p.BaseModel], t.Cli.RuntimeAnnotation], ...]
    ] = (
        (_StringAnnotationModel, str),
        (_OptionalStringAnnotationModel, str),
        (_UnionAnnotationModel, str),
        (_ListAnnotationModel, list[str]),
        (_TupleAnnotationModel, list[str]),
        (_SetAnnotationModel, set),
        (_FrozenSetAnnotationModel, frozenset),
        (_DictAnnotationModel, dict),
        (_AnnotatedStringModel, str),
        (_StringListAliasModel, list[str]),
    )

    @staticmethod
    def _noop_handler(_params: t.Cli.ModelLike) -> bool:
        return True

    @staticmethod
    def _option_spec(command: t.Cli.Command, param_name: str) -> p.Cli.OptionSpec:
        """Return the Typer option object the builder placed on the command signature."""
        spec = inspect.signature(command).parameters[param_name].default
        tm.that(spec.param_decls, none=False)
        return spec

    # ---- generated-command contract -------------------------------------

    def test_model_command_uses_field_alias_as_option_name(self) -> None:
        """Accept a field alias through a real CLI invocation."""
        received: list[TestsFlextCliOptionsUtilsCov._AliasOptionsModel] = []

        def _capture(params: TestsFlextCliOptionsUtilsCov._AliasOptionsModel) -> bool:
            received.append(params)
            return True

        app = cli.create_group(name="alias-options", help_text="Alias options")
        cli.register_command(
            app,
            name="run",
            help_text="Run alias options",
            command=cli.model_command(self._AliasOptionsModel, _capture),
        )
        result = cli.invoke_app(app, args=("--project", "flext"))

        tm.ok(result)
        tm.that(result.value.exit_code, eq=0)
        tm.that(received[0].project_name, eq="flext")

    def test_model_command_honors_custom_param_decls(self) -> None:
        """Accept configured custom declarations through the public CLI."""
        received: list[TestsFlextCliOptionsUtilsCov._CustomDeclModel] = []

        def _capture(params: TestsFlextCliOptionsUtilsCov._CustomDeclModel) -> bool:
            received.append(params)
            return True

        app = cli.create_group(name="custom-options", help_text="Custom options")
        cli.register_command(
            app,
            name="run",
            help_text="Run custom options",
            command=cli.model_command(self._CustomDeclModel, _capture),
        )
        result = cli.invoke_app(app, args=("--projects", "flext"))

        tm.ok(result)
        tm.that(result.value.exit_code, eq=0)
        tm.that(received[0].custom_name, eq="flext")

    def test_model_command_renders_bool_field_as_toggle_flag(self) -> None:
        """Enable a boolean option through its generated positive flag."""
        received: list[TestsFlextCliOptionsUtilsCov._BoolToggleModel] = []

        def _capture(params: TestsFlextCliOptionsUtilsCov._BoolToggleModel) -> bool:
            received.append(params)
            return True

        app = cli.create_group(name="bool-options", help_text="Boolean options")
        cli.register_command(
            app,
            name="run",
            help_text="Run boolean options",
            command=cli.model_command(self._BoolToggleModel, _capture),
        )
        result = cli.invoke_app(app, args=("--debug",))

        tm.ok(result)
        tm.that(result.value.exit_code, eq=0)
        tm.that(received[0].debug, eq=True)

    @pytest.mark.parametrize(("model_cls", "expected"), _ANNOTATION_CASES)
    def test_model_command_normalizes_runtime_annotations(
        self,
        model_cls: t.ModelClass[t.Cli.ModelLike],
        expected: t.Cli.RuntimeAnnotation,
    ) -> None:
        """Expose each supported field annotation in canonical runtime form."""
        command = cli.model_command(model_cls, self._noop_handler)
        resolved = inspect.signature(command).parameters["value"].annotation
        tm.that(resolved, eq=expected)

    def test_model_command_marks_required_field_default_as_ellipsis(self) -> None:
        """Reject a real invocation that omits a required model field."""
        app = cli.create_group(name="required-options", help_text="Required options")
        cli.register_command(
            app,
            name="run",
            help_text="Run required options",
            command=cli.model_command(self._AliasOptionsModel, self._noop_handler),
        )

        result = cli.invoke_app(app, args=())

        tm.ok(result)
        tm.that(result.value.exit_code, eq=2)

    def test_field_default_prefers_settings_value_over_model_default(self) -> None:
        """Prefer the validated settings value over field metadata."""
        settings = self._OptionsDefaultsModel(name="override-name")
        default = u.Cli.field_default(
            "name", self._OptionsDefaultsModel.model_fields["name"], settings
        )
        tm.that(default, eq="override-name")

    def test_field_default_normalizes_sequence_default_to_tuple(self) -> None:
        """Normalize a generated sequence default to an immutable tuple."""
        default = u.Cli.field_default(
            "generated", self._OptionsDefaultsModel.model_fields["generated"], None
        )
        tm.that(default, eq=("gen", "value"))

    def test_field_default_preserves_normalizable_mapping(self) -> None:
        """Preserve a mapping containing only supported CLI atoms."""
        default = u.Cli.field_default(
            "valid_mapping",
            self._OptionsDefaultsModel.model_fields["valid_mapping"],
            None,
        )
        tm.that(default, eq=dict(c.Tests.OPTIONS_FIELD_DEFAULT_VALID_MAPPING))

    def test_field_default_drops_non_normalizable_mapping_to_none(self) -> None:
        """Reject a mapping containing values unsupported by the CLI."""
        default = u.Cli.field_default(
            "invalid_mapping",
            self._OptionsDefaultsModel.model_fields["invalid_mapping"],
            None,
        )
        tm.that(default, none=True)

    # ---- end-to-end command invocation ----------------------------------

    def test_invoking_command_passes_validated_model_to_handler(self) -> None:
        """Pass one validated request model to the registered handler."""
        received: dict[str, TestsFlextCliOptionsUtilsCov._GreetModel] = {}

        def _capture(params: TestsFlextCliOptionsUtilsCov._GreetModel) -> str:
            received["model"] = params
            return f"handled:{params.name}"

        command = cli.model_command(self._GreetModel, _capture)
        result = command(name="ada", shout=True)

        tm.that(result, eq="handled:ada")
        tm.that(received["model"].name, eq="ada")
        tm.that(received["model"].shout, eq=True)

    def test_invoking_command_coerces_raw_values_through_model_validation(self) -> None:
        """Validate raw command values before the handler receives them."""

        def _handler(params: TestsFlextCliOptionsUtilsCov._GreetModel) -> bool:
            return params.shout

        command = cli.model_command(self._GreetModel, _handler)
        result = command(name="grace", shout="true")

        tm.that(result, eq=True)

    def test_invoking_command_rejects_missing_required_field(self) -> None:
        """Reject direct calls missing a required request field."""
        command = cli.model_command(self._GreetModel, self._noop_handler)
        with pytest.raises(m.ValidationError):
            command(shout=True)

    def test_invoking_command_uses_parsed_values_without_mutating_settings(
        self,
    ) -> None:
        """Keep source settings immutable while passing parsed values onward."""
        # Write-back into the settings model was removed (commit f5f83dee);
        # the observable contract is now: parsed values reach the handler
        # through the validated model and the settings instance stays intact.
        settings = self._OptionsDefaultsModel(name="start-name")
        received: dict[str, TestsFlextCliOptionsUtilsCov._OptionsDefaultsModel] = {}

        def _capture(params: TestsFlextCliOptionsUtilsCov._OptionsDefaultsModel) -> str:
            received["model"] = params
            return params.name

        command = cli.model_command(
            self._OptionsDefaultsModel, _capture, settings=settings
        )

        result = command(name="parsed-name")

        tm.that(result, eq="parsed-name")
        tm.that(received["model"].name, eq="parsed-name")
        tm.that(settings.name, eq="start-name")


__all__: list[str] = ["TestsFlextCliOptionsUtilsCov"]
