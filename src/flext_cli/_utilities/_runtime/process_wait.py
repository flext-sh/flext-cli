"""Blocking root-process reaping isolated from lifecycle coordination.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli import c, p


class FlextCliUtilitiesRuntimeProcessWait:
    """Reap a root process once and wake event-driven lifecycle monitoring."""

    @staticmethod
    def _wait_for_root_process(
        process: p.Cli.ProcessHandle,
        state: p.Cli.RuntimeProcessState,
    ) -> None:
        try:
            state.return_codes.append(process.wait())
        except c.EXC_OS_VALUE as exc:
            state.failures.append(f"root process wait error: {exc}")
        finally:
            state.process_done.set()
            state.wake.set()


__all__: list[str] = ["FlextCliUtilitiesRuntimeProcessWait"]
