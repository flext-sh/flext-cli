"""Coverage tests for flext_cli._utilities.options."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import pytest
from typer.models import OptionInfo

from flext_cli._utilities.options import (
    FlextCliUtilitiesOptionBuilder,
    FlextCliUtilitiesOptions,
)
from tests import c, m, t

type OptionalStringAlias = str | None
type StringListAlias = list[str]

ANNOTATION_CASES: tuple[tuple[object, object], ...] = (
    (str, str),
    (OptionalStringAlias, str),
    (str | int, str),
    (list[str], list[str]),
    (tuple[str, ...], list[str]),
    (set[str], set),
    (frozenset[str], frozenset),
    (dict[str, int], dict),
    (Annotated[str, "meta"], str),
    (StringListAlias, list[str]),
)


class OptionsDefaultsModel(m.BaseModel):
    """Model used to exercise field-default normalization paths."""

    name: str = "default-name"
    tags: tuple[str, ...] = ("a", "b")
    generated: tuple[str, ...] = m.Field(default_factory=lambda: ("gen", "value"))
    valid_mapping: t.Cli.DefaultMapping = m.Field(
        default_factory=lambda: dict(c.Tests.OPTIONS_FIELD_DEFAULT_VALID_MAPPING),
    )
    invalid_mapping: object = m.Field(
        default_factory=lambda: dict(c.Tests.OPTIONS_FIELD_DEFAULT_INVALID_MAPPING),
    )


class TestsFlextCliOptionsUtilsCov:
    """Data-driven coverage for FlextCliUtilitiesOptions."""

    @pytest.mark.parametrize(
        ("field_name", "expect_build_ok"), c.Tests.OPTIONS_BUILD_CASES
    )
    def test_option_builder_build_cases(
        self,
        field_name: str,
        expect_build_ok: bool,
    ) -> None:
        builder = FlextCliUtilitiesOptionBuilder(
            field_name,
            c.Tests.OPTIONS_REGISTRY_VALID,
        )
        option_info = builder.build()
        assert isinstance(option_info, OptionInfo)
        assert expect_build_ok is True
        assert option_info.help is not None
        if field_name == "project":
            assert option_info.param_decls is not None
            assert "--project" in option_info.param_decls
            assert "--projects" in option_info.param_decls
        if field_name == "custom_name":
            assert option_info.param_decls is not None
            assert "--custom-name" in option_info.param_decls

    def test_option_builder_build_missing_registry_metadata_raises(self) -> None:
        builder = FlextCliUtilitiesOptionBuilder(
            "missing",
            c.Tests.OPTIONS_REGISTRY_EMPTY,
        )
        with pytest.raises(TypeError):
            builder.build()

    def test_build_option_proxy(self) -> None:
        option_info = FlextCliUtilitiesOptions.build_option(
            "project",
            c.Tests.OPTIONS_REGISTRY_VALID,
        )
        assert isinstance(option_info, OptionInfo)
        assert option_info.param_decls is not None
        assert "--projects" in option_info.param_decls

    @pytest.mark.parametrize(("annotation", "expected"), ANNOTATION_CASES)
    def test_resolve_typer_annotation_cases(
        self,
        annotation: t.Cli.RuntimeAnnotation,
        expected: object,
    ) -> None:
        result = FlextCliUtilitiesOptions.resolve_typer_annotation(annotation)
        assert result == expected

    @pytest.mark.parametrize(
        ("value", "expected"),
        c.Tests.OPTIONS_IS_STRING_SEQUENCE_CASES,
    )
    def test_is_string_sequence_cases(
        self,
        value: t.Cli.CliDefaultSource,
        expected: bool,
    ) -> None:
        assert FlextCliUtilitiesOptions.is_string_sequence(value) is expected

    def test_is_string_sequence_false_for_path(self) -> None:
        assert FlextCliUtilitiesOptions.is_string_sequence(Path("/tmp/demo")) is False

    def test_is_string_sequence_false_for_mapping(self) -> None:
        assert FlextCliUtilitiesOptions.is_string_sequence({"count": 1}) is False

    @pytest.mark.parametrize(
        ("value", "expected"),
        c.Tests.OPTIONS_NORMALIZE_ATOM_CASES,
    )
    def test_normalize_cli_atom_cases(
        self,
        value: t.Cli.CliDefaultSource,
        expected: t.Cli.DefaultAtom | None,
    ) -> None:
        assert FlextCliUtilitiesOptions.normalize_cli_atom(value) == expected

    def test_normalize_cli_atom_path(self) -> None:
        result = FlextCliUtilitiesOptions.normalize_cli_atom(Path("/tmp/demo"))
        assert result == "/tmp/demo"

    def test_normalize_cli_atom_invalid_returns_none(self) -> None:
        result = FlextCliUtilitiesOptions.normalize_cli_atom(
            dict(c.Tests.OPTIONS_FIELD_DEFAULT_VALID_MAPPING),
        )
        assert result is None

    def test_field_default_prefers_settings_value(self) -> None:
        settings = OptionsDefaultsModel(name="override-name")
        field_info = OptionsDefaultsModel.model_fields["name"]
        result = FlextCliUtilitiesOptions.field_default("name", field_info, settings)
        assert result == "override-name"

    def test_field_default_uses_default_factory_sequence(self) -> None:
        field_info = OptionsDefaultsModel.model_fields["generated"]
        result = FlextCliUtilitiesOptions.field_default("generated", field_info, None)
        assert result == ("gen", "value")

    def test_field_default_returns_valid_mapping(self) -> None:
        field_info = OptionsDefaultsModel.model_fields["valid_mapping"]
        result = FlextCliUtilitiesOptions.field_default(
            "valid_mapping", field_info, None
        )
        assert result == dict(c.Tests.OPTIONS_FIELD_DEFAULT_VALID_MAPPING)

    def test_field_default_invalid_mapping_returns_none(self) -> None:
        field_info = OptionsDefaultsModel.model_fields["invalid_mapping"]
        result = FlextCliUtilitiesOptions.field_default(
            "invalid_mapping", field_info, None
        )
        assert result is None

    @pytest.mark.parametrize(
        ("args", "bool_options", "value_options", "expected"),
        c.Tests.OPTIONS_REORDER_CASES,
    )
    def test_reorder_prefixed_options_cases(
        self,
        args: tuple[str, ...],
        bool_options: tuple[str, ...],
        value_options: tuple[str, ...],
        expected: tuple[str, ...],
    ) -> None:
        result = FlextCliUtilitiesOptions.reorder_prefixed_options(
            args,
            bool_options=bool_options,
            value_options=value_options,
        )
        assert result == list(expected)

    def test_reorder_prefixed_options_empty_args(self) -> None:
        result = FlextCliUtilitiesOptions.reorder_prefixed_options(
            (),
            bool_options=("--verbose",),
            value_options=("--project",),
        )
        assert result == []


__all__: list[str] = ["TestsFlextCliOptionsUtilsCov"]
