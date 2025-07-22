"""Application services for FLEXT CLI."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from flext_core.domain.shared_types import ServiceResult

if TYPE_CHECKING:
    from flext_cli.config import CLIConfig


class CLIApplicationService:
    """Main CLI application service."""

    def __init__(self, config: CLIConfig) -> None:
        """Initialize CLI application service."""
        self.config = config

    def get_status(self) -> ServiceResult[dict[str, Any]]:
        """Get CLI status."""
        result_data: dict[str, Any] = {
            "status": "ready",
            "config": {
                "api_url": self.config.api_url,
                "timeout": self.config.timeout,
                "output_format": self.config.output_format,
            },
        }
        return ServiceResult.ok(data=result_data)


__all__ = ["CLIApplicationService"]
