"""Behavioral tests for the public CLI option helpers on ``u.Cli``.

Every assertion targets an observable contract of the public helpers:
annotation resolution, atom normalization, string-sequence detection,
field-default resolution, option-spec construction and argument reordering.
No private state, collaborator spying, or patching is used.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from flext_cli import c, m
from tests.typings import t
from tests.utilities import u


class TestsFlextCliOptions:
    """Exercise the public option helpers exposed through ``u.Cli``."""

    class _OptionSettings(m.BaseModel):
        """Settings model used to exercise public default normalization."""

        output_path: Path = Path("reports/output.json")
        tags: t.StrSequence = ("lint", "typecheck")
        flags: dict[str, bool] = {"debug": True}

    @pytest.mark.parametrize(
        ("annotation", "expected"),
        [
            (str | None, str),
            (str | int, str),
            (dict[str, int], dict),
            (frozenset[str], frozenset),
            (set[str], set),
            (int, int),
        ],
    )
    def test_resolve_typer_annotation_maps_scalars_unions_and_collections(
        self,
        annotation: t.Cli.RuntimeAnnotation,
        expected: type,
    ) -> None:
        assert u.Cli.resolve_typer_annotation(annotation) is expected

    def test_resolve_typer_annotation_maps_string_sequence_to_list_of_str(
        self,
    ) -> None:
        assert u.Cli.resolve_typer_annotation(t.StrSequence) == list[str]

    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            (Path("reports/out.json"), "reports/out.json"),
            (["lint", "test"], ("lint", "test")),
            (("lint", "test"), ("lint", "test")),
            ("plain", "plain"),
            (42, 42),
            (True, True),
            ({"bad": "value"}, None),
            ([1, 2, 3], None),
        ],
    )
    def test_normalize_cli_atom_returns_typer_ready_value_or_none(
        self,
        value: t.Cli.CliDefaultSource,
        expected: t.Cli.DefaultAtom | None,
    ) -> None:
        assert u.Cli.normalize_cli_atom(value) == expected

    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            (("lint", "test"), True),
            (["lint", "test"], True),
            ((), True),
            (Path("reports/out.json"), False),
            ("lint", False),
            (b"lint", False),
            ((1, 2), False),
        ],
    )
    def test_is_string_sequence_recognizes_only_str_sequences(
        self,
        value: t.Cli.CliDefaultSource,
        expected: bool,
    ) -> None:
        assert u.Cli.is_string_sequence(value) is expected

    def test_field_default_prefers_settings_scalar_over_field_metadata(self) -> None:
        settings = self._OptionSettings()
        fields = self._OptionSettings.model_fields

        assert (
            u.Cli.field_default("output_path", fields["output_path"], settings)
            == "reports/output.json"
        )

    def test_field_default_normalizes_sequence_field_to_tuple(self) -> None:
        settings = self._OptionSettings()
        fields = self._OptionSettings.model_fields

        assert u.Cli.field_default("tags", fields["tags"], settings) == (
            "lint",
            "typecheck",
        )

    def test_field_default_normalizes_mapping_field_preserving_entries(self) -> None:
        settings = self._OptionSettings()
        fields = self._OptionSettings.model_fields

        assert u.Cli.field_default("flags", fields["flags"], settings) == {
            "debug": True,
        }

    def test_field_default_falls_back_to_field_metadata_without_settings(self) -> None:
        fields = self._OptionSettings.model_fields

        assert (
            u.Cli.field_default("output_path", fields["output_path"], None)
            == "reports/output.json"
        )

    def test_build_option_registers_aliases_and_short_flag_from_spec(self) -> None:
        option = u.Cli.build_option("project", {"project": {"short": "p"}})

        param_decls = option.param_decls
        assert param_decls is not None
        assert "--project" in param_decls
        assert "--projects" in param_decls
        assert "-p" in param_decls

    def test_build_option_reads_canonical_registry_contract(self) -> None:
        option = u.Cli.build_option("debug", c.Cli.CLI_PARAM_REGISTRY)

        param_decls = option.param_decls
        assert param_decls is not None
        assert "--debug" in param_decls

    def test_reorder_prefixed_options_moves_shared_flags_after_subcommand(self) -> None:
        reordered = u.Cli.reorder_prefixed_options(
            ["--debug", "--log-level", "DEBUG", "check", "--all"],
            bool_options=("--debug",),
            value_options=("--log-level",),
        )

        assert reordered == ["check", "--debug", "--log-level", "DEBUG", "--all"]

    def test_reorder_prefixed_options_handles_equals_joined_value_option(self) -> None:
        reordered = u.Cli.reorder_prefixed_options(
            ["--log-level=DEBUG", "check", "--all"],
            bool_options=("--debug",),
            value_options=("--log-level",),
        )

        assert reordered == ["check", "--log-level=DEBUG", "--all"]

    @pytest.mark.parametrize(
        "args",
        [
            ["check", "--all"],
            [],
        ],
    )
    def test_reorder_prefixed_options_is_identity_without_leading_prefixes(
        self,
        args: list[str],
    ) -> None:
        assert (
            u.Cli.reorder_prefixed_options(
                args,
                bool_options=("--debug",),
                value_options=("--log-level",),
            )
            == args
        )

    def test_reorder_prefixed_options_is_idempotent(self) -> None:
        once = u.Cli.reorder_prefixed_options(
            ["--debug", "check", "--all"],
            bool_options=("--debug",),
            value_options=("--log-level",),
        )
        twice = u.Cli.reorder_prefixed_options(
            once,
            bool_options=("--debug",),
            value_options=("--log-level",),
        )

        assert once == twice == ["check", "--debug", "--all"]
