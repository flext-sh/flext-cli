"""Command coverage tests."""

from __future__ import annotations

import os
from collections.abc import (
    Generator,
)
from contextlib import contextmanager
from pathlib import Path

from flext_tests import tm

from flext_cli import FlextCliCmd
from tests import c


@contextmanager
def _temporary_home(path: Path) -> Generator[None]:
    original_home = os.environ.get("HOME")
    try:
        os.environ["HOME"] = str(path)
        yield
    finally:
        if original_home is None:
            os.environ.pop("HOME", None)
        else:
            os.environ["HOME"] = original_home


class TestsFlextCliCmdCov:
    """Coverage tests for FlextCliCmd."""

    def test_validate_settings_succeeds_when_structure_is_missing(
        self,
        tmp_path: Path,
    ) -> None:
        """validate_settings must report the canonical structure without failing."""
        cmd = FlextCliCmd()
        with _temporary_home(tmp_path):
            result = cmd.validate_settings()
        tm.ok(result)

    def test_validate_settings_succeeds_with_real_structure(
        self,
        tmp_path: Path,
    ) -> None:
        """validate_settings must accept the standard FLEXT directory layout."""
        base_dir = tmp_path / c.Cli.PATH_FLEXT_DIR_NAME
        base_dir.mkdir()
        for subdir in c.Cli.STANDARD_SUBDIRS:
            (base_dir / subdir).mkdir()
        cmd = FlextCliCmd()
        with _temporary_home(tmp_path):
            result = cmd.validate_settings()
        tm.ok(result)

    def test_settings_snapshot_reflects_real_home_directory(
        self,
        tmp_path: Path,
    ) -> None:
        """settings_snapshot must expose the resolved canonical settings directory."""
        settings_dir = tmp_path / c.Cli.PATH_FLEXT_DIR_NAME
        settings_dir.mkdir()
        with _temporary_home(tmp_path):
            result = FlextCliCmd.settings_snapshot()
        tm.ok(result)
        tm.that(result.value.settings_dir, eq=str(settings_dir))
        tm.that(result.value.settings_exists, eq=True)

    def test_show_settings_succeeds_with_real_snapshot(
        self,
        tmp_path: Path,
    ) -> None:
        """show_settings must succeed when the canonical settings snapshot is readable."""
        (tmp_path / c.Cli.PATH_FLEXT_DIR_NAME).mkdir()
        cmd = FlextCliCmd()
        with _temporary_home(tmp_path):
            result = cmd.show_settings()
        tm.ok(result)
        tm.that(result.value, eq=True)
