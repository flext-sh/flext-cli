"""Behavioral contract tests for flext_cli ``u.Cli`` cmd/runtime/validation helpers.

Exercises only the public surface exposed through ``u.Cli``: the ``r[T]``
outcome of fallible operations, the public model state they produce, and the
observable contract of environment resolution. No private attributes, no
internal-collaborator spying, no line-coverage pokes.
"""

from __future__ import annotations

from collections.abc import Callable

import pytest

from tests.constants import c
from tests.models import m
from tests.typings import t
from tests.utilities import u

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

        assert result.success
        snapshot = result.unwrap()
        assert isinstance(snapshot, m.Cli.SettingsSnapshot)
        dumped = snapshot.model_dump()
        assert set(dumped) == {
            "settings_dir",
            "settings_exists",
            "settings_readable",
            "settings_writable",
            "timestamp",
        }
        assert isinstance(snapshot.settings_exists, bool)

    def test_cmd_settings_snapshot_is_idempotent_in_shape(self) -> None:
        first = u.Cli.cmd_settings_snapshot()
        second = u.Cli.cmd_settings_snapshot()

        assert first.success
        assert second.success
        assert set(first.unwrap().model_dump()) == set(second.unwrap().model_dump())

    # ------------------------------------------------------------- runtime
    def test_process_env_inherits_and_applies_override(self) -> None:
        env = u.Cli.process_env(overrides={"FLEXT_CLI_TEST_KEY": "present"})

        assert env["FLEXT_CLI_TEST_KEY"] == "present"

    def test_process_env_removes_inherited_key(self) -> None:
        inherited = u.Cli.process_env()
        present_key = next(iter(inherited))

        pruned = u.Cli.process_env(remove_keys=(present_key,))

        assert present_key not in pruned

    def test_process_env_removing_unknown_key_is_a_noop(self) -> None:
        baseline = u.Cli.process_env()
        pruned = u.Cli.process_env(remove_keys=("__definitely_missing__",))

        assert pruned == baseline

    # ---------------------------------------------------------- validation
    def test_process_mapping_maps_every_value_on_success(self) -> None:
        result = u.Cli.process_mapping(
            {"a": 1, "b": 2},
            lambda _key, value: value * 10,
        )

        assert result.success
        assert result.unwrap() == {"a": 10, "b": 20}

    def test_process_mapping_fail_mode_stops_at_first_error(self) -> None:
        result = u.Cli.process_mapping({"a": 1}, _raise_bad, on_error="fail")

        assert result.failure
        assert "a" in (result.error or "")
        assert "bad-item" in (result.error or "")

    def test_process_mapping_collect_mode_aggregates_errors(self) -> None:
        result = u.Cli.process_mapping({"a": 1}, _raise_bad, on_error="collect")

        assert result.failure
        assert "a: bad-item" in (result.error or "")

    def test_process_mapping_skip_mode_yields_only_successful_items(self) -> None:
        def raise_on_a(key: str, value: int) -> int:
            if key == "a":
                msg = "boom"
                raise ValueError(msg)
            return value

        result = u.Cli.process_mapping({"a": 1, "b": 2}, raise_on_a, on_error="skip")

        assert result.success
        assert result.unwrap() == {"b": 2}

    @pytest.mark.parametrize("output_format", tuple(c.Cli.OUTPUT_FORMATS))
    def test_validate_format_accepts_every_supported_format(
        self,
        output_format: str,
    ) -> None:
        result = u.Cli.validate_format(output_format)

        assert result.success
        assert result.unwrap() == output_format.lower()

    def test_validate_format_normalizes_case_on_success(self) -> None:
        canonical = next(iter(c.Cli.OUTPUT_FORMATS))

        result = u.Cli.validate_format(canonical.upper())

        assert result.success
        assert result.unwrap() == canonical.lower()

    def test_validate_format_rejects_unknown_and_echoes_original_input(self) -> None:
        result = u.Cli.validate_format("BAD")

        assert result.failure
        assert "BAD" in (result.error or "")

    @pytest.mark.parametrize("value", ["ok", "  padded  ", 0, 1])
    def test_validate_not_empty_accepts_meaningful_values(
        self,
        value: t.Cli.CliValue,
    ) -> None:
        result = u.Cli.validate_not_empty(value, name="field")

        assert result.success
        assert result.unwrap() is True

    @pytest.mark.parametrize("value", [None, "", "   "])
    def test_validate_not_empty_rejects_empty_and_names_the_field(
        self,
        value: t.Cli.CliValue | None,
    ) -> None:
        result = u.Cli.validate_not_empty(value, name="myfield")

        assert result.failure
        assert "myfield" in (result.error or "")


__all__: list[str] = ["TestsFlextCliCmdRuntimeValidationBranchCov"]
