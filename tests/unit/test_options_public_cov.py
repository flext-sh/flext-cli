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
from tests import t
from tests import u
from flext_tests import tm


class TestsFlextCliOptions:
    """Exercise the public option helpers exposed through ``u.Cli``."""

    class _OptionSettings(m.BaseModel):
        """Settings model used to exercise public default normalization."""

        output_path: Path = Path("reports/output.json")
        tags: t.StrSequence = ("lint", "typecheck")
        flags: dict[str, bool] = m.Field(default_factory=lambda: {"debug": True})

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
        self, annotation: t.Cli.RuntimeAnnotation, expected: type
    ) -> None:
        """Resolve scalar, union, and collection annotations canonically."""
        tm.that(u.Cli.resolve_typer_annotation(annotation), eq=expected)

    def test_resolve_typer_annotation_maps_string_sequence_to_list_of_str(self) -> None:
        """Map the canonical string sequence alias to a repeatable CLI list."""
        tm.that(u.Cli.resolve_typer_annotation(t.StrSequence), eq=list[str])

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
        self, value: t.Cli.DefaultSource, expected: t.Cli.DefaultAtom | None
    ) -> None:
        """Normalize supported CLI atoms and reject unsupported values."""
        tm.that(u.Cli.cli_normalize_atom(value), eq=expected)

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
        self, value: t.Cli.DefaultSource, *, expected: bool
    ) -> None:
        """Recognize only sequences whose every member is a string."""
        tm.that(u.Cli.is_string_sequence(value), eq=expected)

    def test_field_default_prefers_settings_scalar_over_field_metadata(self) -> None:
        """Prefer a scalar sourced from validated settings."""
        settings = self._OptionSettings()
        fields = self._OptionSettings.model_fields

        tm.that(
            u.Cli.field_default("output_path", fields["output_path"], settings),
            eq="reports/output.json",
        )

    def test_field_default_normalizes_sequence_field_to_tuple(self) -> None:
        """Normalize a settings sequence to an immutable tuple."""
        settings = self._OptionSettings()
        fields = self._OptionSettings.model_fields

        tm.that(
            u.Cli.field_default("tags", fields["tags"], settings),
            eq=("lint", "typecheck"),
        )

    def test_field_default_normalizes_mapping_field_preserving_entries(self) -> None:
        """Preserve supported entries from a settings mapping."""
        settings = self._OptionSettings()
        fields = self._OptionSettings.model_fields

        tm.that(
            u.Cli.field_default("flags", fields["flags"], settings), eq={"debug": True}
        )

    def test_field_default_falls_back_to_field_metadata_without_settings(self) -> None:
        """Use field metadata when no settings object is supplied."""
        fields = self._OptionSettings.model_fields

        tm.that(
            u.Cli.field_default("output_path", fields["output_path"], None),
            eq="reports/output.json",
        )

    def test_build_option_registers_aliases_and_short_flag_from_spec(self) -> None:
        """Build ordered long, plural, and short declarations from metadata."""
        option = u.Cli.build_option("project", {"project": {"short": "p"}})

        declarations = option.declarations
        declarations = tm.not_none(declarations)
        tm.that(declarations, has="--project")
        tm.that(declarations, has="--projects")
        tm.that(declarations, has="-p")

    def test_build_option_reads_canonical_registry_contract(self) -> None:
        """Build an option from the canonical CLI parameter registry."""
        option = u.Cli.build_option("debug", c.Cli.CLI_PARAM_REGISTRY)

        declarations = option.declarations
        declarations = tm.not_none(declarations)
        tm.that(declarations, has="--debug")

    def test_reorder_prefixed_options_moves_shared_flags_after_subcommand(self) -> None:
        """Move shared prefix flags immediately after the subcommand."""
        reordered = u.Cli.reorder_prefixed_options(
            ["--debug", "--log-level", "DEBUG", "check", "--all"],
            bool_options=("--debug",),
            value_options=("--log-level",),
        )

        tm.that(reordered, eq=["check", "--debug", "--log-level", "DEBUG", "--all"])

    def test_reorder_prefixed_options_handles_equals_joined_value_option(self) -> None:
        """Preserve an equals-joined value while reordering its option."""
        reordered = u.Cli.reorder_prefixed_options(
            ["--log-level=DEBUG", "check", "--all"],
            bool_options=("--debug",),
            value_options=("--log-level",),
        )

        tm.that(reordered, eq=["check", "--log-level=DEBUG", "--all"])

    @pytest.mark.parametrize("args", [["check", "--all"], []])
    def test_reorder_prefixed_options_is_identity_without_leading_prefixes(
        self, args: list[str]
    ) -> None:
        """Preserve argument order when no shared option precedes the command."""
        tm.that(
            u.Cli.reorder_prefixed_options(
                args, bool_options=("--debug",), value_options=("--log-level",)
            ),
            eq=args,
        )

    def test_reorder_prefixed_options_is_idempotent(self) -> None:
        """Return the same ordering when applied repeatedly."""
        once = u.Cli.reorder_prefixed_options(
            ["--debug", "check", "--all"],
            bool_options=("--debug",),
            value_options=("--log-level",),
        )
        twice = u.Cli.reorder_prefixed_options(
            once, bool_options=("--debug",), value_options=("--log-level",)
        )

        tm.that(once, eq=twice)
