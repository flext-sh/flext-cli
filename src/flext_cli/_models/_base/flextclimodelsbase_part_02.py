"""CLI Pydantic domain models.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Annotated, ClassVar, Self

from flext_core import m, t

from flext_cli import c
from flext_cli._models import FlextCliModelsAtomicState


class FlextCliModelsBasePart02:
    """Implementation part for FlextCliModelsBasePart02."""

    class AtomicPhysicalIdentity(m.BaseModel):
        """Physical identity shared by every descriptor-authenticated leaf state.

        A subclass whose presence is not the physical device itself overrides
        ``_physically_present``; the identity validation is shared by every
        state, and each subclass keeps its own failure wording.
        """

        model_config: ClassVar[t.ConfigDict] = m.ConfigDict(
            extra="forbid",
            frozen=True,
            arbitrary_types_allowed=True,
        )
        atomic_state_label: ClassVar[str] = "atomic physical state"
        atomic_presence_message: ClassVar[str] = (
            "atomic physical state requires mode, device, inode, and link count "
            "exactly when it exists"
        )

        path: Annotated[Path, m.Field(description="Absolute leaf path")]
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
            m.Field(
                ge=0,
                le=0o7777,
                strict=True,
                description="Exact permission bits, or None when absent",
            ),
        ] = None
        device: Annotated[
            int | None,
            m.Field(
                ge=0,
                strict=True,
                description="Physical device, or None when absent",
            ),
        ] = None
        inode: Annotated[
            int | None,
            m.Field(
                ge=0,
                strict=True,
                description="Physical inode, or None when absent",
            ),
        ] = None
        link_count: Annotated[
            int | None,
            m.Field(
                ge=1,
                strict=True,
                description="Observed link count (>= 1), or None when absent",
            ),
        ] = None
        file_attributes: Annotated[
            int | None,
            m.Field(
                ge=0,
                strict=True,
                description="Host file attributes when available",
            ),
        ] = None
        reparse_tag: Annotated[
            int | None,
            m.Field(ge=0, strict=True, description="Host reparse tag when available"),
        ] = None

        @m.field_validator("path")
        @classmethod
        def _validate_absolute_path(cls, value: Path) -> Path:
            """Reject ambiguous relative identities instead of normalizing them.

            Returns:
                The resulting ``Path``.

            """
            return FlextCliModelsAtomicState.validate_atomic_state_path(
                value,
                label=cls.atomic_state_label,
            )

        def _physically_present(self) -> bool:
            """Return whether the leaf physically exists.

            Returns:
                ``True`` when the identity carries a physical device.

            """
            return self.device is not None

        @m.model_validator(mode="after")
        def _validate_physical_identity(self) -> Self:
            """Require one complete, uniquely owned, non-reparse identity.

            Returns:
                The validated model instance.

            Raises:
                ValueError: If the physical tuple does not match presence, an
                    absent leaf carries host metadata, the parent identity is
                    incomplete, or the leaf is a reparse point.

            """
            label = self.atomic_state_label
            present = self._physically_present()
            physical = (self.mode, self.device, self.inode, self.link_count)
            if any((value is not None) != present for value in physical):
                raise ValueError(self.atomic_presence_message)
            if not present and (
                self.file_attributes is not None or self.reparse_tag is not None
            ):
                msg = f"absent {label} cannot contain host metadata"
                raise ValueError(msg)
            FlextCliModelsAtomicState.validate_parent_identity(
                self.parent_device,
                self.parent_inode,
                present=present,
                label=label,
            )
            FlextCliModelsAtomicState.validate_non_reparse_state(
                self.file_attributes,
                self.reparse_tag,
                label=label,
            )
            return self

    class AtomicFileIdentity(AtomicPhysicalIdentity):
        """Shared physical identity of an existing or absent regular file."""

        model_config: ClassVar[t.ConfigDict] = m.ConfigDict(
            ser_json_bytes="base64",
            val_json_bytes="base64",
        )
        atomic_state_label: ClassVar[str] = "atomic file state"
        atomic_presence_message: ClassVar[str] = (
            "atomic file identity must contain mode, device, inode, and link "
            "count, or none of them"
        )

    class AtomicFileState(AtomicFileIdentity):
        """Exact content and physical identity for one regular file version."""

        content: Annotated[
            bytes | None,
            m.Field(strict=True, description="Exact bytes, or None when absent"),
        ] = None

        @m.model_validator(mode="after")
        def _validate_content_presence(self) -> Self:
            """Require exact bytes if and only if the physical file exists.

            Returns:
                The validated model instance.

            Raises:
                ValueError: If content presence and physical presence disagree.

            """
            if (self.content is not None) != (self.device is not None):
                msg = "atomic file content and physical presence must agree"
                raise ValueError(msg)
            return self

    class AtomicFileReceipt(AtomicFileIdentity):
        """Authenticated file version and digest without a buffered payload."""

        size: Annotated[
            int | None, m.Field(ge=0, strict=True, description="Exact byte length")
        ] = None
        sha256: Annotated[
            str | None,
            m.Field(
                pattern=r"^[0-9a-f]{64}$",
                strict=True,
                description="Digest of the complete authenticated descriptor",
            ),
        ] = None
        version_key: Annotated[
            tuple[int, ...] | None,
            m.Field(description="Native descriptor version used for guarded reads"),
        ] = None

        @m.model_validator(mode="after")
        def _validate_receipt_presence(self) -> Self:
            """Require complete measurements if and only if the file exists.

            Returns:
                The validated model instance.

            Raises:
                ValueError: If receipt measurements and physical presence disagree.

            """
            measured = (
                self.size is not None,
                self.sha256 is not None,
                self.version_key is not None,
            )
            if any(measured) != all(measured) or all(measured) != (
                self.device is not None
            ):
                msg = "atomic receipt measurements and physical presence must agree"
                raise ValueError(msg)
            return self

    class PromptRuntimeState(m.FlexibleInternalModel):
        """Centralized runtime state for CLI prompt behavior."""

        model_config: ClassVar[t.ConfigDict] = m.ConfigDict(
            extra="forbid",
            validate_assignment=True,
        )

        interactive: bool = m.Field(
            default=True, description="Whether prompt interaction is enabled"
        )
        quiet: bool = m.Field(
            default=False, description="Whether prompt output is suppressed"
        )
        default_timeout: Annotated[
            int,
            m.Field(description="Default prompt timeout in seconds"),
        ] = c.Cli.PROMPT_DEFAULT_TIMEOUT

    class AuthCredentialsPayload(m.BaseModel):
        """Validated auth payload for token or username/password flows."""

        model_config: ClassVar[t.ConfigDict] = m.ConfigDict(
            extra="forbid",
            validate_assignment=True,
        )
        token: Annotated[
            str | None,
            m.Field(None, description="Direct authentication token", strict=True),
        ] = None
        username: Annotated[
            str,
            m.Field("", description="Authentication username", strict=True),
        ] = ""
        password: Annotated[
            str,
            m.Field("", description="Authentication password", strict=True),
        ] = ""

    class ProcessEnvironmentSpec(m.BaseModel):
        """Validated process environment contract for runtime command execution."""

        model_config: ClassVar[t.ConfigDict] = m.ConfigDict(extra="forbid", frozen=True)
        base_env: Annotated[
            Mapping[str, str],
            m.Field(
                description="Base environment inherited from the current process",
            ),
        ] = m.Field(default_factory=lambda: c.Cli.EMPTY_STR_MAPPING)
        overrides: Annotated[
            Mapping[str, str],
            m.Field(
                description="Explicit environment overrides for the child process",
            ),
        ] = m.Field(default_factory=lambda: c.Cli.EMPTY_STR_MAPPING)
        remove_keys: Annotated[
            Sequence[str],
            m.Field(
                description="Environment keys removed before applying overrides",
            ),
        ] = m.Field(default_factory=tuple)

        @m.computed_field
        @property
        def resolved(self) -> dict[str, str]:
            """Resolved environment mapping after removals and overrides."""
            return self.resolve()

        def resolve(self) -> dict[str, str]:
            """Type-safe accessor for the computed environment mapping.

            Returns:
                The resulting ``dict[str, str]``.

            """
            remove_keys = frozenset(self.remove_keys)
            resolved = {
                key: value
                for key, value in self.base_env.items()
                if key not in remove_keys
            }
            resolved.update({
                key: value
                for key, value in self.overrides.items()
                if key not in remove_keys
            })
            return resolved


__all__: list[str] = ["FlextCliModelsBasePart02"]
