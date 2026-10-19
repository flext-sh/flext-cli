"""Behavioral tests for the public ``u.Cli`` conversion contract.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from tests import c, m, tm, u

if TYPE_CHECKING:
    from tests import t


class TestsFlextCliConversion:
    """Behavioral contract of ``u.Cli`` conversion helpers."""

    @staticmethod
    @pytest.mark.parametrize(
        ("kind", "value", "default", "expected"),
        [
            (c.Cli.TypeKind.STR, "  name  ", "fallback", "name"),
            (c.Cli.TypeKind.STR, "  ", " fallback ", " fallback "),
            (c.Cli.TypeKind.STR, 0, "fallback", "fallback"),
            (c.Cli.TypeKind.STR, 7, None, "7"),
            (c.Cli.TypeKind.STR, None, 7, ""),
            (c.Cli.TypeKind.BOOL, 1, False, True),
            (c.Cli.TypeKind.BOOL, "false", False, True),
            (c.Cli.TypeKind.BOOL, [], True, False),
            (c.Cli.TypeKind.BOOL, None, 1, False),
            (c.Cli.TypeKind.BOOL, None, True, True),
            (c.Cli.TypeKind.DICT, {"count": 1}, {"fallback": 2}, {"count": 1}),
            (c.Cli.TypeKind.DICT, {}, {"fallback": 2}, {}),
            (c.Cli.TypeKind.DICT, "invalid", {"fallback": 2}, {"fallback": 2}),
            (c.Cli.TypeKind.DICT, None, {"nested": [1, None]}, {"nested": [1, None]}),
            (c.Cli.TypeKind.DICT, None, "invalid", {}),
            (c.Cli.TypeKind.DICT, [], None, {}),
        ],
    )
    def test_resolve_typed_extract_preserves_conversion_semantics(
        kind: t.Cli.TypeKind,
        value: t.JsonValue | None,
        default: t.JsonValue | None,
        expected: t.Cli.TypedExtractValue,
    ) -> None:
        """Conversion and kind-specific defaults belong to the utility surface."""
        tm.that(u.Cli.resolve_typed_extract(kind, value, default), eq=expected)

    @staticmethod
    @pytest.mark.parametrize(
        ("kind", "default", "expected"),
        c.Tests.CONVERSION_STR_CASES,
    )
    def test_default_for_type_kind_str(
        kind: t.Cli.TypeKind,
        default: t.JsonValue | None,
        expected: t.JsonValue,
    ) -> None:
        """Verify that default for type kind str."""
        result = u.Cli.default_for_type_kind(kind, default)
        tm.that(result, eq=expected)

    @staticmethod
    @pytest.mark.parametrize(
        ("kind", "default", "expected"),
        c.Tests.CONVERSION_BOOL_CASES,
    )
    def test_default_for_type_kind_bool(
        kind: t.Cli.TypeKind,
        default: t.JsonValue | None,
        expected: t.JsonValue,
    ) -> None:
        """Verify that default for type kind bool."""
        result = u.Cli.default_for_type_kind(kind, default)
        tm.that(result, eq=expected)

    @staticmethod
    @pytest.mark.parametrize(
        ("kind", "default", "expected"),
        c.Tests.CONVERSION_DICT_CASES,
    )
    def test_default_for_type_kind_dict(
        kind: t.Cli.TypeKind,
        default: t.JsonValue | None,
        expected: t.JsonValue,
    ) -> None:
        """Verify that default for type kind dict."""
        result = u.Cli.default_for_type_kind(kind, default)
        tm.that(result, eq=expected)

    @staticmethod
    def test_cli_args_to_model_success_binds_all_fields() -> None:
        """Verify that cli args to model success binds all fields."""
        result = u.Cli.cli_args_to_model(
            m.Tests.SampleInput,
            {"name": "alice", "count": 2, "dry_run": False, "output_format": "json"},
        )
        model: m.Tests.SampleInput = tm.ok(result)
        tm.that(model.name, eq="alice")
        tm.that(model.count, eq=2)

    @staticmethod
    def test_cli_args_to_model_applies_declared_defaults() -> None:
        """Verify that cli args to model applies declared defaults."""
        result = u.Cli.cli_args_to_model(m.Tests.SampleInput, {"name": "bob"})
        model: m.Tests.SampleInput = tm.ok(result)
        tm.that(model.count, eq=1)
        tm.that(model.dry_run, eq=False)

    @staticmethod
    def test_cli_args_to_model_validation_failure_reports_model() -> None:
        """Verify that cli args to model validation failure reports model."""
        result = u.Cli.cli_args_to_model(m.Tests.SampleInput, {"name": 123})
        error = tm.fail(result)
        tm.that(error, has="SampleInput")

    @staticmethod
    def test_resolve_optional_path_with_path(tmp_path: Path) -> None:
        """Verify that resolve optional path with path."""
        result = u.Cli.resolve_optional_path(tmp_path, default=Path("/fallback"))
        tm.that(result, eq=tmp_path)

    @staticmethod
    def test_resolve_optional_path_with_str(tmp_path: Path) -> None:
        """Verify that resolve optional path with str."""
        result = u.Cli.resolve_optional_path(str(tmp_path), default=Path("/fallback"))
        tm.that(result, eq=tmp_path)

    @staticmethod
    def test_resolve_optional_path_with_empty_str(tmp_path: Path) -> None:
        """Verify that resolve optional path with empty str."""
        result = u.Cli.resolve_optional_path("  ", default=tmp_path)
        tm.that(result, eq=tmp_path)

    @staticmethod
    def test_resolve_optional_path_with_none(tmp_path: Path) -> None:
        """Verify that resolve optional path with none."""
        result = u.Cli.resolve_optional_path(None, default=tmp_path)
        tm.that(result, eq=tmp_path)

    @staticmethod
    def test_normalize_optional_text_path(tmp_path: Path) -> None:
        """Verify that normalize optional text path."""
        result = u.Cli.normalize_optional_text(tmp_path)
        tm.that(result, eq=str(tmp_path))

    @staticmethod
    def test_normalize_optional_text_str() -> None:
        """Verify that normalize optional text str."""
        result = u.Cli.normalize_optional_text("  hello  ")
        tm.that(result, eq="hello")

    @staticmethod
    def test_normalize_optional_text_empty_str() -> None:
        """Verify that normalize optional text empty str."""
        result = u.Cli.normalize_optional_text("   ")
        tm.that(result, eq=None)

    @staticmethod
    def test_normalize_optional_text_none() -> None:
        """Verify that normalize optional text none."""
        result = u.Cli.normalize_optional_text(None)
        tm.that(result, eq=None)

    @staticmethod
    def test_normalize_optional_text_int() -> None:
        """Verify that normalize optional text int."""
        result = u.Cli.normalize_optional_text(42)
        tm.that(result, eq="42")

    @staticmethod
    def test_normalize_required_text_present() -> None:
        """Verify that normalize required text present."""
        result = u.Cli.normalize_required_text("hello", default="fallback")
        tm.that(result, eq="hello")

    @staticmethod
    def test_normalize_required_text_empty_uses_default() -> None:
        """Verify that normalize required text empty uses default."""
        result = u.Cli.normalize_required_text("  ", default="fallback")
        tm.that(result, eq="fallback")

    @staticmethod
    def test_normalize_required_text_none_uses_default() -> None:
        """Verify that normalize required text none uses default."""
        result = u.Cli.normalize_required_text(None, default="fallback")
        tm.that(result, eq="fallback")
