"""Generic typed PPTX service."""

from __future__ import annotations

from flext_cli import m, s, t


class FlextCliPptx(s[m.Cli.RuntimeStatus]):
    """Expose byte-only PPTX operations and re-exported types for public API composition."""

    # NOTE (multi-agent, mro-j2yt.1): this service contains no document or
    # customer rules; consumers provide immutable plans and receive bytes/models.


__all__: t.VariadicTuple[str] = ("FlextCliPptx",)
