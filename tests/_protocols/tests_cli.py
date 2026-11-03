# AUTO-GENERATED FILE — Regenerate with: make gen
"""Source-derived structural model contracts.

Copyright (c) 2026 FLEXT Team. All rights reserved.
tests/_protocols/tests_cli
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from pathlib import Path
from typing import Protocol, runtime_checkable

from flext_tests import FlextTestsProtocols

from tests import c


class TestsFlextCliProtocolsTestsCli:
    """Own the structural contracts declared by its model source."""

    @runtime_checkable
    class SampleInput(FlextTestsProtocols.Model, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def name(self) -> str:
            """Target name."""
            ...

        @property
        def count(self) -> int:
            """How many times."""
            ...

        @property
        def dry_run(self) -> bool:
            """Dry-run mode."""
            ...

        @property
        def output_format(self) -> c.Cli.OutputFormats:
            """Output format."""
            ...

    @runtime_checkable
    class SampleOutput(FlextTestsProtocols.Model, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def message(self) -> str:
            """User-facing success message."""
            ...

    @runtime_checkable
    class RepeatableInput(FlextTestsProtocols.Model, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def make_arg(self) -> list[str]:
            """Repeatable make-style arg."""
            ...

    @runtime_checkable
    class ReportRow(FlextTestsProtocols.Model, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def id(self) -> int:
            """Row identifier."""
            ...

        @property
        def name(self) -> str:
            """Row display name."""
            ...

        @property
        def status(self) -> str:
            """Row status label."""
            ...

    @runtime_checkable
    class UserPreferences(FlextTestsProtocols.Model, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def theme(self) -> str:
            """UI theme name."""
            ...

        @property
        def notifications(self) -> bool:
            """Notification toggle."""
            ...

    @runtime_checkable
    class DeploymentConfig(FlextTestsProtocols.Model, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def environment(self) -> str:
            """Target environment."""
            ...

        @property
        def replicas(self) -> int:
            """Replica count."""
            ...

    @runtime_checkable
    class ImportRecord(FlextTestsProtocols.Model, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def id(self) -> int:
            """Record identifier."""
            ...

        @property
        def name(self) -> str:
            """Record name."""
            ...

        @property
        def value(self) -> str:
            """Record value."""
            ...

    @runtime_checkable
    class SummaryStats(FlextTestsProtocols.Model, Protocol):
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
    class ProjectFailureInfo(FlextTestsProtocols.Model, Protocol):
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
