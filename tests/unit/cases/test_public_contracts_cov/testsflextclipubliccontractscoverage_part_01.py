"""Public contract coverage tests for the flext-cli facade and models.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import (
    Iterable,
    Iterator,
    Mapping,
    MutableMapping,
    MutableSequence,
    Sequence,
)

from typing_extensions import TypeForm

from flext_cli import FlextCliModels, FlextCliSettings, cli, settings
from tests import c, m, p, tm, u


class TestsFlextCliPublicContractsCoveragePart01:
    """Implementation part for TestsFlextCliPublicContractsCoveragePart01."""

    @staticmethod
    def test_inherited_settings_preset_validates_and_round_trips() -> None:
        """The CLI model facade inherits a functioning settings preset."""
        instance = FlextCliModels.BaseSettings()
        adapter = u.type_adapter(TypeForm(FlextCliModels.PydanticBaseSettings))
        tm.ok(adapter.validate_python(instance) is instance)
        restored = FlextCliModels.BaseSettings.model_validate_json(
            instance.model_dump_json()
        )
        tm.that(restored.model_dump(), eq=instance.model_dump())

    @staticmethod
    def test_inherited_settings_config_controls_environment_resolution() -> None:
        """Native settings configuration governs field resolution and overrides."""
        settings_config = m.Tests.InheritedSettings.model_config
        prefix = settings_config.get("env_prefix")
        case_sensitive = settings_config.get("case_sensitive")
        prefix = tm.not_none(prefix)
        case_sensitive = tm.not_none(case_sensitive)
        with u.Tests.env_vars_context(
            env_vars={
                f"{prefix}topic": "from-environment",
                f"{prefix}TOPIC": "from-uppercase",
            },
        ):
            resolved = m.Tests.InheritedSettings()
            explicit = m.Tests.InheritedSettings(topic="from-constructor")
        tm.that(
            resolved.topic,
            eq="from-environment" if case_sensitive else "from-uppercase",
        )
        tm.that(explicit.topic, eq="from-constructor")

    @staticmethod
    def test_public_facade_and_settings_contract() -> None:
        # NOTE (multi-agent): flat cli_* settings (§2.6) — fresh instances come
        # from ``settings.clone()`` and test-runtime detection lives in
        # ``u.Cli.cli_test_env`` (behavior moved off the settings model).
        """Verify that public facade and settings contract."""
        FlextCliSettings.reset_for_testing()

        fresh_settings = settings.clone()
        tm.that(fresh_settings, is_=p.Cli.Settings)
        tm.fail(u.Cli.cli_test_env(fresh_settings))

        shell_settings = settings.clone(cli_shell_command="pytest -k smoke")
        tm.ok(u.Cli.cli_test_env(shell_settings))

        pytest_settings = settings.clone(
            cli_pytest_current_test=(
                "tests/unit/test_public_contracts_cov.py::test_public_facade"
            ),
        )
        tm.ok(u.Cli.cli_test_env(pytest_settings))

        ci_settings = settings.clone(cli_ci=True)
        tm.ok(u.Cli.cli_test_env(ci_settings))

        FlextCliSettings.reset_for_testing()

        facade_result = cli.execute()

        tm.ok(facade_result)
        tm.that(facade_result.value.status, eq=(c.Cli.ServiceStatus.OPERATIONAL))
        tm.that(facade_result.value.service, eq=c.Cli.FLEXT_CLI)
