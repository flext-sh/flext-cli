"""Immutable default values shared by CLI declaration models."""

from __future__ import annotations

from types import MappingProxyType

from flext_cli import t


def empty_json_mapping() -> t.JsonMapping:
    """Create an immutable empty JSON mapping for one model instance."""
    return MappingProxyType({})


def empty_str_mapping() -> t.StrMapping:
    """Create an immutable empty string mapping for one model instance."""
    return MappingProxyType({})


__all__: tuple[str, ...] = ()
