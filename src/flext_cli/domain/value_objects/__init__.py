"""Value objects for FLEXT CLI domain."""

from __future__ import annotations

from enum import StrEnum
from typing import TYPE_CHECKING, Any

from flext_core.domain.pydantic_base import DomainValueObject
from pydantic import Field

if TYPE_CHECKING:
    from flext_cli.domain.value_objects.cli_context import CLIProfile


class OutputFormat(StrEnum):
    """Output format options."""

    TABLE = "table"
    JSON = "json"
    YAML = "yaml"
    TEXT = "text"
    PRETTY = "pretty"


class OutputConfig(DomainValueObject):
    """Output configuration."""

    format: OutputFormat = OutputFormat.TABLE
    no_color: bool = False
    verbose: bool = False
    quiet: bool = False
    show_headers: bool = True
    indent: int = 2


class AuthConfig(DomainValueObject):
    """Authentication configuration."""

    token: str | None = None

    @property
    def has_admin_rights(self) -> bool:
        """Check if user has admin rights."""
        return self.token is not None


class CLIContext(DomainValueObject):
    """CLI execution context."""

    verbose: bool = False
    config_path: str | None = None
    debug: bool = False
    timeout_seconds: int = 30
    is_production: bool = False
    output: OutputConfig = Field(default_factory=OutputConfig)
    auth: AuthConfig = Field(default_factory=AuthConfig)

    @property
    def is_quiet(self) -> bool:
        """Check if quiet mode is enabled."""
        return self.output.quiet

    @property
    def is_verbose(self) -> bool:
        """Check if verbose mode is enabled."""
        return self.output.verbose or self.verbose

    @property
    def is_debug(self) -> bool:
        """Check if debug mode is enabled."""
        return self.debug

    @property
    def supports_color(self) -> bool:
        """Check if color output is supported."""
        return not self.output.no_color

    @property
    def is_authenticated(self) -> bool:
        """Check if user is authenticated."""
        return self.auth.token is not None

    def with_profile(self, profile: CLIProfile) -> CLIContext:
        """Create new context with profile."""
        return self.model_copy(update={
            "config_path": f"{profile.name}.yaml",
        })


__all__ = ["AuthConfig", "CLIContext", "OutputConfig", "OutputFormat"]
