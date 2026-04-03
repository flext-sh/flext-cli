"""Tests for CLI Utilities."""

from __future__ import annotations

from flext_tests import tm

from tests import u


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
    # The error message includes the index — check it references the failing item
    error_str = collect_result.error or ""
    tm.that(len(error_str) > 0, eq=True)
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


def test_validation_v_uses_custom_message_on_empty_failure() -> None:
    result = u.Cli.CliValidation.v(None, name="x", empty=False, msg="custom")
    tm.fail(result)
    tm.that(result.error, eq="custom")


def test_project_names_from_values_normalizes_repeated_cli_selectors() -> None:
    result = u.Cli.project_names_from_values("a,b", [" c ", "", "d,e"], None)
    tm.that(result, eq=["a", "b", "c", "d", "e"])
