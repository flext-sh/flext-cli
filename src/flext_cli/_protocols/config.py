"""Config-domain protocols part (composed into ``p.Cli`` via MRO).

Structural, field-level protocols for the validated config domains — never
model classes, never ``Any``/``object``. No runtime project imports; importable
by ``c``/``t``/``p``/``m``/``u`` without creating a cycle (foundation purity).

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable


class FlextCliProtocolsConfig:
    """Config-domain protocol namespace (structural types; no project imports)."""

    @runtime_checkable
    class FileIteration(Protocol):
        """Structural Git-aware file-selection policy."""

        @property
        def executable(self) -> str: ...

        @property
        def timeout_seconds(self) -> int: ...

        @property
        def scope_files_args(self) -> tuple[str, ...]: ...

        @property
        def output_separator(self) -> str: ...

    @runtime_checkable
    class Cli(Protocol):
        """Structural surface of the validated ``Cli`` config domain."""

        @property
        def name(self) -> str: ...

        @property
        def version(self) -> str: ...

        @property
        def file_iteration(self) -> FlextCliProtocolsConfig.FileIteration: ...


__all__: list[str] = ["FlextCliProtocolsConfig"]
