"""Behavioral tests for ``u.Cli.yaml_*`` public YAML helpers.

Exercises the observable contract of ``FlextCliUtilitiesYaml`` through the
``u.Cli`` facade only: ``r[T]`` success/failure outcomes, returned values,
error-message semantics, and round-trip idempotence. No private state,
collaborators, or internals are touched.

Covered public API: ``yaml_safe_load``, ``yaml_parse``, ``yaml_load_mapping``,
``yaml_load_list``, ``yaml_dump``, ``yaml_dump_str``.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.constants import c
from tests.models import m
from tests.utilities import u

if TYPE_CHECKING:
    from pathlib import Path

    from tests.typings import t


class TestsFlextCliYamlCov:
    """Behavioral contract tests for the ``u.Cli.yaml_*`` helpers."""

    # ── yaml_parse ──────────────────────────────────────────────────

    @pytest.mark.parametrize(
        ("text", "expect_ok", "expect_empty"),
        c.Tests.YAML_PARSE_CASES,
    )
    def test_yaml_parse_reports_outcome_per_input(
        self,
        text: str,
        expect_ok: bool,
        expect_empty: bool,
    ) -> None:
        result = u.Cli.yaml_parse(text)

        assert result.success == expect_ok
        if expect_ok:
            assert result.value == {} if expect_empty else result.value != {}
        else:
            # Failure carries a descriptive, non-empty error message.
            assert result.error

    def test_yaml_parse_preserves_nested_mapping_values(self) -> None:
        result = u.Cli.yaml_parse(c.Tests.YAML_VALID_CONTENT)

        assert result.success
        assert result.unwrap() == {"key": "value", "nested": {"foo": "bar"}}

    def test_yaml_parse_top_level_list_is_rejected_as_non_mapping(self) -> None:
        result = u.Cli.yaml_parse(c.Tests.YAML_NON_MAPPING_CONTENT)

        assert result.failure
        assert result.error is not None
        assert "not a mapping" in result.error

    def test_yaml_parse_malformed_yaml_fails_with_parse_error(self) -> None:
        result = u.Cli.yaml_parse(c.Tests.YAML_INVALID_CONTENT)

        assert result.failure
        assert result.error is not None
        assert "parse error" in result.error

    # ── yaml_safe_load ───────────────────────────────────────────────

    def test_yaml_safe_load_returns_parsed_mapping(self, tmp_path: Path) -> None:
        yaml_file = tmp_path / "valid.yml"
        yaml_file.write_text(c.Tests.YAML_VALID_CONTENT, encoding="utf-8")

        result = u.Cli.yaml_safe_load(yaml_file)

        assert result.success
        assert result.unwrap() == {"key": "value", "nested": {"foo": "bar"}}

    def test_yaml_safe_load_missing_file_reports_not_found(
        self,
        tmp_path: Path,
    ) -> None:
        missing = tmp_path / "nonexistent.yml"

        result = u.Cli.yaml_safe_load(missing)

        assert result.failure
        assert result.error is not None
        assert "not found" in result.error
        assert str(missing) in result.error

    def test_yaml_safe_load_invalid_yaml_fails(self, tmp_path: Path) -> None:
        bad_file = tmp_path / "bad.yml"
        bad_file.write_text(c.Tests.YAML_INVALID_CONTENT, encoding="utf-8")

        result = u.Cli.yaml_safe_load(bad_file)

        assert result.failure
        assert result.error is not None
        assert "parse error" in result.error

    def test_yaml_safe_load_non_mapping_file_fails(self, tmp_path: Path) -> None:
        list_file = tmp_path / "list.yml"
        list_file.write_text(c.Tests.YAML_NON_MAPPING_CONTENT, encoding="utf-8")

        result = u.Cli.yaml_safe_load(list_file)

        assert result.failure
        assert result.error is not None
        assert "not a mapping" in result.error

    def test_yaml_safe_load_empty_file_yields_empty_mapping(
        self,
        tmp_path: Path,
    ) -> None:
        empty_file = tmp_path / "empty.yml"
        empty_file.write_text("", encoding="utf-8")

        result = u.Cli.yaml_safe_load(empty_file)

        assert result.success
        assert result.unwrap() == {}

    # ── yaml_load_mapping ────────────────────────────────────────────

    def test_yaml_load_mapping_returns_full_mapping(self, tmp_path: Path) -> None:
        yaml_file = tmp_path / "m.yml"
        yaml_file.write_text(c.Tests.YAML_VALID_CONTENT, encoding="utf-8")

        result = u.Cli.yaml_load_mapping(yaml_file)

        assert result == {"key": "value", "nested": {"foo": "bar"}}

    def test_yaml_load_mapping_missing_defaults_to_empty(
        self,
        tmp_path: Path,
    ) -> None:
        result = u.Cli.yaml_load_mapping(tmp_path / "missing.yml")

        assert result == {}

    def test_yaml_load_mapping_missing_uses_provided_default(
        self,
        tmp_path: Path,
    ) -> None:
        default: t.JsonMapping = {"fallback": True}

        result = u.Cli.yaml_load_mapping(tmp_path / "missing.yml", default=default)

        assert result == default

    def test_yaml_load_mapping_invalid_yaml_uses_default(
        self,
        tmp_path: Path,
    ) -> None:
        bad_file = tmp_path / "bad.yml"
        bad_file.write_text(c.Tests.YAML_INVALID_CONTENT, encoding="utf-8")

        result = u.Cli.yaml_load_mapping(bad_file, default={"safe": 1})

        assert result == {"safe": 1}

    # ── yaml_load_list ───────────────────────────────────────────────

    @pytest.mark.parametrize(
        ("content", "expect_list"),
        c.Tests.YAML_LIST_CASES,
    )
    def test_yaml_load_list_returns_list_only_for_sequences(
        self,
        tmp_path: Path,
        content: str,
        expect_list: bool,
    ) -> None:
        data_file = tmp_path / "data.yml"
        data_file.write_text(content, encoding="utf-8")

        result = u.Cli.yaml_load_list(data_file)

        if expect_list:
            assert list(result) == ["a", "b", "c"]
        else:
            assert list(result) == []

    def test_yaml_load_list_missing_file_returns_empty(
        self,
        tmp_path: Path,
    ) -> None:
        result = u.Cli.yaml_load_list(tmp_path / "nope.yml")

        assert list(result) == []

    def test_yaml_load_list_invalid_yaml_returns_empty(
        self,
        tmp_path: Path,
    ) -> None:
        bad_file = tmp_path / "bad.yml"
        bad_file.write_text(c.Tests.YAML_INVALID_CONTENT, encoding="utf-8")

        result = u.Cli.yaml_load_list(bad_file)

        assert list(result) == []

    # ── yaml_dump ────────────────────────────────────────────────────

    @pytest.mark.parametrize(
        ("data", "sort_keys", "expect_ok"),
        c.Tests.YAML_DUMP_CASES,
    )
    def test_yaml_dump_writes_roundtrippable_file(
        self,
        tmp_path: Path,
        data: t.JsonMapping,
        sort_keys: bool,
        expect_ok: bool,
    ) -> None:
        outfile = tmp_path / "out.yml"

        result = u.Cli.yaml_dump(outfile, data, sort_keys=sort_keys)

        assert result.success == expect_ok
        assert result.unwrap() is True
        # The written file re-parses to exactly the original mapping.
        assert u.Cli.yaml_safe_load(outfile).unwrap() == data

    def test_yaml_dump_creates_missing_parent_directories(
        self,
        tmp_path: Path,
    ) -> None:
        deep = tmp_path / "a" / "b" / "c" / "out.yml"

        result = u.Cli.yaml_dump(deep, {"x": 1})

        assert result.success
        assert u.Cli.yaml_safe_load(deep).unwrap() == {"x": 1}

    # ── yaml_dump_str ────────────────────────────────────────────────

    def test_yaml_dump_str_roundtrips_through_parse(self) -> None:
        payload: t.JsonMapping = {"hello": "world", "count": 3}

        text = u.Cli.yaml_dump_str(payload)

        assert u.Cli.yaml_parse(text).unwrap() == payload

    def test_yaml_dump_str_sort_keys_orders_output(self) -> None:
        text = u.Cli.yaml_dump_str({"b": 2, "a": 1}, sort_keys=True)

        assert text.index("a:") < text.index("b:")

    def test_yaml_dump_str_empty_mapping_parses_back_to_empty(self) -> None:
        text = u.Cli.yaml_dump_str({})

        assert u.Cli.yaml_parse(text).unwrap() == {}

    def test_yaml_dump_str_serializes_pydantic_model_fields(self) -> None:
        model = m.Cli.TableConfig()

        text = u.Cli.yaml_dump_str(model)

        assert u.Cli.yaml_parse(text).unwrap() == model.model_dump()


__all__: list[str] = ["TestsFlextCliYamlCov"]
