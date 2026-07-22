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
from flext_tests import tm
from tests import c, p, t


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

    class DictAnnotationModel(m.BaseModel):
        """Group the DictAnnotationModel test behavior."""

        value: dict[str, int]

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
        valid_mapping: t.Cli.DefaultMapping = m.Field(
            dict(c.Tests.OPTIONS_FIELD_DEFAULT_VALID_MAPPING), validate_default=True
        )
        invalid_mapping: t.JsonValue = m.Field(
            dict(c.Tests.OPTIONS_FIELD_DEFAULT_INVALID_MAPPING), validate_default=True
        )

    _ANNOTATION_CASES: ClassVar[
        tuple[tuple[type[t.Cli.ModelLike], t.Cli.RuntimeAnnotation], ...]
    ] = (
        (StringAnnotationModel, str),
        (OptionalStringAnnotationModel, str),
        (UnionAnnotationModel, str),
        (ListAnnotationModel, list[str]),
        (TupleAnnotationModel, list[str]),
        (SetAnnotationModel, set),
        (FrozenSetAnnotationModel, frozenset),
        (DictAnnotationModel, dict),
        (AnnotatedStringModel, str),
        (StringListAliasModel, list[str]),
    )

    @staticmethod
    def _noop_handler(_params: t.Cli.ModelLike) -> bool:
        return True

    @staticmethod
    def _option_spec(
        command: t.Cli.CliCommand, param_name: str
    ) -> p.Tests.FrameworkOption:
        """Return the Typer option object the builder placed on the command signature."""
        spec = inspect.signature(command).parameters[param_name].default
        tm.that(spec.param_decls, empty=False)
        return spec

    # ---- generated-command contract -------------------------------------

    def test_model_command_uses_field_alias_as_option_name(self) -> None:
        """Verify that model command uses field alias as option name."""
        command = cli.model_command(self.AliasOptionsModel, self._noop_handler)
        spec = self._option_spec(command, "project_name")
        tm.that(spec.param_decls, has="--project")

    def test_model_command_honors_custom_param_decls(self) -> None:
        """Verify that model command honors custom param decls."""
        command = cli.model_command(self.CustomDeclModel, self._noop_handler)
        spec = self._option_spec(command, "custom_name")
        tm.that(spec.param_decls, has="--custom-name")
        tm.that(spec.param_decls, has="--projects")

    def test_model_command_renders_bool_field_as_toggle_flag(self) -> None:
        """Verify that model command renders bool field as toggle flag."""
        command = cli.model_command(self.BoolToggleModel, self._noop_handler)
        spec = self._option_spec(command, "debug")
        tm.that(spec.param_decls, eq=["--debug/--no-debug"])

    @pytest.mark.parametrize(("model_cls", "expected"), _ANNOTATION_CASES)
    def test_model_command_normalizes_runtime_annotations(
        self, model_cls: type[t.Cli.ModelLike], expected: t.Cli.RuntimeAnnotation
    ) -> None:
        """Verify that model command normalizes runtime annotations."""
        command = cli.model_command(model_cls, self._noop_handler)
        resolved = inspect.signature(command).parameters["value"].annotation
        tm.that(resolved == expected, eq=True)

    def test_model_command_marks_required_field_default_as_ellipsis(self) -> None:
        """Verify that model command marks required field default as ellipsis."""
        command = cli.model_command(self.AliasOptionsModel, self._noop_handler)
        spec = self._option_spec(command, "project_name")
        tm.that(spec.default is ..., eq=True)

    def test_field_default_prefers_settings_value_over_model_default(self) -> None:
        """Verify that field default prefers settings value over model default."""
        settings = self.OptionsDefaultsModel(name="override-name")
        command = cli.model_command(
            self.OptionsDefaultsModel, self._noop_handler, settings=settings
        )
        spec = self._option_spec(command, "name")
        tm.that(spec.default, eq="override-name")

    def test_field_default_normalizes_sequence_default_to_tuple(self) -> None:
        """Verify that field default normalizes sequence default to tuple."""
        command = cli.model_command(self.OptionsDefaultsModel, self._noop_handler)
        spec = self._option_spec(command, "generated")
        tm.that(spec.default, eq=("gen", "value"))

    def test_field_default_preserves_normalizable_mapping(self) -> None:
        """Verify that field default preserves normalizable mapping."""
        command = cli.model_command(self.OptionsDefaultsModel, self._noop_handler)
        spec = self._option_spec(command, "valid_mapping")
        tm.that(spec.default, eq=dict(c.Tests.OPTIONS_FIELD_DEFAULT_VALID_MAPPING))

    def test_field_default_drops_non_normalizable_mapping_to_none(self) -> None:
        """Verify that field default drops non normalizable mapping to none."""
        command = cli.model_command(self.OptionsDefaultsModel, self._noop_handler)
        spec = self._option_spec(command, "invalid_mapping")
        tm.that(spec.default, none=True)

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
