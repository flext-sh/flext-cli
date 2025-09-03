"""Minimal core service for tests built on new patterns."""

from __future__ import annotations

from flext_core import FlextResult
from flext_core.domain_services import FlextDomainService


class FlextCliService(FlextDomainService[FlextResult[str]]):
    """Lightweight service exposing health check as FlextResult."""

    def execute(self) -> FlextResult[str]:
        """Execute service request - required by FlextDomainService."""
        return FlextResult[str].ok("CLI service executed successfully")

    def flext_cli_health(self) -> FlextResult[str]:
        return FlextResult[str].ok("healthy")


__all__ = ["FlextCliService"]
