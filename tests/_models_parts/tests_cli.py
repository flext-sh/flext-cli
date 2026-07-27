"""Split test model namespace."""

from __future__ import annotations

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
        ] = m.Field([], validate_default=True)

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


__all__: list[str] = ["TestsFlextCliModelsCli"]
