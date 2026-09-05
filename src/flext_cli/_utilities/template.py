"""Generic Jinja2 template helpers shared through ``u.Cli.template_render``.

flext-cli owns the universal template engine (ADR-005). Any FLEXT project or the
``~/.ai-hub`` control plane renders ``templates/*.j2`` through here instead of
importing Jinja2 directly or inlining template bodies in Python strings.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from pathlib import Path
from typing import ClassVar

from jinja2 import BaseLoader, Environment, StrictUndefined
from jinja2.exceptions import TemplateError, TemplateNotFound
from jinja2.loaders import FileSystemLoader
from jinja2.sandbox import SandboxedEnvironment
from jinja2.utils import select_autoescape

from flext_cli import c, m, p, r, t
from flext_cli._utilities._files_parts.flextcliutilitiesfiles_part_03 import (
    FlextCliUtilitiesFiles as FlextCliUtilitiesFilesPart03,
)
from flext_core import u


class FlextCliUtilitiesTemplate:
    """Generic Jinja2 render helpers (ADR-005 template SSOT)."""

    class _AuthenticatedLoader(BaseLoader):
        """Load every Jinja source once from descriptor-authenticated bytes."""

        def __init__(self, search_path: Path) -> None:
            self.search_path = search_path
            self.source_states: dict[Path, m.Cli.AtomicFileState] = {}
            self.failure: str | None = None

        def get_source(
            self, environment: Environment, template: str
        ) -> tuple[str, str, None]:
            """Return immutable captured text for one root-contained template."""
            del environment
            relative = Path(template)
            source = (self.search_path / relative).absolute()
            if (
                relative.is_absolute()
                or ".." in relative.parts
                or not source.is_relative_to(self.search_path)
            ):
                self.failure = f"template source escapes its root: {template}"
                raise TemplateNotFound(template)
            existing = self.source_states.get(source)
            if existing is None:
                snapshot = FlextCliUtilitiesFilesPart03.atomic_read_binary_file_state(
                    source, required=True
                )
                if snapshot.failure:
                    self.failure = (
                        snapshot.error or f"template snapshot failed: {source}"
                    )
                    raise TemplateNotFound(template)
                existing = snapshot.value
                self.source_states[source] = existing
            if existing.content is None:
                self.failure = f"authenticated template has no bytes: {source}"
                raise TemplateNotFound(template)
            try:
                content = existing.content.decode(c.Cli.ENCODING_DEFAULT)
            except UnicodeDecodeError as exc:
                self.failure = f"decode authenticated template {source}: {exc}"
                raise TemplateNotFound(template) from exc
            return content, str(source), None

    # NOTE (multi-agent, mro-wkii.17 / agent: make_ssot_audit): template
    # contexts retain their validated model identity until the Jinja egress.
    # Why: Jinja caches compiled template bytecode on the environment, so a
    # fresh environment per render recompiles every template source. One
    # environment per search directory keeps that cache alive for the process
    # while auto_reload still serves edited sources.
    _environments: ClassVar[t.Cli.TemplateEnvironmentCache] = {}

    @classmethod
    def template_environment(cls, search_path: Path) -> SandboxedEnvironment:
        """Return the process-wide strict, sandboxed engine for a directory."""
        key = str(search_path.resolve())
        cached = cls._environments.get(key)
        if cached is not None:
            return cached
        environment = SandboxedEnvironment(
            loader=FileSystemLoader(key),
            undefined=StrictUndefined,
            trim_blocks=c.Cli.TEMPLATE_TRIM_BLOCKS,
            lstrip_blocks=c.Cli.TEMPLATE_LSTRIP_BLOCKS,
            keep_trailing_newline=c.Cli.TEMPLATE_KEEP_TRAILING_NEWLINE,
            autoescape=select_autoescape(),
            auto_reload=True,
        )
        cls._environments[key] = environment
        return environment

    @staticmethod
    def template_render(path: Path, context: p.Model) -> p.Result[str]:
        """Render a ``templates/*.j2`` file with ``context`` → ``r[str]``.

        Fail-closed: a missing template or any Jinja error (including undefined
        variables via ``StrictUndefined``) is a failed ``r[T]``.
        """
        if not path.is_file():
            return r[str].fail(f"{c.Cli.ERR_TEMPLATE_NOT_FOUND}: {path}")
        env = FlextCliUtilitiesTemplate.template_environment(path.parent)
        rendered = u.try_(
            lambda: env.get_template(path.name).render(context.model_dump(mode="json")),
            catch=(TemplateError, OSError),
            op_name="template_render",
        )
        if rendered.failure:
            return r[str].from_failure(rendered)
        return r[str].ok(rendered.value)

    @staticmethod
    def template_render_authenticated(
        path: Path, context: p.Model
    ) -> p.Result[m.Cli.AuthenticatedTemplateRender]:
        """Render only descriptor-authenticated bytes and return all source states."""
        source = path.expanduser().absolute()
        loader = FlextCliUtilitiesTemplate._AuthenticatedLoader(source.parent)
        environment = SandboxedEnvironment(
            loader=loader,
            undefined=StrictUndefined,
            trim_blocks=c.Cli.TEMPLATE_TRIM_BLOCKS,
            lstrip_blocks=c.Cli.TEMPLATE_LSTRIP_BLOCKS,
            keep_trailing_newline=c.Cli.TEMPLATE_KEEP_TRAILING_NEWLINE,
            autoescape=select_autoescape(),
            auto_reload=False,
        )
        rendered = u.try_(
            lambda: environment.get_template(source.name).render(
                context.model_dump(mode="json")
            ),
            catch=(TemplateError, OSError),
            op_name="template_render_authenticated",
        )
        if rendered.failure:
            return r[m.Cli.AuthenticatedTemplateRender].fail(
                loader.failure
                or rendered.error
                or f"{c.Cli.ERR_TEMPLATE_RENDER_FAILED}: {source}"
            )
        return r[m.Cli.AuthenticatedTemplateRender].ok(
            m.Cli.AuthenticatedTemplateRender(
                rendered=rendered.value,
                source_states=tuple(loader.source_states.values()),
            )
        )

    @staticmethod
    def template_render_to(path: Path, dest: Path, context: p.Model) -> p.Result[bool]:
        """Render ``path`` with ``context`` and write it to ``dest`` → ``r[bool]``."""
        rendered = FlextCliUtilitiesTemplate.template_render(path, context)
        if rendered.failure:
            return r[bool].from_failure(rendered)
        return u.try_(
            lambda: FlextCliUtilitiesTemplate._write(dest, rendered.value),
            catch=OSError,
            op_name="template_render_to",
        )

    @staticmethod
    def template_render_dir(
        templates_root: Path,
        output_root: Path,
        context: p.Model,
        entries: t.SequenceOf[m.Cli.TemplateRenderEntry],
        *,
        strip_suffix: str = c.Cli.TEMPLATE_SUFFIX,
        overwrite: bool = False,
    ) -> p.Result[m.Cli.TemplateRenderReport]:
        """Render every entry from ``templates_root`` into ``output_root``.

        Generic, folder-parameterized engine (ADR-005): the caller supplies the
        templates folder, an ordered list of entries (data), and a context; the
        engine mirrors the tree, strips the template suffix, and reports
        created/skipped/failed per entry. It carries no FLEXT naming policy —
        output paths and context are fully resolved by the caller.

        Fail-closed on a missing templates root. Per-entry render failures and
        path-escape attempts are accumulated in ``TemplateRenderReport.failed``;
        the caller decides the fail policy (the report is always returned).
        """
        if not templates_root.is_dir():
            return r[m.Cli.TemplateRenderReport].fail(
                f"{c.Cli.ERR_TEMPLATE_NOT_FOUND}: {templates_root}"
            )
        root = output_root.resolve()
        created: list[Path] = []
        skipped: list[Path] = []
        failed: list[tuple[Path, str]] = []
        for entry in entries:
            out_rel = entry.output_relpath
            if strip_suffix and str(out_rel).endswith(strip_suffix):
                out_rel = Path(str(out_rel)[: -len(strip_suffix)])
            dest = output_root / out_rel
            try:
                if not dest.resolve().is_relative_to(root):
                    failed.append((dest, c.Cli.ERR_TEMPLATE_OUTPUT_ESCAPE))
                    continue
            except (OSError, ValueError):
                failed.append((dest, c.Cli.ERR_TEMPLATE_OUTPUT_ESCAPE))
                continue
            if not entry.when:
                skipped.append(dest)
                continue
            if dest.exists() and not (entry.overwrite or overwrite):
                skipped.append(dest)
                continue
            src = templates_root / entry.relpath_template
            result = FlextCliUtilitiesTemplate.template_render_to(src, dest, context)
            if result.failure:
                failed.append((dest, result.error or c.Cli.ERR_TEMPLATE_RENDER_FAILED))
                continue
            created.append(dest)
        report = m.Cli.TemplateRenderReport(
            created=tuple(created), skipped=tuple(skipped), failed=tuple(failed)
        )
        return r[m.Cli.TemplateRenderReport].ok(report)

    @staticmethod
    def _write(dest: Path, content: str) -> bool:
        """Write ``content`` to ``dest``, creating parents; return ``True``."""
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(content, encoding=c.Cli.ENCODING_DEFAULT)
        return True


__all__: t.MutableSequenceOf[str] = ["FlextCliUtilitiesTemplate"]
