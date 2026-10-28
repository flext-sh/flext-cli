"""Generic typed XLSX service.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli import p, s


class FlextCliXlsx(s[p.Cli.RuntimeStatus]):
    """Expose byte-only XLSX operations for later public API composition."""

    # NOTE (multi-agent, mro-j2yt.1): this service contains no document or
    # customer rules; consumers provide immutable plans and receive bytes/models.


__all__: tuple[str, ...] = ("FlextCliXlsx",)
