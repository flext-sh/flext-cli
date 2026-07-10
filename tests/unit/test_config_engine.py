"""Behavior contract for the ADR-005 flext-cli universal engine.

Covers ``u.Cli.template_render`` (Jinja2, StrictUndefined, sandboxed),
``u.Cli.config_load`` / ``config_load_dir`` (multi-format, reuses core
``u.config_env_override``), and ``u.Cli.schema_validate`` (JSON Schema).
"""

from __future__ import annotations

import os
from pathlib import Path

from tests.constants import c
from tests.models import m
from tests.utilities import u


class TestsFlextCliConfigEngine:
    def test_template_render_ok(self, tmp_path: Path) -> None:
        tpl = tmp_path / "greeting.j2"
        tpl.write_text("port={{ server.port }}\n", encoding="utf-8")
        result = u.Cli.template_render(tpl, {"server": {"port": 8080}})
        assert result.success
        assert result.unwrap() == "port=8080\n"

    def test_template_render_strict_undefined_fails(self, tmp_path: Path) -> None:
        tpl = tmp_path / "greeting.j2"
        tpl.write_text("{{ missing_var }}\n", encoding="utf-8")
        result = u.Cli.template_render(tpl, {})
        assert result.failure

    def test_template_render_missing_source_fails(self, tmp_path: Path) -> None:
        result = u.Cli.template_render(tmp_path / "absent.j2", {})
        assert result.failure
        assert c.Cli.ERR_TEMPLATE_NOT_FOUND in (result.error or "")

    def test_template_render_to_writes(self, tmp_path: Path) -> None:
        tpl = tmp_path / "t.j2"
        tpl.write_text("value={{ x }}", encoding="utf-8")
        dest = tmp_path / "out" / "rendered.txt"
        result = u.Cli.template_render_to(tpl, dest, {"x": 42})
        assert result.success
        assert dest.read_text(encoding="utf-8") == "value=42"

    def test_config_load_yaml_expands_env(self, tmp_path: Path) -> None:
        source = tmp_path / "app.yaml"
        source.write_text("path: ${CFG_ENGINE_HOME}/data\n", encoding="utf-8")
        os.environ["CFG_ENGINE_HOME"] = "/eng"
        try:
            result = u.Cli.config_load(source)
        finally:
            os.environ.pop("CFG_ENGINE_HOME", None)
        assert result.success
        doc = result.unwrap()
        assert isinstance(doc, m.ConfigDocument)
        assert doc.data["path"] == "/eng/data"
        assert doc.source_path == str(source)

    def test_config_load_json_and_toml(self, tmp_path: Path) -> None:
        j = tmp_path / "a.json"
        j.write_text('{"k": 1}', encoding="utf-8")
        t_src = tmp_path / "a.toml"
        t_src.write_text("k = 2\n", encoding="utf-8")
        assert u.Cli.config_load(j).unwrap().data["k"] == 1
        assert u.Cli.config_load(t_src).unwrap().data["k"] == 2

    def test_config_load_unsupported_format_fails(self, tmp_path: Path) -> None:
        bad = tmp_path / "a.ini"
        bad.write_text("k=1", encoding="utf-8")
        result = u.Cli.config_load(bad)
        assert result.failure
        assert c.Cli.ERR_CONFIG_UNSUPPORTED_FORMAT in (result.error or "")

    def test_schema_validate_valid_and_invalid(self, tmp_path: Path) -> None:
        schema = tmp_path / "s.schema.json"
        schema.write_text(
            '{"type":"object","required":["port"],'
            '"properties":{"port":{"type":"integer"}}}',
            encoding="utf-8",
        )
        assert u.Cli.schema_validate({"port": 8080}, schema).success
        assert u.Cli.schema_validate({"port": "x"}, schema).failure

    def test_config_load_with_schema_pairs(self, tmp_path: Path) -> None:
        source = tmp_path / "app.yaml"
        source.write_text("port: 9000\n", encoding="utf-8")
        schema = tmp_path / "app.schema.json"
        schema.write_text('{"type":"object","required":["port"]}', encoding="utf-8")
        ok = u.Cli.config_load(source, schema_path=schema)
        assert ok.success
        assert ok.unwrap().schema_ref == str(schema)

    def test_config_load_dir_auto_pairs_schemas(self, tmp_path: Path) -> None:
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
        assert result.success
        docs = result.unwrap()
        assert set(docs.keys()) == {"agents", "mcp"}
        assert docs["mcp"].schema_ref == str(schemas / "mcp.schema.json")
        assert docs["agents"].schema_ref is None


class TestsFlextCliTemplateRenderDir:
    """Behavior contract for the generic folder engine ``template_render_dir``."""

    def test_render_dir_ok_and_strips_suffix(self, tmp_path: Path) -> None:
        root = tmp_path / "tpl"
        (root / "sub").mkdir(parents=True)
        (root / "a.txt.j2").write_text("A={{ x }}\n", encoding="utf-8")
        (root / "sub" / "b.txt.j2").write_text("B={{ y }}\n", encoding="utf-8")
        out = tmp_path / "out"
        entries = (
            m.Cli.TemplateRenderEntry(
                relpath_template=Path("a.txt.j2"),
                output_relpath=Path("a.txt.j2"),
            ),
            m.Cli.TemplateRenderEntry(
                relpath_template=Path("sub/b.txt.j2"),
                output_relpath=Path("sub/b.txt.j2"),
            ),
        )
        result = u.Cli.template_render_dir(root, out, {"x": 1, "y": 2}, entries)
        assert result.success
        report = result.unwrap()
        assert report.ok
        assert len(report.created) == 2
        assert (out / "a.txt").read_text(encoding="utf-8") == "A=1\n"
        assert (out / "sub" / "b.txt").read_text(encoding="utf-8") == "B=2\n"

    def test_render_dir_when_false_skips(self, tmp_path: Path) -> None:
        root = tmp_path / "tpl"
        root.mkdir()
        (root / "a.j2").write_text("x", encoding="utf-8")
        out = tmp_path / "out"
        entries = (
            m.Cli.TemplateRenderEntry(
                relpath_template=Path("a.j2"),
                output_relpath=Path("a"),
                when=False,
            ),
        )
        report = u.Cli.template_render_dir(root, out, {}, entries).unwrap()
        assert len(report.skipped) == 1
        assert not report.created
        assert not (out / "a").exists()

    def test_render_dir_overwrite_policy(self, tmp_path: Path) -> None:
        root = tmp_path / "tpl"
        root.mkdir()
        (root / "a.j2").write_text("new={{ v }}", encoding="utf-8")
        out = tmp_path / "out"
        out.mkdir()
        (out / "a").write_text("old", encoding="utf-8")
        skip_entries = (
            m.Cli.TemplateRenderEntry(
                relpath_template=Path("a.j2"),
                output_relpath=Path("a"),
            ),
        )
        skipped = u.Cli.template_render_dir(
            root, out, {"v": 1}, skip_entries,
        ).unwrap()
        assert len(skipped.skipped) == 1
        assert (out / "a").read_text(encoding="utf-8") == "old"
        over_entries = (
            m.Cli.TemplateRenderEntry(
                relpath_template=Path("a.j2"),
                output_relpath=Path("a"),
                overwrite=True,
            ),
        )
        created = u.Cli.template_render_dir(
            root, out, {"v": 2}, over_entries,
        ).unwrap()
        assert len(created.created) == 1
        assert (out / "a").read_text(encoding="utf-8") == "new=2"

    def test_render_dir_blocks_escape(self, tmp_path: Path) -> None:
        root = tmp_path / "tpl"
        root.mkdir()
        (root / "a.j2").write_text("x", encoding="utf-8")
        out = tmp_path / "out"
        entries = (
            m.Cli.TemplateRenderEntry(
                relpath_template=Path("a.j2"),
                output_relpath=Path("../escape"),
            ),
        )
        report = u.Cli.template_render_dir(root, out, {}, entries).unwrap()
        assert not report.ok
        assert c.Cli.ERR_TEMPLATE_OUTPUT_ESCAPE in report.failed[0][1]
        assert not (tmp_path / "escape").exists()

    def test_render_dir_missing_root_fails(self, tmp_path: Path) -> None:
        result = u.Cli.template_render_dir(
            tmp_path / "nope", tmp_path / "out", {}, (),
        )
        assert result.failure

    def test_render_dir_collects_render_failures(self, tmp_path: Path) -> None:
        root = tmp_path / "tpl"
        root.mkdir()
        (root / "bad.j2").write_text("{{ missing }}\n", encoding="utf-8")
        out = tmp_path / "out"
        entries = (
            m.Cli.TemplateRenderEntry(
                relpath_template=Path("bad.j2"),
                output_relpath=Path("bad"),
            ),
        )
        report = u.Cli.template_render_dir(root, out, {}, entries).unwrap()
        assert not report.ok
        assert len(report.failed) == 1
