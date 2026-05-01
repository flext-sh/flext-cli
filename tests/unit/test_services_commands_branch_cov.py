"""Branch coverage tests for flext_cli.services.commands."""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from flext_cli.services.commands import FlextCliCommands
from flext_core import r
from tests import c, t


@dataclass
class NonCallableEntry:
    """Simple command entry replacement with a non-callable handler."""

    handler: object


class TestsFlextCliServicesCommandsBranchCov:
    """Exercise remaining FlextCliCommands branches."""

    def test_execute_command_non_callable_handler_fails(self) -> None:
        service = FlextCliCommands.create(name="app")
        service._commands["bad"] = NonCallableEntry(handler="not-callable")
        result = service.execute_command("bad")
        assert result.failure
        assert c.Cli.ERR_HANDLER_NOT_CALLABLE.format(name="bad") in (result.error or "")

    def test_execute_command_signature_mismatch_retries_without_args(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        service = FlextCliCommands.create(name="app")
        debug_calls: list[tuple[str, str]] = []

        def handler() -> object:
            return r[t.JsonPayload].ok({"retried": True})

        service.register_handler("retry", handler)
        monkeypatch.setattr(
            service.logger,
            "debug",
            lambda message, command_name, error: debug_calls.append((
                command_name,
                error,
            )),
        )
        result = service.execute_command("retry", args=("arg",))
        assert result.success
        assert result.value == {"retried": True}
        assert debug_calls and debug_calls[0][0] == "retry"

    def test_execute_command_safe_exception_returns_failure(self) -> None:
        service = FlextCliCommands.create(name="app")
        error_message = "explode"

        def handler() -> object:
            raise ValueError(error_message)

        service.register_handler("boom", handler)
        result = service.execute_command("boom")
        assert result.failure
        assert error_message in (result.error or "")


__all__: list[str] = ["TestsFlextCliServicesCommandsBranchCov"]
