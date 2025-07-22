"""CLI context value objects."""

from __future__ import annotations

from flext_core.domain.pydantic_base import DomainValueObject


class CLIProfile(DomainValueObject):
    """CLI profile configuration."""

    name: str
    api_url: str
    timeout: int = 30
    verify_ssl: bool = True


__all__ = ["CLIProfile"]
