"""Environment-file reading primitives shared through ``u.Cli``."""

from __future__ import annotations

import os
from pathlib import Path

from flext_cli import c, p, r, t


class FlextCliUtilitiesEnv:
    """Read ``KEY=VALUE`` environment files exposed directly on ``u.Cli``."""

    @staticmethod
    def env_reader(
        path: t.Cli.TextPath,
        *,
        overlay_process_env: bool = True,
    ) -> p.Result[t.StrDict]:
        """Read a ``KEY=VALUE`` environment file into a plain string mapping.

        Parses the desktop-style environment file (e.g. ``~/.config/environment``):
        comments, blank lines, and non-identifier keys (such as ``ALIAS ls=...``)
        are skipped, and surrounding single or double quotes are stripped from the
        value. An absent file is a legitimate empty state, not a failure.

        When ``overlay_process_env`` is true (default), the file values are
        overlaid onto ``os.environ`` with existing non-blank process variables
        winning, matching shell ``${VAR:-default}`` precedence. When false, only
        the file's own parsed pairs are returned.
        """
        resolved = Path(path)
        values: t.StrDict = {}
        if resolved.exists():
            try:
                content = resolved.read_text(encoding=c.DEFAULT_ENCODING)
            except c.EXC_OS_VALUE as exc:
                return r[t.StrDict].fail(f"cannot read env file {resolved}: {exc}")
            for raw in content.splitlines():
                line = raw.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, value = line.partition("=")
                key = key.strip()
                if not key.replace("_", "").isalnum():
                    continue
                values[key] = value.strip().strip('"').strip("'")
        if not overlay_process_env:
            return r[t.StrDict].ok(values)
        merged: t.StrDict = dict(os.environ)
        for key, value in values.items():
            if not merged.get(key) and value:
                merged[key] = value
        return r[t.StrDict].ok(merged)


__all__: list[str] = ["FlextCliUtilitiesEnv"]
