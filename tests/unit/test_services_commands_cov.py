"""Coverage tests for services/commands.py.

Targets: create, execute, execute_command, register_handler, list_commands,
         run_cli.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli import FlextCli
from tests import c, p, r, t


class TestsFlextCliServicesCommandsCov:
    """Data-driven coverage tests for public command-registry behavior."""

    @staticmethod
    def _ok_payload(**payload: t.JsonValue) -> p.Result[t.JsonPayload]:
        return r[t.JsonPayload].ok(payload)

    @staticmethod
    def _fail_payload(error: str = "") -> p.Result[t.JsonPayload]:
        return r[t.JsonPayload].fail(error)

    # ── create ────────────────────────────────────────────────────────

    def test_create_sets_name(self) -> None:
        svc = FlextCli.create(name="my-app")
        assert svc.name == "my-app"

    def test_create_with_description(self) -> None:
        svc = FlextCli.create(name="app", description="My App CLI")
        assert svc.name == "app"

    # ── execute ───────────────────────────────────────────────────────

    def test_execute_returns_status(self) -> None:
        svc = FlextCli.create(name="app")
        result = svc.execute()
        assert result.success
        assert result.value[c.Cli.DICT_KEY_STATUS] == c.Cli.ServiceStatus.OPERATIONAL
        assert result.value[c.Cli.DICT_KEY_SERVICE] == c.Cli.CMD_SERVICE_NAME

    # ── register_handler ──────────────────────────────────────────────

    def test_register_handler_valid(self) -> None:
        svc = FlextCli.create(name="app")
        result = svc.register_handler("run", lambda: self._ok_payload(status="ok"))
        assert result.success

    def test_register_handler_empty_name(self) -> None:
        svc = FlextCli.create(name="app")
        result = svc.register_handler("", lambda: self._fail_payload())
        assert result.failure

    def test_register_handler_whitespace_name(self) -> None:
        svc = FlextCli.create(name="app")
        result = svc.register_handler("   ", lambda: self._fail_payload())
        assert result.failure

    # ── execute_command ───────────────────────────────────────────────

    def test_execute_command_registered(self) -> None:
        svc = FlextCli.create(name="app")
        svc.register_handler("do-thing", lambda: self._ok_payload(done=True))
        result = svc.execute_command("do-thing")
        assert result.success

    def test_execute_command_not_found(self) -> None:
        svc = FlextCli.create(name="app")
        result = svc.execute_command("nonexistent")
        assert result.failure

    def test_execute_command_empty_name(self) -> None:
        svc = FlextCli.create(name="app")
        result = svc.execute_command("")
        assert result.failure

    def test_execute_command_whitespace_name(self) -> None:
        svc = FlextCli.create(name="app")
        result = svc.execute_command("   ")
        assert result.failure

    def test_execute_command_with_kwargs(self) -> None:
        svc = FlextCli.create(name="app")

        def greet(greet_name: str = "world") -> p.Result[t.JsonPayload]:
            return self._ok_payload(msg=f"hello {greet_name}")

        svc.register_handler("greet", greet)
        result = svc.execute_command("greet", greet_name="test")
        assert result.success

    def test_execute_command_with_args(self) -> None:
        svc = FlextCli.create(name="app")

        def echo(value: t.JsonValue) -> p.Result[t.JsonPayload]:
            return self._ok_payload(echo=value)

        svc.register_handler("echo", echo)
        result = svc.execute_command("echo", args=["hello"])
        assert result.success

    # ── list_commands ─────────────────────────────────────────────────

    def test_list_commands_empty(self) -> None:
        svc = FlextCli.create(name="app")
        result = svc.list_commands()
        assert result.success
        assert list(result.value) == []

    def test_list_commands_populated(self) -> None:
        svc = FlextCli.create(name="app")
        svc.register_handler("cmd1", lambda: self._ok_payload(cmd=1))
        svc.register_handler("cmd2", lambda: self._ok_payload(cmd=2))
        result = svc.list_commands()
        assert result.success
        assert set(result.value) == {"cmd1", "cmd2"}

    # ── run_cli ───────────────────────────────────────────────────────

    def test_run_cli_no_args(self) -> None:
        svc = FlextCli.create(name="app")
        result = svc.run_cli()
        assert result.success

    def test_run_cli_help_flag(self) -> None:
        svc = FlextCli.create(name="app")
        result = svc.run_cli(["--help"])
        assert result.success

    def test_run_cli_version_flag(self) -> None:
        svc = FlextCli.create(name="myapp")
        result = svc.run_cli(["--version"])
        assert result.success

    def test_run_cli_unknown_command(self) -> None:
        svc = FlextCli.create(name="app")
        result = svc.run_cli(["unknown-cmd"])
        assert result.failure

    def test_run_cli_registered_command(self) -> None:
        svc = FlextCli.create(name="app")
        svc.register_handler("deploy", lambda: self._ok_payload(deployed=True))
        result = svc.run_cli(["deploy"])
        assert result.success


__all__: list[str] = ["TestsFlextCliServicesCommandsCov"]
