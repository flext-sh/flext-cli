"""Typed YAML model service.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli import p, s, t


class FlextCliYamlModel(s[p.Cli.RuntimeStatus]):
    """Expose model-only YAML egress for public API composition."""

    # NOTE (multi-agent, mro-j2yt.1): public API MRO composition is deferred
    # until the private implementation and real round trip are independently green.


__all__: t.VariadicTuple[str] = ("FlextCliYamlModel",)
