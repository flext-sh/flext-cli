"""FlextCli protocol definitions - Structural typing contracts.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

from flext_cli._protocols._base.flextcliprotocolsbase_part_02 import (
    FlextCliProtocolsBase as FlextCliProtocolsBasePart02,
)

if TYPE_CHECKING:
    from pathlib import Path

    from flext_core import p, t


class FlextCliProtocolsBase(FlextCliProtocolsBasePart02):
    """Implementation part for FlextCliProtocolsBase."""

    # mro-wkii.17.26 (codex): this p fragment consumes only upstream aliases
    # and contracts inherited from the preceding fragment, never its own facade.
    @runtime_checkable
    class CommandRunner(Protocol):
        """Contract for generic command execution services."""

        def run(
            self,
            cmd: t.StrSequence,
            cwd: str | Path | None = None,
            timeout: int | None = None,
            env: t.StrMapping | None = None,
            remove_env_keys: t.StrSequence = (),
        ) -> p.Result[FlextCliProtocolsBasePart02.CommandOutput]:
            """Execute a command and require zero exit status."""
            ...

        def capture(
            self,
            cmd: t.StrSequence,
            cwd: str | Path | None = None,
            timeout: int | None = None,
            env: t.StrMapping | None = None,
            remove_env_keys: t.StrSequence = (),
        ) -> p.Result[str]:
            """Execute a command and return stripped stdout."""
            ...

        def run_raw(
            self,
            cmd: t.StrSequence,
            cwd: str | Path | None = None,
            timeout: int | None = None,
            env: t.StrMapping | None = None,
            remove_env_keys: t.StrSequence = (),
            input_data: bytes | None = None,
        ) -> p.Result[FlextCliProtocolsBasePart02.CommandOutput]:
            """Execute a command without enforcing zero exit status."""
            ...

        # mro-zf1s: binary execution shares the runner contract through p.Cli.
        def run_bytes(
            self,
            cmd: t.StrSequence,
            cwd: str | Path | None = None,
            timeout: int | None = None,
            env: t.StrMapping | None = None,
            remove_env_keys: t.StrSequence = (),
            input_data: bytes | None = None,
        ) -> p.Result[FlextCliProtocolsBasePart02.CommandBytesOutput]:
            """Execute a command and preserve byte-exact output."""
            ...

        def run_checked(
            self,
            cmd: t.StrSequence,
            cwd: str | Path | None = None,
            timeout: int | None = None,
            env: t.StrMapping | None = None,
            remove_env_keys: t.StrSequence = (),
        ) -> p.Result[bool]:
            """Execute a command and return a success flag."""
            ...

        def run_to_file(
            self,
            cmd: t.StrSequence,
            output_file: str | Path,
            cwd: str | Path | None = None,
            timeout: int | None = None,
            env: t.StrMapping | None = None,
            remove_env_keys: t.StrSequence = (),
        ) -> p.Result[int]:
            """Execute a command and write combined output to a file."""
            ...

    @runtime_checkable
    class ParamsConfig(Protocol):
        """Protocol for CLI parameters configuration."""

        @property
        def debug(self) -> bool | None:
            """Whether debug mode is enabled."""
            ...

        @property
        def log_format(self) -> str | None:
            """Configured log format."""
            ...

        @property
        def log_level(self) -> str | None:
            """Configured log level."""
            ...

        @property
        def no_color(self) -> bool | None:
            """Whether color is disabled."""
            ...

        @property
        def output_format(self) -> str | None:
            """Configured output format."""
            ...

        @property
        def params(self) -> t.JsonMapping:
            """Validated configuration parameters."""
            ...

        @property
        def quiet(self) -> bool | None:
            """Whether quiet mode is enabled."""
            ...

        @property
        def trace(self) -> bool | None:
            """Whether trace mode is enabled."""
            ...

        @property
        def verbose(self) -> bool | None:
            """Whether verbose mode is enabled."""
            ...


__all__: tuple[str, ...] = ("FlextCliProtocolsBase",)
