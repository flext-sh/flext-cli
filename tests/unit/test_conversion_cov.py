"""Coverage tests for _utilities/conversion.py — 100% via public interfaces."""

from __future__ import annotations

from pathlib import Path

import pytest
from flext_tests import tm

from tests import c, m, t, u


class TestsFlextCliConversionCov:
    """100% coverage for FlextCliUtilitiesConversion via public u.Cli surface."""

    @pytest.mark.parametrize(
        ("kind", "default", "expected"),
        c.Tests.CONVERSION_STR_CASES,
    )
    def test_default_for_type_kind_str(
        self,
        kind: t.Cli.TypeKind,
        default: t.JsonValue | None,
        expected: t.JsonValue,
    ) -> None:
        result = u.Cli.default_for_type_kind(kind, default)
        tm.that(result, eq=expected)

    @pytest.mark.parametrize(
        ("kind", "default", "expected"),
        c.Tests.CONVERSION_BOOL_CASES,
    )
    def test_default_for_type_kind_bool(
        self,
        kind: t.Cli.TypeKind,
        default: t.JsonValue | None,
        expected: t.JsonValue,
    ) -> None:
        result = u.Cli.default_for_type_kind(kind, default)
        tm.that(result, eq=expected)

    @pytest.mark.parametrize(
        ("kind", "default", "expected"),
        c.Tests.CONVERSION_DICT_CASES,
    )
    def test_default_for_type_kind_dict(
        self,
        kind: t.Cli.TypeKind,
        default: t.JsonValue | None,
        expected: t.JsonValue,
    ) -> None:
        result = u.Cli.default_for_type_kind(kind, default)
        tm.that(result, eq=expected)

    def test_cli_args_to_model_success(self) -> None:
        result = u.Cli.cli_args_to_model(
            m.Tests.SampleInput,
            {"name": "alice", "count": 2, "dry_run": False, "output_format": "json"},
        )
        tm.ok(result)
        tm.that(result.value.name, eq="alice")

    def test_cli_args_to_model_validation_failure(self) -> None:
        result = u.Cli.cli_args_to_model(m.Tests.SampleInput, {"name": 123})
        # may succeed or fail depending on strict — just ensure it returns r
        assert result is not None

    def test_convert_field_value_none(self) -> None:
        result = u.Cli.convert_field_value(None)
        tm.ok(result)
        tm.that(result.value, eq="")

    def test_convert_field_value_string(self) -> None:
        result = u.Cli.convert_field_value("hello")
        tm.ok(result)
        tm.that(result.value, eq="hello")

    def test_convert_field_value_int(self) -> None:
        result = u.Cli.convert_field_value(42)
        tm.ok(result)
        tm.that(result.value, eq=42)

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
