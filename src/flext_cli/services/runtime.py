"""DSL service for external process runtime helpers.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli import p, s, t, u


class FlextCliRuntime(s[p.Cli.RuntimeStatus]):
    """Expose process execution helpers through ``cli`` and ``FlextCli``."""

    @staticmethod
    def run_raw(
        cmd: t.StrSequence,
        cwd: t.Cli.TextPath | None = None,
        timeout: int | None = None,
        *,
        options: p.Cli.ProcessOptions | None = None,
        capture: bool = True,
        env: t.StrMapping | None = None,
        remove_env_keys: t.StrSequence | None = None,
    ) -> p.Result[p.Cli.CommandOutput]:
        """Execute through the canonical process owner and retain its outcome.

        Returns:
            The original command output or the causal execution failure.

        """
        return u.Cli.run_raw(
            cmd,
            cwd=cwd,
            timeout=timeout,
            options=options,
            capture=capture,
            env=env,
            remove_env_keys=remove_env_keys,
        )


__all__: t.MutableSequenceOf[str] = ["FlextCliRuntime"]
