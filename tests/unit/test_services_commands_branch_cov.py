"""Branch coverage tests for flext_cli.services.commands."""

from __future__ import annotations

from flext_cli import cli
from tests import p, r, t


class TestsFlextCliServicesCommandsBranchCov:
    """Exercise public failure branches for command execution."""

    def test_execute_command_signature_mismatch_fails(self) -> None:
        service = cli.create(name="app")

        def handler() -> p.Result[t.JsonPayload]:
            return r[t.JsonPayload].ok({"retried": True})

        service.register_handler("retry", handler)
        result = service.execute_command("retry", args=("arg",))
        assert result.failure
        assert "takes 0 positional arguments but 1 was given" in (result.error or "")

    def test_execute_command_safe_exception_returns_failure(self) -> None:
        service = cli.create(name="app")
        error_message = "explode"

        def handler() -> p.Result[t.JsonPayload]:
            raise ValueError(error_message)

        service.register_handler("boom", handler)
        result = service.execute_command("boom")
        assert result.failure
        assert error_message in (result.error or "")


__all__: list[str] = ["TestsFlextCliServicesCommandsBranchCov"]
