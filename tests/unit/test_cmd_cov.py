"""Command coverage tests."""

from __future__ import annotations

import os
from collections.abc import Generator
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


class TestsCliCmdCov:
    """Coverage tests for FlextCliCmd."""

    def test_validate_config_succeeds_when_structure_is_missing(
        self,
        tmp_path: Path,
    ) -> None:
        """validate_config must report the canonical structure without failing."""
        cmd = FlextCliCmd()
        with _temporary_home(tmp_path):
            result = cmd.validate_config()
        tm.ok(result)

    def test_validate_config_succeeds_with_real_structure(
        self,
        tmp_path: Path,
    ) -> None:
        """validate_config must accept the standard FLEXT directory layout."""
        base_dir = tmp_path / c.Cli.PATH_FLEXT_DIR_NAME
        base_dir.mkdir()
        for subdir in c.Cli.STANDARD_SUBDIRS:
            (base_dir / subdir).mkdir()
        cmd = FlextCliCmd()
        with _temporary_home(tmp_path):
            result = cmd.validate_config()
        tm.ok(result)

    def test_config_snapshot_reflects_real_home_directory(
        self,
        tmp_path: Path,
    ) -> None:
        """config_snapshot must expose the resolved canonical config directory."""
        config_dir = tmp_path / c.Cli.PATH_FLEXT_DIR_NAME
        config_dir.mkdir()
        with _temporary_home(tmp_path):
            result = FlextCliCmd.config_snapshot()
        tm.ok(result)
        tm.that(result.value.config_dir, eq=str(config_dir))
        tm.that(result.value.config_exists, eq=True)

    def test_show_config_succeeds_with_real_snapshot(
        self,
        tmp_path: Path,
    ) -> None:
        """show_config must succeed when the canonical config snapshot is readable."""
        (tmp_path / c.Cli.PATH_FLEXT_DIR_NAME).mkdir()
        cmd = FlextCliCmd()
        with _temporary_home(tmp_path):
            result = cmd.show_config()
        tm.ok(result)
        tm.that(result.value, eq=True)
