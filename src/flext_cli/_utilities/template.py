"""Generic Jinja2 template helpers shared through ``u.Cli.render_template``.

flext-cli owns the universal template engine (ADR-005). Any FLEXT project or the
``~/.ai-hub`` control plane renders ``templates/*.j2`` through here instead of
importing Jinja2 directly or inlining template bodies in Python strings.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from jinja2 import StrictUndefined
from jinja2.exceptions import TemplateError
from jinja2.loaders import FileSystemLoader
from jinja2.sandbox import SandboxedEnvironment
from jinja2.utils import select_autoescape

from flext_cli import c, p, r, t
from flext_core import u

if TYPE_CHECKING:
    from pathlib import Path


class FlextCliUtilitiesTemplate:
    """Generic Jinja2 render helpers (ADR-005 template SSOT)."""

    @staticmethod
    def _environment(search_path: Path) -> SandboxedEnvironment:
        """Build the shared strict, sandboxed Jinja environment for a directory."""
        return SandboxedEnvironment(
            loader=FileSystemLoader(str(search_path)),
            undefined=StrictUndefined,
            trim_blocks=c.Cli.TEMPLATE_TRIM_BLOCKS,
            lstrip_blocks=c.Cli.TEMPLATE_LSTRIP_BLOCKS,
            keep_trailing_newline=c.Cli.TEMPLATE_KEEP_TRAILING_NEWLINE,
            autoescape=select_autoescape(),
        )

    @staticmethod
    def render_template(
        path: Path,
        context: t.JsonMapping,
    ) -> p.Result[str]:
        """Render a ``templates/*.j2`` file with ``context`` → ``r[str]``.

        Fail-closed: a missing template or any Jinja error (including undefined
        variables via ``StrictUndefined``) is a failed ``r[T]``.
        """
        if not path.is_file():
            return r[str].fail(f"{c.Cli.ERR_TEMPLATE_NOT_FOUND}: {path}")
        env = FlextCliUtilitiesTemplate._environment(path.parent)
        rendered = u.try_(
            lambda: env.get_template(path.name).render(dict(context)),
            catch=(TemplateError, OSError),
            op_name="render_template",
        )
        if rendered.failure:
            return r[str].fail(
                rendered.error or f"{c.Cli.ERR_TEMPLATE_RENDER_FAILED}: {path}",
            )
        return r[str].ok(rendered.value)

    @staticmethod
    def render_template_to(
        path: Path,
        dest: Path,
        context: t.JsonMapping,
    ) -> p.Result[bool]:
        """Render ``path`` with ``context`` and write it to ``dest`` → ``r[bool]``."""
        rendered = FlextCliUtilitiesTemplate.render_template(path, context)
        if rendered.failure:
            return r[bool].fail(rendered.error or c.Cli.ERR_TEMPLATE_RENDER_FAILED)
        return u.try_(
            lambda: FlextCliUtilitiesTemplate._write(dest, rendered.value),
            catch=OSError,
            op_name="render_template_to",
        )

    @staticmethod
    def _write(dest: Path, content: str) -> bool:
        """Write ``content`` to ``dest``, creating parents; return ``True``."""
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(content, encoding=c.Cli.ENCODING_DEFAULT)
        return True


__all__: t.MutableSequenceOf[str] = ["FlextCliUtilitiesTemplate"]
