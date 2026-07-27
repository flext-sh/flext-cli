"""Behavior contract for the ADR-005 flext-cli universal engine.

Covers ``u.Cli.template_render`` (Jinja2, StrictUndefined, sandboxed),
``u.Cli.config_load`` / ``config_load_dir`` (multi-format, reuses core
``u.config_env_override``), and ``u.Cli.schema_validate`` (JSON Schema).
"""

from __future__ import annotations

import os
from pathlib import Path

from flext_tests import tm
from tests import c, m, u


class TestsFlextCliConfigEngine:
    """Group the TestsFlextCliConfigEngine test behavior."""

    def test_template_render_ok(self, tmp_path: Path) -> None:
        """Verify that template render ok."""
        tpl = tmp_path / "greeting.j2"
        tpl.write_text("port={{ server.port }}\n", encoding="utf-8")
        server = m.Tests.TemplateServer(port=8080)
        context = m.Tests.TemplateServerContext(server=server)
        result = u.Cli.template_render(tpl, context)
        tm.ok(result)
        tm.that(result.unwrap(), eq="port=8080\n")

    def test_template_render_strict_undefined_fails(self, tmp_path: Path) -> None:
        """Verify that template render strict undefined fails."""
        tpl = tmp_path / "greeting.j2"
        tpl.write_text("{{ missing_var }}\n", encoding="utf-8")
        result = u.Cli.template_render(tpl, m.Tests.TemplateEmpty())
        tm.fail(result)

    def test_template_render_missing_source_fails(self, tmp_path: Path) -> None:
        """Verify that template render missing source fails."""
        result = u.Cli.template_render(tmp_path / "absent.j2", m.Tests.TemplateEmpty())
        tm.fail(result)
        tm.that((result.error or ""), has=c.Cli.ERR_TEMPLATE_NOT_FOUND)

    def test_template_render_to_writes(self, tmp_path: Path) -> None:
        """Verify that template render to writes."""
        tpl = tmp_path / "t.j2"
        tpl.write_text("value={{ value }}", encoding="utf-8")
        dest = tmp_path / "out" / "rendered.txt"
        result = u.Cli.template_render_to(tpl, dest, m.Tests.TemplateValue(value=42))
        tm.ok(result)
        tm.that(dest.read_text(encoding="utf-8"), eq="value=42")

    def test_config_load_yaml_expands_env(self, tmp_path: Path) -> None:
        """Verify that config load yaml expands env."""
        source = tmp_path / "app.yaml"
        source.write_text("path: ${CFG_ENGINE_HOME}/data\n", encoding="utf-8")
        os.environ["CFG_ENGINE_HOME"] = "/eng"
        try:
            result = u.Cli.config_load(source)
        finally:
            os.environ.pop("CFG_ENGINE_HOME", None)
        tm.ok(result)
        doc = result.unwrap()
        tm.that(doc, is_=m.ConfigDocument)
        tm.that(doc.data["path"], eq="/eng/data")
        tm.that(doc.source_path, eq=str(source))

    def test_config_load_json_and_toml(self, tmp_path: Path) -> None:
        """Verify that config load json and toml."""
        j = tmp_path / "a.json"
        j.write_text('{"k": 1}', encoding="utf-8")
        t_src = tmp_path / "a.toml"
        t_src.write_text("k = 2\n", encoding="utf-8")
        tm.that(u.Cli.config_load(j).unwrap().data["k"], eq=1)
        tm.that(u.Cli.config_load(t_src).unwrap().data["k"], eq=2)

    def test_config_load_unsupported_format_fails(self, tmp_path: Path) -> None:
        """Verify that config load unsupported format fails."""
        bad = tmp_path / "a.ini"
        bad.write_text("k=1", encoding="utf-8")
        result = u.Cli.config_load(bad)
        tm.fail(result)
        tm.that((result.error or ""), has=c.Cli.ERR_CONFIG_UNSUPPORTED_FORMAT)

    def test_schema_validate_valid_and_invalid(self, tmp_path: Path) -> None:
        """Verify that schema validate valid and invalid."""
        schema = tmp_path / "s.schema.json"
        schema.write_text(
            '{"type":"object","required":["port"],'
            '"properties":{"port":{"type":"integer"}}}',
            encoding="utf-8",
        )
        tm.ok(u.Cli.schema_validate({"port": 8080}, schema))
        tm.fail(u.Cli.schema_validate({"port": "x"}, schema))

    def test_config_load_with_schema_pairs(self, tmp_path: Path) -> None:
        """Verify that config load with schema pairs."""
        source = tmp_path / "app.yaml"
        source.write_text("port: 9000\n", encoding="utf-8")
        schema = tmp_path / "app.schema.json"
        schema.write_text('{"type":"object","required":["port"]}', encoding="utf-8")
        ok = u.Cli.config_load(source, schema_path=schema)
        tm.ok(ok)
        tm.that(ok.unwrap().schema_ref, eq=str(schema))

    def test_config_load_dir_auto_pairs_schemas(self, tmp_path: Path) -> None:
        """Verify that config load dir auto pairs schemas."""
        cfg = tmp_path / "config"
        cfg.mkdir()
        schemas = tmp_path / "schemas"
        schemas.mkdir()
        (cfg / "mcp.yaml").write_text("enabled: true\n", encoding="utf-8")
        (cfg / "agents.yaml").write_text("count: 3\n", encoding="utf-8")
        (schemas / "mcp.schema.json").write_text(
            '{"type":"object","required":["enabled"]}', encoding="utf-8"
        )
        result = u.Cli.config_load_dir(cfg)
        tm.ok(result)
        docs = result.unwrap()
        tm.that(set(docs.keys()), eq={"agents", "mcp"})
        tm.that(docs["mcp"].schema_ref, eq=str(schemas / "mcp.schema.json"))
        tm.that(docs["agents"].schema_ref, none=True)


class TestsFlextCliTemplateRenderDir:
    """Behavior contract for the generic folder engine ``template_render_dir``."""

    def test_render_dir_ok_and_strips_suffix(self, tmp_path: Path) -> None:
        """Verify that render dir ok and strips suffix."""
        root = tmp_path / "tpl"
        (root / "sub").mkdir(parents=True)
        (root / "a.txt.j2").write_text("A={{ value }}\n", encoding="utf-8")
        (root / "sub" / "b.txt.j2").write_text("B={{ value }}\n", encoding="utf-8")
        out = tmp_path / "out"
        entries = (
            m.Cli.TemplateRenderEntry(
                relpath_template=Path("a.txt.j2"), output_relpath=Path("a.txt.j2")
            ),
            m.Cli.TemplateRenderEntry(
                relpath_template=Path("sub/b.txt.j2"),
                output_relpath=Path("sub/b.txt.j2"),
            ),
        )
        result = u.Cli.template_render_dir(
            root, out, m.Tests.TemplateValue(value=1), entries
        )
        tm.ok(result)
        report = result.unwrap()
        tm.that(report.failed, empty=True)
        tm.that(len(report.created), eq=2)
        tm.that((out / "a.txt").read_text(encoding="utf-8"), eq="A=1\n")
        tm.that((out / "sub" / "b.txt").read_text(encoding="utf-8"), eq="B=1\n")

    def test_render_dir_when_false_skips(self, tmp_path: Path) -> None:
        """Verify that render dir when false skips."""
        root = tmp_path / "tpl"
        root.mkdir()
        (root / "a.j2").write_text("x", encoding="utf-8")
        out = tmp_path / "out"
        entries = (
            m.Cli.TemplateRenderEntry(
                relpath_template=Path("a.j2"), output_relpath=Path("a"), when=False
            ),
        )
        report = u.Cli.template_render_dir(
            root, out, m.Tests.TemplateEmpty(), entries
        ).unwrap()
        tm.that(len(report.skipped), eq=1)
        tm.that(report.created, empty=True)
        tm.that((out / "a").exists(), eq=False)

    def test_render_dir_overwrite_policy(self, tmp_path: Path) -> None:
        """Verify that render dir overwrite policy."""
        root = tmp_path / "tpl"
        root.mkdir()
        (root / "a.j2").write_text("new={{ value }}", encoding="utf-8")
        out = tmp_path / "out"
        out.mkdir()
        (out / "a").write_text("old", encoding="utf-8")
        skip_entries = (
            m.Cli.TemplateRenderEntry(
                relpath_template=Path("a.j2"), output_relpath=Path("a")
            ),
        )
        skipped = u.Cli.template_render_dir(
            root, out, m.Tests.TemplateValue(value=1), skip_entries
        ).unwrap()
        tm.that(len(skipped.skipped), eq=1)
        tm.that((out / "a").read_text(encoding="utf-8"), eq="old")
        over_entries = (
            m.Cli.TemplateRenderEntry(
                relpath_template=Path("a.j2"), output_relpath=Path("a"), overwrite=True
            ),
        )
        created = u.Cli.template_render_dir(
            root, out, m.Tests.TemplateValue(value=2), over_entries
        ).unwrap()
        tm.that(len(created.created), eq=1)
        tm.that((out / "a").read_text(encoding="utf-8"), eq="new=2")

    def test_render_dir_blocks_escape(self, tmp_path: Path) -> None:
        """Verify that render dir blocks escape."""
        root = tmp_path / "tpl"
        root.mkdir()
        (root / "a.j2").write_text("x", encoding="utf-8")
        out = tmp_path / "out"
        entries = (
            m.Cli.TemplateRenderEntry(
                relpath_template=Path("a.j2"), output_relpath=Path("../escape")
            ),
        )
        report = u.Cli.template_render_dir(
            root, out, m.Tests.TemplateEmpty(), entries
        ).unwrap()
        tm.that(report.failed, empty=False)
        tm.that(report.failed[0][1], has=c.Cli.ERR_TEMPLATE_OUTPUT_ESCAPE)
        tm.that((tmp_path / "escape").exists(), eq=False)

    def test_render_dir_missing_root_fails(self, tmp_path: Path) -> None:
        """Verify that render dir missing root fails."""
        result = u.Cli.template_render_dir(
            tmp_path / "nope", tmp_path / "out", m.Tests.TemplateEmpty(), ()
        )
        tm.fail(result)

    def test_render_dir_collects_render_failures(self, tmp_path: Path) -> None:
        """Verify that render dir collects render failures."""
        root = tmp_path / "tpl"
        root.mkdir()
        (root / "bad.j2").write_text("{{ missing }}\n", encoding="utf-8")
        out = tmp_path / "out"
        entries = (
            m.Cli.TemplateRenderEntry(
                relpath_template=Path("bad.j2"), output_relpath=Path("bad")
            ),
        )
        report = u.Cli.template_render_dir(
            root, out, m.Tests.TemplateEmpty(), entries
        ).unwrap()
        # NOTE (multi-agent, mro-wkii.17 / agent: make_ssot_audit): assert the
        # public failure payload directly; TemplateRenderReport has no behavior.
        tm.that(report.failed, empty=False)
        tm.that(len(report.failed), eq=1)
