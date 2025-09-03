"""Minimal core service for tests built on new patterns."""

from __future__ import annotations

from flext_core import FlextDomainService, FlextResult


class FlextCliService(FlextDomainService[FlextResult[str]]):
    """Lightweight service exposing health check as FlextResult."""

    def flext_cli_health(self) -> FlextResult[str]:
        return FlextResult[str].ok("healthy")


__all__ = ["FlextCliService"]
