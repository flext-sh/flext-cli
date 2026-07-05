"""FLEXT CLI Settings behavioral tests.

Exercises the observable public contract of ``FlextCliSettings`` and the
``cli`` runtime settings surface: default field state, the namespaced ``Cli``
branch, the ``test_env`` computed field truth table, partial ``model_validate``
state application, ``model_dump`` shape, and the ``fetch_global`` singleton /
``new_settings`` factory contracts.

Modules tested: flext_cli.settings.FlextCliSettings, flext_cli.cli settings API

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import pytest
from flext_tests import tm

from flext_cli import cli
from flext_cli.settings import FlextCliSettings
from tests.constants import c
from tests.protocols import p


class TestsFlextCliSettingsUnit:
    """Observable behavior of the CLI settings contract.

    Class name retains the ``Unit`` suffix because the canonical
    ``TestsFlextCliSettings`` symbol is already owned by ``tests/settings.py``
    and this name is registered in the (read-only) tests export registries.
    """

    def test_new_settings_returns_settings_contract(self) -> None:
        """new_settings hands back an object satisfying the Settings protocol."""
        settings = cli.new_settings()
        tm.that(settings, none=False)
        tm.that(settings, is_=p.Cli.Settings)

    def test_settings_property_exposes_settings_contract(self) -> None:
        """The cli.settings property exposes the shared Settings surface."""
        settings = cli.settings
        tm.that(settings, none=False)
        tm.that(settings, is_=p.Cli.Settings)

    @pytest.mark.parametrize(
        ("field_name", "expected"),
        [
            ("verbose", False),
            ("quiet", False),
            ("no_color", False),
            ("app_name", c.Cli.FLEXT_CLI),
            ("log_verbosity", c.Cli.LogVerbosity.COMPACT),
            ("cli_log_level", c.LogLevel.INFO),
            ("output_format", c.Cli.OUTPUT_DEFAULT_FORMAT_TYPE),
            ("ci", False),
            ("config_file", None),
            ("token_file", None),
        ],
    )
    def test_cli_branch_default_field_state(
        self,
        field_name: str,
        expected: object,
    ) -> None:
        """A freshly built settings object exposes documented Cli defaults."""
        branch = cli.new_settings().Cli
        tm.that(getattr(branch, field_name), eq=expected)

    def test_top_level_debug_default_is_false(self) -> None:
        """The inherited top-level debug flag defaults to disabled."""
        tm.that(cli.new_settings().debug, eq=False)

    @pytest.mark.parametrize(
        ("pytest_current_test", "shell_command", "ci", "expected"),
        [
            (None, None, False, False),
            ("tests/unit/test_settings.py::case", None, False, True),
            (None, "poetry run pytest -q", False, True),
            (None, "PYTEST wrapper", False, True),
            (None, "make lint", False, False),
            (None, None, True, True),
            ("case", "make lint", True, True),
        ],
    )
    def test_test_env_computed_truth_table(
        self,
        pytest_current_test: str | None,
        shell_command: str | None,
        ci: bool,
        expected: bool,
    ) -> None:
        """test_env is true iff pytest markers or CI mode are present.

        Built directly on the nested value model so the ambient FLEXT_CLI_*
        environment cannot leak into the computed result.
        """
        branch = FlextCliSettings.CliSettings(
            pytest_current_test=pytest_current_test,
            shell_command=shell_command,
            ci=ci,
        )
        tm.that(branch.test_env, eq=expected)

    @pytest.mark.parametrize("level", list(c.LogLevel))
    def test_cli_log_level_preserves_each_level(self, level: c.LogLevel) -> None:
        """Every log level round-trips through the cli_log_level field."""
        branch = FlextCliSettings.CliSettings(cli_log_level=level)
        tm.that(branch.cli_log_level, eq=level)

    @pytest.mark.parametrize("verbosity", list(c.Cli.LogVerbosity))
    def test_log_verbosity_preserves_each_mode(
        self,
        verbosity: c.Cli.LogVerbosity,
    ) -> None:
        """Every declared log verbosity mode is retained as public state."""
        branch = FlextCliSettings.CliSettings(log_verbosity=verbosity)
        tm.that(branch.log_verbosity, eq=verbosity)

    def test_model_validate_applies_cli_overrides(self) -> None:
        """Partial model_validate applies overrides and recomputes test_env."""
        settings = FlextCliSettings.model_validate({
            "Cli": {"verbose": True, "ci": True}
        })
        tm.that(settings.Cli.verbose, eq=True)
        tm.that(settings.Cli.ci, eq=True)
        tm.that(settings.Cli.test_env, eq=True)

    def test_model_validate_rejects_unknown_cli_field(self) -> None:
        """Unknown Cli fields raise pydantic ValidationError (fail-loud)."""
        with pytest.raises(ValueError, match="test_env"):
            FlextCliSettings.model_validate(
                {"Cli": {"test_env": True}},
            )

    def test_model_dump_exposes_cli_branch_and_computed_fields(self) -> None:
        """model_dump surfaces the Cli branch, its fields, and computed values."""
        dumped = cli.new_settings().model_dump()
        tm.that(dumped, is_=dict)
        tm.that(dumped, has="Cli")
        tm.that(dumped, has="effective_log_level")
        tm.that(dumped["Cli"], has="verbose")
        tm.that(dumped["Cli"], has="test_env")

    def test_fetch_global_returns_shared_singleton(self) -> None:
        """fetch_global returns the same process-wide instance each call."""
        tm.that(
            FlextCliSettings.fetch_global(),
            eq=FlextCliSettings.fetch_global(),
        )

    def test_new_settings_yields_distinct_instances(self) -> None:
        """new_settings is a factory: each call is an independent object."""
        first = cli.new_settings()
        second = cli.new_settings()
        tm.that(first, eq=second)
        assert first is not second

    def test_reset_for_testing_restores_usable_defaults(self) -> None:
        """After reset, a rebuilt settings object still exposes valid defaults."""
        cli.new_settings()
        cli.settings.reset_for_testing()
        rebuilt = cli.new_settings()
        tm.that(rebuilt, none=False)
        tm.that(rebuilt.Cli.verbose, eq=False)
        tm.that(rebuilt.Cli.app_name, eq=c.Cli.FLEXT_CLI)
