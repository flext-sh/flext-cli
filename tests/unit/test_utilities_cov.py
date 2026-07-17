"""Behavioral tests for the CLI utilities public contract (``u`` / ``u.Cli``).

Exercises only the observable contract of the utility helpers:
- ``u.process`` — item processing with predicate filtering and error policy.
- ``u.Cli.process_mapping`` — keyed processing with fail/collect/skip policy.
- ``u.Cli.validate_not_empty`` — emptiness validation returning ``r[bool]``.
- ``u.Cli.project_names_from_values`` / ``project_numbers_from_values`` —
  CLI selector normalization.
"""

from __future__ import annotations

import pytest
from flext_tests import tm

from tests import t
from tests import u


def _raise_on_zero(value: int) -> int:
    """Processor that divides 10 by ``value`` and raises on zero."""
    if value == 0:
        msg = "div zero"
        raise ValueError(msg)
    return 10 // value


def _raise_on_zero_kv(_key: str, value: int) -> int:
    """Delegate key/value arguments to :func:`_raise_on_zero`."""
    return _raise_on_zero(value)


class TestsFlextCliUtilitiesCov:
    """Behavioral contract for CLI utility helpers."""

    def test_process_returns_mapped_values_on_success(self) -> None:
        """Verify that process returns mapped values on success."""
        result = u.process([1, 2, 5], _raise_on_zero)
        tm.ok(result)
        tm.that(list(result.unwrap()), eq=[10, 5, 2])

    def test_process_fails_when_processor_raises(self) -> None:
        """Verify that process fails when processor raises."""
        result = u.process([1, 0], _raise_on_zero, on_error="fail")
        tm.fail(result)
        tm.that(result.error or "", has="0")

    def test_process_skip_policy_drops_failing_items(self) -> None:
        """Verify that process skip policy drops failing items."""
        result = u.process([1, 0, 5], _raise_on_zero, on_error="skip")
        tm.ok(result)
        tm.that(list(result.unwrap()), eq=[10, 2])

    def test_process_predicate_excludes_items_before_processing(self) -> None:
        """Verify that process predicate excludes items before processing."""
        result = u.process([1, 0, 5], _raise_on_zero, predicate=lambda x: x != 0)
        tm.ok(result)
        tm.that(list(result.unwrap()), eq=[10, 2])

    def test_process_mapping_returns_mapped_values_on_success(self) -> None:
        """Verify that process mapping returns mapped values on success."""
        result = u.Cli.process_mapping({"a": 2, "b": 5}, _raise_on_zero_kv)
        tm.ok(result)
        tm.that(result.unwrap(), eq={"a": 5, "b": 2})

    def test_process_mapping_fail_policy_reports_offending_key(self) -> None:
        """Verify that process mapping fail policy reports offending key."""
        result = u.Cli.process_mapping(
            {"ok": 2, "bad": 0}, _raise_on_zero_kv, on_error="fail"
        )
        tm.fail(result)
        tm.that(result.error or "", has="bad")

    def test_process_mapping_collect_policy_reports_offending_key(self) -> None:
        """Verify that process mapping collect policy reports offending key."""
        result = u.Cli.process_mapping(
            {"ok": 2, "bad": 0}, _raise_on_zero_kv, on_error="collect"
        )
        tm.fail(result)
        tm.that(result.error or "", has="bad")

    def test_process_mapping_skip_policy_keeps_only_successes(self) -> None:
        """Verify that process mapping skip policy keeps only successes."""
        result = u.Cli.process_mapping(
            {"ok": 2, "bad": 0}, _raise_on_zero_kv, on_error="skip"
        )
        tm.ok(result)
        tm.that(result.unwrap(), eq={"ok": 5})

    @pytest.mark.parametrize("value", [None, "", "   "])
    def test_validate_not_empty_fails_for_empty_inputs(self, value: str | None) -> None:
        """Verify that validate not empty fails for empty inputs."""
        result = u.Cli.validate_not_empty(value, name="project")
        tm.fail(result)
        tm.that(result.error or "", has="project")

    @pytest.mark.parametrize("value", ["name", " padded ", 0, 42])
    def test_validate_not_empty_succeeds_for_present_values(
        self, value: t.Cli.Value
    ) -> None:
        """Verify that validate not empty succeeds for present values."""
        result = u.Cli.validate_not_empty(value, name="project")
        tm.ok(result)
        tm.that(result.unwrap(), eq=True)

    def test_project_names_flattens_repeated_and_comma_selectors(self) -> None:
        """Verify that project names flattens repeated and comma selectors."""
        result = u.Cli.project_names_from_values("a,b", [" c ", "", "d,e"], None)
        tm.that(result, eq=["a", "b", "c", "d", "e"])

    def test_project_names_returns_none_when_no_selectors(self) -> None:
        """Verify that project names returns none when no selectors."""
        tm.that(u.Cli.project_names_from_values(None), eq=None)
        tm.that(u.Cli.project_names_from_values("   "), eq=None)

    def test_project_numbers_flattens_and_converts_to_int(self) -> None:
        """Verify that project numbers flattens and converts to int."""
        result = u.Cli.project_numbers_from_values("1,2", [" 3 ", "", "4,5"], None)
        tm.that(result, eq=[1, 2, 3, 4, 5])

    def test_project_numbers_uses_default_when_no_selectors(self) -> None:
        """Verify that project numbers uses default when no selectors."""
        result = u.Cli.project_numbers_from_values(None, default=(7, 8))
        tm.that(result, eq=[7, 8])

    def test_project_numbers_returns_none_without_selectors_or_default(self) -> None:
        """Verify that project numbers returns none without selectors or default."""
        tm.that(u.Cli.project_numbers_from_values(None), eq=None)


__all__: list[str] = ["TestsFlextCliUtilitiesCov"]
