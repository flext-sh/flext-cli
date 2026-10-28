"""Public API facade for flext-cli.

Copyright (c) 2025 FLEXT Team. All rights reserved.
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

from flext_cli.services import (
    FlextCliAuth,
    FlextCliCli,
    FlextCliCommonParams,
    FlextCliDocx,
    FlextCliFileTools,
    FlextCliFormatters,
    FlextCliOutput,
    FlextCliPipeline,
    FlextCliPptx,
    FlextCliPrompts,
    FlextCliRuntime,
    FlextCliTables,
    FlextCliXlsx,
)


class FlextCli(
    FlextCliAuth,
    FlextCliCli,
    FlextCliCommonParams,
    FlextCliDocx,
    FlextCliFileTools,
    FlextCliFormatters,
    FlextCliOutput,
    FlextCliPipeline,
    FlextCliPrompts,
    FlextCliPptx,
    FlextCliRuntime,
    FlextCliTables,
    FlextCliXlsx,
):
    """Coordinate CLI operations through one explicit service composition root."""


cli: FlextCli = FlextCli.fetch_global()
"""Process-wide ``FlextCli`` facade singleton exposing every CLI service via MRO."""


__all__: MutableSequence[str] = ["FlextCli", "cli"]
