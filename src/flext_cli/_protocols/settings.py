"""Settings-domain protocols part (composed into ``p.Cli`` via MRO).

Structural, field-level protocols for the validated config domains — never
model classes, never ``Any``/``object``. No runtime project imports; importable
by ``c``/``t``/``p``/``m``/``u`` without creating a cycle (foundation purity).

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable
from flext_core import p


class FlextCliProtocolsSettings:
    """Settings-domain protocol namespace (structural types; no project imports)."""

    @runtime_checkable
    class Settings(p.Settings, Protocol):
        """Protocol for CLI runtime settings consumed by the public services.

        Flat ``cli_*`` scalars (§2.6) loadable from env/.env; the nested
        ``Cli`` branch was removed. ``clone`` and the base contract come from
        the upstream ``p.Settings``; the ``cli_*`` fields below are the
        flext-cli surface consumers type against as ``p.Cli.Settings``.
        """

        @property
        def cli_app_name(self) -> str:
            """CLI application name."""
            ...

        @property
        def cli_ci(self) -> bool:
            """Whether running in a CI environment."""
            ...

        @property
        def cli_config_file(self) -> str | None:
            """Optional CLI config file path."""
            ...

        @property
        def cli_log_level(self) -> str:
            """CLI log level."""
            ...

        @property
        def cli_log_verbosity(self) -> str:
            """CLI log verbosity."""
            ...

        @property
        def cli_no_color(self) -> bool:
            """Whether color output is disabled."""
            ...

        @property
        def cli_output_format(self) -> str:
            """CLI output format."""
            ...

        @property
        def cli_pytest_current_test(self) -> str | None:
            """Current pytest test id when under test, else None."""
            ...

        @property
        def cli_quiet(self) -> bool:
            """Whether quiet mode is enabled."""
            ...

        @property
        def cli_shell_command(self) -> str | None:
            """Originating shell command, if known."""
            ...

        @property
        def cli_token_file(self) -> str | None:
            """Optional auth token file path."""
            ...

        @property
        def cli_verbose(self) -> bool:
            """Whether verbose mode is enabled."""
            ...

        @property
        def debug(self) -> bool:
            """Check if debug mode is enabled."""
            ...

        @property
        def trace(self) -> bool:
            """Check if trace mode is enabled."""
            ...

        @classmethod
        def reset_for_testing(cls) -> None:
            """Reset the process-wide singleton (test isolation only)."""
            ...
