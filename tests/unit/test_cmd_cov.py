"""Behavioral tests for the public ``FlextCli`` settings-command surface.

Every test exercises the public contract only: the ``r[T]`` outcome of the
command methods and the public fields of :class:`m.Cli.SettingsSnapshot`.
No private attributes, no internal-collaborator spying, no patching of the
unit under test. HOME (an external boundary) and ``tmp_path`` are the only
things steered, so the filesystem-derived snapshot is fully deterministic.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import os
from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from flext_cli import cli
from tests import c, m, t, tm

if TYPE_CHECKING:
    from collections.abc import Generator


class TestsFlextCliCmdCov:
    """Contract tests for the settings commands exposed on ``FlextCli``."""

    @staticmethod
    @contextmanager
    def _home(path: Path) -> Generator[None]:
        """Point HOME at ``path`` for the duration of the block (external boundary)."""
        original = os.environ.get("HOME")
        os.environ["HOME"] = str(path)
        try:
            yield
        finally:
            if original is None:
                os.environ.pop("HOME", None)
            else:
                os.environ["HOME"] = original

    @staticmethod
    def _make_flext_dir(root: Path, *, with_subdirs: bool = False) -> Path:
        """Create the canonical ``.flext`` directory (optionally its subdirs).

        Returns:
            The resulting ``Path``.

        """
        base: Path = root / c.Cli.PATH_FLEXT_DIR_NAME
        base.mkdir()
        if with_subdirs:
            for subdir in c.Cli.STANDARD_SUBDIRS:
                (base / subdir).mkdir()
        return base

    @pytest.mark.parametrize("with_subdirs", [False, True])
    def test_validate_settings_succeeds_when_directory_present(
        self,
        tmp_path: Path,
        *,
        with_subdirs: bool,
    ) -> None:
        """validate_settings reports success whether or not subdirs exist."""
        self._make_flext_dir(tmp_path, with_subdirs=with_subdirs)
        with self._home(tmp_path):
            result = cli.validate_settings()
        tm.ok(tm.ok(result))

    def test_validate_settings_succeeds_when_structure_absent(
        self,
        tmp_path: Path,
    ) -> None:
        """validate_settings is non-fatal on a missing canonical structure."""
        with self._home(tmp_path):
            result = cli.validate_settings()
        tm.ok(tm.ok(result))

    def test_validate_settings_is_idempotent(self, tmp_path: Path) -> None:
        """Repeated validate_settings calls yield the same successful outcome."""
        self._make_flext_dir(tmp_path, with_subdirs=True)
        with self._home(tmp_path):
            first = cli.validate_settings()
            second = cli.validate_settings()
        tm.ok(tm.ok(first))
        tm.ok(tm.ok(second))

    def test_settings_snapshot_reports_existing_directory(self, tmp_path: Path) -> None:
        """settings_snapshot resolves the canonical dir and marks it present."""
        settings_dir = self._make_flext_dir(tmp_path)
        with self._home(tmp_path):
            result = cli.settings_snapshot()
        snapshot: m.Cli.SettingsSnapshot = tm.ok(result)
        tm.that(snapshot.settings_dir, eq=str(settings_dir))
        tm.ok(snapshot.settings_exists)
        tm.ok(snapshot.settings_readable)
        tm.ok(snapshot.settings_writable)
        tm.that(snapshot.timestamp, empty=False)

    def test_settings_snapshot_reports_absent_directory(self, tmp_path: Path) -> None:
        """settings_snapshot flags a missing dir as absent/unreadable/unwritable."""
        with self._home(tmp_path):
            result = cli.settings_snapshot()
        snapshot: m.Cli.SettingsSnapshot = tm.ok(result)
        tm.that(snapshot.settings_dir, eq=str(tmp_path / c.Cli.PATH_FLEXT_DIR_NAME))
        tm.fail(snapshot.settings_exists)
        tm.fail(snapshot.settings_readable)
        tm.fail(snapshot.settings_writable)

    def test_settings_snapshot_round_trips_through_public_dump(
        self,
        tmp_path: Path,
    ) -> None:
        """The snapshot's public model_dump preserves its contract fields."""
        settings_dir = self._make_flext_dir(tmp_path)
        with self._home(tmp_path):
            result = cli.settings_snapshot()
        dumped: t.JsonDict = tm.ok(result).model_dump()
        tm.that(dumped["settings_dir"], eq=str(settings_dir))
        tm.ok(dumped["settings_exists"])
        tm.that(
            set(dumped)
            >= {
                "settings_dir",
                "settings_exists",
                "settings_readable",
                "settings_writable",
                "timestamp",
            },
            eq=True,
        )

    def test_show_settings_succeeds_when_snapshot_readable(
        self,
        tmp_path: Path,
    ) -> None:
        """show_settings succeeds when the canonical snapshot is resolvable."""
        self._make_flext_dir(tmp_path)
        with self._home(tmp_path):
            result = cli.show_settings()
        tm.ok(tm.ok(result))

    def test_show_settings_succeeds_without_existing_directory(
        self,
        tmp_path: Path,
    ) -> None:
        """show_settings still succeeds when no settings directory exists."""
        with self._home(tmp_path):
            result = cli.show_settings()
        tm.ok(tm.ok(result))
