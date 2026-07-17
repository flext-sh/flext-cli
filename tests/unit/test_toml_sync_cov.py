"""Behavioral contract tests for the public TOML sync helpers on ``u.Cli``.

Each ``toml_*sync*`` / ``toml_*merge*`` / ``toml_*remove*`` helper is a pure,
in-place synchronizer whose public contract is:

* return ``True`` iff the container was mutated, ``False`` when already in sync;
* leave the container holding exactly the expected value afterwards;
* be idempotent -- a second identical call is a no-op returning ``False``.

Assertions here exercise that observable contract through the public read
helpers (``toml_value``, ``toml_as_string_list``, ``toml_as_mapping``) rather
than poking internals. No filesystem or network I/O -- purely in-memory
tomlkit documents and plain mappings.
"""

from __future__ import annotations

import pytest
from flext_tests import tm
from tomlkit.items import Table

from tests import t, u


class TestsFlextCliTomlSyncCoverage:
    """Public-contract behavior of the ``u.Cli.toml_*`` synchronizers."""

    @pytest.fixture
    def project_table(self) -> Table:
        """Fresh ``[project]`` table inside an empty document."""
        return u.Cli.toml_ensure_table(u.Cli.toml_document(), "project")

    # -- scalar sync -----------------------------------------------------

    def test_sync_value_writes_expected_and_reports_mutation(
        self, project_table: Table
    ) -> None:
        # Arrange
        """Verify that sync value writes expected and reports mutation."""
        project_table["name"] = "old"

        # Act
        changed = u.Cli.toml_sync_value(project_table, "name", "flext-demo")

        # Assert
        tm.that(changed, eq=True)
        tm.that(u.Cli.toml_value(project_table, "name"), eq="flext-demo")

    def test_sync_value_is_idempotent_when_already_in_sync(
        self, project_table: Table
    ) -> None:
        # Arrange
        """Verify that sync value is idempotent when already in sync."""
        u.Cli.toml_sync_value(project_table, "name", "flext-demo")

        # Act
        second = u.Cli.toml_sync_value(project_table, "name", "flext-demo")

        # Assert
        tm.that(second, eq=False)
        tm.that(u.Cli.toml_value(project_table, "name"), eq="flext-demo")

    def test_sync_value_creates_missing_key(self, project_table: Table) -> None:
        # Act
        """Verify that sync value creates missing key."""
        changed = u.Cli.toml_sync_value(project_table, "version", "1.2.3")

        # Assert
        tm.that(changed, eq=True)
        tm.that(u.Cli.toml_value(project_table, "version"), eq="1.2.3")

    # -- string-list sync ------------------------------------------------

    def test_sync_string_list_stores_sorted_values(self, project_table: Table) -> None:
        # Act
        """Verify that sync string list stores sorted values."""
        changed = u.Cli.toml_sync_string_list(
            project_table, "authors", ("zoe", "anna"), sort_values=True
        )

        # Assert
        tm.that(changed, eq=True)
        tm.that(
            list(u.Cli.toml_as_string_list(project_table["authors"])),
            eq=["anna", "zoe"],
        )

    def test_sync_string_list_sorted_ignores_input_order(
        self, project_table: Table
    ) -> None:
        # Arrange
        """Verify that sync string list sorted ignores input order."""
        u.Cli.toml_sync_string_list(
            project_table, "authors", ("zoe", "anna"), sort_values=True
        )

        # Act -- same set, different order, sorted comparison -> no mutation
        changed = u.Cli.toml_sync_string_list(
            project_table, "authors", ("anna", "zoe"), sort_values=True
        )

        # Assert
        tm.that(changed, eq=False)

    def test_merge_string_list_unions_and_sorts(self, project_table: Table) -> None:
        # Arrange
        """Verify that merge string list unions and sorts."""
        u.Cli.toml_sync_string_list(project_table, "authors", ("anna", "zoe"))

        # Act
        changed = u.Cli.toml_merge_string_list(project_table, "authors", ("marlon",))

        # Assert
        tm.that(changed, eq=True)
        tm.that(
            list(u.Cli.toml_as_string_list(project_table["authors"])),
            eq=["anna", "marlon", "zoe"],
        )

    def test_merge_string_list_noop_when_subset_present(
        self, project_table: Table
    ) -> None:
        # Arrange -- already the sorted union
        """Verify that merge string list noop when subset present."""
        u.Cli.toml_merge_string_list(
            project_table, "authors", ("anna", "marlon", "zoe")
        )

        # Act
        changed = u.Cli.toml_merge_string_list(
            project_table, "authors", ("anna", "marlon", "zoe")
        )

        # Assert
        tm.that(changed, eq=False)

    # -- mapping-table sync ---------------------------------------------

    def test_sync_mapping_table_writes_expected_mapping(self) -> None:
        # Arrange
        """Verify that sync mapping table writes expected mapping."""
        doc = u.Cli.toml_document()
        tool = u.Cli.toml_ensure_path(doc, ("tool", "ruff"))
        expected: t.JsonMapping = {"ignore": ["W291"], "select": ["E", "F"]}

        # Act
        changed = u.Cli.toml_sync_mapping_table(tool, "lint", expected, sort_keys=True)

        # Assert
        tm.that(changed, eq=True)
        tm.that(u.Cli.toml_as_mapping(tool["lint"]), eq=dict(expected))

    def test_sync_mapping_table_idempotent(self) -> None:
        # Arrange
        """Verify that sync mapping table idempotent."""
        doc = u.Cli.toml_document()
        tool = u.Cli.toml_ensure_path(doc, ("tool", "ruff"))
        expected: t.JsonMapping = {"ignore": ["W291"], "select": ["E", "F"]}
        u.Cli.toml_sync_mapping_table(tool, "lint", expected, sort_keys=True)

        # Act
        second = u.Cli.toml_sync_mapping_table(tool, "lint", expected, sort_keys=True)

        # Assert
        tm.that(second, eq=False)

    def test_sync_mapping_table_drops_stale_keys(self) -> None:
        # Arrange -- seed a table carrying a key not in the new expected mapping
        """Verify that sync mapping table drops stale keys."""
        doc = u.Cli.toml_document()
        tool = u.Cli.toml_ensure_path(doc, ("tool", "ruff"))
        u.Cli.toml_sync_mapping_table(tool, "lint", {"select": ["E"], "stale": ["X"]})

        # Act
        changed = u.Cli.toml_sync_mapping_table(tool, "lint", {"select": ["E", "F"]})

        # Assert
        tm.that(changed, eq=True)
        tm.that(u.Cli.toml_as_mapping(tool["lint"]), eq={"select": ["E", "F"]})

    # -- key removal -----------------------------------------------------

    def test_remove_key_if_present_reports_and_deletes(
        self, project_table: Table
    ) -> None:
        # Arrange
        """Verify that remove key if present reports and deletes."""
        project_table["obsolete"] = "remove-me"

        # Act
        removed = u.Cli.toml_remove_key_if_present(project_table, "obsolete")
        again = u.Cli.toml_remove_key_if_present(project_table, "obsolete")

        # Assert
        tm.that(removed, eq=True)
        tm.that(again, eq=False)
        tm.that(u.Cli.toml_value(project_table, "obsolete"), none=True)

    # -- plain-mapping helpers ------------------------------------------

    @pytest.fixture
    def payload(self) -> dict[str, t.JsonValue]:
        """Fresh plain pyproject-style mapping."""
        return {"project": {"name": "demo"}, "obsolete": True}

    def test_mapping_remove_key_if_present_reports_and_deletes(
        self, payload: dict[str, t.JsonValue]
    ) -> None:
        # Act
        """Verify that mapping remove key if present reports and deletes."""
        removed = u.Cli.toml_mapping_remove_key_if_present(payload, "obsolete")
        again = u.Cli.toml_mapping_remove_key_if_present(payload, "obsolete")

        # Assert
        tm.that(removed, eq=True)
        tm.that(again, eq=False)
        tm.that(payload, lacks="obsolete")

    def test_mapping_sync_value_writes_expected(
        self, payload: dict[str, t.JsonValue]
    ) -> None:
        # Arrange
        """Verify that mapping sync value writes expected."""
        build: t.JsonValue = {"requires": ["setuptools>=70"]}

        # Act
        changed = u.Cli.toml_mapping_sync_value(payload, "build-system", build)

        # Assert
        tm.that(changed, eq=True)
        tm.that(payload["build-system"], eq=build)

    def test_mapping_sync_value_idempotent(
        self, payload: dict[str, t.JsonValue]
    ) -> None:
        # Arrange
        """Verify that mapping sync value idempotent."""
        build: t.JsonValue = {"requires": ["setuptools>=70"]}
        u.Cli.toml_mapping_sync_value(payload, "build-system", build)

        # Act
        second = u.Cli.toml_mapping_sync_value(payload, "build-system", build)

        # Assert
        tm.that(second, eq=False)

    def test_mapping_merge_then_sorted_sync_is_noop(
        self, payload: dict[str, t.JsonValue]
    ) -> None:
        # Arrange
        """Verify that mapping merge then sorted sync is noop."""
        changed = u.Cli.toml_mapping_merge_string_list(
            payload, "plugins", ("pytest", "ruff")
        )

        # Act -- same set in another order under sorted comparison
        second = u.Cli.toml_mapping_sync_string_list(
            payload, "plugins", ("ruff", "pytest"), sort_values=True
        )

        # Assert
        tm.that(changed, eq=True)
        tm.that(second, eq=False)
        tm.that(payload["plugins"], eq=["pytest", "ruff"])

    def test_mapping_sync_mapping_table_writes_and_is_idempotent(
        self, payload: dict[str, t.JsonValue]
    ) -> None:
        # Arrange
        """Verify that mapping sync mapping table writes and is idempotent."""
        expected: t.JsonMapping = {"ruff": {"fix": True}}

        # Act
        changed = u.Cli.toml_mapping_sync_mapping_table(
            payload, "tool", expected, sort_keys=True
        )
        second = u.Cli.toml_mapping_sync_mapping_table(
            payload, "tool", expected, sort_keys=True
        )

        # Assert
        tm.that(changed, eq=True)
        tm.that(second, eq=False)
        tm.that(payload["tool"], eq=dict(expected))
