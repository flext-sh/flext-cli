"""Coverage tests for the public TOML synchronization helpers on ``u.Cli``."""

from __future__ import annotations

from tests.typings import t
from tests.utilities import u


class TestsFlextCliTomlSyncCoverage:
    """Exercise public TOML sync helpers with real pyproject-style payloads."""

    def test_document_sync_helpers_manage_scalar_lists_and_tables(self) -> None:
        doc = u.Cli.toml_document()
        project = u.Cli.toml_ensure_table(doc, "project")
        project["name"] = "demo"
        project["obsolete"] = "remove-me"

        assert u.Cli.toml_sync_value(project, "name", "flext-demo") is True
        assert u.Cli.toml_sync_value(project, "name", "flext-demo") is False

        assert (
            u.Cli.toml_sync_string_list(
                project,
                "authors",
                ("zoe", "anna"),
                sort_values=True,
            )
            is True
        )
        assert (
            u.Cli.toml_sync_string_list(
                project,
                "authors",
                ("anna", "zoe"),
                sort_values=True,
            )
            is False
        )

        assert u.Cli.toml_merge_string_list(project, "authors", ("marlon",)) is True
        assert (
            u.Cli.toml_merge_string_list(
                project,
                "authors",
                ("anna", "marlon", "zoe"),
            )
            is False
        )

        tool = u.Cli.toml_ensure_path(doc, ("tool", "ruff"))
        assert (
            u.Cli.toml_sync_mapping_table(
                tool,
                "lint",
                {"ignore": ["W291"], "select": ["E", "F"]},
                sort_keys=True,
            )
            is True
        )
        assert (
            u.Cli.toml_sync_mapping_table(
                tool,
                "lint",
                {"ignore": ["W291"], "select": ["E", "F"]},
                sort_keys=True,
            )
            is False
        )

        assert u.Cli.toml_remove_key_if_present(project, "obsolete") is True
        assert u.Cli.toml_remove_key_if_present(project, "obsolete") is False

    def test_mapping_sync_helpers_manage_plain_payloads(self) -> None:
        payload: dict[str, t.JsonValue] = {
            "project": {"name": "demo"},
            "obsolete": True,
        }

        assert u.Cli.toml_mapping_remove_key_if_present(payload, "obsolete") is True
        assert u.Cli.toml_mapping_remove_key_if_present(payload, "obsolete") is False

        assert (
            u.Cli.toml_mapping_sync_value(
                payload,
                "build-system",
                {"requires": ["setuptools>=70"]},
            )
            is True
        )
        assert (
            u.Cli.toml_mapping_sync_value(
                payload,
                "build-system",
                {"requires": ["setuptools>=70"]},
            )
            is False
        )

        assert (
            u.Cli.toml_mapping_merge_string_list(
                payload,
                "plugins",
                ("pytest", "ruff"),
            )
            is True
        )
        assert (
            u.Cli.toml_mapping_sync_string_list(
                payload,
                "plugins",
                ("ruff", "pytest"),
                sort_values=True,
            )
            is False
        )

        assert (
            u.Cli.toml_mapping_sync_mapping_table(
                payload,
                "tool",
                {"ruff": {"fix": True}},
                sort_keys=True,
            )
            is True
        )
        assert (
            u.Cli.toml_mapping_sync_mapping_table(
                payload,
                "tool",
                {"ruff": {"fix": True}},
                sort_keys=True,
            )
            is False
        )
