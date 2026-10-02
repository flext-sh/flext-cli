"""Installed-distribution metadata utilities for the CLI facade.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from importlib import metadata
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

    from flext_cli import t


class FlextCliUtilitiesMetadata:
    """Installed-distribution metadata utilities."""

    @staticmethod
    def installed_distributions(
        path: t.StrSequence | None = None,
    ) -> Sequence[metadata.Distribution]:
        """Return the installed distributions, sorted for deterministic scans.

        Args:
            path: Optional sys.path entries to scope the scan (defaults to the
                interpreter's full sys.path).

        Returns:
            The discovered ``importlib.metadata.Distribution`` objects, sorted
            by name and version so repeated scans compare equal.

        """
        scan_paths = [str(entry) for entry in path] if path else None
        found = metadata.distributions(path=scan_paths)
        named = (
            installed
            for installed in found
            if installed.metadata.get("Name")
        )
        return sorted(
            named,
            key=lambda installed: (
                str(installed.metadata.get("Name", "")),
                str(installed.version),
            ),
        )
