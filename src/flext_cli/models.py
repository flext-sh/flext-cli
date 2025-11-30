"""FlextCli models module - Pydantic models with StrEnum."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Self

from flext_core import FlextModels
from pydantic import ConfigDict, Field

from .constants import FlextCliConstants


class FlextCliModels(FlextModels):
    """FlextCli models extending FlextModels.

    REGRAS:
    ───────
    1. Herdar de FlextModels, NUNCA BaseModel direto
    2. ConfigDict com frozen=True, extra="forbid"
    3. StrEnum de constants, NÃO criar novos
    4. field_validator para validação complexa
    5. Self para métodos de transformação
    """

    class CliCommand(FlextModels.Entity):
        """CLI command model."""

        model_config = ConfigDict(
            frozen=True,
            extra="forbid",
            use_enum_values=True,
            validate_default=True,
            str_strip_whitespace=True,
        )

        name: str = Field(
            ...,
            min_length=1,
            description="Command name",
        )

        description: str = Field(
            ...,
            min_length=1,
            description="Command description",
        )

        args: Sequence[str] = Field(
            default_factory=list,
            description="Command arguments",
        )

        status: FlextCliConstants.Domain.Status = Field(
            default=FlextCliConstants.Domain.Status.PENDING,
            description="Command execution status",
        )

        def with_status(self, status: FlextCliConstants.Domain.Status) -> Self:
            """Return copy with new status."""
            return self.model_copy(update={"status": status})

        def with_args(self, args: Sequence[str]) -> Self:
            """Return copy with new arguments."""
            return self.model_copy(update={"args": list(args)})

    class CliContext(FlextModels.Value):
        """CLI execution context model."""

        model_config = ConfigDict(
            frozen=True,
            extra="forbid",
            use_enum_values=True,
        )

        cwd: str = Field(
            ...,
            description="Current working directory",
        )

        env: Mapping[str, str] = Field(
            default_factory=dict,
            description="Environment variables",
        )

        args: Sequence[str] = Field(
            default_factory=list,
            description="Command line arguments",
        )

        output_format: FlextCliConstants.OutputFormats = Field(
            default=FlextCliConstants.OutputFormats.TABLE,
            description="Output format preference",
        )

    class CliOutput(FlextModels.Value):
        """CLI output configuration model."""

        model_config = ConfigDict(
            frozen=True,
            extra="forbid",
        )

        format: FlextCliConstants.OutputFormats = Field(
            default=FlextCliConstants.OutputFormats.TABLE,
            description="Output format",
        )

        headers: Sequence[str] = Field(
            default_factory=list,
            description="Table headers",
        )

        show_headers: bool = Field(
            default=True,
            description="Whether to show headers",
        )

        color: bool = Field(
            default=True,
            description="Whether to use colors",
        )

    class CommandResult(FlextModels.Value):
        """Result of command execution."""

        model_config = ConfigDict(
            frozen=True,
            extra="forbid",
        )

        command: str = Field(
            ...,
            description="Executed command",
        )

        exit_code: int = Field(
            default=0,
            ge=0,
            description="Exit code",
        )

        stdout: str = Field(
            default="",
            description="Standard output",
        )

        stderr: str = Field(
            default="",
            description="Standard error",
        )

        duration: float = Field(
            default=0.0,
            ge=0.0,
            description="Execution duration in seconds",
        )

        @property
        def success(self) -> bool:
            """Check if command succeeded."""
            return self.exit_code == 0

        @property
        def has_output(self) -> bool:
            """Check if command produced output."""
            return bool(self.stdout or self.stderr)

    class CliConfig(FlextModels.Entity):
        """CLI configuration model."""

        model_config = ConfigDict(
            frozen=True,
            extra="forbid",
            use_enum_values=True,
            validate_default=True,
        )

        server_type: FlextCliConstants.ServerType = Field(
            default=FlextCliConstants.ServerType.OUD,
            description="Server type",
        )

        output_format: FlextCliConstants.OutputFormats = Field(
            default=FlextCliConstants.OutputFormats.TABLE,
            description="Default output format",
        )

        verbosity: FlextCliConstants.LogVerbosity = Field(
            default=FlextCliConstants.LogVerbosity.COMPACT,
            description="Log verbosity level",
        )

        timeout: int = Field(
            default=30,
            ge=1,
            le=300,
            description="Default timeout in seconds",
        )

        color: bool = Field(
            default=True,
            description="Enable colored output",
        )

        confirm_actions: bool = Field(
            default=True,
            description="Require confirmation for destructive actions",
        )
