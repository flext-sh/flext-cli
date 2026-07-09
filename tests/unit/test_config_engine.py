"""Behavior contract for the ADR-005 flext-cli universal engine.

Covers ``u.Cli.render_template`` (Jinja2, StrictUndefined, sandboxed),
``u.Cli.config_load`` / ``config_load_dir`` (multi-format, reuses core
``u.config_env_override``), and ``u.Cli.yaml_validate_schema`` (JSON Schema).
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

from tests.constants import c
from tests.models import m
from tests.utilities import u

if TYPE_CHECKING:
    from pathlib import Path


class TestsFlextCliConfigEngine:
    def test_render_template_ok(self, tmp_path: Path) -> None:
        tpl = tmp_path / "greeting.j2"
        tpl.write_text("port={{ server.port }}\n", encoding="utf-8")
        result = u.Cli.render_template(tpl, {"server": {"port": 8080}})
        assert result.success
        assert result.unwrap() == "port=8080\n"

    def test_render_template_strict_undefined_fails(self, tmp_path: Path) -> None:
        tpl = tmp_path / "greeting.j2"
        tpl.write_text("{{ missing_var }}\n", encoding="utf-8")
        result = u.Cli.render_template(tpl, {})
        assert result.failure

    def test_render_template_missing_source_fails(self, tmp_path: Path) -> None:
        result = u.Cli.render_template(tmp_path / "absent.j2", {})
        assert result.failure
        assert c.Cli.ERR_TEMPLATE_NOT_FOUND in (result.error or "")

    def test_render_template_to_writes(self, tmp_path: Path) -> None:
        tpl = tmp_path / "t.j2"
        tpl.write_text("value={{ x }}", encoding="utf-8")
        dest = tmp_path / "out" / "rendered.txt"
        result = u.Cli.render_template_to(tpl, dest, {"x": 42})
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

    def test_yaml_validate_schema_valid_and_invalid(self, tmp_path: Path) -> None:
        schema = tmp_path / "s.schema.json"
        schema.write_text(
            '{"type":"object","required":["port"],'
            '"properties":{"port":{"type":"integer"}}}',
            encoding="utf-8",
        )
        assert u.Cli.yaml_validate_schema({"port": 8080}, schema).success
        assert u.Cli.yaml_validate_schema({"port": "x"}, schema).failure

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
