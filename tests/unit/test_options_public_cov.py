"""Public coverage tests for the CLI option helpers on ``u.Cli``."""

from __future__ import annotations

from pathlib import Path

from flext_cli import m
from tests.constants import c
from tests.typings import t
from tests.utilities import u


class _OptionSettings(m.BaseModel):
    """Settings model used to exercise public default normalization."""

    output_path: Path = Path("reports/output.json")
    tags: t.StrSequence = ("lint", "typecheck")
    flags: dict[str, bool] = {"debug": True}


class TestsFlextCliOptionsPublicCoverage:
    """Exercise public option helpers through `u.Cli` only."""

    def test_resolve_typer_annotation_covers_union_sequence_and_collections(
        self,
    ) -> None:
        optional_string = u.Cli.resolve_typer_annotation(str | None)
        repeated_strings = u.Cli.resolve_typer_annotation(t.StrSequence)
        plain_mapping = u.Cli.resolve_typer_annotation(dict[str, int])
        frozen_values = u.Cli.resolve_typer_annotation(frozenset[str])
        multi_union = u.Cli.resolve_typer_annotation(str | int)

        assert optional_string is str
        assert repeated_strings == list[str]
        assert plain_mapping is dict
        assert frozen_values is frozenset
        assert multi_union is str

    def test_option_defaults_and_atoms_normalize_public_values(self) -> None:
        settings = _OptionSettings()
        fields = _OptionSettings.model_fields

        assert u.Cli.normalize_cli_atom(Path("reports/out.json")) == "reports/out.json"
        assert u.Cli.normalize_cli_atom(["lint", "test"]) == ("lint", "test")
        assert u.Cli.normalize_cli_atom({"bad": "value"}) is None
        assert u.Cli.is_string_sequence(("lint", "test")) is True
        assert u.Cli.is_string_sequence(Path("reports/out.json")) is False

        assert (
            u.Cli.field_default("output_path", fields["output_path"], settings)
            == "reports/output.json"
        )
        assert u.Cli.field_default("tags", fields["tags"], settings) == (
            "lint",
            "typecheck",
        )
        assert u.Cli.field_default("flags", fields["flags"], settings) == {
            "debug": True,
        }

    def test_build_option_and_reorder_prefixed_options_cover_registry_contract(
        self,
    ) -> None:
        project_option = u.Cli.build_option("project", {"project": {"short": "p"}})
        debug_option = u.Cli.build_option(
            "debug",
            c.Cli.CLI_PARAM_REGISTRY,
        )

        reordered = u.Cli.reorder_prefixed_options(
            ["--debug", "--log-level", "DEBUG", "check", "--all"],
            bool_options=("--debug",),
            value_options=("--log-level",),
        )
        unchanged = u.Cli.reorder_prefixed_options(
            ["check", "--all"],
            bool_options=("--debug",),
            value_options=("--log-level",),
        )
        project_param_decls = project_option.param_decls
        debug_param_decls = debug_option.param_decls

        assert project_param_decls is not None
        assert debug_param_decls is not None
        assert "--project" in project_param_decls
        assert "--projects" in project_param_decls
        assert "-p" in project_param_decls
        assert "--debug" in debug_param_decls
        assert reordered == ["check", "--debug", "--log-level", "DEBUG", "--all"]
        assert unchanged == ["check", "--all"]
