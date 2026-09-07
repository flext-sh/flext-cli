"""CLI Pydantic domain models."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, ClassVar, Self

from flext_cli import c, p, t
from flext_cli._models import atomic_state
from flext_core import m, u


class FlextCliModelsBase:
    """Implementation part for FlextCliModelsBase."""

    class AtomicDirectoryState(m.BaseModel):
        """Exact empty-directory presence and physical identity."""

        model_config: ClassVar[t.ConfigDict] = m.ConfigDict(
            extra="forbid", frozen=True, arbitrary_types_allowed=True
        )
        path: Annotated[Path, m.Field(description="Absolute directory path")]
        exists: Annotated[
            bool, m.Field(strict=True, description="Whether the directory exists")
        ]
        parent_device: Annotated[
            int | None,
            m.Field(
                ge=0,
                strict=True,
                description="Physical parent device, or None when the chain is absent",
            ),
        ] = None
        parent_inode: Annotated[
            int | None,
            m.Field(
                ge=0,
                strict=True,
                description="Physical parent inode, or None when the chain is absent",
            ),
        ] = None
        mode: Annotated[
            int | None,
            m.Field(ge=0, le=0o7777, strict=True, description="Permission bits"),
        ] = None
        device: Annotated[
            int | None, m.Field(ge=0, strict=True, description="Physical device")
        ] = None
        inode: Annotated[
            int | None, m.Field(ge=0, strict=True, description="Physical inode")
        ] = None
        link_count: Annotated[
            int | None, m.Field(ge=1, strict=True, description="Exact link count")
        ] = None
        file_attributes: Annotated[
            int | None, m.Field(ge=0, strict=True, description="Host attributes")
        ] = None
        reparse_tag: Annotated[
            int | None, m.Field(ge=0, strict=True, description="Host reparse tag")
        ] = None

        @u.field_validator("path")
        @classmethod
        def _validate_absolute_path(cls, value: Path) -> Path:
            return atomic_state.validate_atomic_state_path(
                value, label="atomic directory state"
            )

        @u.model_validator(mode="after")
        def _validate_presence_tuple(self) -> Self:
            physical = (self.mode, self.device, self.inode, self.link_count)
            if (self.exists and not all(value is not None for value in physical)) or (
                not self.exists and any(value is not None for value in physical)
            ):
                msg = (
                    "atomic directory state requires mode, device, inode, and link "
                    "count exactly when it exists"
                )
                raise ValueError(msg)
            if not self.exists and (
                self.file_attributes is not None or self.reparse_tag is not None
            ):
                msg = "absent atomic directory state cannot contain host metadata"
                raise ValueError(msg)
            atomic_state.validate_parent_identity(
                self.parent_device,
                self.parent_inode,
                present=self.exists,
                label="atomic directory state",
            )
            atomic_state.validate_non_reparse_state(
                self.file_attributes, self.reparse_tag, label="atomic directory state"
            )
            return self

    class CommandEntryModel(m.BaseModel):
        """Single command entry: name + handler. Use m.Cli.CommandEntryModel."""

        model_config: ClassVar[t.ConfigDict] = m.ConfigDict(
            arbitrary_types_allowed=True, extra="forbid"
        )
        name: Annotated[t.NonEmptyStr, m.Field(..., description="Command name")]
        handler: Annotated[
            t.Cli.JsonCommandFn, m.Field(..., description="Command handler callable")
        ]

    class ResultCommandRoute(m.BaseModel):
        """Type-erased route contract for heterogeneous batch registration."""

        model_config: ClassVar[t.ConfigDict] = m.ConfigDict(
            arbitrary_types_allowed=True, extra="forbid", frozen=True
        )
        name: Annotated[t.NonEmptyStr, m.Field(..., description="Command name")]
        help_text: Annotated[str, m.Field(..., description="User-facing help text")]
        model_cls: Annotated[
            t.ModelClass[t.Cli.ModelLike],
            m.Field(..., description="Pydantic input model class"),
        ]
        handler: Annotated[
            p.Cli.ResultRouteHandler,
            m.Field(..., description="Command handler returning r[...]"),
        ]
        success_message: Annotated[
            str | None, m.Field(None, description="Static success message")
        ] = None
        success_formatter: Annotated[
            t.Cli.SuccessMessageFormatter | None,
            m.Field(None, description="Dynamic success formatter"),
        ] = None
        success_type: Annotated[
            c.Cli.MessageTypes, m.Field(description="CLI output style on success")
        ] = c.Cli.MessageTypes.SUCCESS


__all__: list[str] = ["FlextCliModelsBase"]
