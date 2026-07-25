"""FlextCli protocol definitions - Structural typing contracts.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

from flext_core import p

if TYPE_CHECKING:
    from flext_cli import c


class FlextCliProtocolsBase:
    """Implementation part for FlextCliProtocolsBase."""

    @runtime_checkable
    class CliSettings(p.Model, Protocol):
        """Namespaced CLI runtime settings branch."""

        @property
        def app_name(self) -> str:
            """CLI application name."""
            ...

        @property
        def cli_log_level(self) -> c.LogLevel | str:
            """Get CLI log level."""
            ...

        @property
        def log_verbosity(self) -> str:
            """Get log verbosity mode."""
            ...

        @property
        def no_color(self) -> bool:
            """Check if color output is disabled."""
            ...

        @property
        def output_format(self) -> str:
            """Get configured output format."""
            ...

        @property
        def quiet(self) -> bool:
            """Check if quiet mode is enabled."""
            ...

        @property
        def verbose(self) -> bool:
            """Check if verbose mode is enabled."""
            ...

        config_file: str | None
        """Mutable path to the configured settings file."""

        token_file: str | None
        """Mutable path to the configured authentication token file."""

        ci: bool
        """Whether the current runtime is a CI environment."""

        pytest_current_test: str | None
        """Current pytest test identifier, when present."""

        shell_command: str | None
        """Current shell command propagated by the runtime environment."""

        @property
        def test_env(self) -> bool:
            """Whether prompt services should use test-safe behavior."""
            ...


__all__: list[str] = ["FlextCliProtocolsBase"]
