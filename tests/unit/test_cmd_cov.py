"""Behavioral tests for the public ``FlextCli`` settings-command surface.

Every test exercises the public contract only: the ``r[T]`` outcome of the
command methods and the public fields of :class:`m.Cli.SettingsSnapshot`.
No private attributes, no internal-collaborator spying, no patching of the
unit under test. HOME (an external boundary) and ``tmp_path`` are the only
things steered, so the filesystem-derived snapshot is fully deterministic.
"""

from __future__ import annotations

import os
from contextlib import contextmanager
from typing import TYPE_CHECKING

import pytest
from flext_tests import tm

from flext_cli import cli
from tests.constants import c

if TYPE_CHECKING:
    from collections.abc import Generator
    from pathlib import Path


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
        """Create the canonical ``.flext`` directory (optionally its subdirs)."""
        base = root / c.Cli.PATH_FLEXT_DIR_NAME
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
        assert tm.ok(result) is True

    def test_validate_settings_succeeds_when_structure_absent(
        self,
        tmp_path: Path,
    ) -> None:
        """validate_settings is non-fatal on a missing canonical structure."""
        with self._home(tmp_path):
            result = cli.validate_settings()
        assert tm.ok(result) is True

    def test_validate_settings_is_idempotent(self, tmp_path: Path) -> None:
        """Repeated validate_settings calls yield the same successful outcome."""
        self._make_flext_dir(tmp_path, with_subdirs=True)
        with self._home(tmp_path):
            first = cli.validate_settings()
            second = cli.validate_settings()
        assert tm.ok(first) is True
        assert tm.ok(second) is True

    def test_settings_snapshot_reports_existing_directory(
        self,
        tmp_path: Path,
    ) -> None:
        """settings_snapshot resolves the canonical dir and marks it present."""
        settings_dir = self._make_flext_dir(tmp_path)
        with self._home(tmp_path):
            result = cli.settings_snapshot()
        snapshot = tm.ok(result)
        tm.that(snapshot.settings_dir, eq=str(settings_dir))
        tm.that(snapshot.settings_exists, eq=True)
        tm.that(snapshot.settings_readable, eq=True)
        tm.that(snapshot.settings_writable, eq=True)
        assert snapshot.timestamp

    def test_settings_snapshot_reports_absent_directory(
        self,
        tmp_path: Path,
    ) -> None:
        """settings_snapshot flags a missing dir as absent/unreadable/unwritable."""
        with self._home(tmp_path):
            result = cli.settings_snapshot()
        snapshot = tm.ok(result)
        tm.that(
            snapshot.settings_dir,
            eq=str(tmp_path / c.Cli.PATH_FLEXT_DIR_NAME),
        )
        tm.that(snapshot.settings_exists, eq=False)
        tm.that(snapshot.settings_readable, eq=False)
        tm.that(snapshot.settings_writable, eq=False)

    def test_settings_snapshot_round_trips_through_public_dump(
        self,
        tmp_path: Path,
    ) -> None:
        """The snapshot's public model_dump preserves its contract fields."""
        settings_dir = self._make_flext_dir(tmp_path)
        with self._home(tmp_path):
            result = cli.settings_snapshot()
        dumped = tm.ok(result).model_dump()
        assert dumped["settings_dir"] == str(settings_dir)
        assert dumped["settings_exists"] is True
        assert set(dumped) >= {
            "settings_dir",
            "settings_exists",
            "settings_readable",
            "settings_writable",
            "timestamp",
        }

    def test_show_settings_succeeds_when_snapshot_readable(
        self,
        tmp_path: Path,
    ) -> None:
        """show_settings succeeds when the canonical snapshot is resolvable."""
        self._make_flext_dir(tmp_path)
        with self._home(tmp_path):
            result = cli.show_settings()
        assert tm.ok(result) is True

    def test_show_settings_succeeds_without_existing_directory(
        self,
        tmp_path: Path,
    ) -> None:
        """show_settings still succeeds when no settings directory exists."""
        with self._home(tmp_path):
            result = cli.show_settings()
        assert tm.ok(result) is True
