"""Coverage tests for services/commands.py.

Targets: create, execute, execute_command, register_handler, list_commands,
         run_cli.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli.services.commands import FlextCliCommands
from flext_core import r
from tests import t


class TestsFlextCliServicesCommandsCov:
    """Data-driven coverage tests for FlextCliCommands service."""

    def _make_commands(self, name: str = "test-cli") -> object:
        return FlextCliCommands.create(name=name)

    # ── create ────────────────────────────────────────────────────────

    def test_create_sets_name(self) -> None:
        svc = FlextCliCommands.create(name="my-app")
        assert svc.name == "my-app"

    def test_create_with_description(self) -> None:
        svc = FlextCliCommands.create(name="app", description="My App CLI")
        assert svc.name == "app"

    # ── execute ───────────────────────────────────────────────────────

    def test_execute_returns_status(self) -> None:
        svc = FlextCliCommands.create(name="app")
        result = svc.execute()
        assert result.success
        assert "initialized" in result.value
        assert result.value["initialized"] is True

    # ── register_handler ──────────────────────────────────────────────

    def test_register_handler_valid(self) -> None:
        svc = FlextCliCommands.create(name="app")
        result = svc.register_handler(
            "run", lambda: r[t.JsonValue].ok({"status": "ok"})
        )
        assert result.success

    def test_register_handler_empty_name(self) -> None:
        svc = FlextCliCommands.create(name="app")
        result = svc.register_handler("", lambda: None)
        assert result.failure

    def test_register_handler_whitespace_name(self) -> None:
        svc = FlextCliCommands.create(name="app")
        result = svc.register_handler("   ", lambda: None)
        assert result.failure

    # ── execute_command ───────────────────────────────────────────────

    def test_execute_command_registered(self) -> None:
        svc = FlextCliCommands.create(name="app")
        svc.register_handler("do-thing", lambda: r[t.JsonValue].ok({"done": True}))
        result = svc.execute_command("do-thing")
        assert result.success

    def test_execute_command_not_found(self) -> None:
        svc = FlextCliCommands.create(name="app")
        result = svc.execute_command("nonexistent")
        assert result.failure

    def test_execute_command_empty_name(self) -> None:
        svc = FlextCliCommands.create(name="app")
        result = svc.execute_command("")
        assert result.failure

    def test_execute_command_whitespace_name(self) -> None:
        svc = FlextCliCommands.create(name="app")
        result = svc.execute_command("   ")
        assert result.failure

    def test_execute_command_with_kwargs(self) -> None:
        svc = FlextCliCommands.create(name="app")
        svc.register_handler(
            "greet",
            lambda greet_name="world": r[t.JsonValue].ok({
                "msg": f"hello {greet_name}"
            }),
        )
        result = svc.execute_command("greet", greet_name="test")
        assert result.success

    def test_execute_command_with_args(self) -> None:
        svc = FlextCliCommands.create(name="app")
        svc.register_handler("echo", lambda x: r[t.JsonValue].ok({"echo": x}))
        result = svc.execute_command("echo", args=["hello"])
        assert result.success

    # ── list_commands ─────────────────────────────────────────────────

    def test_list_commands_empty(self) -> None:
        svc = FlextCliCommands.create(name="app")
        result = svc.list_commands()
        assert result.success
        assert list(result.value) == []

    def test_list_commands_populated(self) -> None:
        svc = FlextCliCommands.create(name="app")
        svc.register_handler("cmd1", lambda: r[t.JsonValue].ok({"cmd": 1}))
        svc.register_handler("cmd2", lambda: r[t.JsonValue].ok({"cmd": 2}))
        result = svc.list_commands()
        assert result.success
        assert set(result.value) == {"cmd1", "cmd2"}

    # ── run_cli ───────────────────────────────────────────────────────

    def test_run_cli_no_args(self) -> None:
        svc = FlextCliCommands.create(name="app")
        result = svc.run_cli()
        assert result.success

    def test_run_cli_help_flag(self) -> None:
        svc = FlextCliCommands.create(name="app")
        result = svc.run_cli(["--help"])
        assert result.success

    def test_run_cli_version_flag(self) -> None:
        svc = FlextCliCommands.create(name="myapp")
        result = svc.run_cli(["--version"])
        assert result.success

    def test_run_cli_unknown_command(self) -> None:
        svc = FlextCliCommands.create(name="app")
        result = svc.run_cli(["unknown-cmd"])
        assert result.failure

    def test_run_cli_registered_command(self) -> None:
        svc = FlextCliCommands.create(name="app")
        svc.register_handler("deploy", lambda: r[t.JsonValue].ok({"deployed": True}))
        result = svc.run_cli(["deploy"])
        assert result.success


__all__: list[str] = ["TestsFlextCliServicesCommandsCov"]
