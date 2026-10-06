"""Behavioral contract tests for the ``u.Cli.params_*`` helpers.

Asserts observable public behavior only: returned models, ``r[T]`` success/
failure outcomes and error messages, and settings state read through the public
API. No private attributes, no internal-collaborator spying, no patching.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import pytest
from flext_tests import tm

import tests
from flext_cli import c, m, p, settings, u


class TestsFlextCliParams:
    """Public contract of the CLI parameter resolution/application helpers."""

    # -- params_resolve -----------------------------------------------------

    @staticmethod
    def test_resolve_merges_model_with_kwargs() -> None:
        """Verify that resolve merges model with kwargs."""
        params = m.Cli.CliParamsConfig(debug=True)
        resolved = u.Cli.params_resolve(params, {"verbose": True})
        tm.that(resolved, is_=m.Cli.CliParamsConfig)
        tm.that(resolved.debug, eq=True)
        tm.that(resolved.verbose, eq=True)

    @staticmethod
    def test_resolve_with_none_params_uses_kwargs_only() -> None:
        """Verify that resolve with none params uses kwargs only."""
        resolved = u.Cli.params_resolve(None, {"quiet": True})
        tm.that(resolved, is_=m.Cli.CliParamsConfig)
        tm.that(resolved.quiet, eq=True)

    @staticmethod
    def test_resolve_kwargs_override_model_values() -> None:
        """Verify that resolve kwargs override model values."""
        params = m.Cli.CliParamsConfig(debug=True)
        resolved = u.Cli.params_resolve(params, {"debug": False})
        tm.that(resolved.debug, eq=False)

    @staticmethod
    def test_resolve_is_idempotent_for_same_inputs() -> None:
        """Verify that resolve is idempotent for same inputs."""
        params = m.Cli.CliParamsConfig(debug=True, verbose=True)
        first = u.Cli.params_resolve(params, {})
        second = u.Cli.params_resolve(params, {})
        tm.that(first.model_dump(), eq=second.model_dump())

    # -- params_set_bool ----------------------------------------------------

    @staticmethod
    def test_set_bool_applies_root_and_cli_flags() -> None:
        """Verify that set bool applies root and cli flags."""
        settings = settings.clone()()
        params = m.Cli.CliParamsConfig(
            debug=True,
            trace=True,
            verbose=True,
            quiet=True,
            no_color=True,
        )
        result = u.Cli.params_set_bool(settings, params)
        tm.ok(result)
        updated = result.value
        tm.that(updated.debug, eq=True)
        tm.that(updated.cli_verbose, eq=True)
        tm.that(updated.cli_quiet, eq=True)
        tm.that(updated.cli_no_color, eq=True)

    @staticmethod
    def test_set_bool_trace_without_debug_fails() -> None:
        """Verify that set bool trace without debug fails."""
        settings = settings.clone()()
        params = m.Cli.CliParamsConfig(trace=True)
        result = u.Cli.params_set_bool(settings, params)
        tm.fail(result)
        tm.that(result.error, eq=tests.c.Cli.CLI_PARAM_ERR_TRACE_REQUIRES_DEBUG)

    @staticmethod
    def test_set_bool_no_flags_returns_settings_unchanged() -> None:
        """Verify that set bool no flags returns settings unchanged."""
        settings = settings.clone()()
        result = u.Cli.params_set_bool(settings, m.Cli.CliParamsConfig())
        tm.ok(result)
        tm.that(result.value.debug is settings.debug, eq=True)
        tm.that(result.value.cli_verbose is settings.cli_verbose, eq=True)

    # -- params_set_log_level ----------------------------------------------

    @staticmethod
    @pytest.mark.parametrize("level", ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
    def test_set_log_level_applies_valid_level(level: str) -> None:
        """Verify that set log level applies valid level."""
        settings = settings.clone()()
        params = m.Cli.CliParamsConfig(log_level=level)
        result = u.Cli.params_set_log_level(settings, params)
        tm.ok(result)
        tm.that(result.value.cli_log_level, eq=level)

    @staticmethod
    def test_set_log_level_none_returns_settings_unchanged() -> None:
        """Verify that set log level none returns settings unchanged."""
        settings = settings.clone()()
        result = u.Cli.params_set_log_level(settings, m.Cli.CliParamsConfig())
        tm.ok(result)
        tm.that(result.value.cli_log_level, eq=settings.cli_log_level)

    @staticmethod
    def test_set_log_level_invalid_fails_with_options_message() -> None:
        """Verify that set log level invalid fails with options message."""
        settings = settings.clone()()
        params = m.Cli.CliParamsConfig(log_level="BOGUS")
        result = u.Cli.params_set_log_level(settings, params)
        tm.fail(result)
        expected = c.Cli.CLI_PARAM_ERR_INVALID_WITH_OPTIONS_FMT.format(
            field_label="log level",
            field_value="BOGUS",
            valid_values=", ".join(c.Cli.LOG_LEVELS),
        )
        tm.that(result.error, eq=expected)

    # -- params_set_format --------------------------------------------------

    @staticmethod
    @pytest.mark.parametrize("log_format", ["compact", "detailed", "full"])
    def test_set_format_applies_valid_log_format(log_format: str) -> None:
        """Verify that set format applies valid log format."""
        settings = settings.clone()()
        params = m.Cli.CliParamsConfig(log_format=log_format)
        result = u.Cli.params_set_format(settings, params)
        tm.ok(result)
        tm.that(result.value.cli_log_verbosity, eq=log_format)

    @staticmethod
    @pytest.mark.parametrize(
        "output_format",
        ["json", "yaml", "csv", "table", "plain", "xml", "text"],
    )
    def test_set_format_applies_valid_output_format(output_format: str) -> None:
        """Verify that set format applies valid output format."""
        settings = settings.clone()()
        params = m.Cli.CliParamsConfig(output_format=output_format)
        result = u.Cli.params_set_format(settings, params)
        tm.ok(result)
        tm.that(result.value.cli_output_format, eq=output_format)

    @staticmethod
    def test_set_format_none_returns_settings_unchanged() -> None:
        """Verify that set format none returns settings unchanged."""
        settings = settings.clone()()
        result = u.Cli.params_set_format(settings, m.Cli.CliParamsConfig())
        tm.ok(result)
        tm.that(result.value.cli_log_verbosity, eq=settings.cli_log_verbosity)
        tm.that(result.value.cli_output_format, eq=settings.cli_output_format)

    @staticmethod
    def test_set_format_invalid_log_format_fails() -> None:
        """Verify that set format invalid log format fails."""
        settings = settings.clone()()
        params = m.Cli.CliParamsConfig(log_format="BAD")
        result = u.Cli.params_set_format(settings, params)
        tm.fail(result)
        expected = c.Cli.CLI_PARAM_ERR_INVALID_WITH_VALID_FMT.format(
            field_label="log format",
            field_value="BAD",
            valid_values=", ".join(c.Cli.CLI_VALID_LOG_FORMATS),
        )
        tm.that(result.error, eq=expected)

    @staticmethod
    def test_set_format_invalid_output_format_fails() -> None:
        """Verify that set format invalid output format fails."""
        settings = settings.clone()()
        params = m.Cli.CliParamsConfig(output_format="BAD")
        result = u.Cli.params_set_format(settings, params)
        tm.fail(result)
        expected = c.Cli.CLI_PARAM_ERR_INVALID_WITH_VALID_FMT.format(
            field_label="output format",
            field_value="BAD",
            valid_values=", ".join(c.Cli.OUTPUT_FORMATS),
        )
        tm.that(result.error, eq=expected)

    # -- params_apply -------------------------------------------------------

    @staticmethod
    def test_apply_chains_all_stages_on_valid_params() -> None:
        """Verify that apply chains all stages on valid params."""
        settings = settings.clone()()
        params = m.Cli.CliParamsConfig(
            debug=True,
            log_level="INFO",
            output_format="yaml",
            log_format="detailed",
        )
        result = u.Cli.params_apply(settings, params)
        tm.ok(result)
        updated = result.value
        tm.that(updated.debug, eq=True)
        tm.that(updated.cli_log_level, eq="INFO")
        tm.that(updated.cli_output_format, eq="yaml")
        tm.that(updated.cli_log_verbosity, eq="detailed")

    @staticmethod
    def test_apply_short_circuits_on_first_stage_failure() -> None:
        """Verify that apply short circuits on first stage failure."""
        settings = settings.clone()()
        params = m.Cli.CliParamsConfig(trace=True)
        result = u.Cli.params_apply(settings, params)
        tm.fail(result)
        tm.that(result.error, eq=tests.c.Cli.CLI_PARAM_ERR_TRACE_REQUIRES_DEBUG)

    @staticmethod
    def test_apply_returns_result_type() -> None:
        """Verify that apply returns result type."""
        settings = settings.clone()()
        result = u.Cli.params_apply(settings, m.Cli.CliParamsConfig())
        tm.that(result, is_=p.Result)
        tm.ok(result)
