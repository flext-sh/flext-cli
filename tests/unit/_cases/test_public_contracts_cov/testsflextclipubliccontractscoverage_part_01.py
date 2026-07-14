"""Public contract coverage tests for the flext-cli facade and models."""

from __future__ import annotations

import inspect

from tests import c
from tests import p
from tests import u

from flext_cli import FlextCliSettings, cli, m, settings
from flext_tests import tm


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
        """Expose settings behavior and typed runtime status through public facades."""
        # NOTE (multi-agent): flat cli_* settings (§2.6) — fresh instances come
        # from ``settings.clone()`` and test-runtime detection lives in
        # ``u.Cli.cli_test_env`` (behavior moved off the settings model).
        FlextCliSettings.reset_for_testing()

        fresh_settings = settings.clone()
        tm.that(fresh_settings, is_=p.Cli.Settings)
        tm.that(u.Cli.cli_test_env(fresh_settings), eq=False)

        shell_settings = settings.clone(cli_shell_command="pytest -k smoke")
        tm.that(u.Cli.cli_test_env(shell_settings), eq=True)

        pytest_settings = settings.clone(
            cli_pytest_current_test=(
                "tests/unit/test_public_contracts_cov.py::test_public_facade"
            )
        )
        tm.that(u.Cli.cli_test_env(pytest_settings), eq=True)

        ci_settings = settings.clone(cli_ci=True)
        tm.that(u.Cli.cli_test_env(ci_settings), eq=True)

        FlextCliSettings.reset_for_testing()

        result = cli.execute()
        tm.ok(result, is_=m.Cli.RuntimeStatus)
        status = result.value

        tm.that(status.status, eq=c.Cli.ServiceStatus.OPERATIONAL)
        tm.that(status.service, eq=c.Cli.FLEXT_CLI)
        tm.that(status.components, is_=m.Cli.RuntimeComponents)
        tm.that(status.components.prompts, eq="available")

    def test_public_model_command_utility_contract(self) -> None:
        """Build and execute model commands through the public utility contract."""
        command_settings = self._CommandModel(label="configured", debug=True)

        def handler(model: TestsFlextCliPublicContractsCoverage._CommandModel) -> str:
            return f"{model.label}:{model.debug}"

        command = u.Cli.build_model_command(
            self._CommandModel, handler, settings=command_settings
        )
        signature = inspect.signature(command)

        # NOTE (multi-agent): ``u.Cli.build_model_command`` renders model-field
        # defaults into the signature; settings-seeded defaults are the
        # ``cli.model_command`` contract, not this utility's.
        tm.that(signature.parameters["label"].default, eq=inspect.Parameter.empty)
        tm.that(signature.parameters["debug"].default, eq=False)
        tm.that(
            u.Cli.model_source_data(
                self._CommandModel, self._CommandSource(label="mapped", debug=None)
            ),
            eq={"label": "mapped"},
        )

        derived = u.Cli.derive_model(
            self._CommandModel,
            {"label": "base"},
            {"debug": True},
            overrides={"label": "override"},
        )

        tm.that(derived.label, eq="override")
        tm.that(derived.debug, eq=True)
        tm.that(command(label="runtime", debug=True), eq="runtime:True")


__all__: list[str] = ["TestsFlextCliPublicContractsCoverage"]
