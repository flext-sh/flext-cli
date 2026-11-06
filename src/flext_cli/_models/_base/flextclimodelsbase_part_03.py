"""CLI Pydantic domain models.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Annotated, ClassVar, override

from flext_core import m

from flext_cli import c, p, t
from flext_cli._models._base.flextclimodelsbase_part_02 import FlextCliModelsBasePart02


class FlextCliModelsBasePart03:
    """Implementation part for FlextCliModelsBasePart03."""

    class AtomicDirectoryState(FlextCliModelsBasePart02.AtomicPhysicalIdentity):
        """Exact empty-directory presence and physical identity."""

        atomic_state_label: ClassVar[str] = "atomic directory state"
        atomic_presence_message: ClassVar[str] = (
            "atomic directory state requires mode, device, inode, and link "
            "count exactly when it exists"
        )

        exists: Annotated[
            bool,
            m.Field(strict=True, description="Whether the directory exists"),
        ]

        @override
        def _physically_present(self) -> bool:
            """Return whether the directory exists.

            Returns:
                The declared ``exists`` flag.

            """
            return self.exists

    class CommandEntryModel(m.BaseModel):
        """Single command entry: name + handler. Use m.Cli.CommandEntryModel."""

        model_config: ClassVar[t.ConfigDict] = m.ConfigDict(
            arbitrary_types_allowed=True,
            extra="forbid",
        )
        name: Annotated[t.NonEmptyStr, m.Field(..., description="Command name")]
        handler: Annotated[
            t.Cli.JsonCommandFn,
            m.Field(..., description="Command handler callable"),
        ]

    class EmptyRequest(m.BaseModel):
        """Shared request model of a service operation that takes no input."""

        model_config: ClassVar[t.ConfigDict] = m.ConfigDict(extra="forbid", frozen=True)

    class CommandMetadata(m.BaseModel):
        """Immutable command identity and user-facing help."""

        model_config: ClassVar[t.ConfigDict] = m.ConfigDict(
            arbitrary_types_allowed=True,
            extra="forbid",
            frozen=True,
        )
        name: Annotated[t.NonEmptyStr, m.Field(..., description="Command name")]
        help_text: Annotated[str, m.Field(..., description="User-facing help text")]

    class ResultCommandRoute(CommandMetadata):
        """Type-erased route contract with inherited, flat command metadata."""

        model_cls: Annotated[
            t.ModelClass[t.Cli.ModelLike],
            m.Field(..., description="Pydantic input model class"),
        ]
        handler: Annotated[
            t.Port[p.Cli.ResultRouteHandler],
            m.Field(..., description="Command handler returning r[...]"),
        ]
        success_message: Annotated[
            str | None,
            m.Field(None, description="Static success message"),
        ] = None
        success_formatter: Annotated[
            t.Cli.SuccessMessageFormatter | None,
            m.Field(None, description="Dynamic success formatter"),
        ] = None
        success_type: Annotated[
            c.Cli.MessageTypes,
            m.Field(description="CLI output style on success"),
        ] = c.Cli.MessageTypes.SUCCESS


__all__: list[str] = ["FlextCliModelsBasePart03"]
