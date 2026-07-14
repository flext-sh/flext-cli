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

from tests import c
from tests import m
from tests import u
from flext_tests import tm

if TYPE_CHECKING:
    from pathlib import Path

    from tests import t


class TestsFlextCliYamlCov:
    """Behavioral contract tests for the ``u.Cli.yaml_*`` helpers."""

    # ── yaml_parse ──────────────────────────────────────────────────

    @pytest.mark.parametrize(("text", "expect_ok"), c.Tests.YAML_PARSE_CASES)
    def test_yaml_parse_reports_outcome_per_input(
        self, text: str, *, expect_ok: bool
    ) -> None:
        """Accept mappings and fail loudly for empty or non-mapping input."""
        result = u.Cli.yaml_parse(text)

        tm.that(result.success, eq=expect_ok)
        if expect_ok:
            tm.that(result.value, empty=False)
        else:
            tm.fail(result)
            tm.that(result.error, empty=False)

    def test_yaml_parse_preserves_nested_mapping_values(self) -> None:
        """Preserve nested mapping values during parsing."""
        result = u.Cli.yaml_parse(c.Tests.YAML_VALID_CONTENT)

        tm.ok(result)
        tm.that(result.unwrap(), eq={"key": "value", "nested": {"foo": "bar"}})

    def test_yaml_parse_top_level_list_is_rejected_as_non_mapping(self) -> None:
        """Reject a top-level sequence when a mapping is required."""
        result = u.Cli.yaml_parse(c.Tests.YAML_NON_MAPPING_CONTENT)

        tm.fail(result)
        tm.that(result.error, none=False)
        tm.that(result.error, has="not a mapping")

    def test_yaml_parse_malformed_yaml_fails_with_parse_error(self) -> None:
        """Report malformed YAML as a parse failure."""
        result = u.Cli.yaml_parse(c.Tests.YAML_INVALID_CONTENT)

        tm.fail(result)
        tm.that(result.error, none=False)
        tm.that(result.error, has="parse error")

    # ── yaml_safe_load ───────────────────────────────────────────────

    def test_yaml_safe_load_returns_parsed_mapping(self, tmp_path: Path) -> None:
        """Load a valid YAML mapping from a file."""
        yaml_file = tmp_path / "valid.yml"
        yaml_file.write_text(c.Tests.YAML_VALID_CONTENT, encoding="utf-8")

        result = u.Cli.yaml_safe_load(yaml_file)

        tm.ok(result)
        tm.that(result.unwrap(), eq={"key": "value", "nested": {"foo": "bar"}})

    def test_yaml_safe_load_missing_file_reports_not_found(
        self, tmp_path: Path
    ) -> None:
        """Report a missing YAML file with its path."""
        missing = tmp_path / "nonexistent.yml"

        result = u.Cli.yaml_safe_load(missing)

        tm.fail(result)
        tm.that(result.error, none=False)
        tm.that(result.error, has="not found")
        tm.that(result.error, has=str(missing))

    def test_yaml_safe_load_invalid_yaml_fails(self, tmp_path: Path) -> None:
        """Fail when a YAML file contains malformed content."""
        bad_file = tmp_path / "bad.yml"
        bad_file.write_text(c.Tests.YAML_INVALID_CONTENT, encoding="utf-8")

        result = u.Cli.yaml_safe_load(bad_file)

        tm.fail(result)
        tm.that(result.error, none=False)
        tm.that(result.error, has="parse error")

    def test_yaml_safe_load_non_mapping_file_fails(self, tmp_path: Path) -> None:
        """Fail when a YAML file contains a top-level sequence."""
        list_file = tmp_path / "list.yml"
        list_file.write_text(c.Tests.YAML_NON_MAPPING_CONTENT, encoding="utf-8")

        result = u.Cli.yaml_safe_load(list_file)

        tm.fail(result)
        tm.that(result.error, none=False)
        tm.that(result.error, has="not a mapping")

    def test_yaml_safe_load_empty_file_fails_loudly(self, tmp_path: Path) -> None:
        """Reject an empty YAML file with a descriptive failure."""
        empty_file = tmp_path / "empty.yml"
        empty_file.write_text("", encoding="utf-8")

        result = u.Cli.yaml_safe_load(empty_file)

        tm.fail(result)
        tm.that(result.error, has="empty")

    # ── yaml_load_mapping ────────────────────────────────────────────

    def test_yaml_load_mapping_returns_full_mapping(self, tmp_path: Path) -> None:
        """Return the complete mapping from the compatibility helper."""
        yaml_file = tmp_path / "m.yml"
        yaml_file.write_text(c.Tests.YAML_VALID_CONTENT, encoding="utf-8")

        result = u.Cli.yaml_load_mapping(yaml_file)

        tm.that(result, eq={"key": "value", "nested": {"foo": "bar"}})

    def test_yaml_load_mapping_missing_defaults_to_empty(self, tmp_path: Path) -> None:
        """Expose the current empty default for a missing mapping file."""
        result = u.Cli.yaml_load_mapping(tmp_path / "missing.yml")

        tm.that(result, eq={})

    def test_yaml_load_mapping_missing_uses_provided_default(
        self, tmp_path: Path
    ) -> None:
        """Expose the current explicit default for a missing mapping file."""
        default: t.JsonMapping = {"fallback": True}

        result = u.Cli.yaml_load_mapping(tmp_path / "missing.yml", default=default)

        tm.that(result, eq=default)

    def test_yaml_load_mapping_invalid_yaml_uses_default(self, tmp_path: Path) -> None:
        """Expose the current explicit default for malformed YAML."""
        bad_file = tmp_path / "bad.yml"
        bad_file.write_text(c.Tests.YAML_INVALID_CONTENT, encoding="utf-8")

        result = u.Cli.yaml_load_mapping(bad_file, default={"safe": 1})

        tm.that(result, eq={"safe": 1})

    # ── yaml_load_list ───────────────────────────────────────────────

    @pytest.mark.parametrize(("content", "expect_list"), c.Tests.YAML_LIST_CASES)
    def test_yaml_load_list_returns_list_only_for_sequences(
        self, tmp_path: Path, content: str, *, expect_list: bool
    ) -> None:
        """Return sequence values only for top-level YAML lists."""
        data_file = tmp_path / "data.yml"
        data_file.write_text(content, encoding="utf-8")

        result = u.Cli.yaml_load_list(data_file)

        if expect_list:
            tm.that(list(result), eq=["a", "b", "c"])
        else:
            tm.that(list(result), eq=[])

    def test_yaml_load_list_missing_file_returns_empty(self, tmp_path: Path) -> None:
        """Expose the current empty sequence for a missing list file."""
        result = u.Cli.yaml_load_list(tmp_path / "nope.yml")

        tm.that(list(result), eq=[])

    def test_yaml_load_list_invalid_yaml_returns_empty(self, tmp_path: Path) -> None:
        """Expose the current empty sequence for malformed list YAML."""
        bad_file = tmp_path / "bad.yml"
        bad_file.write_text(c.Tests.YAML_INVALID_CONTENT, encoding="utf-8")

        result = u.Cli.yaml_load_list(bad_file)

        tm.that(list(result), eq=[])

    # ── yaml_dump ────────────────────────────────────────────────────

    @pytest.mark.parametrize(
        ("data", "sort_keys", "expect_ok"), c.Tests.YAML_DUMP_CASES
    )
    def test_yaml_dump_writes_roundtrippable_file(
        self, tmp_path: Path, data: t.JsonMapping, *, sort_keys: bool, expect_ok: bool
    ) -> None:
        """Write a mapping that round-trips through the public loader."""
        outfile = tmp_path / "out.yml"

        result = u.Cli.yaml_dump(outfile, data, sort_keys=sort_keys)

        tm.that(result.success, eq=expect_ok)
        tm.that(result.unwrap(), eq=True)
        # The written file re-parses to exactly the original mapping.
        tm.that(u.Cli.yaml_safe_load(outfile).unwrap(), eq=data)

    def test_yaml_dump_creates_missing_parent_directories(self, tmp_path: Path) -> None:
        """Create missing parent directories before writing YAML."""
        deep = tmp_path / "a" / "b" / "c" / "out.yml"

        result = u.Cli.yaml_dump(deep, {"x": 1})

        tm.ok(result)
        tm.that(u.Cli.yaml_safe_load(deep).unwrap(), eq={"x": 1})

    # ── yaml_dump_str ────────────────────────────────────────────────

    def test_yaml_dump_str_roundtrips_through_parse(self) -> None:
        """Round-trip an in-memory mapping through YAML text."""
        payload: t.JsonMapping = {"hello": "world", "count": 3}

        text = u.Cli.yaml_dump_str(payload)

        tm.that(u.Cli.yaml_parse(text).unwrap(), eq=payload)

    def test_yaml_dump_str_sort_keys_orders_output(self) -> None:
        """Order serialized mapping keys when requested."""
        text = u.Cli.yaml_dump_str({"b": 2, "a": 1}, sort_keys=True)

        tm.that(text.index("a:") < text.index("b:"), eq=True)

    def test_yaml_dump_str_empty_mapping_parses_back_to_empty(self) -> None:
        """Round-trip an empty mapping without changing its value."""
        text = u.Cli.yaml_dump_str({})

        tm.that(u.Cli.yaml_parse(text).unwrap(), eq={})

    def test_yaml_dump_str_serializes_pydantic_model_fields(self) -> None:
        """Serialize the public fields of a Pydantic model."""
        model = m.Cli.TableConfig()

        text = u.Cli.yaml_dump_str(model)

        tm.that(u.Cli.yaml_parse(text).unwrap(), eq=model.model_dump())


__all__: list[str] = ["TestsFlextCliYamlCov"]
