"""Behavioral tests for the public ``cli.model_command`` builder.

Every assertion targets an observable contract of the public API:

* registered in a real app and invoked with command-line arguments, the
  generated command accepts the option names a user types (aliases, custom
  declarations, bool toggles), parses each annotation into the validated
  field value, rejects a missing required option, and seeds omitted options
  from the settings model or the model defaults; and
* invoking the built command directly drives the same flow: the handler
  receives a validated model built from parsed values, the settings model
  used to seed option defaults is left untouched (invocation never writes
  back into it), and the handler return value flows back to the caller.

No signature introspection, private attribute access, or patching is used.
"""

from __future__ import annotations

from typing import Annotated, ClassVar

import pytest
from flext_tests import tm

from flext_cli import cli, m
from tests import t, u


class TestsFlextCliOptionsUtilsCov:
    """Behavioral coverage for ``cli.model_command`` public behavior."""

    class StringAnnotationModel(m.BaseModel):
        """Group the StringAnnotationModel test behavior."""

        value: str

    class OptionalStringAnnotationModel(m.BaseModel):
        """Group the OptionalStringAnnotationModel test behavior."""

        value: t.Tests.OptionalStringAlias

    class UnionAnnotationModel(m.BaseModel):
        """Group the UnionAnnotationModel test behavior."""

        value: str | int

    class ListAnnotationModel(m.BaseModel):
        """Group the ListAnnotationModel test behavior."""

        value: list[str]

    class TupleAnnotationModel(m.BaseModel):
        """Group the TupleAnnotationModel test behavior."""

        value: t.StrSequence

    class SetAnnotationModel(m.BaseModel):
        """Group the SetAnnotationModel test behavior."""

        value: set[str]

    class FrozenSetAnnotationModel(m.BaseModel):
        """Group the FrozenSetAnnotationModel test behavior."""

        value: frozenset[str]

    class AnnotatedStringModel(m.BaseModel):
        """Group the AnnotatedStringModel test behavior."""

        value: Annotated[str, "meta"]

    class StringListAliasModel(m.BaseModel):
        """Group the StringListAliasModel test behavior."""

        value: t.Tests.StringListAlias

    class AliasOptionsModel(m.BaseModel):
        """Group the AliasOptionsModel test behavior."""

        project_name: str = m.Field(..., alias="project", validate_default=True)

    class CustomDeclModel(m.BaseModel):
        """Group the CustomDeclModel test behavior."""

        custom_name: str = m.Field(
            ...,
            json_schema_extra={"typer_param_decls": ["--custom-name", "--projects"]},
            validate_default=True,
        )

    class BoolToggleModel(m.BaseModel):
        """Group the BoolToggleModel test behavior."""

        debug: bool = False

    class GreetModel(m.BaseModel):
        """Simple request model used to exercise command invocation."""

        name: str
        shout: bool = False

    class OptionsDefaultsModel(m.BaseModel):
        """Model used to exercise field-default normalization paths."""

        name: str = "default-name"
        tags: t.StrSequence = ("a", "b")
        generated: t.StrSequence = m.Field(("gen", "value"), validate_default=True)

    _INVOCATION_CASES: ClassVar[
        t.VariadicTuple[t.Pair[t.StrSequence, t.Cli.ModelLike]]
    ] = (
        (("--value", "x"), StringAnnotationModel(value="x")),
        (("--value", "x"), OptionalStringAnnotationModel(value="x")),
        (("--value", "7"), UnionAnnotationModel(value="7")),
        (("--value", "a", "--value", "b"), ListAnnotationModel(value=["a", "b"])),
        (("--value", "a", "--value", "b"), TupleAnnotationModel(value=["a", "b"])),
        (("--value", "a", "--value", "b"), SetAnnotationModel(value={"a", "b"})),
        (
            ("--value", "a", "--value", "b"),
            FrozenSetAnnotationModel(value=frozenset({"a", "b"})),
        ),
        (("--value", "x"), AnnotatedStringModel(value="x")),
        (("--value", "a", "--value", "b"), StringListAliasModel(value=["a", "b"])),
    )

    @staticmethod
    def _noop_handler(_params: t.Cli.ModelLike) -> bool:
        return True

    @staticmethod
    def _run[M: t.Cli.ModelLike](
        model_cls: t.ModelClass[M],
        args: t.StrSequence,
        *,
        settings: t.Cli.ModelLike | None = None,
    ) -> tuple[m.Cli.InvocationResult, list[M]]:
        """Invoke the generated command through a real app; return what it received."""
        received: list[M] = []

        def _capture(params: M) -> bool:
            received.append(params)
            return True

        app = cli.create_app_with_common_params(
            name="options-app", help_text="Options app"
        )
        cli.register_command(
            app,
            name="run",
            help_text="Run",
            command=cli.model_command(model_cls, _capture, settings=settings),
        )
        invocation = cli.invoke_app(app, args=["run", *args])
        tm.ok(invocation)
        return invocation.value, received

    # ---- generated-command contract, observed through real invocation ----

    def test_model_command_uses_field_alias_as_option_name(self) -> None:
        """The field alias is the option name the CLI accepts."""
        invocation, received = self._run(self.AliasOptionsModel, ["--project", "p1"])
        tm.that(u.Cli.process_succeeded(invocation.outcome), eq=True)
        tm.that(received[0].project_name, eq="p1")

    @pytest.mark.parametrize("option", ["--custom-name", "--projects"])
    def test_model_command_honors_custom_param_decls(self, option: str) -> None:
        """Every custom declaration is accepted as the field's option."""
        invocation, received = self._run(self.CustomDeclModel, [option, "v"])
        tm.that(u.Cli.process_succeeded(invocation.outcome), eq=True)
        tm.that(received[0].custom_name, eq="v")

    @pytest.mark.parametrize(
        ("option", "expected"), [("--debug", True), ("--no-debug", False)]
    )
    def test_model_command_renders_bool_field_as_toggle_flag(
        self, option: str, *, expected: bool
    ) -> None:
        """A bool field is driven by an on/off toggle pair."""
        invocation, received = self._run(self.BoolToggleModel, [option])
        tm.that(u.Cli.process_succeeded(invocation.outcome), eq=True)
        tm.that(received[0].debug, eq=expected)

    @pytest.mark.parametrize(("args", "expected"), _INVOCATION_CASES)
    def test_model_command_parses_values_for_each_annotation(
        self, args: t.StrSequence, expected: t.Cli.ModelLike
    ) -> None:
        """Command-line values build the same model as direct construction."""
        invocation, received = self._run(type(expected), args)
        tm.that(u.Cli.process_succeeded(invocation.outcome), eq=True)
        tm.that(received, eq=[expected])

    def test_model_command_rejects_missing_required_option(self) -> None:
        """A required field without its option is a usage failure; no handler call."""
        invocation, received = self._run(self.AliasOptionsModel, [])
        tm.that(u.Cli.process_succeeded(invocation.outcome), eq=False)
        tm.that(received, empty=True)

    def test_field_default_prefers_settings_value_over_model_default(self) -> None:
        """An omitted option takes the value of the supplied settings model."""
        settings = self.OptionsDefaultsModel(name="override-name")
        invocation, received = self._run(
            self.OptionsDefaultsModel, [], settings=settings
        )
        tm.that(u.Cli.process_succeeded(invocation.outcome), eq=True)
        tm.that(received[0].name, eq="override-name")

    def test_field_defaults_reach_handler_when_options_omitted(self) -> None:
        """Omitted options deliver the model defaults to the handler."""
        invocation, received = self._run(self.OptionsDefaultsModel, [])
        tm.that(u.Cli.process_succeeded(invocation.outcome), eq=True)
        expected = self.OptionsDefaultsModel()
        tm.that(received[0].name, eq=expected.name)
        tm.that(tuple(received[0].tags), eq=tuple(expected.tags))
        tm.that(tuple(received[0].generated), eq=tuple(expected.generated))

    # ---- end-to-end command invocation ----------------------------------

    def test_invoking_command_passes_validated_model_to_handler(self) -> None:
        """Verify that invoking command passes validated model to handler."""
        received: dict[str, TestsFlextCliOptionsUtilsCov.GreetModel] = {}

        def _capture(params: TestsFlextCliOptionsUtilsCov.GreetModel) -> str:
            received["model"] = params
            return f"handled:{params.name}"

        command = cli.model_command(self.GreetModel, _capture)
        result = command(name="ada", shout=True)

        tm.that(result, eq="handled:ada")
        tm.that(received["model"].name, eq="ada")
        tm.that(received["model"].shout, eq=True)

    def test_invoking_command_coerces_raw_values_through_model_validation(self) -> None:
        """Verify that invoking command coerces raw values through model validation."""

        def _handler(params: TestsFlextCliOptionsUtilsCov.GreetModel) -> bool:
            return params.shout

        command = cli.model_command(self.GreetModel, _handler)
        result = command(name="grace", shout="true")

        tm.that(result, eq=True)

    def test_invoking_command_rejects_missing_required_field(self) -> None:
        """Verify that invoking command rejects missing required field."""
        command = cli.model_command(self.GreetModel, self._noop_handler)
        with pytest.raises(m.ValidationError):
            command(shout=True)

    def test_invoking_command_uses_parsed_values_without_mutating_settings(
        self,
    ) -> None:
        # Write-back into the settings model was removed (commit f5f83dee);
        # the observable contract is now: parsed values reach the handler
        # through the validated model and the settings instance stays intact.
        """Verify that invoking command uses parsed values without mutating settings."""
        settings = self.OptionsDefaultsModel(name="start-name")
        received: dict[str, TestsFlextCliOptionsUtilsCov.OptionsDefaultsModel] = {}

        def _capture(params: TestsFlextCliOptionsUtilsCov.OptionsDefaultsModel) -> str:
            received["model"] = params
            return params.name

        command = cli.model_command(
            self.OptionsDefaultsModel, _capture, settings=settings
        )

        result = command(name="parsed-name")

        tm.that(result, eq="parsed-name")
        tm.that(received["model"].name, eq="parsed-name")
        tm.that(settings.name, eq="start-name")


__all__: list[str] = ["TestsFlextCliOptionsUtilsCov"]
