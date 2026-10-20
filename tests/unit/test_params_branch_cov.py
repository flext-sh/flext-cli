"""Behavioral contract tests for the ``u.Cli.params_*`` helpers.

Asserts observable public behavior only: returned models, ``r[T]`` success/
failure outcomes and error messages, and settings state read through the public
API. No private attributes, no internal-collaborator spying, no patching.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import pytest

from flext_cli import settings
from tests import c, m, p, tm, u


class TestsFlextCliParams:
    """Public contract of the CLI parameter resolution/application helpers."""

    # -- params_resolve -----------------------------------------------------

    @staticmethod
    def test_resolve_merges_model_with_kwargs() -> None:
        """Verify that resolve merges model with kwargs."""
        params = m.Cli.CliParamsConfig(debug=True)
        resolved = u.Cli.params_resolve(params, {"verbose": True})
        tm.that(resolved, is_=m.Cli.CliParamsConfig)
        tm.ok(resolved.debug)
        tm.ok(resolved.verbose)

    @staticmethod
    def test_resolve_with_none_params_uses_kwargs_only() -> None:
        """Verify that resolve with none params uses kwargs only."""
        resolved = u.Cli.params_resolve(None, {"quiet": True})
        tm.that(resolved, is_=m.Cli.CliParamsConfig)
        tm.ok(resolved.quiet)

    @staticmethod
    def test_resolve_kwargs_override_model_values() -> None:
        """Verify that resolve kwargs override model values."""
        params = m.Cli.CliParamsConfig(debug=True)
        resolved = u.Cli.params_resolve(params, {"debug": False})
        tm.fail(resolved.debug)

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
        current = settings.clone()
        params = m.Cli.CliParamsConfig(
            debug=True,
            trace=True,
            verbose=True,
            quiet=True,
            no_color=True,
        )
        result = u.Cli.params_set_bool(current, params)
        tm.ok(result)
        updated = result.value
        tm.ok(updated.debug)
        tm.ok(updated.cli_verbose)
        tm.ok(updated.cli_quiet)
        tm.ok(updated.cli_no_color)

    @staticmethod
    def test_set_bool_trace_without_debug_is_independent() -> None:
        """Enable detail without changing the independent debug flag."""
        current = settings.clone(debug=False)
        params = m.Cli.CliParamsConfig(trace=True)
        result = u.Cli.params_set_bool(current, params)
        tm.ok(result)
        tm.ok(result.value.trace)
        tm.that(result.value.debug, eq=current.debug)

    @staticmethod
    def test_set_bool_no_flags_returns_settings_unchanged() -> None:
        """Verify that set bool no flags returns settings unchanged."""
        current = settings.clone()
        result = u.Cli.params_set_bool(current, m.Cli.CliParamsConfig())
        tm.ok(result)
        tm.ok(result.value.debug is current.debug)
        tm.ok(result.value.cli_verbose is current.cli_verbose)

    # -- params_set_log_level ----------------------------------------------

    @staticmethod
    @pytest.mark.parametrize("level", list(c.LogLevel))
    def test_set_log_level_applies_valid_level(level: c.LogLevel) -> None:
        """Verify that set log level applies valid level."""
        current = settings.clone()
        params = m.Cli.CliParamsConfig(log_level=level)
        result = u.Cli.params_set_log_level(current, params)
        tm.ok(result)
        tm.that(result.value.log_level, eq=level)

    @staticmethod
    def test_set_log_level_none_returns_settings_unchanged() -> None:
        """Verify that set log level none returns settings unchanged."""
        current = settings.clone()
        result = u.Cli.params_set_log_level(current, m.Cli.CliParamsConfig())
        tm.ok(result)
        expected = u.resolve_logging_settings(runtime_settings=current)
        tm.that(result.value.log_level, eq=expected.log_level)

    @staticmethod
    def test_set_log_level_invalid_retains_canonical_cause() -> None:
        """Invalid logging input preserves the Core validation failure."""
        current = settings.clone()
        params = m.Cli.CliParamsConfig(log_level="BOGUS")
        result = u.Cli.params_set_log_level(current, params)
        tm.fail(result)
        tm.that(result.exception, is_=ValueError)
        tm.that(result.error, eq=str(result.exception))

    # -- params_set_format --------------------------------------------------

    @staticmethod
    @pytest.mark.parametrize("log_format", ["compact", "detailed", "full"])
    def test_set_format_applies_valid_log_format(log_format: str) -> None:
        """Verify that set format applies valid log format."""
        current = settings.clone()
        params = m.Cli.CliParamsConfig(log_format=log_format)
        result = u.Cli.params_set_format(current, params)
        tm.ok(result)
        tm.that(result.value.cli_log_verbosity, eq=log_format)

    @staticmethod
    @pytest.mark.parametrize(
        "output_format",
        ["json", "yaml", "csv", "table", "plain", "xml", "text"],
    )
    def test_set_format_applies_valid_output_format(output_format: str) -> None:
        """Verify that set format applies valid output format."""
        current = settings.clone()
        params = m.Cli.CliParamsConfig(output_format=output_format)
        result = u.Cli.params_set_format(current, params)
        tm.ok(result)
        tm.that(result.value.cli_output_format, eq=output_format)

    @staticmethod
    def test_set_format_none_returns_settings_unchanged() -> None:
        """Verify that set format none returns settings unchanged."""
        current = settings.clone()
        result = u.Cli.params_set_format(current, m.Cli.CliParamsConfig())
        tm.ok(result)
        tm.that(result.value.cli_log_verbosity, eq=current.cli_log_verbosity)
        tm.that(result.value.cli_output_format, eq=current.cli_output_format)

    @staticmethod
    def test_set_format_invalid_log_format_fails() -> None:
        """Verify that set format invalid log format fails."""
        current = settings.clone()
        params = m.Cli.CliParamsConfig(log_format="BAD")
        result = u.Cli.params_set_format(current, params)
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
        current = settings.clone()
        params = m.Cli.CliParamsConfig(output_format="BAD")
        result = u.Cli.params_set_format(current, params)
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
        current = settings.clone()
        params = m.Cli.CliParamsConfig(
            debug=True,
            log_level="INFO",
            output_format="yaml",
            log_format="detailed",
        )
        result = u.Cli.params_apply(current, params)
        tm.ok(result)
        updated = result.value
        tm.ok(updated.debug)
        tm.that(updated.log_level, eq=params.log_level)
        tm.that(updated.cli_output_format, eq="yaml")
        tm.that(updated.cli_log_verbosity, eq="detailed")

    @staticmethod
    def test_apply_short_circuits_on_first_stage_failure() -> None:
        """Verify that apply short circuits on first stage failure."""
        current = settings.clone()
        before = current.model_dump()
        params = m.Cli.CliParamsConfig(log_level="INVALID", verbose=True)
        result = u.Cli.params_apply(current, params)
        tm.fail(result)
        tm.that(result.exception, is_=ValueError)
        tm.that(current.model_dump(), eq=before)

    @staticmethod
    def test_apply_returns_result_type() -> None:
        """Verify that apply returns result type."""
        current = settings.clone()
        result = u.Cli.params_apply(current, m.Cli.CliParamsConfig())
        tm.that(result, is_=p.Result)
        tm.ok(result)
