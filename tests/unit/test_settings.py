"""FLEXT CLI Settings behavioral tests.

Exercises the observable public contract of ``FlextCliSettings`` and the
canonical ``settings`` singleton: flat scalar defaults (§2.6), the
``u.Cli.cli_test_env`` truth table, partial ``model_validate`` state
application, ``model_dump`` shape, and the ``fetch_global`` singleton /
``reset_for_testing`` isolation contracts.

Modules tested: flext_cli.settings.FlextCliSettings, flext_cli.settings.settings

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import pytest
from flext_tests import tm

from flext_cli import FlextCliSettings, settings, t, u
from tests import c, p


class TestsFlextCliSettingsUnit:
    """Observable behavior of the flat CLI settings contract.

    Class name retains the ``Unit`` suffix because the canonical
    ``TestsFlextCliSettings`` symbol is already owned by ``tests/settings.py``
    and this name is registered in the (read-only) tests export registries.
    """

    def test_settings_singleton_satisfies_contract(self) -> None:
        """The canonical settings singleton satisfies the Settings protocol."""
        resolved_settings = tm.not_none(settings)
        tm.that(resolved_settings, is_=p.Cli.Settings)

    def test_fetch_global_returns_shared_singleton(self) -> None:
        """fetch_global returns the same process-wide instance each call."""
        tm.that(
            FlextCliSettings.fetch_global() is FlextCliSettings.fetch_global(), eq=True
        )

    @pytest.mark.parametrize(
        ("field_name", "expected"),
        [
            ("cli_verbose", False),
            ("cli_quiet", False),
            ("cli_no_color", False),
            ("cli_app_name", c.Cli.FLEXT_CLI),
            ("cli_log_verbosity", c.Cli.LogVerbosity.COMPACT.value),
            ("cli_log_level", c.LogLevel.INFO.value),
            ("cli_output_format", c.Cli.OUTPUT_DEFAULT_FORMAT_TYPE.value),
            ("cli_ci", False),
            ("cli_config_file", None),
            ("cli_token_file", None),
        ],
    )
    def test_flat_default_field_state(
        self, field_name: str, expected: t.Scalar | None
    ) -> None:
        """A freshly validated settings object exposes documented defaults."""
        built = FlextCliSettings.model_validate({})
        tm.that(getattr(built, field_name), eq=expected)

    def test_top_level_debug_default_is_false(self) -> None:
        """The inherited top-level debug flag defaults to disabled."""
        tm.that(FlextCliSettings.model_validate({}).debug, eq=False)

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
    def test_cli_test_env_truth_table(
        self,
        pytest_current_test: str | None,
        shell_command: str | None,
        *,
        ci: bool,
        expected: bool,
    ) -> None:
        """cli_test_env is true iff pytest markers or CI mode are present."""
        built = FlextCliSettings.model_validate({
            "cli_pytest_current_test": pytest_current_test,
            "cli_shell_command": shell_command,
            "cli_ci": ci,
        })
        tm.that(u.Cli.cli_test_env(built), eq=expected)

    @pytest.mark.parametrize("level", list(c.LogLevel))
    def test_cli_log_level_preserves_each_level(self, level: c.LogLevel) -> None:
        """Every log level round-trips through the cli_log_level field."""
        built = FlextCliSettings.model_validate({"cli_log_level": level.value})
        tm.that(built.cli_log_level, eq=level.value)

    @pytest.mark.parametrize("verbosity", list(c.Cli.LogVerbosity))
    def test_log_verbosity_preserves_each_mode(
        self, verbosity: c.Cli.LogVerbosity
    ) -> None:
        """Every declared log verbosity mode is retained as public state."""
        built = FlextCliSettings.model_validate({"cli_log_verbosity": verbosity.value})
        tm.that(built.cli_log_verbosity, eq=verbosity.value)

    def test_model_validate_applies_flat_overrides(self) -> None:
        """Partial model_validate applies flat overrides onto defaults."""
        built = FlextCliSettings.model_validate({"cli_verbose": True, "cli_ci": True})
        tm.that(built.cli_verbose, eq=True)
        tm.that(built.cli_ci, eq=True)
        tm.that(u.Cli.cli_test_env(built), eq=True)

    def test_model_validate_ignores_unknown_fields(self) -> None:
        """Unknown keys are ignored (extra=ignore) and defaults survive."""
        built = FlextCliSettings.model_validate({"cli_unknown_field": "x"})
        tm.that(built.cli_app_name, eq=c.Cli.FLEXT_CLI)
        tm.that(hasattr(built, "cli_unknown_field"), eq=False)

    def test_model_dump_exposes_flat_scalar_fields(self) -> None:
        """model_dump surfaces the flat cli_* fields without a nested branch."""
        dumped = FlextCliSettings.model_validate({}).model_dump()
        tm.that(dumped, is_=dict)
        tm.that(dumped, has="cli_verbose")
        tm.that(dumped, has="cli_log_level")
        tm.that(dumped, has="cli_output_format")
        tm.that("Cli" in dumped, eq=False)

    def test_clone_yields_distinct_equal_instance(self) -> None:
        """Clone produces an independent object equal to its source."""
        source = FlextCliSettings.model_validate({})
        cloned = source.clone()
        tm.that(cloned == source, eq=True)
        tm.that(cloned is not source, eq=True)

    def test_reset_for_testing_restores_usable_defaults(self) -> None:
        """After reset, fetch_global rebuilds a settings object with defaults."""
        FlextCliSettings.reset_for_testing()
        rebuilt = FlextCliSettings.fetch_global()
        rebuilt = tm.not_none(rebuilt)
        tm.that(rebuilt.cli_verbose, eq=False)
        tm.that(rebuilt.cli_app_name, eq=c.Cli.FLEXT_CLI)
