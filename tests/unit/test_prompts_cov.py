"""Focused coverage checks for prompt-side logging behavior."""

from __future__ import annotations

from typing import Self, override

from flext_tests import tm
from pydantic import PrivateAttr

from flext_cli import FlextCliPrompts
from tests import t


class CaptureLogPrompts(FlextCliPrompts):
    """Prompt service that records log calls locally."""

    _records: list[tuple[str, str]] = PrivateAttr(default_factory=list)

    @property
    def records(self) -> list[tuple[str, str]]:
        return self._records

    def use_input_values(self, values: t.StrSequence) -> Self:
        values_iter = iter(values)
        self._input_reader = lambda _prompt: next(values_iter)
        return self

    @override
    def _log(
        self,
        log_level: str,
        message: str,
        **_context: t.ContainerValue,
    ) -> None:
        self._records.append((log_level, message))


class TestsCliPromptsCov:
    """Extra prompt coverage without monkeypatch or mock."""

    def test_prompt_logs_input_when_not_in_test_env(self) -> None:
        prompts = CaptureLogPrompts().use_input_values(["typed"])
        prompts._test_env_override = False
        result = prompts.prompt("message", default="default")
        tm.ok(result)
        tm.that(result.value, eq="typed")
        tm.that(
            prompts.records,
            has=[("info", "User input for 'message': typed")],
        )

    def test_read_confirmation_input_records_warning_before_retrying(self) -> None:
        prompts = CaptureLogPrompts().use_input_values(["maybe", "y"])
        result = prompts._read_confirmation_input("m", "p", default=False)
        tm.ok(result)
        tm.that(result.value, eq=True)
        tm.that(
            prompts.records,
            has=[("warning", "Invalid confirmation input - please enter yes or no")],
        )
