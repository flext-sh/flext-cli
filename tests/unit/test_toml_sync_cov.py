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

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import pytest
from tomlkit.items import Table

from tests import t, tm, u


class TestsFlextCliTomlSyncCoverage:
    """Public-contract behavior of the ``u.Cli.toml_*`` synchronizers."""

    @pytest.fixture
    @staticmethod
    def project_table() -> Table:
        """Fresh ``[project]`` table inside an empty document.

        Returns:
            The resulting ``Table``.

        """
        table: Table = u.Cli.toml_ensure_table(u.Cli.toml_document(), "project")
        return table

    # -- scalar sync -----------------------------------------------------

    @staticmethod
    def test_sync_value_writes_expected_and_reports_mutation(
        project_table: Table,
    ) -> None:
        # Arrange
        """Verify that sync value writes expected and reports mutation."""
        project_table["name"] = "old"

        # Act
        changed = u.Cli.toml_sync_value(project_table, "name", "flext-demo")

        # Assert
        tm.ok(changed)
        tm.that(u.Cli.toml_value(project_table, "name"), eq="flext-demo")

    @staticmethod
    def test_sync_value_is_idempotent_when_already_in_sync(
        project_table: Table,
    ) -> None:
        # Arrange
        """Verify that sync value is idempotent when already in sync."""
        u.Cli.toml_sync_value(project_table, "name", "flext-demo")

        # Act
        second = u.Cli.toml_sync_value(project_table, "name", "flext-demo")

        # Assert
        tm.fail(second)
        tm.that(u.Cli.toml_value(project_table, "name"), eq="flext-demo")

    @staticmethod
    def test_sync_value_creates_missing_key(project_table: Table) -> None:
        # Act
        """Verify that sync value creates missing key."""
        changed = u.Cli.toml_sync_value(project_table, "version", "1.2.3")

        # Assert
        tm.ok(changed)
        tm.that(u.Cli.toml_value(project_table, "version"), eq="1.2.3")

    # -- string-list sync ------------------------------------------------

    @staticmethod
    def test_sync_string_list_stores_sorted_values(project_table: Table) -> None:
        # Act
        """Verify that sync string list stores sorted values."""
        changed = u.Cli.toml_sync_string_list(
            project_table,
            "authors",
            ("zoe", "anna"),
            sort_values=True,
        )

        # Assert
        tm.ok(changed)
        tm.that(
            list(u.Cli.toml_as_string_list(project_table["authors"])),
            eq=["anna", "zoe"],
        )

    @staticmethod
    def test_sync_string_list_sorted_ignores_input_order(
        project_table: Table,
    ) -> None:
        # Arrange
        """Verify that sync string list sorted ignores input order."""
        u.Cli.toml_sync_string_list(
            project_table,
            "authors",
            ("zoe", "anna"),
            sort_values=True,
        )

        # Act -- same set, different order, sorted comparison -> no mutation
        changed = u.Cli.toml_sync_string_list(
            project_table,
            "authors",
            ("anna", "zoe"),
            sort_values=True,
        )

        # Assert
        tm.fail(changed)

    # -- key removal -----------------------------------------------------

    @staticmethod
    def test_remove_key_if_present_reports_and_deletes(
        project_table: Table,
    ) -> None:
        # Arrange
        """Verify that remove key if present reports and deletes."""
        project_table["obsolete"] = "remove-me"

        # Act
        removed = u.Cli.toml_remove_key_if_present(project_table, "obsolete")
        again = u.Cli.toml_remove_key_if_present(project_table, "obsolete")

        # Assert
        tm.ok(removed)
        tm.fail(again)
        tm.that(u.Cli.toml_value(project_table, "obsolete"), none=True)

    # -- plain-mapping helpers ------------------------------------------

    @pytest.fixture
    @staticmethod
    def payload() -> t.JsonDict:
        """Fresh plain pyproject-style mapping.

        Returns:
            The resulting ``t.JsonDict``.

        """
        return {"project": {"name": "demo"}, "obsolete": True}

    @staticmethod
    def test_mapping_remove_key_if_present_reports_and_deletes(
        payload: t.MutableJsonMapping,
    ) -> None:
        # Act
        """Verify that mapping remove key if present reports and deletes."""
        removed = u.Cli.toml_mapping_remove_key_if_present(payload, "obsolete")
        again = u.Cli.toml_mapping_remove_key_if_present(payload, "obsolete")

        # Assert
        tm.ok(removed)
        tm.fail(again)
        tm.that(payload, lacks="obsolete")

    @staticmethod
    def test_mapping_sync_value_writes_expected(
        payload: t.MutableJsonMapping,
    ) -> None:
        # Arrange
        """Verify that mapping sync value writes expected."""
        build: t.JsonValue = {"requires": ["setuptools>=70"]}

        # Act
        changed = u.Cli.toml_mapping_sync_value(payload, "build-system", build)

        # Assert
        tm.ok(changed)
        tm.that(payload["build-system"], eq=build)

    @staticmethod
    def test_mapping_sync_value_idempotent(payload: t.MutableJsonMapping) -> None:
        # Arrange
        """Verify that mapping sync value idempotent."""
        build: t.JsonValue = {"requires": ["setuptools>=70"]}
        u.Cli.toml_mapping_sync_value(payload, "build-system", build)

        # Act
        second = u.Cli.toml_mapping_sync_value(payload, "build-system", build)

        # Assert
        tm.fail(second)

    @staticmethod
    def test_mapping_merge_then_sorted_sync_is_noop(
        payload: t.MutableJsonMapping,
    ) -> None:
        # Arrange
        """Verify that mapping merge then sorted sync is noop."""
        changed = u.Cli.toml_mapping_merge_string_list(
            payload,
            "plugins",
            ("pytest", "ruff"),
        )

        # Act -- same set in another order under sorted comparison
        second = u.Cli.toml_mapping_sync_string_list(
            payload,
            "plugins",
            ("ruff", "pytest"),
            sort_values=True,
        )

        # Assert
        tm.ok(changed)
        tm.fail(second)
        tm.that(payload["plugins"], eq=["pytest", "ruff"])
