"""Coverage tests for _utilities/yaml.py using constants-driven parametrize.

Targets: yaml_safe_load, yaml_parse, yaml_load_mapping, yaml_load_list,
         yaml_dump, yaml_dump_str.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from pathlib import Path

import pytest

import flext_cli._utilities.yaml as yaml_module
from flext_cli import u
from tests import c, m, t


class TestsFlextCliYamlCov:
    """Data-driven coverage tests for FlextCliUtilitiesYaml."""

    # ── yaml_parse ──────────────────────────────────────────────────

    @pytest.mark.parametrize(
        ("text", "expect_ok", "expect_empty"),
        c.Tests.YAML_PARSE_CASES,
    )
    def test_yaml_parse_parametrized(
        self, text: str, expect_ok: bool, expect_empty: bool
    ) -> None:
        result = u.Cli.yaml_parse(text)
        assert result.success == expect_ok
        if expect_ok and expect_empty:
            assert result.value == {}
        if expect_ok and not expect_empty:
            assert isinstance(result.value, dict)

    # ── yaml_safe_load ───────────────────────────────────────────────

    def test_yaml_safe_load_valid_file(self, tmp_path: Path) -> None:
        yaml_file = tmp_path / "valid.yml"
        yaml_file.write_text(c.Tests.YAML_VALID_CONTENT, encoding="utf-8")
        result = u.Cli.yaml_safe_load(yaml_file)
        assert result.success
        assert "key" in result.value

    def test_yaml_safe_load_missing_file(self, tmp_path: Path) -> None:
        result = u.Cli.yaml_safe_load(tmp_path / "nonexistent.yml")
        assert result.failure

    def test_yaml_safe_load_invalid_yaml(self, tmp_path: Path) -> None:
        bad_file = tmp_path / "bad.yml"
        bad_file.write_text(c.Tests.YAML_INVALID_CONTENT, encoding="utf-8")
        result = u.Cli.yaml_safe_load(bad_file)
        assert result.failure

    def test_yaml_safe_load_non_mapping(self, tmp_path: Path) -> None:
        list_file = tmp_path / "list.yml"
        list_file.write_text(c.Tests.YAML_NON_MAPPING_CONTENT, encoding="utf-8")
        result = u.Cli.yaml_safe_load(list_file)
        assert result.failure

    def test_yaml_safe_load_empty_file(self, tmp_path: Path) -> None:
        empty_file = tmp_path / "empty.yml"
        empty_file.write_text("", encoding="utf-8")
        result = u.Cli.yaml_safe_load(empty_file)
        assert result.success
        assert result.value == {}

    # ── yaml_load_mapping ────────────────────────────────────────────

    def test_yaml_load_mapping_valid(self, tmp_path: Path) -> None:
        yaml_file = tmp_path / "m.yml"
        yaml_file.write_text(c.Tests.YAML_VALID_CONTENT, encoding="utf-8")
        result = u.Cli.yaml_load_mapping(yaml_file)
        assert isinstance(result, dict)
        assert "key" in result

    def test_yaml_load_mapping_missing_returns_default(self, tmp_path: Path) -> None:
        result = u.Cli.yaml_load_mapping(tmp_path / "missing.yml")
        assert result == {}

    def test_yaml_load_mapping_custom_default(self, tmp_path: Path) -> None:
        default = {"fallback": True}
        result = u.Cli.yaml_load_mapping(tmp_path / "missing.yml", default=default)
        assert result == default

    # ── yaml_load_list ───────────────────────────────────────────────

    @pytest.mark.parametrize(
        ("content", "expect_list"),
        c.Tests.YAML_LIST_CASES,
    )
    def test_yaml_load_list_parametrized(
        self, tmp_path: Path, content: str, expect_list: bool
    ) -> None:
        f = tmp_path / "data.yml"
        if content:
            f.write_text(content, encoding="utf-8")
        else:
            f.write_text("", encoding="utf-8")
        result = u.Cli.yaml_load_list(f)
        if expect_list:
            assert isinstance(result, list)
            assert len(result) > 0
        else:
            assert result == []

    def test_yaml_load_list_missing_file(self, tmp_path: Path) -> None:
        result = u.Cli.yaml_load_list(tmp_path / "nope.yml")
        assert result == []

    def test_yaml_load_list_invalid_yaml(self, tmp_path: Path) -> None:
        bad = tmp_path / "bad.yml"
        bad.write_text(c.Tests.YAML_INVALID_CONTENT, encoding="utf-8")
        result = u.Cli.yaml_load_list(bad)
        assert result == []

    # ── yaml_dump ────────────────────────────────────────────────────

    @pytest.mark.parametrize(
        ("data", "sort_keys", "expect_ok"),
        c.Tests.YAML_DUMP_CASES,
    )
    def test_yaml_dump_parametrized(
        self,
        tmp_path: Path,
        data: t.JsonMapping,
        sort_keys: bool,
        expect_ok: bool,
    ) -> None:
        outfile = tmp_path / "out.yml"
        result = u.Cli.yaml_dump(outfile, data, sort_keys=sort_keys)
        assert result.success == expect_ok
        if expect_ok:
            assert outfile.exists()

    def test_yaml_dump_creates_parent_dirs(self, tmp_path: Path) -> None:
        deep = tmp_path / "a" / "b" / "c" / "out.yml"
        result = u.Cli.yaml_dump(deep, {"x": 1})
        assert result.success
        assert deep.exists()

    def test_yaml_safe_load_read_error(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
        yaml_file = tmp_path / "read_error.yml"
        yaml_file.write_text(c.Tests.YAML_VALID_CONTENT, encoding="utf-8")
        read_error = "cannot read"

        def raise_oserror(self: Path, *, encoding: str) -> str:
            raise OSError(read_error)

        monkeypatch.setattr(yaml_module.Path, "read_text", raise_oserror)
        result = u.Cli.yaml_safe_load(yaml_file)
        assert result.failure
        assert "YAML read error" in (result.error or "")

    def test_yaml_parse_validation_error_branch(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(yaml_module, "safe_load", lambda _text: {"bad": object()})
        result = u.Cli.yaml_parse("bad: value")
        assert result.failure
        assert "YAML validation error" in (result.error or "")

    def test_yaml_load_list_validation_error_branch(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
        yaml_file = tmp_path / "list_validation_error.yml"
        yaml_file.write_text("- item", encoding="utf-8")
        monkeypatch.setattr(yaml_module, "safe_load", lambda _text: [object()])
        assert u.Cli.yaml_load_list(yaml_file) == []

    def test_yaml_dump_write_error_branch(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
        dump_error = TypeError("dump boom")
        monkeypatch.setattr(
            yaml_module,
            "safe_dump",
            lambda *args, **kwargs: (_ for _ in ()).throw(dump_error),
        )
        result = u.Cli.yaml_dump(tmp_path / "out.yml", {"k": "v"})
        assert result.failure
        assert "YAML write error" in (result.error or "")

    # ── yaml_dump_str ────────────────────────────────────────────────

    def test_yaml_dump_str_returns_string(self) -> None:
        text = u.Cli.yaml_dump_str({"hello": "world"})
        assert isinstance(text, str)
        assert "hello" in text

    def test_yaml_dump_str_sorted(self) -> None:
        text = u.Cli.yaml_dump_str({"b": 2, "a": 1}, sort_keys=True)
        assert text.index("a:") < text.index("b:")

    def test_yaml_dump_str_empty_dict(self) -> None:
        text = u.Cli.yaml_dump_str({})
        assert isinstance(text, str)

    def test_yaml_dump_str_pydantic_model(self) -> None:
        model = m.Cli.TableConfig()
        text = u.Cli.yaml_dump_str(model)
        assert isinstance(text, str)

    def test_yaml_dump_str_error_branch(self, monkeypatch: pytest.MonkeyPatch) -> None:
        dump_str_error = TypeError("dump-str boom")
        monkeypatch.setattr(
            yaml_module,
            "safe_dump",
            lambda *args, **kwargs: (_ for _ in ()).throw(dump_str_error),
        )
        text = u.Cli.yaml_dump_str({"k": "v"})
        assert text == ""


__all__: list[str] = ["TestsFlextCliYamlCov"]
