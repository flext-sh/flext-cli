"""Coverage tests for public option behavior on ``cli.model_command``."""

from __future__ import annotations

import inspect
from typing import Annotated

import pytest

from flext_cli import cli, m
from tests.constants import c
from tests.protocols import p
from tests.typings import t

type OptionalStringAlias = str | None
type StringListAlias = list[str]


class StringAnnotationModel(m.BaseModel):
    value: str


class OptionalStringAnnotationModel(m.BaseModel):
    value: OptionalStringAlias


class UnionAnnotationModel(m.BaseModel):
    value: str | int


class ListAnnotationModel(m.BaseModel):
    value: list[str]


class TupleAnnotationModel(m.BaseModel):
    value: t.StrSequence


class SetAnnotationModel(m.BaseModel):
    value: set[str]


class FrozenSetAnnotationModel(m.BaseModel):
    value: frozenset[str]


class DictAnnotationModel(m.BaseModel):
    value: dict[str, int]


class AnnotatedStringModel(m.BaseModel):
    value: Annotated[str, "meta"]


class StringListAliasModel(m.BaseModel):
    value: StringListAlias


ANNOTATION_CASES: tuple[tuple[t.Cli.ModelType[m.BaseModel], object], ...] = (
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


class AliasOptionsModel(m.BaseModel):
    project_name: str = m.Field(
        ...,
        alias="project",
        validate_default=True,
    )


class CustomDeclModel(m.BaseModel):
    custom_name: str = m.Field(
        ...,
        json_schema_extra={"typer_param_decls": ["--custom-name", "--projects"]},
        validate_default=True,
    )


class BoolToggleModel(m.BaseModel):
    debug: bool = False


def _noop_handler(_params: t.Cli.ModelLike) -> bool:
    return True


class OptionsDefaultsModel(m.BaseModel):
    """Model used to exercise field-default normalization paths."""

    name: str = "default-name"
    tags: t.StrSequence = ("a", "b")
    generated: t.StrSequence = m.Field(default_factory=lambda: ("gen", "value"))
    valid_mapping: t.Cli.DefaultMapping = m.Field(
        default_factory=lambda: dict(c.Tests.OPTIONS_FIELD_DEFAULT_VALID_MAPPING),
    )
    invalid_mapping: object = m.Field(
        default_factory=lambda: dict(c.Tests.OPTIONS_FIELD_DEFAULT_INVALID_MAPPING),
    )


class TestsFlextCliOptionsUtilsCov:
    """Data-driven coverage for public option generation behavior."""

    def test_model_command_uses_alias_for_option_name(self) -> None:
        command = cli.model_command(AliasOptionsModel, _noop_handler)
        option_info = inspect.signature(command).parameters["project_name"].default
        assert isinstance(option_info, p.Cli.CliOptionSpec)
        assert option_info.param_decls is not None
        assert "--project" in option_info.param_decls

    def test_model_command_supports_custom_param_decls(self) -> None:
        command = cli.model_command(CustomDeclModel, _noop_handler)
        option_info = inspect.signature(command).parameters["custom_name"].default
        assert isinstance(option_info, p.Cli.CliOptionSpec)
        assert option_info.param_decls is not None
        assert "--custom-name" in option_info.param_decls
        assert "--projects" in option_info.param_decls

    def test_model_command_bool_uses_toggle_decl(self) -> None:
        command = cli.model_command(BoolToggleModel, _noop_handler)
        option_info = inspect.signature(command).parameters["debug"].default
        assert isinstance(option_info, p.Cli.CliOptionSpec)
        assert option_info.param_decls == ["--debug/--no-debug"]

    @pytest.mark.parametrize(("model_cls", "expected"), ANNOTATION_CASES)
    def test_model_command_normalizes_runtime_annotations(
        self,
        model_cls: t.Cli.ModelType[t.Cli.ModelLike],
        expected: object,
    ) -> None:
        command = cli.model_command(model_cls, _noop_handler)
        resolved = inspect.signature(command).parameters["value"].annotation
        assert resolved == expected

    def test_field_default_prefers_settings_value(self) -> None:
        settings = OptionsDefaultsModel(name="override-name")
        command = cli.model_command(
            OptionsDefaultsModel,
            _noop_handler,
            settings=settings,
        )
        option_info = inspect.signature(command).parameters["name"].default
        assert isinstance(option_info, p.Cli.CliOptionSpec)
        assert option_info.default == "override-name"

    def test_field_default_uses_default_factory_sequence(self) -> None:
        command = cli.model_command(OptionsDefaultsModel, _noop_handler)
        option_info = inspect.signature(command).parameters["generated"].default
        assert isinstance(option_info, p.Cli.CliOptionSpec)
        assert option_info.default == ("gen", "value")

    def test_field_default_returns_valid_mapping(self) -> None:
        command = cli.model_command(OptionsDefaultsModel, _noop_handler)
        option_info = inspect.signature(command).parameters["valid_mapping"].default
        assert isinstance(option_info, p.Cli.CliOptionSpec)
        assert option_info.default == dict(c.Tests.OPTIONS_FIELD_DEFAULT_VALID_MAPPING)

    def test_field_default_invalid_mapping_returns_none(self) -> None:
        command = cli.model_command(OptionsDefaultsModel, _noop_handler)
        option_info = inspect.signature(command).parameters["invalid_mapping"].default
        assert isinstance(option_info, p.Cli.CliOptionSpec)
        assert option_info.default is None


__all__: list[str] = ["TestsFlextCliOptionsUtilsCov"]
