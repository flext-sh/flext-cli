"""Behavioral tests for cardinality-preserving TOML trivia removal."""

from __future__ import annotations

import pytest
from flext_tests import tm

from tests import u


class TestsFlextCliTomlTrivia:
    """Public contract for safe structural trivia removal."""

    def test_discard_preserves_nested_public_lookups(self) -> None:
        """Discard comment trivia without shifting keyed lookup indexes."""
        rendered = (
            "# managed marker\n"
            "[project]\n"
            'name = "demo"\n'
            "[project.optional-dependencies]\n"
            'dev = ["pytest"]\n'
        )
        document = u.Cli.toml_parse_text(rendered)
        expected = u.Cli.toml_mapping_from_text(rendered)
        if document is None:
            pytest.fail("valid TOML must produce a document")

        u.Cli.toml_discard_unkeyed_items(document, (0,))

        project = u.Cli.toml_table_child(document, "project")
        if project is None:
            pytest.fail("project table must remain addressable")
        optional = u.Cli.toml_table_child(project, "optional-dependencies")
        if optional is None:
            pytest.fail("optional-dependencies table must remain addressable")
        tm.that(u.Cli.toml_item_child(optional, "dev"), none=False)
        tm.that(u.Cli.toml_as_mapping(document), eq=expected)
        tm.that(u.Cli.toml_dumps(document).startswith("# managed marker"), eq=False)

    def test_discard_rejects_keyed_or_duplicate_indexes(self) -> None:
        """Fail loud rather than corrupting a keyed or ambiguous TOML slot."""
        document = u.Cli.toml_parse_text('# comment\nname = "demo"\n')
        if document is None:
            pytest.fail("valid TOML must produce a document")
        original = u.Cli.toml_dumps(document)

        with pytest.raises(ValueError, match="unique"):
            u.Cli.toml_discard_unkeyed_items(document, (0, 0))
        tm.that(u.Cli.toml_dumps(document), eq=original)
        with pytest.raises(ValueError, match="keyed"):
            u.Cli.toml_discard_unkeyed_items(document, (0, 1))
        tm.that(u.Cli.toml_dumps(document), eq=original)
        with pytest.raises(IndexError, match="outside"):
            u.Cli.toml_discard_unkeyed_items(document, (0, 2))
        tm.that(u.Cli.toml_dumps(document), eq=original)


__all__: list[str] = ["TestsFlextCliTomlTrivia"]
