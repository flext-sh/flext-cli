"""Behavioral tests for the public ``u.Cli`` conversion contract."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from flext_tests import tm

from tests import c
from tests import m
from tests import u

if TYPE_CHECKING:
    from tests import t


class TestsFlextCliConversion:
    """Behavioral contract of ``u.Cli`` conversion helpers."""

    @pytest.mark.parametrize(
        ("kind", "default", "expected"), c.Tests.CONVERSION_STR_CASES
    )
    def test_default_for_type_kind_str(
        self, kind: t.Cli.TypeKind, default: t.JsonValue | None, expected: t.JsonValue
    ) -> None:
        result = u.Cli.default_for_type_kind(kind, default)
        tm.that(result, eq=expected)

    @pytest.mark.parametrize(
        ("kind", "default", "expected"), c.Tests.CONVERSION_BOOL_CASES
    )
    def test_default_for_type_kind_bool(
        self, kind: t.Cli.TypeKind, default: t.JsonValue | None, expected: t.JsonValue
    ) -> None:
        result = u.Cli.default_for_type_kind(kind, default)
        tm.that(result, eq=expected)

    @pytest.mark.parametrize(
        ("kind", "default", "expected"), c.Tests.CONVERSION_DICT_CASES
    )
    def test_default_for_type_kind_dict(
        self, kind: t.Cli.TypeKind, default: t.JsonValue | None, expected: t.JsonValue
    ) -> None:
        result = u.Cli.default_for_type_kind(kind, default)
        tm.that(result, eq=expected)

    def test_cli_args_to_model_success_binds_all_fields(self) -> None:
        result = u.Cli.cli_args_to_model(
            m.Tests.SampleInput,
            {"name": "alice", "count": 2, "dry_run": False, "output_format": "json"},
        )
        model = tm.ok(result)
        tm.that(model.name, eq="alice")
        tm.that(model.count, eq=2)

    def test_cli_args_to_model_applies_declared_defaults(self) -> None:
        result = u.Cli.cli_args_to_model(m.Tests.SampleInput, {"name": "bob"})
        model = tm.ok(result)
        tm.that(model.count, eq=1)
        tm.that(model.dry_run, eq=False)

    def test_cli_args_to_model_validation_failure_reports_model(self) -> None:
        result = u.Cli.cli_args_to_model(m.Tests.SampleInput, {"name": 123})
        error = tm.fail(result)
        tm.that(error, has="SampleInput")

    def test_resolve_optional_path_with_path(self, tmp_path: Path) -> None:
        result = u.Cli.resolve_optional_path(tmp_path, default=Path("/fallback"))
        tm.that(result, eq=tmp_path)

    def test_resolve_optional_path_with_str(self, tmp_path: Path) -> None:
        result = u.Cli.resolve_optional_path(str(tmp_path), default=Path("/fallback"))
        tm.that(result, eq=tmp_path)

    def test_resolve_optional_path_with_empty_str(self, tmp_path: Path) -> None:
        result = u.Cli.resolve_optional_path("  ", default=tmp_path)
        tm.that(result, eq=tmp_path)

    def test_resolve_optional_path_with_none(self, tmp_path: Path) -> None:
        result = u.Cli.resolve_optional_path(None, default=tmp_path)
        tm.that(result, eq=tmp_path)

    def test_normalize_optional_text_path(self, tmp_path: Path) -> None:
        result = u.Cli.normalize_optional_text(tmp_path)
        tm.that(result, eq=str(tmp_path))

    def test_normalize_optional_text_str(self) -> None:
        result = u.Cli.normalize_optional_text("  hello  ")
        tm.that(result, eq="hello")

    def test_normalize_optional_text_empty_str(self) -> None:
        result = u.Cli.normalize_optional_text("   ")
        tm.that(result, eq=None)

    def test_normalize_optional_text_none(self) -> None:
        result = u.Cli.normalize_optional_text(None)
        tm.that(result, eq=None)

    def test_normalize_optional_text_int(self) -> None:
        result = u.Cli.normalize_optional_text(42)
        tm.that(result, eq="42")

    def test_normalize_required_text_present(self) -> None:
        result = u.Cli.normalize_required_text("hello", default="fallback")
        tm.that(result, eq="hello")

    def test_normalize_required_text_empty_uses_default(self) -> None:
        result = u.Cli.normalize_required_text("  ", default="fallback")
        tm.that(result, eq="fallback")

    def test_normalize_required_text_none_uses_default(self) -> None:
        result = u.Cli.normalize_required_text(None, default="fallback")
        tm.that(result, eq="fallback")
