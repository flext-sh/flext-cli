"""Public pre-execution failures for explicitly selected native isolation.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import platform
import sys
from pathlib import Path

from tests import m, tm, u


class TestsFlextCliRuntimeProcessIsolation:
    """Isolation prerequisites fail before any command can execute."""

    @staticmethod
    def _request(tmp_path: Path) -> m.Cli.ProcessReadOnlyIsolation:
        """Capture real local files for negative pre-execution contracts."""
        source = tmp_path / "source.py"
        source.write_text('"""Captured source."""\n', encoding="utf-8")
        policy = tmp_path / "invalid-filter"
        policy.write_bytes(b"invalid")
        return m.Cli.ProcessReadOnlyIsolation(
            platform="linux",
            architecture=platform.machine(),
            launcher=tm.ok(
                u.Cli.atomic_read_binary_file_state(
                    Path(sys.executable).resolve(), required=True
                )
            ),
            seccomp_filter=tm.ok(
                u.Cli.atomic_read_binary_file_state(policy, required=True)
            ),
            sources=(
                tm.ok(u.Cli.atomic_read_binary_file_state(source, required=True)),
            ),
            runtime_trees=(),
            runtime_files=(),
            environment=(),
        )

    @staticmethod
    def test_unsupported_native_identity_fails_before_command(
        tmp_path: Path,
    ) -> None:
        """A different filter ABI never starts the supplied command."""
        isolation = TestsFlextCliRuntimeProcessIsolation._request(tmp_path)
        isolation = isolation.model_copy(
            update={
                "architecture": f"{isolation.architecture}-different",
            }
        )
        result = u.Cli.run_raw(
            [sys.executable, "-c", "raise SystemExit(71)"],
            cwd=tmp_path,
            options=m.Cli.ProcessOptions(isolation=isolation),
        )

        tm.fail(result)
        tm.that(result.error or "", has="no qualified native platform capability")
        tm.that(isinstance(result.exception, ValueError), eq=True)

    @staticmethod
    def test_isolation_refuses_inherited_caller_descriptors(
        tmp_path: Path,
    ) -> None:
        """A caller capability cannot be carried into the isolated import."""
        isolation = TestsFlextCliRuntimeProcessIsolation._request(tmp_path)
        result = u.Cli.run_bytes(
            [sys.executable, "-c", "raise SystemExit(71)"],
            cwd=tmp_path,
            options=m.Cli.ProcessOptions(isolation=isolation, pass_fds=(1,)),
        )

        tm.fail(result)
        expected = (
            "cannot inherit caller file descriptors"
            if sys.platform == "linux"
            else "no qualified native platform capability"
        )
        tm.that(result.error or "", has=expected)

    @staticmethod
    def test_invalid_filter_does_not_create_durable_output(
        tmp_path: Path,
    ) -> None:
        """A malformed policy fails before even parent output preparation."""
        isolation = TestsFlextCliRuntimeProcessIsolation._request(tmp_path)
        output = tmp_path / "output" / "raw.log"
        result = u.Cli.run_to_file(
            [sys.executable, "-c", "raise SystemExit(71)"],
            output,
            cwd=tmp_path,
            options=m.Cli.ProcessOptions(isolation=isolation),
        )

        tm.fail(result)
        expected = (
            "complete native seccomp BPF filter"
            if sys.platform == "linux"
            else "no qualified native platform capability"
        )
        tm.that(result.error or "", has=expected)
        tm.that(output.parent.exists(), eq=False)
