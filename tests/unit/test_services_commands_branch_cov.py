"""Branch coverage tests for flext_cli.services.commands."""

from __future__ import annotations

from flext_cli.services.commands import FlextCliCommands
from flext_core import r
from tests import c, m, p, t


class TestsFlextCliServicesCommandsBranchCov:
    """Exercise remaining FlextCliCommands branches."""

    def test_execute_command_non_callable_handler_fails(self) -> None:
        service = FlextCliCommands.create(name="app")
        service._commands["bad"] = m.Cli.CommandEntryModel.model_construct(
            name="bad",
            handler="not-callable",
        )
        result = service.execute_command("bad")
        assert result.failure
        assert c.Cli.ERR_HANDLER_NOT_CALLABLE.format(name="bad") in (result.error or "")

    def test_execute_command_signature_mismatch_fails(self) -> None:
        service = FlextCliCommands.create(name="app")

        def handler() -> p.Result[t.JsonPayload]:
            return r[t.JsonPayload].ok({"retried": True})

        service.register_handler("retry", handler)
        result = service.execute_command("retry", args=("arg",))
        assert result.failure
        assert "takes 0 positional arguments but 1 was given" in (result.error or "")

    def test_execute_command_safe_exception_returns_failure(self) -> None:
        service = FlextCliCommands.create(name="app")
        error_message = "explode"

        def handler() -> p.Result[t.JsonPayload]:
            raise ValueError(error_message)

        service.register_handler("boom", handler)
        result = service.execute_command("boom")
        assert result.failure
        assert error_message in (result.error or "")


__all__: list[str] = ["TestsFlextCliServicesCommandsBranchCov"]
