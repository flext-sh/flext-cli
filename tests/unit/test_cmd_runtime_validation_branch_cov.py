"""Behavioral contract tests for flext_cli ``u.Cli`` cmd/runtime/validation helpers.

Exercises only the public surface exposed through ``u.Cli``: the ``r[T]``
outcome of fallible operations, the public model state they produce, and the
observable contract of environment resolution. No private attributes, no
internal-collaborator spying, no line-coverage pokes.
"""

from __future__ import annotations

from collections.abc import Callable

import pytest

from tests import c
from tests import m
from tests import t
from tests import u
from flext_tests import tm

type MappingProcessor = Callable[[str, int], int]


def _raise_bad(key: str, value: int) -> int:
    """Processor that always raises to drive the error-handling branches."""
    msg = "bad-item"
    raise ValueError(msg)


class TestsFlextCliCmdRuntimeValidationBranchCov:
    """Public-contract behavior of cmd, runtime, and validation helpers."""

    # ----------------------------------------------------------------- cmd
    def test_cmd_settings_snapshot_returns_populated_snapshot_model(self) -> None:
        result = u.Cli.cmd_settings_snapshot()

        tm.ok(result)
        snapshot = result.unwrap()
        tm.that(snapshot, is_=m.Cli.SettingsSnapshot)
        dumped = snapshot.model_dump()
        tm.that(
            set(dumped),
            eq={
                "settings_dir",
                "settings_exists",
                "settings_readable",
                "settings_writable",
                "timestamp",
            },
        )
        tm.that(snapshot.settings_exists, is_=bool)

    def test_cmd_settings_snapshot_is_idempotent_in_shape(self) -> None:
        first = u.Cli.cmd_settings_snapshot()
        second = u.Cli.cmd_settings_snapshot()

        tm.ok(first)
        tm.ok(second)
        tm.that(set(first.unwrap().model_dump()), eq=set(second.unwrap().model_dump()))

    # ------------------------------------------------------------- runtime
    def test_process_env_inherits_and_applies_override(self) -> None:
        env = u.Cli.process_env(overrides={"FLEXT_CLI_TEST_KEY": "present"})

        tm.that(env["FLEXT_CLI_TEST_KEY"], eq="present")

    def test_process_env_removes_inherited_key(self) -> None:
        inherited = u.Cli.process_env()
        present_key = next(iter(inherited))

        pruned = u.Cli.process_env(remove_keys=(present_key,))

        tm.that(pruned, lacks=present_key)

    def test_process_env_removing_unknown_key_is_a_noop(self) -> None:
        baseline = u.Cli.process_env()
        pruned = u.Cli.process_env(remove_keys=("__definitely_missing__",))

        tm.that(pruned, eq=baseline)

    # ---------------------------------------------------------- validation
    def test_process_mapping_maps_every_value_on_success(self) -> None:
        result = u.Cli.process_mapping({"a": 1, "b": 2}, lambda _key, value: value * 10)

        tm.ok(result)
        tm.that(result.unwrap(), eq={"a": 10, "b": 20})

    def test_process_mapping_fail_mode_stops_at_first_error(self) -> None:
        result = u.Cli.process_mapping({"a": 1}, _raise_bad, on_error="fail")

        tm.fail(result)
        tm.that((result.error or ""), has="a")
        tm.that((result.error or ""), has="bad-item")

    def test_process_mapping_collect_mode_aggregates_errors(self) -> None:
        result = u.Cli.process_mapping({"a": 1}, _raise_bad, on_error="collect")

        tm.fail(result)
        tm.that((result.error or ""), has="a: bad-item")

    def test_process_mapping_skip_mode_yields_only_successful_items(self) -> None:
        def raise_on_a(key: str, value: int) -> int:
            if key == "a":
                msg = "boom"
                raise ValueError(msg)
            return value

        result = u.Cli.process_mapping({"a": 1, "b": 2}, raise_on_a, on_error="skip")

        tm.ok(result)
        tm.that(result.unwrap(), eq={"b": 2})

    @pytest.mark.parametrize("output_format", tuple(c.Cli.OUTPUT_FORMATS))
    def test_validate_format_accepts_every_supported_format(
        self, output_format: str
    ) -> None:
        result = u.Cli.validate_format(output_format)

        tm.ok(result)
        tm.that(result.unwrap(), eq=output_format.lower())

    def test_validate_format_normalizes_case_on_success(self) -> None:
        canonical = next(iter(c.Cli.OUTPUT_FORMATS))

        result = u.Cli.validate_format(canonical.upper())

        tm.ok(result)
        tm.that(result.unwrap(), eq=canonical.lower())

    def test_validate_format_rejects_unknown_and_echoes_original_input(self) -> None:
        result = u.Cli.validate_format("BAD")

        tm.fail(result)
        tm.that((result.error or ""), has="BAD")

    @pytest.mark.parametrize("value", ["ok", "  padded  ", 0, 1])
    def test_validate_not_empty_accepts_meaningful_values(
        self, value: t.Cli.CliValue
    ) -> None:
        result = u.Cli.validate_not_empty(value, name="field")

        tm.ok(result)
        tm.that(result.unwrap(), eq=True)

    @pytest.mark.parametrize("value", [None, "", "   "])
    def test_validate_not_empty_rejects_empty_and_names_the_field(
        self, value: t.Cli.CliValue | None
    ) -> None:
        result = u.Cli.validate_not_empty(value, name="myfield")

        tm.fail(result)
        tm.that((result.error or ""), has="myfield")


__all__: list[str] = ["TestsFlextCliCmdRuntimeValidationBranchCov"]
