"""CLI Pydantic domain models."""

from __future__ import annotations

from typing import Annotated, ClassVar

from flext_cli import c, p, t
from flext_core import m


class FlextCliModelsBase:
    """Implementation part for FlextCliModelsBase."""

    class CommandEntryModel(m.BaseModel):
        """Single command entry: name + handler. Use m.Cli.CommandEntryModel."""

        model_config: ClassVar[m.ConfigDict] = m.ConfigDict(
            arbitrary_types_allowed=True,
            extra="forbid",
        )
        name: Annotated[t.NonEmptyStr, m.Field(..., description="Command name")]
        handler: Annotated[
            t.Cli.JsonCommandFn,
            m.Field(..., description="Command handler callable"),
        ]

    class ResultCommandRoute(m.BaseModel):
        """Type-erased route contract for heterogeneous batch registration."""

        model_config: ClassVar[m.ConfigDict] = m.ConfigDict(
            arbitrary_types_allowed=True,
            extra="forbid",
            frozen=True,
        )
        name: Annotated[t.NonEmptyStr, m.Field(..., description="Command name")]
        help_text: Annotated[str, m.Field(..., description="User-facing help text")]
        model_cls: Annotated[
            t.Cli.ModelType[t.Cli.ModelLike],
            m.Field(..., description="Pydantic input model class"),
        ]
        handler: Annotated[
            t.Cli.ResultRouteHandler,
            m.Field(..., description="Command handler returning r[...]"),
        ]
        success_message: Annotated[
            str | None,
            m.Field(None, description="Static success message"),
        ] = None
        success_formatter: Annotated[
            p.Cli.SuccessMessageFormatter[t.Cli.ResultValue] | None,
            m.Field(None, description="Dynamic success formatter"),
        ] = None
        success_type: Annotated[
            c.Cli.MessageTypes,
            m.Field(
                description="CLI output style on success",
            ),
        ] = c.Cli.MessageTypes.SUCCESS


__all__: list[str] = ["FlextCliModelsBase"]
