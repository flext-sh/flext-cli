"""FLEXT CLI Constants - Single unique CLI constants class.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import ClassVar

from flext_core import FlextConstants


class FlextCliConstants(FlextConstants):
    """CLI-specific constants extending flext-core FlextConstants.

    Single unique class for the module following flext-core inheritance patterns.
    All functionality should be available through FlextConstants base class.
    """

    # Reference to flext-core constants for inheritance
    Core: ClassVar = FlextConstants

    class CliMessages:
        """Docstring for CliMessages."""

        # Interactive section
        INTERACTIVE_FEATURE_HELP = "Interactive commands: REPL, completion, history"
        INFO_USE_HELP = "Use --help for more information"

        # Version info
        VERSION_CLI = "FLEXT CLI"
        VERSION_PYTHON = "Python"
        VERSION_FLEXT_CORE = "FLEXT Core"

        # Debug/diagnostics
        DEBUG_FLEXT_CORE_NOT_DETECTED = "FLEXT Core version not detected"
        DEBUG_INFORMATION = "Debug Information"
        DEBUG_CONFIGURATION = "Configuration"
        DEBUG_PYTHON_EXECUTABLE = "Python Executable"
        DEBUG_PLATFORM = "Platform"
        DEBUG_SERVICE_CONNECTIVITY = "Service connectivity check"


# =============================================================================
# EXPORTS - Single unique class following user requirements
# =============================================================================

__all__ = [
    "FlextCliConstants",
]
