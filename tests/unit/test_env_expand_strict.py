"""Behavioral tests for the strict ``u.Cli.env_expand`` mode and documents.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_tests import tm

from flext_cli import u

if TYPE_CHECKING:
    from pathlib import Path


class TestsFlextCliUtilitiesEnvExpandStrict:
    """Strict expansion fails loud on undeclared names and placeholder residue."""

    @staticmethod
    def test_strict_resolves_nested_default(tmp_path: Path) -> None:
        """A nested default resolves once its inner token expands."""
        home = str(tmp_path)

        result = u.Cli.env_expand(
            "${FLEXT_CLI_STATE:-${FLEXT_CLI_HOME}/.local/state}/logs",
            {"FLEXT_CLI_HOME": home},
            strict=True,
        )

        tm.that(tm.ok(result), eq=f"{home}/.local/state/logs")

    @staticmethod
    def test_strict_fails_on_undeclared_name_without_default() -> None:
        """An unset name with no default is a failure, never an empty segment."""
        tm.fail(u.Cli.env_expand("a-${FLEXT_CLI_UNSET}-b", {}, strict=True))

    @staticmethod
    def test_strict_fails_on_placeholder_residue() -> None:
        """A placeholder outside the closed grammar never survives silently."""
        tm.fail(u.Cli.env_expand("${c.Cli.HOME}/x", {}, strict=True))

    @staticmethod
    def test_strict_fails_without_fixed_point() -> None:
        """A self-referencing value fails instead of looping forever."""
        tm.fail(
            u.Cli.env_expand("${LOOP}", {"LOOP": "x${LOOP}"}, strict=True),
        )

    @staticmethod
    def test_default_mode_keeps_empty_segment() -> None:
        """Without ``strict`` the historical empty-segment contract holds."""
        result = u.Cli.env_expand("a-${FLEXT_CLI_UNSET}-b", {})

        tm.that(tm.ok(result), eq="a--b")

    @staticmethod
    def test_document_expands_leaves_and_keeps_skipped_subtrees() -> None:
        """Every leaf expands except subtrees under a skipped key."""
        result = u.Cli.env_expand_document(
            {
                "root": "${FLEXT_CLI_HOME}",
                "items": ["${FLEXT_CLI_HOME}/a", 3],
                "nested": {"agents": {"home": "${HOME}"}},
                "agents": {"home": "${HOME}"},
            },
            {"FLEXT_CLI_HOME": "/srv"},
            skip_keys=frozenset({"agents"}),
        )

        tm.that(
            tm.ok(result),
            eq={
                "root": "/srv",
                "items": ["/srv/a", 3],
                "nested": {"agents": {"home": "${HOME}"}},
                "agents": {"home": "${HOME}"},
            },
        )

    @staticmethod
    def test_document_fails_on_undeclared_leaf() -> None:
        """One undeclared leaf fails the whole document."""
        tm.fail(u.Cli.env_expand_document({"a": ["${FLEXT_CLI_UNSET}"]}, {}))
