"""Generic TOML helpers shared through ``u.Cli.toml_*``.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import tomlkit
from tomlkit.toml_document import TOMLDocument

from flext_cli import c, e, p, r, t

if TYPE_CHECKING:
    from pathlib import Path


class FlextCliUtilitiesTomlPart06:
    """Implementation part for FlextCliUtilitiesTomlPart06."""

    @staticmethod
    def toml_read(path: Path) -> TOMLDocument | None:
        """Read a TOML document, returning ``None`` on missing or invalid files.

        Returns:
            The resulting ``TOMLDocument | None``.

        """
        from flext_core import u
        if not path.exists():
            return None
        parsed: TOMLDocument | None
        try:
            parsed = tomlkit.parse(path.read_text(encoding=c.Cli.ENCODING_DEFAULT))
        except c.EXC_OS_VALUE as exc:
            u.fetch_logger(__name__).warning(
                "Failed to read or parse TOML document",
                path=str(path),
                error=str(exc),
                error_type=type(exc).__name__,
            )
            parsed = None
        return parsed

    @staticmethod
    def toml_read_document(path: Path) -> p.Result[TOMLDocument]:
        """Read a TOML document with ``r`` semantics.

        Returns:
            The resulting ``p.Result[TOMLDocument]``.

        """
        if not path.exists():
            return e.fail_not_found("TOML file", str(path), result_type=r[TOMLDocument])
        doc = FlextCliUtilitiesTomlPart06.toml_read(path)
        if doc is None:
            return e.fail_validation(
                f"TOML parse failed for: {path}",
                result_type=r[TOMLDocument],
            )
        return r[TOMLDocument].ok(doc)

    @staticmethod
    def toml_read_json(path: Path) -> p.Result[t.JsonMapping]:
        """Read TOML and return the unwrapped root table as ``JsonMapping``.

        Returns:
            The resulting ``p.Result[t.JsonMapping]``.

        """
        from flext_cli._utilities import FlextCliUtilitiesTomlPart01
        if not path.exists():
            return e.fail_not_found(
                "TOML file",
                str(path),
                result_type=r[t.JsonMapping],
            )
        try:
            original_rendered = path.read_text(encoding=c.Cli.ENCODING_DEFAULT)
        except OSError as exc:
            return e.fail_operation("read TOML", exc, result_type=r[t.JsonMapping])
        mapping = FlextCliUtilitiesTomlPart01.toml_mapping_from_text(original_rendered)
        if mapping is None:
            return e.fail_validation(
                f"TOML parse failed for: {path}",
                result_type=r[t.JsonMapping],
            )
        return r[t.JsonMapping].ok(mapping)

    @staticmethod
    def _resolve_taplo_config(path: Path) -> Path | None:
        """Resolve the nearest ``.taplo.toml`` for a pyproject file.

        Returns:
            The resulting ``Path | None``.

        """
        resolved = path.resolve()
        for candidate in (resolved.parent, *resolved.parents):
            config_path = candidate / ".taplo.toml"
            if config_path.is_file():
                return config_path
        return None

    @staticmethod
    def _format_pyproject(path: Path) -> p.Result[bool]:
        """Format managed ``pyproject.toml`` files with taplo when available.

        Returns:
            The resulting ``p.Result[bool]``.

        """
        from flext_cli._utilities import FlextCliUtilitiesRuntime
        from flext_core import u
        if path.name != "pyproject.toml":
            return r[bool].ok(value=False)
        command = ["taplo", "format"]
        config_path = FlextCliUtilitiesTomlPart06._resolve_taplo_config(path)
        if config_path is not None:
            command.extend(["--config", str(config_path)])
        command.append(str(path))
        return (
            u.Cli
            .run_raw(command, cwd=path.parent)
            .map_error(lambda err: err or f"taplo format failed: {path}")
            .flat_map(
                lambda output: (
                    r[bool].ok(value=True)
                    if FlextCliUtilitiesRuntime.process_succeeded(output.outcome)
                    else r[bool].fail(
                        (output.stderr or output.stdout).strip()
                        or f"taplo format failed: {path}",
                    )
                ),
            )
        )

    @staticmethod
    def toml_write_document(path: Path, doc: TOMLDocument) -> p.Result[bool]:
        """Write a TOML document and format managed pyproject files.

        Returns:
            The resulting ``p.Result[bool]``.

        """
        from flext_core import u
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            u.write_file(path, doc.as_string(), encoding=c.Cli.ENCODING_DEFAULT)
        except OSError as exc:
            return e.fail_operation("TOML write", exc, result_type=r[bool])
        return (
            FlextCliUtilitiesTomlPart06
            ._format_pyproject(path)
            .map_error(lambda err: err or f"taplo format failed: {path}")
            .map(lambda _ok: True)
        )


__all__: list[str] = ["FlextCliUtilitiesTomlPart06"]
