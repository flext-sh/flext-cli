"""Tests for CLI Utilities."""

from __future__ import annotations

import types
from enum import StrEnum

import pytest
from flext_cli import u
from flext_core import r


def test_process_fail_and_collect_paths() -> None:
    values = [1, 0]

    fail_result = u.Cli.process(
        values,
        lambda x: (_ for _ in ()).throw(ValueError("div zero")) if x == 0 else 10 // x,
        on_error="fail",
    )
    assert fail_result.is_failure

    collect_result = u.Cli.process(
        values,
        lambda x: (_ for _ in ()).throw(ValueError("div zero")) if x == 0 else 10 // x,
        on_error="collect",
    )
    assert collect_result.is_failure
    assert "[1]" in (collect_result.error or "")

    skipped = u.Cli.process(values, lambda x: 10 // x, predicate=lambda x: x != 0)
    assert skipped.is_success


def test_process_mapping_fail_and_collect_paths() -> None:
    data = {"ok": 2, "bad": 0}

    fail_result = u.Cli.process_mapping(
        data,
        lambda _k, v: (
            (_ for _ in ()).throw(ValueError("div zero")) if v == 0 else 10 // v
        ),
        on_error="fail",
    )
    assert fail_result.is_failure

    collect_result = u.Cli.process_mapping(
        data,
        lambda _k, v: (
            (_ for _ in ()).throw(ValueError("div zero")) if v == 0 else 10 // v
        ),
        on_error="collect",
    )
    assert collect_result.is_failure
    assert "bad" in (collect_result.error or "")


def test_validate_required_string_raises_value_error() -> None:
    raised = False
    try:
        u.Cli.validate_required_string("", context="Token")
    except ValueError:
        raised = True
    assert raised


def test_validation_v_uses_custom_message_on_empty_failure() -> None:
    result = u.Cli.CliValidation.v(None, name="x", empty=False, msg="custom")

    assert result.is_failure
    assert result.error == "custom"


def test_validation_state_requires_criteria() -> None:
    result = u.Cli.CliValidation.v_state("active")

    assert result.is_failure
    assert "no validation criteria" in (result.error or "")


def test_normalize_union_type_returns_none_when_inner_is_none(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    union_type = str | None
    original = u.TypeNormalizer.normalize_annotation

    def fake(annotation: object) -> type | None:
        if annotation is str:
            return None
        return original(annotation)

    monkeypatch.setattr(u.TypeNormalizer, "normalize_annotation", staticmethod(fake))

    result = u.TypeNormalizer.normalize_union_type(union_type)

    assert result is None


def test_normalize_union_type_returns_none_for_empty_normalized_list(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    union_type = str | int
    monkeypatch.setattr(
        u.TypeNormalizer,
        "normalize_annotation",
        staticmethod(lambda _annotation: None),
    )

    result = u.TypeNormalizer.normalize_union_type(union_type)

    assert result is None


def test_normalize_union_type_returns_annotation_for_none_only_args(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "flext_cli.utilities.get_args",
        lambda _annotation: (types.NoneType,),
    )

    union_type = str | int
    result = u.TypeNormalizer.normalize_union_type(union_type)

    assert result == union_type


def test_validated_with_result_returns_failure_on_validation_error() -> None:
    @u.TypeNormalizer.Args.validated_with_result
    def parse_int(value: int):
        return r.ok(value)

    result = parse_int(value="not-int")

    assert result.is_failure
    assert "validation" in (result.error or "").lower()


def test_parse_kwargs_skips_missing_enum_field_key() -> None:
    class Mode(StrEnum):
        FAST = "fast"

    result = u.TypeNormalizer.Args.parse_kwargs({"other": "x"}, {"mode": Mode})

    assert result.is_success
    assert "other" in result.value
