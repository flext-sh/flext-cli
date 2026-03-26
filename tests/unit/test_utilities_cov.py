"""Tests for CLI Utilities."""

from __future__ import annotations

from flext_tests import tm

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
    tm.that((collect_result.error or ""), has="[1]")
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
    tm.that((collect_result.error or ""), has="bad")


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
    tm.that((result.error or ""), has="no validation criteria")
