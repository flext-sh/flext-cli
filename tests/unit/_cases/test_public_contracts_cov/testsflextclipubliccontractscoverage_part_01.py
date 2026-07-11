"""Public contract coverage tests for the flext-cli facade and models."""

from __future__ import annotations

import inspect

from tests.constants import c
from tests.protocols import p
from tests.utilities import u

from flext_cli import FlextCliSettings, cli, m, settings


class TestsFlextCliPublicContractsCoverage:
    """Implementation part for TestsFlextCliPublicContractsCoverage."""

    class _CommandModel(m.BaseModel):
        """Minimal public model for utility command construction."""

        label: str
        debug: bool = False

    class _CommandSource(m.BaseModel):
        """Source model used to exercise `u.Cli.model_source_data()`."""

        label: str
        debug: bool | None = None

    def test_public_facade_and_settings_contract(self) -> None:
        # NOTE (multi-agent): flat cli_* settings (§2.6) — fresh instances come
        # from ``settings.clone()`` and test-runtime detection lives in
        # ``u.Cli.cli_test_env`` (behavior moved off the settings model).
        FlextCliSettings.reset_for_testing()

        fresh_settings = settings.clone()
        assert isinstance(fresh_settings, p.Cli.Settings)
        assert u.Cli.cli_test_env(fresh_settings) is False

        shell_settings = settings.clone(cli_shell_command="pytest -k smoke")
        assert u.Cli.cli_test_env(shell_settings) is True

        pytest_settings = settings.clone(
            cli_pytest_current_test=(
                "tests/unit/test_public_contracts_cov.py::test_public_facade"
            ),
        )
        assert u.Cli.cli_test_env(pytest_settings) is True

        ci_settings = settings.clone(cli_ci=True)
        assert u.Cli.cli_test_env(ci_settings) is True

        FlextCliSettings.reset_for_testing()

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
        command_settings = self._CommandModel(label="configured", debug=True)

        def handler(
            model: TestsFlextCliPublicContractsCoverage._CommandModel,
        ) -> str:
            return f"{model.label}:{model.debug}"

        command = u.Cli.build_model_command(
            self._CommandModel,
            handler,
            settings=command_settings,
        )
        signature = inspect.signature(command)

        # NOTE (multi-agent): ``u.Cli.build_model_command`` renders model-field
        # defaults into the signature; settings-seeded defaults are the
        # ``cli.model_command`` contract, not this utility's.
        assert signature.parameters["label"].default is inspect.Parameter.empty
        assert signature.parameters["debug"].default is False
        assert u.Cli.model_source_data(
            self._CommandModel,
            self._CommandSource(label="mapped", debug=None),
        ) == {"label": "mapped"}

        derived = u.Cli.derive_model(
            self._CommandModel,
            {"label": "base"},
            {"debug": True},
            overrides={"label": "override"},
        )

        assert derived.label == "override"
        assert derived.debug is True
        assert command(label="runtime", debug=True) == "runtime:True"


__all__: list[str] = ["TestsFlextCliPublicContractsCoverage"]
