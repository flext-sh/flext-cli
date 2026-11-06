"""FlextCli protocol definitions - Structural typing contracts.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flext_cli._protocols._base import FlextCliProtocolsBaseFlextclimodelsbasePart01


from collections.abc import Sequence
from typing import Protocol, runtime_checkable

from flext_cli._protocols._base import FlextCliProtocolsBasePart02

if TYPE_CHECKING:
    from flext_core import p

    from flext_cli import t
    from flext_cli._protocols.process import FlextCliProtocolsProcess


class FlextCliProtocolsBasePart03(FlextCliProtocolsBasePart02):
    """Implementation part for FlextCliProtocolsBasePart03."""

    @runtime_checkable
    class CommandRunner(Protocol):
        """Contract for generic command execution services."""

        def run(
            self,
            cmd: Sequence[str],
            cwd: t.Cli.TextPath | None = None,
            timeout: int | None = None,
            *,
            options: FlextCliProtocolsProcess.ProcessOptions | None = None,
            capture: bool = True,
        ) -> p.Result[FlextCliProtocolsBaseFlextclimodelsbasePart01.CommandOutput]:
            """Execute a command and require zero exit status."""
            ...

        def capture(
            self,
            cmd: Sequence[str],
            cwd: t.Cli.TextPath | None = None,
            timeout: int | None = None,
            *,
            options: FlextCliProtocolsProcess.ProcessOptions | None = None,
        ) -> p.Result[str]:
            """Execute a command and return stripped stdout."""
            ...

        def run_raw(
            self,
            cmd: Sequence[str],
            cwd: t.Cli.TextPath | None = None,
            timeout: int | None = None,
            *,
            options: FlextCliProtocolsProcess.ProcessOptions | None = None,
            capture: bool = True,
        ) -> p.Result[FlextCliProtocolsBaseFlextclimodelsbasePart01.CommandOutput]:
            """Execute a command without enforcing zero exit status."""
            ...

        # mro-zf1s: binary execution shares the runner contract through p.Cli.
        def run_bytes(
            self,
            cmd: Sequence[str],
            cwd: t.Cli.TextPath | None = None,
            timeout: int | None = None,
            *,
            options: FlextCliProtocolsProcess.ProcessOptions | None = None,
        ) -> p.Result[FlextCliProtocolsBaseFlextclimodelsbasePart01.CommandBytesOutput]:
            """Execute a command and preserve byte-exact output."""
            ...

        def run_checked(
            self,
            cmd: Sequence[str],
            cwd: t.Cli.TextPath | None = None,
            timeout: int | None = None,
            *,
            options: FlextCliProtocolsProcess.ProcessOptions | None = None,
            capture: bool = True,
        ) -> p.Result[bool]:
            """Execute a command and return a success flag."""
            ...

        def run_live(
            self,
            cmd: Sequence[str],
            cwd: t.Cli.TextPath | None = None,
            timeout: int | None = None,
            *,
            options: FlextCliProtocolsProcess.ProcessOptions | None = None,
        ) -> p.Result[FlextCliProtocolsBaseFlextclimodelsbasePart01.CommandOutput]:
            """Execute a checked command with inherited live output."""
            ...

        def run_to_file(
            self,
            cmd: Sequence[str],
            output_file: t.Cli.TextPath,
            cwd: t.Cli.TextPath | None = None,
            timeout: int | None = None,
            *,
            options: FlextCliProtocolsProcess.ProcessOptions | None = None,
        ) -> p.Result[FlextCliProtocolsBaseFlextclimodelsbasePart01.ProcessOutcome]:
            """Execute once with exact combined or separate durable output."""
            ...


__all__: list[str] = ["FlextCliProtocolsBasePart03"]
