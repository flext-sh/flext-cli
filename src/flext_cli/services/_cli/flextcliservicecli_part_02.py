"""FLEXT CLI - Unified Typer abstraction service.

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

from flext_cli import p, u
from flext_cli.services._cli import FlextCliCliPart01


class FlextCliCliPart02(FlextCliCliPart01):
    """Implementation part for FlextCliCliPart02."""

    @staticmethod
    def add_group(
        app: p.Cli.Application,
        *,
        name: str,
        group: p.Cli.Application,
    ) -> None:
        """Attach a subcommand group to an application.

        Args:
            app: Application receiving the group.
            name: Name the group registers under.
            group: Group application to attach.

        """
        u.Cli.framework_add_group(app, name=name, group=group)

    @staticmethod
    def create_group(*, help_text: str, name: str | None = None) -> p.Cli.Application:
        """Create a Typer command group without re-registering global params.

        Args:
            help_text: Group help text.
            name: Optional group name.

        Returns:
            The resulting ``p.Cli.Application``.

        """
        return u.Cli.framework_create_app(
            name=name,
            help_text=help_text,
            add_completion=True,
        )


__all__: list[str] = ["FlextCliCliPart02"]
