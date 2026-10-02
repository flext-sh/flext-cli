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

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import Annotated, ClassVar

import pytest
from flext_tests import tm

from flext_cli import c, cli, m
from tests import t, u


class TestsFlextCliOptionsUtilsCov:
    """Behavioral coverage for ``cli.model_command`` public behavior."""

    def test_public_option_specs_match_registered_cli_forms(self) -> None:
        """Credential routers read the same declarations users can invoke."""
        cases = (
            (self.AliasOptionsModel, "project_name", {"--project"}),
            (self.CustomDeclModel, "custom_name", {"--custom-name", "--projects"}),
            (self.BoolToggleModel, "debug", {"--debug", "--no-debug"}),
        )
        for model_cls, field_name, expected in cases:
            spec, _ = cli.model_option_spec(
                field_name, model_cls.model_fields[field_name], None,
            )
            assert {
                option for declaration in spec.declarations for option in declaration.split("/")
            } == expected
        assert set(c.Cli.CLI_GLOBAL_PARAM_FIELDS) <= set(m.Cli.CliParamsConfig.model_fields)

    def test_parse_only_route_distinguishes_help_from_option_values(self) -> None:
        """A pre-execution router reads the model contract without invoking it."""
        parsed = cli.parse_model_options(
            self.CustomDeclModel, ("--projects", "--help"),
        )
        assert parsed.values["custom_name"] == "--help"
        assert parsed.help_requested is False
        help_route = cli.parse_model_options(self.CustomDeclModel, ("--help",))
        assert help_route.help_requested is True
        with pytest.raises(ValueError, match="duplicated"):
            cli.parse_model_options(
                self.CustomDeclModel,
                ("--projects", "one", "--custom-name", "two"),
            )

    def test_parse_only_global_prefix_uses_registered_fields(self) -> None:
        """Global options leave the protected command token unconsumed."""
        parsed = cli.parse_model_options(
            m.Cli.CliParamsConfig,
            ("--debug", "--log-level", "INFO", "wip", "start"),
            field_names=c.Cli.CLI_GLOBAL_PARAM_FIELDS,
            stop_at_positional=True,
        )
        assert parsed.values == {"debug": True, "log_level": "INFO"}
        assert parsed.remaining == ("wip", "start")

    def test_parse_only_repeated_options_match_registered_command(self) -> None:
        """Sequence options retain every token accepted by the real CLI."""
        arguments = ("--value", "first", "--value", "second")
        parsed = cli.parse_model_options(self.ListAnnotationModel, arguments)
        invocation, received = self._run(self.ListAnnotationModel, arguments)
        tm.that(u.Cli.process_succeeded(invocation.outcome), eq=True)
        assert parsed.values["value"] == received[0].value

    @pytest.mark.parametrize(("option", "expected"), [("--off", True), ("--on", False)])
    def test_parse_only_bool_polarity_matches_registered_command(
        self, option: str, *, expected: bool,
    ) -> None:
        """Test parse only bool polarity matches registered command."""
        parsed = cli.parse_model_options(self.ReverseToggleModel, (option,))
        invocation, received = self._run(self.ReverseToggleModel, [option])
        tm.that(u.Cli.process_succeeded(invocation.outcome), eq=True)
        assert parsed.values["enabled"] is expected
        assert received[0].enabled is expected

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

    class ReverseToggleModel(m.BaseModel):
        """Custom Boolean names derive polarity from declaration order."""

        enabled: bool = m.Field(
            False, json_schema_extra={"typer_param_decls": ["--off/--on"]},
        )

    class GreetModel(m.BaseModel):
        """Simple request model used to exercise command invocation."""

        name: str
        shout: bool = False

    class OptionsDefaultsModel(m.BaseModel):
        """Model used to exercise field-default normalization paths."""

        name: str = "default-name"
        tags: t.StrSequence = ("a", "b")
        generated: t.StrSequence = m.Field(("gen", "value"), validate_default=True)

    class IntSequenceDefaultModel(m.BaseModel):
        """Model whose validated default has no CLI option form."""

        counts: t.SequenceOf[int] = (1, 2)

    class NestedListSettings(m.BaseModel):
        """Settings whose value is not a CLI default source at all."""

        value: t.SequenceOf[t.SequenceOf[int]] = ((1,),)

    class StrSequenceDefaultModel(m.BaseModel):
        """Model seeded by ``NestedListSettings``."""

        value: t.StrSequence = ("a",)

    class ImmutableMappingDefaultModel(m.BaseModel):
        """An immutable default retains the field's declared mapping contract."""

        bindings: t.MappingKV[str, t.StrSequence] = m.Field(
            default_factory=lambda: MappingProxyType({"owner": ("first", "second")}),
            description="Declared symbol owner bindings.",
        )

    class InvalidMappingDefaultModel(m.BaseModel):
        """Field constraints apply before a structured default becomes JSON."""

        bindings: Annotated[t.MappingKV[str, t.StrSequence], m.Field(min_length=1)] = (
            m.Field(
                default_factory=lambda: MappingProxyType[str, t.StrSequence]({}),
                description="A nonempty mapping with an invalid empty default.",
            )
        )

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
        """Invoke the generated command through a real app; return what it received.

        Returns:
            The resulting ``tuple[m.Cli.InvocationResult, list[M]]``.

        """
        received: list[M] = []

        def _capture(params: M) -> bool:
            received.append(params)
            return True

        app = cli.create_app_with_common_params(
            name="options-app",
            help_text="Options app",
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

    def test_immutable_mapping_default_reaches_real_cli_handler(self) -> None:
        """Omitted JSON options validate immutable metadata through their schema."""
        outcome, received = self._run(self.ImmutableMappingDefaultModel, ())
        tm.that(u.Cli.process_succeeded(outcome.outcome), eq=True)
        tm.that(len(received), eq=1)
        expected = self.ImmutableMappingDefaultModel()
        tm.that(received[0].bindings, eq=expected.bindings)

    def test_immutable_mapping_option_accepts_explicit_json(self) -> None:
        """The same generated option parses an explicit payload normally."""
        payload = '{"selected":["third"]}'
        outcome, received = self._run(
            self.ImmutableMappingDefaultModel,
            ("--bindings", payload),
        )
        tm.that(u.Cli.process_succeeded(outcome.outcome), eq=True)
        expected = self.ImmutableMappingDefaultModel.model_validate_json(
            '{"bindings":' + payload + "}",
        )
        tm.that(received[0].bindings, eq=expected.bindings)

    def test_mapping_settings_default_uses_the_same_field_contract(self) -> None:
        """Validated settings override metadata without changing serialization."""
        settings = self.ImmutableMappingDefaultModel(
            bindings=MappingProxyType({"configured": ("settings",)}),
        )
        outcome, received = self._run(
            self.ImmutableMappingDefaultModel,
            (),
            settings=settings,
        )
        tm.that(u.Cli.process_succeeded(outcome.outcome), eq=True)
        tm.that(received[0].bindings, eq=settings.bindings)

    def test_invalid_structured_default_keeps_field_validation_failure(self) -> None:
        """Default rendering cannot bypass the declared minimum mapping length."""
        with pytest.raises(m.ValidationError, match="at least 1 item"):
            cli.model_command(self.InvalidMappingDefaultModel, self._noop_handler)

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
        ("option", "expected"),
        [("--debug", True), ("--no-debug", False)],
    )
    def test_model_command_renders_bool_field_as_toggle_flag(
        self,
        option: str,
        *,
        expected: bool,
    ) -> None:
        """A bool field is driven by an on/off toggle pair."""
        invocation, received = self._run(self.BoolToggleModel, [option])
        tm.that(u.Cli.process_succeeded(invocation.outcome), eq=True)
        tm.that(received[0].debug, eq=expected)

    @pytest.mark.parametrize(("args", "expected"), _INVOCATION_CASES)
    def test_model_command_parses_values_for_each_annotation(
        self,
        args: t.StrSequence,
        expected: t.Cli.ModelLike,
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

    def test_model_command_rejects_default_without_cli_form_at_build(self) -> None:
        """A validated default no option can carry fails the build, naming it."""
        with pytest.raises(TypeError, match="counts"):
            cli.model_command(self.IntSequenceDefaultModel, self._noop_handler)

    def test_model_command_propagates_invalid_default_source_at_build(self) -> None:
        """A settings value outside the default-source contract escapes unchanged."""
        settings = self.NestedListSettings()
        with pytest.raises(m.ValidationError):
            cli.model_command(
                self.StrSequenceDefaultModel,
                self._noop_handler,
                settings=settings,
            )

    def test_field_default_prefers_settings_value_over_model_default(self) -> None:
        """An omitted option takes the value of the supplied settings model."""
        settings = self.OptionsDefaultsModel(name="override-name")
        invocation, received = self._run(
            self.OptionsDefaultsModel,
            [],
            settings=settings,
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
            self.OptionsDefaultsModel,
            _capture,
            settings=settings,
        )

        result = command(name="parsed-name")

        tm.that(result, eq="parsed-name")
        tm.that(received["model"].name, eq="parsed-name")
        tm.that(settings.name, eq="start-name")
