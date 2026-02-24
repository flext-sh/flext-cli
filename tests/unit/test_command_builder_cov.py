from __future__ import annotations

import pytest
from typer.models import OptionInfo

from flext_cli.command_builder import FlextCliCommandBuilder as FlextCommandBuilder


def test_builder_collects_options_arguments_groups_and_middleware() -> None:
    builder = FlextCommandBuilder("sync")

    group_option = OptionInfo(default=None, param_decls=["--x"])

    result = (
        builder
        .with_option("--host/-h", default="localhost", help_="host")
        .with_option_group([group_option])
        .with_argument("name", str, required=True)
        .with_middleware(lambda _ctx: None)
        .handler(lambda *_args, **_kwargs: None)
        .build()
    )

    assert result.name == "sync"
    assert builder._arguments[0] == ("name", str, True)
    assert len(builder._options) == 2
    assert len(builder._middleware) == 1


def test_create_option_info_sets_additional_kwargs() -> None:
    info = FlextCommandBuilder._create_option_info(
        default=False,
        param_decls=["--flag"],
        help_text="flag",
        hidden=True,
    )

    assert isinstance(info, OptionInfo)
    assert info.default is False
    assert info.param_decls == ["--flag"]
    assert getattr(info, "hidden") is True


def test_build_raises_when_protocol_check_fails(monkeypatch) -> None:
    builder = FlextCommandBuilder("broken")
    monkeypatch.setattr(
        FlextCommandBuilder, "_is_command_protocol", staticmethod(lambda _obj: False)
    )

    with pytest.raises(TypeError):
        builder.build()


def test_is_command_protocol_false_for_incompatible_object() -> None:
    class NotCommand:
        name = 1
        description = 2

    assert FlextCommandBuilder._is_command_protocol(NotCommand()) is False
