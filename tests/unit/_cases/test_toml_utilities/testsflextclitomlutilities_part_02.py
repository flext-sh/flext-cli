"""Tests for the generic TOML helpers exposed via ``u.Cli.toml_*``."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_tests import tm
from tests.utilities import u

if TYPE_CHECKING:
    from tests.typings import t


class TestsFlextCliTomlUtilities:
    """Implementation part for TestsFlextCliTomlUtilities."""

    def test_ensure_table_reuses_existing(self) -> None:
        parent = u.Cli.toml_table()
        existing = u.Cli.toml_table()
        existing["key"] = "value"
        parent["section"] = existing

        table = u.Cli.toml_ensure_table(parent, "section")

        tm.that(u.Cli.toml_value(table, "key"), eq="value")

    def test_path_helpers_navigate_and_lookup_tables(self) -> None:
        doc = u.Cli.toml_document()

        created = u.Cli.toml_ensure_path(doc, ("tool", "ruff", "lint"))
        created["select"] = u.Cli.toml_array(["E", "F"])

        resolved = u.Cli.toml_table_path(doc, ("tool", "ruff", "lint"))

        assert resolved is not None
        tm.that(
            u.Cli.toml_as_string_list(u.Cli.toml_item_child(resolved, "select")),
            eq=["E", "F"],
        )
        tm.that(u.Cli.toml_table_path(doc, ("tool", "mypy")), none=True)

    def test_dot_path_and_navigate_path_keep_tool_prefix_stable(self) -> None:
        doc = u.Cli.toml_document()
        table = u.Cli.toml_navigate_path(doc, ["tool", "pytest", "ini_options"])

        table["addopts"] = "-q"

        tm.that(
            u.Cli.toml_dot_path("", "tool", "pytest", "ini_options"),
            eq="tool.pytest.ini_options",
        )
        tm.that(
            u.Cli.toml_value(
                u.Cli.toml_navigate_path(doc, ["pytest", "ini_options"]),
                "addopts",
            ),
            eq="-q",
        )

    def test_as_mapping_and_lookup_helpers(self) -> None:
        mapping: t.MappingKV[str, t.Scalar] = {"key": "value"}
        tm.that(u.Cli.toml_as_mapping(mapping), eq=mapping)
        tm.that(u.Cli.toml_as_mapping("bad"), none=True)
        doc = u.Cli.toml_document()
        doc["a"] = 1
        doc["b"] = [1, 2]
        tm.that(u.Cli.toml_value(doc, "a"), eq=1)
        tm.that(u.Cli.toml_value(doc, "b"), eq=[1, 2])
        tm.that(u.Cli.toml_value(doc, "missing"), none=True)

    def test_mapping_path_normalizes_toml_document_children(self) -> None:
        doc = u.Cli.toml_document()
        project = u.Cli.toml_table()
        tool = u.Cli.toml_table()
        pytest_config = u.Cli.toml_table()
        pytest_config["addopts"] = "-q"
        tool["pytest"] = pytest_config
        project["name"] = "demo"
        doc["project"] = project
        doc["tool"] = tool

        resolved = u.Cli.toml_mapping_path(doc, ["tool", "pytest"])

        tm.that(resolved, none=False)
        assert resolved is not None
        tm.that(resolved["addopts"], eq="-q")

    def test_mapping_from_text_and_document_builder_round_trip(self) -> None:
        text = (
            "[project]\n"
            'name = "demo"\n'
            'dependencies = ["httpx>=0.27"]\n'
            "\n"
            "[tool.pytest.ini_options]\n"
            'addopts = ["-q"]\n'
        )

        mapping = u.Cli.toml_mapping_from_text(text)

        tm.that(mapping, none=False)
        assert mapping is not None
        document = u.Cli.toml_document_from_mapping(mapping)
        project = u.Cli.toml_table_child(document, "project")
        tm.that(project is not None, eq=True)
        assert project is not None
        tm.that(u.Cli.toml_value(project, "name"), eq="demo")
        tm.that(
            u.Cli.toml_as_string_list(u.Cli.toml_item_child(project, "dependencies")),
            eq=["httpx>=0.27"],
        )

    def test_mapping_from_text_rejects_invalid_toml(self) -> None:
        tm.that(u.Cli.toml_mapping_from_text("[project"), none=True)


__all__: list[str] = ["TestsFlextCliTomlUtilities"]
