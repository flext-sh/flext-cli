"""Tests for CLI Utilities."""

from __future__ import annotations

import types
from enum import StrEnum, unique
from typing import Annotated

import pytest
from flext_core import r
from flext_tests import tm
from pydantic import Field

from flext_cli import u


def test_process_fail_and_collect_paths() -> None:
    values = [1, 0]
    fail_result = u.Cli.process(
        values,
        lambda x: (_ for _ in ()).throw(ValueError("div zero")) if x == 0 else 10 // x,
        on_error="fail",
    )
    tm.fail(fail_result)
    collect_result = u.Cli.process(
        values,
        lambda x: (_ for _ in ()).throw(ValueError("div zero")) if x == 0 else 10 // x,
        on_error="collect",
    )
    tm.fail(collect_result)
    tm.that("[1]" in (collect_result.error or ""), eq=True)
    skipped = u.Cli.process(values, lambda x: 10 // x, predicate=lambda x: x != 0)
    tm.ok(skipped)


def test_process_mapping_fail_and_collect_paths() -> None:
    data = {"ok": 2, "bad": 0}
    fail_result = u.Cli.process_mapping(
        data,
        lambda _k, v: (
            (_ for _ in ()).throw(ValueError("div zero")) if v == 0 else 10 // v
        ),
        on_error="fail",
    )
    tm.fail(fail_result)
    collect_result = u.Cli.process_mapping(
        data,
        lambda _k, v: (
            (_ for _ in ()).throw(ValueError("div zero")) if v == 0 else 10 // v
        ),
        on_error="collect",
    )
    tm.fail(collect_result)
    tm.that("bad" in (collect_result.error or ""), eq=True)


def test_validate_required_string_raises_value_error() -> None:
    raised = False
    try:
        u.Cli.validate_required_string("", context="Token")
    except ValueError:
        raised = True
    tm.that(raised, eq=True)


def test_validation_v_uses_custom_message_on_empty_failure() -> None:
    result = u.Cli.CliValidation.v(None, name="x", empty=False, msg="custom")
    tm.fail(result)
    tm.that(result.error, eq="custom")


def test_validation_state_requires_criteria() -> None:
    result = u.Cli.CliValidation.v_state("active")
    tm.fail(result)
    tm.that("no validation criteria" in (result.error or ""), eq=True)


def test_normalize_union_type_returns_none_when_inner_is_none(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    union_type = str | None
    original = u.Cli.TypeNormalizer.normalize_annotation

    def fake(
        annotation: type | types.UnionType | None,
    ) -> type | types.UnionType | None:
        if annotation is str:
            return None
        return original(annotation)

    monkeypatch.setattr(
        u.Cli.TypeNormalizer, "normalize_annotation", staticmethod(fake)
    )
    result = u.Cli.TypeNormalizer.normalize_union_type(union_type)
    tm.that(result is None, eq=True)


def test_normalize_union_type_returns_none_for_empty_normalized_list(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    union_type = str | int
    monkeypatch.setattr(
        u.Cli.TypeNormalizer,
        "normalize_annotation",
        staticmethod(lambda _annotation: None),
    )
    result = u.Cli.TypeNormalizer.normalize_union_type(union_type)
    tm.that(result is None, eq=True)


def test_normalize_union_type_returns_annotation_for_none_only_args(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "flext_cli.utilities.get_args", lambda _annotation: (types.NoneType,)
    )
    union_type = str | int
    result = u.Cli.TypeNormalizer.normalize_union_type(union_type)
    tm.that(result, eq=union_type)


def test_validated_with_result_returns_failure_on_validation_error() -> None:

    @u.Cli.TypeNormalizer.Args.validated_with_result
    def parse_int(value: Annotated[int, Field(gt=0)]) -> r[int]:
        return r[int].ok(value)

    result = parse_int(value=-1)
    tm.fail(result)
    tm.that("validation" in (result.error or "").lower(), eq=True)


def test_parse_kwargs_skips_missing_enum_field_key() -> None:

    @unique
    class Mode(StrEnum):
        FAST = "fast"

    result = u.Cli.TypeNormalizer.Args.parse_kwargs({"other": "x"}, {"mode": Mode})
    tm.ok(result)
    tm.that("other" in result.value, eq=True)
