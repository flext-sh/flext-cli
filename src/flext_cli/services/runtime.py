"""DSL service for external process runtime helpers.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import (
    Iterable,
    Iterator,
    Mapping,
    MutableMapping,
    MutableSequence,
    Sequence,
)

from collections.abc import MutableSequence

from flext_cli import p, s


class FlextCliRuntime(s[p.Cli.RuntimeStatus]):
    """Expose process execution helpers through ``cli`` and ``FlextCli``."""


__all__: MutableSequence[str] = ["FlextCliRuntime"]
