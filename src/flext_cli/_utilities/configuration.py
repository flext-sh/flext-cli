"""CLI configuration helpers shared through ``u.Cli``."""

from __future__ import annotations

import os
from datetime import UTC, datetime
from pathlib import Path

from flext_cli import c, m, t


class FlextCliUtilitiesConfiguration:
    """Configuration and selector methods exposed directly on ``u.Cli``."""

    @staticmethod
    def project_names_from_values(
        *values: t.Cli.ProjectNamesValue,
    ) -> list[str] | None:
        """Normalize repeated or comma-separated CLI selector values."""
        names: list[str] = []
        for value in values:
            if value is None:
                continue
            raw_values = [value] if isinstance(value, str) else list(value)
            for raw_value in raw_values:
                for comma_group in raw_value.split(","):
                    names.extend(
                        item.strip() for item in comma_group.split() if item.strip()
                    )
        return names or None

    @staticmethod
    def config_snapshot() -> m.Cli.ConfigSnapshot:
        """Return the canonical CLI configuration snapshot."""
        path = Path.home() / c.Cli.PATH_FLEXT_DIR_NAME
        exists = path.exists()
        return m.Cli.ConfigSnapshot(
            config_dir=str(path),
            config_exists=exists,
            config_readable=exists and os.access(path, os.R_OK),
            config_writable=exists and os.access(path, os.W_OK),
            timestamp=datetime.now(UTC).isoformat(),
        )

    @staticmethod
    def validate_config_structure() -> t.StrSequence:
        """Validate the canonical CLI configuration directory structure."""
        base = Path.home() / c.Cli.PATH_FLEXT_DIR_NAME
        ok = c.Cli.SYMBOL_SUCCESS_MARK
        fail = c.Cli.SYMBOL_FAILURE_MARK
        lines = [
            f"{ok} Configuration directory exists"
            if base.exists()
            else f"{fail} Configuration directory missing",
        ]
        for subdir in c.Cli.STANDARD_SUBDIRS:
            path = base / subdir
            lines.append(
                c.Cli.MSG_SUBDIR_EXISTS.format(symbol=ok, subdir=subdir)
                if path.exists()
                else c.Cli.MSG_SUBDIR_MISSING.format(
                    symbol=fail,
                    subdir=subdir,
                ),
            )
        return lines


__all__ = [
    "FlextCliUtilitiesConfiguration",
]
