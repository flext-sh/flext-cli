"""Tests for the generic TOML helpers exposed via ``u.Cli.toml_*``."""

from __future__ import annotations

import os
import stat
import tomllib
from collections.abc import (
    Generator,
    Mapping,
)
from contextlib import contextmanager
from pathlib import Path

from flext_tests import tm

from tests import t, u


@contextmanager
def _temporary_environment(
    overrides: t.StrMapping,
) -> Generator[None]:
    original_values = {key: os.environ.get(key) for key in overrides}
    try:
        for key, value in overrides.items():
            os.environ[key] = value
        yield
    finally:
        for key, value in original_values.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


class TestsFlextCliTomlUtilities:
    """Tests for TOML read operations."""

    def test_read_existing_file(self, tmp_path: Path) -> None:
        toml_file = tmp_path / "test.toml"
        toml_file.write_text(
            '[section]\nkey = "value"\nnumber = 42\n',
            encoding="utf-8",
        )

        doc = u.Cli.toml_read(toml_file)

        assert doc is not None
        section = u.Cli.toml_table_child(doc, "section")
        assert section is not None
        tm.that(u.Cli.toml_value(section, "key"), eq="value")
        tm.that(u.Cli.toml_value(section, "number"), eq=42)

    def test_read_nonexistent_file(self, tmp_path: Path) -> None:
        tm.that(u.Cli.toml_read(tmp_path / "missing.toml"), none=True)

    def test_read_invalid_toml(self, tmp_path: Path) -> None:
        toml_file = tmp_path / "invalid.toml"
        toml_file.write_text("[invalid\nkey = value", encoding="utf-8")
        tm.that(u.Cli.toml_read(toml_file), none=True)

    def test_read_document_existing_file(self, tmp_path: Path) -> None:
        toml_file = tmp_path / "test.toml"
        toml_file.write_text('[section]\nkey = "value"  # comment\n', encoding="utf-8")

        result = u.Cli.toml_read_document(toml_file)

        tm.ok(result)
        section = u.Cli.toml_table_child(result.value, "section")
        assert section is not None
        tm.that(u.Cli.toml_value(section, "key"), eq="value")

    def test_read_document_nonexistent_file(self, tmp_path: Path) -> None:
        tm.fail(
            u.Cli.toml_read_document(tmp_path / "missing.toml"),
            has="failed to read TOML",
        )

    def test_write_document(self, tmp_path: Path) -> None:
        toml_file = tmp_path / "doc.toml"
        doc = u.Cli.toml_document()
        doc["section"] = {"key": "value"}

        result = u.Cli.toml_write_document(toml_file, doc)

        tm.ok(result)
        tm.that(toml_file.exists(), eq=True)

    def test_write_creates_parent_directories(self, tmp_path: Path) -> None:
        toml_file = tmp_path / "nested" / "deep" / "file.toml"
        doc = u.Cli.toml_document()
        doc["key"] = "value"

        tm.ok(u.Cli.toml_write_document(toml_file, doc))
        tm.that(toml_file.exists(), eq=True)

    def test_write_pyproject_runs_taplo(self, tmp_path: Path) -> None:
        pyproject = tmp_path / "pyproject.toml"
        taplo_config = tmp_path / ".taplo.toml"
        command_log = tmp_path / "taplo.log"
        bin_dir = tmp_path / "bin"
        bin_dir.mkdir()
        taplo_config.write_text("", encoding="utf-8")
        taplo = bin_dir / "taplo"
        taplo.write_text(
            "#!/bin/sh\n"
            f"printf '%s\\n' \"$PWD\" > '{command_log}'\n"
            'for arg in "$@"; do\n'
            f"  printf '%s\\n' \"$arg\" >> '{command_log}'\n"
            "done\n",
            encoding="utf-8",
        )
        taplo.chmod(stat.S_IRWXU)
        doc = u.Cli.toml_document()
        doc["project"] = {"name": "demo"}
        with _temporary_environment({
            "PATH": f"{bin_dir}:{os.environ.get('PATH', '')}",
        }):
            tm.ok(u.Cli.toml_write_document(pyproject, doc))
        logged_command = command_log.read_text(encoding="utf-8").splitlines()
        tm.that(logged_command[0], eq=str(tmp_path))
        tm.that(logged_command[1:3], eq=["format", "--config"])
        tm.that(logged_command, contains="--config")
        tm.that(logged_command, contains=str(taplo_config))
        tm.that(logged_command, contains=str(pyproject))

    def test_write_permission_error(self, tmp_path: Path) -> None:
        readonly_dir = tmp_path / "readonly"
        readonly_dir.mkdir()
        toml_file = readonly_dir / "test.toml"
        Path(readonly_dir).chmod(stat.S_IRUSR | stat.S_IXUSR)
        try:
            doc = u.Cli.toml_document()
            doc["key"] = "value"
            result = u.Cli.toml_write_document(toml_file, doc)
            tm.fail(result, has="TOML write error")
        finally:
            Path(readonly_dir).chmod(stat.S_IRWXU)

    def test_array_creates_multiline(self) -> None:
        arr = u.Cli.toml_array(["a", "b", "c"])
        arr_text = arr.as_string()
        tm.that(arr_text, has='"a"')
        tm.that(arr_text, has='"b"')
        tm.that(arr_text, has='"c"')

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
                u.Cli.toml_navigate_path(doc, ["pytest", "ini_options"]), "addopts"
            ),
            eq="-q",
        )

    def test_as_mapping_and_lookup_helpers(self) -> None:
        mapping: Mapping[str, t.Scalar] = {"key": "value"}
        tm.that(u.Cli.toml_as_mapping(mapping), eq=mapping)
        tm.that(u.Cli.toml_as_mapping("bad"), none=True)
        doc = u.Cli.toml_document()
        doc["a"] = 1
        doc["b"] = [1, 2]
        tm.that(u.Cli.toml_value(doc, "a"), eq=1)
        tm.that(u.Cli.toml_value(doc, "b"), eq=[1, 2])
        tm.that(u.Cli.toml_value(doc, "missing"), none=True)

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
        _ = u.Cli.toml_mapping_sync_mapping_table(
            sources,
            "flext-core",
            {"workspace": True},
            changes,
            "synced flext-core",
            sort_keys=True,
        )
        _ = u.Cli.toml_mapping_sync_string_list(
            u.Cli.toml_mapping_ensure_path(payload, ("tool", "uv", "workspace")),
            "members",
            ("flext-cli", "flext-core"),
            changes,
            "synced members",
            sort_values=True,
        )

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
