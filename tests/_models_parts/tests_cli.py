"""Split test model namespace."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

from flext_cli import m
from tests import c


class TestsFlextCliModelsCli:
    """Split test model namespace."""

    class SampleInput(m.BaseModel):
        """Small request model for exercising model-driven CLI generation."""

        name: Annotated[str, m.Field(description="Target name")]
        count: Annotated[int, m.Field(description="How many times")] = 1
        dry_run: Annotated[bool, m.Field(description="Dry-run mode")] = False
        output_format: Annotated[
            c.Cli.OutputFormats, m.Field(description="Output format")
        ] = c.Cli.OutputFormats.TABLE

    class SampleOutput(m.BaseModel):
        """Concrete output model for result-route tests."""

        message: Annotated[str, m.Field(description="User-facing success message")]

    class RepeatableInput(m.BaseModel):
        """Exercise repeatable CLI options derived from list-typed fields."""

        make_arg: Annotated[
            list[str], m.Field(description="Repeatable make-style arg")
        ] = m.Field(default_factory=list, validate_default=True)

    class ReportRow(m.BaseModel):
        """Tabular report row used by the export-report example."""

        id: Annotated[int, m.Field(description="Row identifier")]
        name: Annotated[str, m.Field(description="Row display name")]
        status: Annotated[str, m.Field(description="Row status label")]

    class UserPreferences(m.BaseModel):
        """User preference record used by the file-operation example."""

        theme: Annotated[str, m.Field(description="UI theme name")]
        notifications: Annotated[bool, m.Field(description="Notification toggle")]

    class DeploymentConfig(m.BaseModel):
        """Deployment settings used by the file-operation example."""

        environment: Annotated[str, m.Field(description="Target environment")]
        replicas: Annotated[int, m.Field(description="Replica count")]

    class ImportRecord(m.BaseModel):
        """Imported data record used by the file-operation example."""

        id: Annotated[int, m.Field(description="Record identifier")]
        name: Annotated[str, m.Field(description="Record name")]
        value: Annotated[str, m.Field(description="Record value")]

    class SummaryStats(m.FrozenModel):
        """Orchestration summary payload satisfying ``p.Cli.SummaryStats``."""

        verb: Annotated[str, m.Field(description="Verb label")]
        total: Annotated[int, m.Field(description="Total processed items")]
        success: Annotated[int, m.Field(description="Successful items")]
        failed: Annotated[int, m.Field(description="Failed items")]
        skipped: Annotated[int, m.Field(description="Skipped items")]
        elapsed: Annotated[float, m.Field(description="Elapsed seconds")]

    class ProjectFailureInfo(m.FrozenModel):
        """Per-project failure payload satisfying ``p.Cli.ProjectFailureInfo``."""

        project: Annotated[str, m.Field(description="Project name")]
        elapsed: Annotated[float, m.Field(description="Elapsed seconds")]
        error_count: Annotated[int, m.Field(description="Total project errors")]
        log_path: Annotated[Path, m.Field(description="Project log path")]
        max_show: Annotated[int, m.Field(description="Maximum errors rendered")]
        errors: Annotated[
            tuple[str, ...], m.Field(description="Rendered error excerpt lines")
        ]


__all__: list[str] = ["TestsFlextCliModelsCli"]
