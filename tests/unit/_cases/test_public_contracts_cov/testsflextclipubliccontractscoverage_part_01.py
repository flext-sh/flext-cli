"""Public contract coverage tests for the flext-cli facade and models."""

from __future__ import annotations

import inspect

from tests.constants import c
from tests.protocols import p
from tests.utilities import u

from flext_cli import cli, m


class _CommandModel(m.BaseModel):
    """Minimal public model for utility command construction."""

    label: str
    debug: bool = False


class _CommandSource(m.BaseModel):
    """Source model used to exercise `u.Cli.model_source_data()`."""

    label: str
    debug: bool | None = None


class TestsFlextCliPublicContractsCoverage:
    """Implementation part for TestsFlextCliPublicContractsCoverage."""

    def test_public_facade_and_settings_contract(self) -> None:
        cli.settings.reset_for_testing()

        fresh_settings = cli.new_settings()
        assert isinstance(fresh_settings, p.Cli.Settings)
        assert fresh_settings.Cli.test_env is False

        cli.settings.reset_for_testing()
        shell_settings = cli.new_settings()
        shell_settings = shell_settings.model_copy(
            update={
                "Cli": shell_settings.Cli.model_copy(
                    update={"shell_command": "pytest -k smoke"}
                )
            }
        )
        assert shell_settings.Cli.test_env is True

        cli.settings.reset_for_testing()
        pytest_settings = cli.new_settings()
        pytest_settings = pytest_settings.model_copy(
            update={
                "Cli": pytest_settings.Cli.model_copy(
                    update={
                        "pytest_current_test": (
                            "tests/unit/test_public_contracts_cov.py::test_public_facade"
                        )
                    }
                )
            }
        )
        assert pytest_settings.Cli.test_env is True

        cli.settings.reset_for_testing()
        ci_settings = cli.new_settings()
        ci_settings = ci_settings.model_copy(
            update={"Cli": ci_settings.Cli.model_copy(update={"ci": True})}
        )
        assert ci_settings.Cli.test_env is True

        cli.settings.reset_for_testing()

        facade_result = cli.execute()

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


__all__: list[str] = ["TestsFlextCliPublicContractsCoverage"]
