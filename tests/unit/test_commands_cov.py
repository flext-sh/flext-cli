from __future__ import annotations

from collections.abc import Sequence

from flext_core import r

from flext_cli.commands import FlextCliCommands


def test_name_and_description_properties_are_returned() -> None:
    commands = FlextCliCommands(name="demo", description="Demo CLI")

    assert commands.name == "demo"
    assert commands.description == "Demo CLI"


def test_register_command_rejects_blank_name() -> None:
    commands = FlextCliCommands()

    result = commands.register_command("   ", lambda: "ok")

    assert result.is_failure
    assert "non-empty" in (result.error or "")


def test_execute_command_rejects_invalid_name_input() -> None:
    commands = FlextCliCommands()

    result = commands.execute_command("")

    assert result.is_failure
    assert "Invalid command name" in (result.error or "")


def test_execute_command_returns_default_success_when_handler_returns_none() -> None:
    commands = FlextCliCommands()

    def handler(*_args: Sequence[str], **_kwargs: object) -> None:
        return None

    commands.register_command("noop", handler)
    result = commands.execute_command("noop")

    assert result.is_success
    assert result.value == {"status": "success", "command": "noop"}


def test_execute_command_propagates_failure_from_flext_result() -> None:
    commands = FlextCliCommands()

    def failing_handler() -> r[str]:
        return r[str].fail("boom")

    commands.register_command("fail", failing_handler)
    result = commands.execute_command("fail")

    assert result.is_failure
    assert result.error == "boom"


def test_run_cli_version_option_returns_name() -> None:
    commands = FlextCliCommands(name="my-cli")

    result = commands.run_cli(["--version"])

    assert result.is_success
    assert result.value == {"status": "version", "name": "my-cli"}


def test_create_command_group_rejects_blank_name() -> None:
    commands = FlextCliCommands()

    result = commands.create_command_group("", commands={"x": {"handler": lambda: 1}})

    assert result.is_failure
    assert "non-empty" in (result.error or "")
