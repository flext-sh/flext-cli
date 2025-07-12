"""CLI service container for dependency injection."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import ConfigDict
from pydantic import Field

from flext_core.config.base import BaseSettings
from flext_core.domain.pydantic_base import DomainBaseModel

if TYPE_CHECKING:
    from rich.console import Console


class CLIServiceContainer(DomainBaseModel):
    """Service container for CLI dependency injection."""

    name: str = Field(..., description="Service container name")
    version: str = Field(..., description="Service container version")


class CLIConfig(BaseSettings):
    """CLI configuration using flext-core patterns."""

    output_format: str = Field(default="table", description="Default output format")
    debug: bool = Field(default=False, description="Enable debug mode")
    quiet: bool = Field(default=False, description="Enable quiet mode")
    no_color: bool = Field(default=False, description="Disable colored output")

    model_config = ConfigDict(
        env_prefix="FLEXT_CLI_",
        case_sensitive=False,
    )


class CLIContext(DomainBaseModel):
    """CLI context for command execution."""

    config: CLIConfig = Field(..., description="CLI configuration")
    console: Console | None = Field(default=None, description="Rich console instance")
