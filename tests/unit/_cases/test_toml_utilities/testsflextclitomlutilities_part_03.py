"""Tests for the generic TOML helpers exposed via ``u.Cli.toml_*``."""

from __future__ import annotations

import tomllib
from typing import TYPE_CHECKING

from flext_tests import tm
from tests import u

if TYPE_CHECKING:
    from pathlib import Path

    from tests import t


class TestsFlextCliTomlUtilities:
    """Implementation part for TestsFlextCliTomlUtilities."""

    def test_mapping_helpers_sync_nested_tables(self) -> None:
        """Verify that mapping helpers sync nested tables."""
        payload: dict[str, t.JsonValue] = {
            "tool": {"uv": {"sources": {"stale": {"workspace": True}}}}
        }
        changes: list[str] = []

        sources = u.Cli.toml_mapping_ensure_path(payload, ("tool", "uv", "sources"))
        if u.Cli.toml_mapping_sync_mapping_table(
            sources, "flext-core", {"workspace": True}, sort_keys=True
        ):
            changes.append("synced flext-core")
        if u.Cli.toml_mapping_sync_string_list(
            u.Cli.toml_mapping_ensure_path(payload, ("tool", "uv", "workspace")),
            "members",
            ("flext-cli", "flext-core"),
            sort_values=True,
        ):
            changes.append("synced members")

        tm.that(changes, eq=["synced flext-core", "synced members"])
        tool = u.Cli.toml_mapping_child(payload, "tool")
        tm.that(tool is not None, eq=True)
        tool = tm.not_none(tool)
        uv = u.Cli.toml_mapping_child(tool, "uv")
        tm.that(uv is not None, eq=True)
        uv = tm.not_none(uv)
        workspace = u.Cli.toml_mapping_child(uv, "workspace")
        workspace = tm.not_none(workspace)
        workspace = tm.not_none(workspace)
        tm.that(workspace.get("members"), eq=["flext-cli", "flext-core"])

    def test_read_json_and_write_mapping_round_trip(self, tmp_path: Path) -> None:
        """Verify that read json and write mapping round trip."""
        toml_file = tmp_path / "pyproject.toml"
        toml_file.write_text(
            '[project]\nname = "demo"\ndependencies = ["httpx>=0.27"]\n',
            encoding="utf-8",
        )

        result = u.Cli.toml_read_json(toml_file)

        tm.ok(result)
        project = u.Cli.toml_mapping_child(result.value, "project")
        project = tm.not_none(project)
        project = tm.not_none(project)
        tm.that(project.get("name"), eq="demo")
        updated_payload: dict[str, t.JsonValue] = {
            key: result.value[key] for key in result.value
        }
        updated_payload["tool"] = {
            "uv": {"sources": {"flext-core": {"workspace": True}}}
        }
        tm.ok(u.Cli.toml_write_mapping(toml_file, updated_payload))
        rendered = tomllib.loads(toml_file.read_text(encoding="utf-8"))
        project = rendered["project"]
        tm.that(project, is_=dict)
        tm.that(project["name"], eq="demo")
        tool = rendered["tool"]
        tm.that(tool, is_=dict)
        uv = tool["uv"]
        tm.that(uv, is_=dict)
        sources = uv["sources"]
        tm.that(sources, is_=dict)
        flext_core = sources["flext-core"]
        tm.that(flext_core, is_=dict)
        tm.that(flext_core["workspace"], eq=True)


__all__: list[str] = ["TestsFlextCliTomlUtilities"]
