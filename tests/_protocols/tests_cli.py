# AUTO-GENERATED FILE — Regenerate with: make gen
"""Source-derived structural model contracts.

Copyright (c) 2026 FLEXT Team. All rights reserved.
tests/_protocols/tests_cli
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Protocol, runtime_checkable

from flext_tests import FlextTestsProtocols

if TYPE_CHECKING:
    from tests import c


class TestsFlextCliProtocolsTestsCli:
    """Own the structural contracts declared by its model source."""

    @runtime_checkable
    class SampleInput(FlextTestsProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        name: str
        count: int
        dry_run: bool
        output_format: c.Cli.OutputFormats

    @runtime_checkable
    class SampleOutput(FlextTestsProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        message: str

    @runtime_checkable
    class RepeatableInput(FlextTestsProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        make_arg: list[str]

    @runtime_checkable
    class ReportRow(FlextTestsProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        id: int
        name: str
        status: str

    @runtime_checkable
    class UserPreferences(FlextTestsProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        theme: str
        notifications: bool

    @runtime_checkable
    class DeploymentConfig(FlextTestsProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        environment: str
        replicas: int

    @runtime_checkable
    class ImportRecord(FlextTestsProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        id: int
        name: str
        value: str

    @runtime_checkable
    class SummaryStats(FlextTestsProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def verb(self) -> str:
            """Verb label."""
            ...

        @property
        def total(self) -> int:
            """Total processed items."""
            ...

        @property
        def success(self) -> int:
            """Successful items."""
            ...

        @property
        def failed(self) -> int:
            """Failed items."""
            ...

        @property
        def skipped(self) -> int:
            """Skipped items."""
            ...

        @property
        def elapsed(self) -> float:
            """Elapsed seconds."""
            ...

    @runtime_checkable
    class ProjectFailureInfo(FlextTestsProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def project(self) -> str:
            """Project name."""
            ...

        @property
        def elapsed(self) -> float:
            """Elapsed seconds."""
            ...

        @property
        def error_count(self) -> int:
            """Total project errors."""
            ...

        @property
        def log_path(self) -> Path:
            """Project log path."""
            ...

        @property
        def max_show(self) -> int:
            """Maximum errors rendered."""
            ...

        @property
        def errors(self) -> tuple[str, ...]:
            """Rendered error excerpt lines."""
            ...


__all__: list[str] = [
    "TestsFlextCliProtocolsTestsCli",
]
