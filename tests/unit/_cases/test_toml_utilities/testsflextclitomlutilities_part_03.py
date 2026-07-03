"""Tests for the generic TOML helpers exposed via ``u.Cli.toml_*``."""

from __future__ import annotations

import tomllib
from pathlib import Path

from flext_tests import tm
from tests.typings import t
from tests.utilities import u


class TestsFlextCliTomlUtilities:
    """Implementation part for TestsFlextCliTomlUtilities."""

    def test_mapping_helpers_sync_nested_tables(self) -> None:
        payload: dict[str, t.JsonValue] = {
            "tool": {
                "uv": {
                    "sources": {
                        "stale": {"workspace": True},
                    },
                },
            },
        }
        changes: list[str] = []

        sources = u.Cli.toml_mapping_ensure_path(payload, ("tool", "uv", "sources"))
        if u.Cli.toml_mapping_sync_mapping_table(
            sources,
            "flext-core",
            {"workspace": True},
            sort_keys=True,
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
        assert tool is not None
        uv = u.Cli.toml_mapping_child(tool, "uv")
        tm.that(uv is not None, eq=True)
        assert uv is not None
        workspace = u.Cli.toml_mapping_child(uv, "workspace")
        tm.that(workspace, none=False)
        assert workspace is not None
        tm.that(workspace.get("members"), eq=["flext-cli", "flext-core"])

    def test_read_json_and_write_mapping_round_trip(self, tmp_path: Path) -> None:
        toml_file = tmp_path / "pyproject.toml"
        toml_file.write_text(
            '[project]\nname = "demo"\ndependencies = ["httpx>=0.27"]\n',
            encoding="utf-8",
        )

        result = u.Cli.toml_read_json(toml_file)

        tm.ok(result)
        project = u.Cli.toml_mapping_child(result.value, "project")
        tm.that(project, none=False)
        assert project is not None
        tm.that(project.get("name"), eq="demo")
        updated_payload: dict[str, t.JsonValue] = {
            key: result.value[key] for key in result.value
        }
        updated_payload["tool"] = {
            "uv": {
                "sources": {
                    "flext-core": {"workspace": True},
                },
            },
        }
        tm.ok(u.Cli.toml_write_mapping(toml_file, updated_payload))
        rendered = tomllib.loads(toml_file.read_text(encoding="utf-8"))
        project = rendered["project"]
        assert isinstance(project, dict)
        tm.that(project["name"], eq="demo")
        tool = rendered["tool"]
        assert isinstance(tool, dict)
        uv = tool["uv"]
        assert isinstance(uv, dict)
        sources = uv["sources"]
        assert isinstance(sources, dict)
        flext_core = sources["flext-core"]
        assert isinstance(flext_core, dict)
        tm.that(flext_core["workspace"], eq=True)


__all__: list[str] = ["TestsFlextCliTomlUtilities"]
