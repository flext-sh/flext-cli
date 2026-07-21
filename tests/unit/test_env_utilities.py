"""Behavioral tests for the ``u.Cli.env_reader`` environment-file utility.

Exercises the observable public contract of ``FlextCliUtilitiesEnv.env_reader``
exposed through the canonical ``u.Cli`` namespace: KEY=VALUE parsing, comment /
blank / non-identifier skipping, quote stripping, the absent-file empty state,
and the process-environment overlay precedence.

Modules tested: flext_cli._utilities.env.FlextCliUtilitiesEnv

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import os
from pathlib import Path

from flext_cli import u
from flext_tests import tm


class TestsFlextCliUtilitiesEnv:
    """CLIProxy-style KEY=VALUE environment files parsed through ``u.Cli``."""

    @staticmethod
    def _write(path: Path, body: str) -> Path:
        path.write_text(body, encoding="utf-8")
        return path

    def test_env_reader_parses_key_value_pairs(self, tmp_path: Path) -> None:
        """Simple KEY=VALUE lines are parsed into a mapping."""
        env_file = self._write(
            tmp_path / "environment",
            "ZAI_API_TOKEN=secret-token\nPROXY_INTERNAL_API_KEY=k1\n",
        )

        result = u.Cli.env_reader(env_file, overlay_process_env=False)

        values = tm.ok(result)
        tm.that(values["ZAI_API_TOKEN"], eq="secret-token")
        tm.that(values["PROXY_INTERNAL_API_KEY"], eq="k1")

    def test_env_reader_skips_comments_blanks_and_non_identifier_keys(
        self, tmp_path: Path
    ) -> None:
        """Comments, blank lines, and alias-style non-identifier keys are ignored."""
        env_file = self._write(
            tmp_path / "environment",
            "# comment\n\nALIAS ls='ls -la'\nZAI_API_TOKEN=tok\n",
        )

        result = u.Cli.env_reader(env_file, overlay_process_env=False)

        tm.that(tm.ok(result), eq={"ZAI_API_TOKEN": "tok"})

    def test_env_reader_strips_surrounding_quotes(self, tmp_path: Path) -> None:
        """Single or double quotes around the value are stripped."""
        env_file = self._write(
            tmp_path / "environment",
            'SINGLE=\'one\'\nDOUBLE="two"\n',
        )

        result = u.Cli.env_reader(env_file, overlay_process_env=False)

        tm.that(tm.ok(result), eq={"SINGLE": "one", "DOUBLE": "two"})

    def test_env_reader_missing_file_returns_empty_mapping(
        self, tmp_path: Path
    ) -> None:
        """An absent env file is a legitimate empty state, not a failure."""
        result = u.Cli.env_reader(
            tmp_path / "does-not-exist", overlay_process_env=False
        )

        tm.that(tm.ok(result), eq={})

    def test_env_reader_overlays_process_env_without_overriding(
        self, tmp_path: Path
    ) -> None:
        """With overlay on, existing non-blank process vars win over file values."""
        env_file = self._write(
            tmp_path / "environment",
            "ONLY_IN_FILE=file-value\nALSO_IN_PROC=file-loses\n",
        )
        os.environ["ALSO_IN_PROC"] = "proc-wins"
        try:
            result = u.Cli.env_reader(env_file, overlay_process_env=True)
        finally:
            os.environ.pop("ALSO_IN_PROC", None)

        values = tm.ok(result)
        tm.that(values["ONLY_IN_FILE"], eq="file-value")
        tm.that(values["ALSO_IN_PROC"], eq="proc-wins")
