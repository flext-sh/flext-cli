# AUTO-GENERATED FILE — Regenerate with: make gen
"""Internal package for runtime.

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

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from flext_cli._utilities._runtime.commands import FlextCliUtilitiesRuntimeCommands
    from flext_cli._utilities._runtime.darwin_process_group import (
        FlextCliUtilitiesRuntimeDarwinProcessGroup,
    )
    from flext_cli._utilities._runtime.process_cleanup import (
        FlextCliUtilitiesRuntimeProcessCleanup,
    )
    from flext_cli._utilities._runtime.process_execution import (
        FlextCliUtilitiesRuntimeProcessExecution,
    )
    from flext_cli._utilities._runtime.process_group import (
        FlextCliUtilitiesRuntimeProcessGroup,
    )
    from flext_cli._utilities._runtime.process_monitor import (
        FlextCliUtilitiesRuntimeProcessMonitor,
    )
    from flext_cli._utilities._runtime.process_outcome import (
        FlextCliUtilitiesRuntimeProcessOutcome,
    )
    from flext_cli._utilities._runtime.process_output import (
        FlextCliUtilitiesRuntimeProcessOutput,
    )
    from flext_cli._utilities._runtime.process_resources import (
        FlextCliUtilitiesRuntimeProcessResources,
    )
    from flext_cli._utilities._runtime.process_start import (
        FlextCliUtilitiesRuntimeProcessStart,
    )
    from flext_cli._utilities._runtime.process_stream import (
        FlextCliUtilitiesRuntimeProcessStream,
    )
    from flext_cli._utilities._runtime.process_threads import (
        FlextCliUtilitiesRuntimeProcessThreads,
    )
    from flext_cli._utilities._runtime.process_timing import (
        FlextCliUtilitiesRuntimeProcessTiming,
    )
    from flext_cli._utilities._runtime.process_wait import (
        FlextCliUtilitiesRuntimeProcessWait,
    )
    from flext_cli._utilities._runtime.run_to_file import (
        FlextCliUtilitiesRuntimeRunToFile,
    )
    from flext_cli._utilities._runtime.windows_job_start import (
        FlextCliUtilitiesRuntimeWindowsJobStart,
    )
    from flext_cli._utilities._runtime.windows_job_state import (
        FlextCliUtilitiesRuntimeWindowsJobState,
    )

__all__: tuple[str, ...] = (
    "FlextCliUtilitiesRuntimeCommands",
    "FlextCliUtilitiesRuntimeDarwinProcessGroup",
    "FlextCliUtilitiesRuntimeProcessCleanup",
    "FlextCliUtilitiesRuntimeProcessExecution",
    "FlextCliUtilitiesRuntimeProcessGroup",
    "FlextCliUtilitiesRuntimeProcessMonitor",
    "FlextCliUtilitiesRuntimeProcessOutcome",
    "FlextCliUtilitiesRuntimeProcessOutput",
    "FlextCliUtilitiesRuntimeProcessResources",
    "FlextCliUtilitiesRuntimeProcessStart",
    "FlextCliUtilitiesRuntimeProcessStream",
    "FlextCliUtilitiesRuntimeProcessThreads",
    "FlextCliUtilitiesRuntimeProcessTiming",
    "FlextCliUtilitiesRuntimeProcessWait",
    "FlextCliUtilitiesRuntimeRunToFile",
    "FlextCliUtilitiesRuntimeWindowsJobStart",
    "FlextCliUtilitiesRuntimeWindowsJobState",
)

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType({
        "FlextCliUtilitiesRuntimeCommands": ".commands",
        "FlextCliUtilitiesRuntimeDarwinProcessGroup": ".darwin_process_group",
        "FlextCliUtilitiesRuntimeProcessCleanup": ".process_cleanup",
        "FlextCliUtilitiesRuntimeProcessExecution": ".process_execution",
        "FlextCliUtilitiesRuntimeProcessGroup": ".process_group",
        "FlextCliUtilitiesRuntimeProcessMonitor": ".process_monitor",
        "FlextCliUtilitiesRuntimeProcessOutcome": ".process_outcome",
        "FlextCliUtilitiesRuntimeProcessOutput": ".process_output",
        "FlextCliUtilitiesRuntimeProcessResources": ".process_resources",
        "FlextCliUtilitiesRuntimeProcessStart": ".process_start",
        "FlextCliUtilitiesRuntimeProcessStream": ".process_stream",
        "FlextCliUtilitiesRuntimeProcessThreads": ".process_threads",
        "FlextCliUtilitiesRuntimeProcessTiming": ".process_timing",
        "FlextCliUtilitiesRuntimeProcessWait": ".process_wait",
        "FlextCliUtilitiesRuntimeRunToFile": ".run_to_file",
        "FlextCliUtilitiesRuntimeWindowsJobStart": ".windows_job_start",
        "FlextCliUtilitiesRuntimeWindowsJobState": ".windows_job_state",
    }),
    public_exports=__all__,
)
