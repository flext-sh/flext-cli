"""Public contract coverage tests for the flext-cli facade and models."""

from __future__ import annotations


from tests import c
from tests import m

from flext_cli import r
from flext_tests import tm

from pathlib import Path

from tests import p


class TestsFlextCliPublicContractsCoverage:
    """Implementation part for TestsFlextCliPublicContractsCoverage."""

    def test_public_model_contracts_cover_cli_shapes(self, tmp_path: Path) -> None:
        output = m.Cli.CommandOutput(
            stdout="out", stderr="err", exit_code=0, duration=0.25
        )
        display = m.Cli.DisplayData(data={"name": "flext", "count": 1})
        loaded = m.Cli.LoadedConfig(content={"debug": True})
        normalized = m.Cli.JsonNormalized({"name": "flext"})
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
            _params: p.Tests.SampleInput,
        ) -> p.Result[p.Tests.SampleOutput]:
            return r[p.Tests.SampleOutput].ok(m.Tests.SampleOutput(message="ok"))

        route = m.Cli.ResultCommandRoute(
            name="inspect",
            help_text="Inspect data",
            model_cls=m.Tests.SampleInput,
            handler=route_handler,
        )
        table = m.Cli.TableConfig(table_format=c.Cli.TabularFormat.TABLE)
        snapshot = m.Cli.SettingsSnapshot(
            settings_dir=str(tmp_path), settings_exists=True, settings_readable=True
        )
        option = m.Cli.OptionMetadata(help="Show help", short="h", default=True)
        write_options = m.Cli.JsonWriteOptions(
            indent=4, sort_keys=True, ensure_ascii=True
        )

        tm.that(output.stdout, eq="out")
        assert abs(output.duration - 0.25) < 1e-9
        tm.that(display.model_dump(), eq={"name": "flext", "count": 1})
        tm.that(loaded.content, eq={"debug": True})
        tm.that(normalized.model_dump(), eq={"name": "flext"})
        tm.that(m.Cli.JsonNormalizedList(value={"ok": True}).resolved, eq={"ok": True})
        tm.that(
            m.Cli.JsonNormalizedList(
                value="plain-text", default={"fallback": "yes"}
            ).resolved,
            eq={"fallback": "yes"},
        )
        tm.that(summary.root, eq={"status": "ok"})
        tm.that(prompt_state.interactive, eq=True)
        tm.that(prompt_state.quiet, eq=True)
        tm.that(auth.token, eq="token-123")
        tm.that(environment.resolve(), eq={"KEEP": "1", "ADD": "3"})
        tm.that(environment.resolved, eq={"KEEP": "1", "ADD": "3"})
        tm.that(entry.name, eq="inspect")
        tm.that(route.success_type, eq=c.Cli.MessageTypes.SUCCESS)
        tm.that(table.table_backend_format, eq=c.Cli.TabularFormat.SIMPLE)
        tm.that(snapshot.settings_exists, eq=True)
        tm.that(option.default, eq=True)
        tm.that(m.Cli.LogLevelResolved(raw=" debug ").resolved, eq=c.LogLevel.DEBUG)
        assert (
            m.Cli.TypedExtract(
                type_kind=c.Cli.TypeKind.STR, value="  name  ", default="fallback"
            ).resolved
            == "name"
        )
        assert (
            m.Cli.TypedExtract(type_kind=c.Cli.TypeKind.BOOL, value=1).resolved is True
        )
        tm.that(
            m.Cli.TypedExtract(
                type_kind=c.Cli.TypeKind.DICT, value={"count": 1}
            ).resolved,
            eq={"count": 1},
        )
        tm.that(
            m.Cli.TypedExtract(
                type_kind=c.Cli.TypeKind.DICT, value=None, default={"fallback": 2}
            ).resolved,
            eq={"fallback": 2},
        )
        tm.that(write_options.indent, eq=4)
        tm.that(write_options.sort_keys, eq=True)
        tm.that(write_options.ensure_ascii, eq=True)


__all__: list[str] = ["TestsFlextCliPublicContractsCoverage"]
