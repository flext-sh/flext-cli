"""Public contract coverage tests for the flext-cli facade and models."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tests.constants import c
from tests.models import m

from flext_cli import r

if TYPE_CHECKING:
    from pathlib import Path

    from tests.protocols import p


class TestsFlextCliPublicContractsCoverage:
    """Implementation part for TestsFlextCliPublicContractsCoverage."""

    def test_public_model_contracts_cover_cli_shapes(self, tmp_path: Path) -> None:
        output = m.Cli.CommandOutput(
            stdout="out",
            stderr="err",
            exit_code=0,
            duration=0.25,
        )
        display = m.Cli.DisplayData(data={"name": "flext", "count": 1})
        loaded = m.Cli.LoadedConfig(content={"debug": True})
        normalized = m.Cli.CliNormalizedJson({"name": "flext"})
        summary = m.Cli.SuccessSummaryDetails({"status": "ok"})
        prompt_state = m.Cli.PromptRuntimeState(quiet=True)
        auth = m.Cli.AuthCredentialsPayload(token="token-123")
        environment = m.Cli.ProcessEnvironmentSpec(
            base_env={"KEEP": "1", "DROP": "2"},
            overrides={"ADD": "3"},
            remove_keys=("DROP",),
        )
        entry = m.Cli.CommandEntryModel(name="inspect", handler=lambda: True)

        def route_handler(
            _params: m.Tests.SampleInput,
        ) -> p.Result[m.Tests.SampleOutput]:
            return r[m.Tests.SampleOutput].ok(m.Tests.SampleOutput(message="ok"))

        route = m.Cli.ResultCommandRoute(
            name="inspect",
            help_text="Inspect data",
            model_cls=m.Tests.SampleInput,
            handler=route_handler,
        )
        table = m.Cli.TableConfig(table_format=c.Cli.TabularFormat.TABLE)
        snapshot = m.Cli.SettingsSnapshot(
            settings_dir=str(tmp_path),
            settings_exists=True,
            settings_readable=True,
        )
        option = m.Cli.OptionMetadata(help="Show help", short="h", default=True)
        write_options = m.Cli.JsonWriteOptions(
            indent=4,
            sort_keys=True,
            ensure_ascii=True,
        )

        assert output.stdout == "out"
        assert abs(output.duration - 0.25) < 1e-9
        assert display.model_dump() == {"name": "flext", "count": 1}
        assert loaded.content == {"debug": True}
        assert normalized.model_dump() == {"name": "flext"}
        assert m.Cli.NormalizedJsonList(value={"ok": True}).resolved == {"ok": True}
        assert m.Cli.NormalizedJsonList(
            value="plain-text",
            default={"fallback": "yes"},
        ).resolved == {"fallback": "yes"}
        assert summary.root == {"status": "ok"}
        assert prompt_state.interactive is True
        assert prompt_state.quiet is True
        assert auth.token == "token-123"
        assert environment.resolve() == {"KEEP": "1", "ADD": "3"}
        assert environment.resolved == {"KEEP": "1", "ADD": "3"}
        assert entry.name == "inspect"
        assert route.success_type == c.Cli.MessageTypes.SUCCESS
        assert table.table_backend_format == c.Cli.TabularFormat.SIMPLE
        assert snapshot.settings_exists is True
        assert option.default is True
        assert m.Cli.LogLevelResolved(raw=" debug ").resolved == c.LogLevel.DEBUG
        assert (
            m.Cli.TypedExtract(
                type_kind=c.Cli.TypeKind.STR,
                value="  name  ",
                default="fallback",
            ).resolved
            == "name"
        )
        assert (
            m.Cli.TypedExtract(
                type_kind=c.Cli.TypeKind.BOOL,
                value=1,
            ).resolved
            is True
        )
        assert m.Cli.TypedExtract(
            type_kind=c.Cli.TypeKind.DICT,
            value={"count": 1},
        ).resolved == {"count": 1}
        assert m.Cli.TypedExtract(
            type_kind=c.Cli.TypeKind.DICT,
            value=None,
            default={"fallback": 2},
        ).resolved == {"fallback": 2}
        assert write_options.indent == 4
        assert write_options.sort_keys is True
        assert write_options.ensure_ascii is True


__all__: list[str] = ["TestsFlextCliPublicContractsCoverage"]
