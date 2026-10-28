"""FlextCli protocol definitions - Structural typing contracts.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import (
    Iterable,
    Iterator,
    Mapping,
    MutableMapping,
    MutableSequence,
    Sequence,
)

from typing import TYPE_CHECKING, Protocol, runtime_checkable

from flext_core import p

if TYPE_CHECKING:
    from flext_cli import t


class FlextCliProtocolsBasePart01:
    """Implementation part for FlextCliProtocolsBasePart01."""

    @runtime_checkable
    class AtomicFileReceipt(p.Model, Protocol):
        """Read-only source, parent identity and digest of a captured file."""

        @property
        def path(self) -> t.Cli.TextPath: ...

        @property
        def version_key(self) -> tuple[int, ...] | None: ...

        @property
        def size(self) -> int | None: ...

        @property
        def mode(self) -> int | None: ...

        @property
        def parent_device(self) -> int | None: ...

        @property
        def parent_inode(self) -> int | None: ...

        @property
        def sha256(self) -> str | None: ...

        @property
        def device(self) -> int | None: ...

        @property
        def inode(self) -> int | None: ...

        @property
        def link_count(self) -> int | None: ...

        @property
        def file_attributes(self) -> int | None: ...

        @property
        def reparse_tag(self) -> int | None: ...

    @runtime_checkable
    class RuntimeComponents(p.Base, Protocol):
        """Public availability state of the canonical CLI components."""

        @property
        def settings(self) -> str: ...

        @property
        def formatters(self) -> str: ...

        @property
        def prompts(self) -> str: ...

        @property
        def rules(self) -> str: ...

    @runtime_checkable
    class RuntimeStatus(p.Base, Protocol):
        """Complete public status payload returned by CLI service handlers."""

        @property
        def status(self) -> str: ...

        @property
        def service(self) -> str: ...

        @property
        def timestamp(self) -> str: ...

        @property
        def version(self) -> str: ...

        @property
        def components(self) -> FlextCliProtocolsBasePart01.RuntimeComponents: ...

    @runtime_checkable
    class CliSettings(Protocol):
        """Flat CLI runtime settings (§2.6 — simple scalars only).

        NOTE (multi-agent): the nested ``Cli`` branch was removed; settings
        are flat ``cli_*`` scalars loadable from env/.env. Test-runtime
        detection moved to ``u.Cli.cli_test_env`` (behavior lives in the
        utilities layer, never on settings). Plain ``Protocol`` (not
        ``p.Model``): pyrefly cannot reconcile pydantic ``model_fields``
        metaclass descriptors on this hot path — structural field access is
        the whole contract.
        """

        @property
        def cli_app_name(self) -> str:
            """CLI application name."""
            ...

        @property
        def cli_log_verbosity(self) -> str:
            """Log verbosity mode."""
            ...

        @property
        def cli_no_color(self) -> bool:
            """Whether color output is disabled."""
            ...

        @property
        def cli_output_format(self) -> str:
            """Configured output format."""
            ...

        @property
        def cli_process_heartbeat_seconds(self) -> float:
            """Live child-process heartbeat interval in seconds."""
            ...

        @property
        def cli_quiet(self) -> bool:
            """Whether quiet mode is enabled."""
            ...

        @property
        def cli_verbose(self) -> bool:
            """Whether verbose mode is enabled."""
            ...

        cli_config_file: str | None
        """Path to the configured settings file."""

        cli_token_file: str | None
        """Path to the configured authentication token file."""

        cli_ci: bool
        """Whether the current runtime is a CI environment."""

        cli_pytest_current_test: str | None
        """Current pytest test identifier, when present."""

        cli_shell_command: str | None
        """Current shell command propagated by the runtime environment."""


__all__: list[str] = ["FlextCliProtocolsBasePart01"]
