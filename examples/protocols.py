"""FLEXT CLI example protocols."""

from __future__ import annotations

from collections.abc import (
    Callable,
)
from typing import Protocol, runtime_checkable

from flext_cli import p


class ExamplesFlextCliProtocols(p):
    """Public examples protocol facade extending flext-cli protocols."""

    @runtime_checkable
    class CliMainWithGroups(Protocol):
        """Protocol for a CLI entrypoint with group and command decorators.

        Business Rule:
        ──────────────
        Typer CLI applications provide group() and command() decorators for
        organizing commands. This protocol defines the interface needed by plugins.

        Audit Implications:
        ───────────────────
        - Plugins must check hasattr() before calling group()/command()
        - Runtime protocol checks keep the plugin contract independent from Typer internals
        """

        def command(
            self,
            *args: str,
            **kwargs: str,
        ) -> Callable[[Callable[..., None]], Callable[..., None]]:
            """Create a command decorator."""
            ...

        def group(
            self,
            *args: str,
            **kwargs: str,
        ) -> Callable[[Callable[..., None]], Callable[..., None]]:
            """Create a command group decorator."""
            ...

    @runtime_checkable
    class GroupWithCommands(Protocol):
        """Protocol for command group objects with command decorator.

        Business Rule:
        ──────────────
        Typer groups provide command() decorator for registering commands.
        This protocol defines the interface needed by plugins.

        Audit Implications:
        ───────────────────
        - Groups are created by group() decorator
        - Commands are registered using command() decorator on groups
        """

        def command(
            self,
            *args: str,
            **kwargs: str,
        ) -> Callable[[Callable[..., None]], Callable[..., None]]:
            """Create a command decorator."""
            ...


p = ExamplesFlextCliProtocols

__all__: list[str] = [
    "ExamplesFlextCliProtocols",
    "p",
]
