"""Public contract coverage tests for the flext-cli facade and models."""

from __future__ import annotations

import inspect
from pathlib import Path

import pytest

from flext_cli import c, m, p, r, u
from flext_cli.api import FlextCli
from flext_cli.base import FlextCliServiceBase
from flext_cli.settings import FlextCliSettings
from tests import m as test_m


class _CommandModel(m.BaseModel):
    """Minimal public model for utility command construction."""

    label: str
    debug: bool = False


class _CommandSource(m.BaseModel):
    """Source model used to exercise `u.Cli.model_source_data()`."""

    label: str
    debug: bool | None = None


class TestsFlextCliPublicContractsCoverage:
    """Exercise public CLI contracts through facade, settings, models, and utilities."""

    def test_public_facade_and_settings_contract(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.delenv(c.Cli.ENV_VAR_PYTEST_CURRENT_TEST, raising=False)
        monkeypatch.delenv(c.Cli.ENV_VAR_SHELL_COMMAND, raising=False)
        monkeypatch.delenv(c.Cli.ENV_VAR_CI, raising=False)

        base_service = FlextCliServiceBase()
        base_result = base_service.execute()

        assert base_result.success
        assert base_result.value == {}

        fresh_settings = base_service.new_settings()
        assert isinstance(fresh_settings, FlextCliSettings)
        assert fresh_settings.test_env is False

        shell_settings = FlextCliSettings()
        shell_settings.shell_command = "pytest -k smoke"
        assert shell_settings.test_env is True

        pytest_settings = FlextCliSettings()
        pytest_settings.pytest_current_test = (
            "tests/unit/test_public_contracts_cov.py::test_public_facade"
        )
        assert pytest_settings.test_env is True

        ci_settings = FlextCliSettings()
        ci_settings.ci = True
        assert ci_settings.test_env is True

        facade = FlextCli()
        facade_result = facade.execute()

        assert facade_result.success
        assert facade_result.value[c.Cli.DICT_KEY_STATUS] == (
            c.Cli.ServiceStatus.OPERATIONAL
        )
        assert facade_result.value[c.Cli.DICT_KEY_SERVICE] == c.Cli.FLEXT_CLI
        components = facade_result.value.get("components")
        assert isinstance(components, dict)
        assert components["prompts"] == "available"

    def test_public_model_command_utility_contract(self) -> None:
        settings = _CommandModel(label="configured", debug=True)

        def handler(model: _CommandModel) -> str:
            return f"{model.label}:{model.debug}"

        command = u.Cli.build_model_command(
            _CommandModel,
            handler,
            settings=settings,
        )
        signature = inspect.signature(command)

        assert signature.parameters["label"].default is inspect.Parameter.empty
        assert signature.parameters["debug"].default is True
        assert u.Cli.model_source_data(
            _CommandModel,
            _CommandSource(label="mapped", debug=None),
        ) == {"label": "mapped"}

        derived = u.Cli.derive_model(
            _CommandModel,
            {"label": "base"},
            {"debug": True},
            overrides={"label": "override"},
        )

        assert derived.label == "override"
        assert derived.debug is True
        assert command(label="runtime", debug=True) == "runtime:True"

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
            _params: test_m.Tests.SampleInput,
        ) -> p.Result[test_m.Tests.SampleOutput]:
            return r[test_m.Tests.SampleOutput].ok(
                test_m.Tests.SampleOutput(message="ok")
            )

        route = m.Cli.ResultCommandRoute(
            name="inspect",
            help_text="Inspect data",
            model_cls=test_m.Tests.SampleInput,
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

    def test_public_pipeline_model_contracts(self, tmp_path: Path) -> None:
        context = m.Cli.PipelineStageContext(
            workspace_root=tmp_path,
            shared={},
            settings={"mode": "test"},
        )

        def stage_handler(
            current: m.Cli.PipelineStageContext,
        ) -> p.Result[m.Cli.PipelineStageResult]:
            return r[m.Cli.PipelineStageResult].ok(
                m.Cli.PipelineStageResult(
                    stage_id="build",
                    status=c.Cli.PipelineStageStatus.OK,
                    output={"workspace": str(current.workspace_root)},
                )
            )

        spec = m.Cli.PipelineStageSpec(
            stage_id="build",
            depends_on=frozenset({"fetch"}),
            handler=stage_handler,
            retry=1,
        )
        pipeline = m.Cli.PipelineResult(
            stages=[
                m.Cli.PipelineStageResult(
                    stage_id="ok",
                    status=c.Cli.PipelineStageStatus.OK,
                ),
                m.Cli.PipelineStageResult(
                    stage_id="fail",
                    status=c.Cli.PipelineStageStatus.FAILED,
                    error="boom",
                ),
                m.Cli.PipelineStageResult(
                    stage_id="skip",
                    status=c.Cli.PipelineStageStatus.SKIPPED,
                ),
            ],
            total_duration_ms=10.5,
        )
        stage_result = spec.handler(context)

        assert context.settings == {"mode": "test"}
        assert spec.retry == 1
        assert pipeline.success is False
        assert [stage.stage_id for stage in pipeline.failed_stages] == ["fail"]
        assert [stage.stage_id for stage in pipeline.skipped_stages] == ["skip"]
        assert stage_result.success
        assert stage_result.value.output == {"workspace": str(tmp_path)}
