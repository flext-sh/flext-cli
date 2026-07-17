"""Behavioral contract tests for the ``u.Cli.params_*`` helpers.

Asserts observable public behavior only: returned models, ``r[T]`` success/
failure outcomes and error messages, and settings state read through the public
API. No private attributes, no internal-collaborator spying, no patching.
"""

from __future__ import annotations

import pytest
from flext_tests import tm

from flext_cli import FlextCliSettings, c, m, p, u
from tests import c as tc


class TestsFlextCliParams:
    """Public contract of the CLI parameter resolution/application helpers."""

    # -- params_resolve -----------------------------------------------------

    def test_resolve_merges_model_with_kwargs(self) -> None:
        """Verify that resolve merges model with kwargs."""
        params = m.Cli.ParamsConfig(debug=True)
        resolved = u.Cli.params_resolve(params, {"verbose": True})
        tm.that(resolved, is_=m.Cli.ParamsConfig)
        tm.that(resolved.debug, eq=True)
        tm.that(resolved.verbose, eq=True)

    def test_resolve_with_none_params_uses_kwargs_only(self) -> None:
        """Verify that resolve with none params uses kwargs only."""
        resolved = u.Cli.params_resolve(None, {"quiet": True})
        tm.that(resolved, is_=m.Cli.ParamsConfig)
        tm.that(resolved.quiet, eq=True)

    def test_resolve_kwargs_override_model_values(self) -> None:
        """Verify that resolve kwargs override model values."""
        params = m.Cli.ParamsConfig(debug=True)
        resolved = u.Cli.params_resolve(params, {"debug": False})
        tm.that(resolved.debug, eq=False)

    def test_resolve_is_idempotent_for_same_inputs(self) -> None:
        """Verify that resolve is idempotent for same inputs."""
        params = m.Cli.ParamsConfig(debug=True, verbose=True)
        first = u.Cli.params_resolve(params, {})
        second = u.Cli.params_resolve(params, {})
        tm.that(first.params, eq=second.params)

    # -- params_set_bool ----------------------------------------------------

    def test_set_bool_applies_root_and_cli_flags(self) -> None:
        """Verify that set bool applies root and cli flags."""
        settings = FlextCliSettings.model_validate({})
        params = m.Cli.ParamsConfig(
            debug=True, trace=True, verbose=True, quiet=True, no_color=True
        )
        result = u.Cli.params_set_bool(settings, params)
        tm.ok(result)
        updated = result.value
        tm.that(updated.debug, eq=True)
        tm.that(updated.cli_verbose, eq=True)
        tm.that(updated.cli_quiet, eq=True)
        tm.that(updated.cli_no_color, eq=True)

    def test_set_bool_trace_without_debug_fails(self) -> None:
        """Verify that set bool trace without debug fails."""
        settings = FlextCliSettings.model_validate({})
        params = m.Cli.ParamsConfig(trace=True)
        result = u.Cli.params_set_bool(settings, params)
        tm.fail(result)
        tm.that(result.error, eq=tc.Cli.CLI_PARAM_ERR_TRACE_REQUIRES_DEBUG)

    def test_set_bool_no_flags_returns_settings_unchanged(self) -> None:
        """Verify that set bool no flags returns settings unchanged."""
        settings = FlextCliSettings.model_validate({})
        result = u.Cli.params_set_bool(settings, m.Cli.ParamsConfig())
        tm.ok(result)
        tm.that(result.value.debug is settings.debug, eq=True)
        tm.that(result.value.cli_verbose is settings.cli_verbose, eq=True)

    # -- params_set_log_level ----------------------------------------------

    @pytest.mark.parametrize("level", ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
    def test_set_log_level_applies_valid_level(self, level: str) -> None:
        """Verify that set log level applies valid level."""
        settings = FlextCliSettings.model_validate({})
        params = m.Cli.ParamsConfig(log_level=level)
        result = u.Cli.params_set_log_level(settings, params)
        tm.ok(result)
        tm.that(result.value.cli_log_level, eq=level)

    def test_set_log_level_none_returns_settings_unchanged(self) -> None:
        """Verify that set log level none returns settings unchanged."""
        settings = FlextCliSettings.model_validate({})
        result = u.Cli.params_set_log_level(settings, m.Cli.ParamsConfig())
        tm.ok(result)
        tm.that(result.value.cli_log_level, eq=settings.cli_log_level)

    def test_set_log_level_invalid_fails_with_options_message(self) -> None:
        """Verify that set log level invalid fails with options message."""
        settings = FlextCliSettings.model_validate({})
        params = m.Cli.ParamsConfig(log_level="BOGUS")
        result = u.Cli.params_set_log_level(settings, params)
        tm.fail(result)
        expected = c.Cli.CLI_PARAM_ERR_INVALID_WITH_OPTIONS_FMT.format(
            field_label="log level",
            field_value="BOGUS",
            valid_values=", ".join(c.Cli.LOG_LEVELS),
        )
        tm.that(result.error, eq=expected)

    # -- params_set_format --------------------------------------------------

    @pytest.mark.parametrize("log_format", ["compact", "detailed", "full"])
    def test_set_format_applies_valid_log_format(self, log_format: str) -> None:
        """Verify that set format applies valid log format."""
        settings = FlextCliSettings.model_validate({})
        params = m.Cli.ParamsConfig(log_format=log_format)
        result = u.Cli.params_set_format(settings, params)
        tm.ok(result)
        tm.that(result.value.cli_log_verbosity, eq=log_format)

    @pytest.mark.parametrize(
        "output_format", ["json", "yaml", "csv", "table", "plain", "xml", "text"]
    )
    def test_set_format_applies_valid_output_format(self, output_format: str) -> None:
        """Verify that set format applies valid output format."""
        settings = FlextCliSettings.model_validate({})
        params = m.Cli.ParamsConfig(output_format=output_format)
        result = u.Cli.params_set_format(settings, params)
        tm.ok(result)
        tm.that(result.value.cli_output_format, eq=output_format)

    def test_set_format_none_returns_settings_unchanged(self) -> None:
        """Verify that set format none returns settings unchanged."""
        settings = FlextCliSettings.model_validate({})
        result = u.Cli.params_set_format(settings, m.Cli.ParamsConfig())
        tm.ok(result)
        tm.that(result.value.cli_log_verbosity, eq=settings.cli_log_verbosity)
        tm.that(result.value.cli_output_format, eq=settings.cli_output_format)

    def test_set_format_invalid_log_format_fails(self) -> None:
        """Verify that set format invalid log format fails."""
        settings = FlextCliSettings.model_validate({})
        params = m.Cli.ParamsConfig(log_format="BAD")
        result = u.Cli.params_set_format(settings, params)
        tm.fail(result)
        expected = c.Cli.CLI_PARAM_ERR_INVALID_WITH_VALID_FMT.format(
            field_label="log format",
            field_value="BAD",
            valid_values=", ".join(c.Cli.CLI_VALID_LOG_FORMATS),
        )
        tm.that(result.error, eq=expected)

    def test_set_format_invalid_output_format_fails(self) -> None:
        """Verify that set format invalid output format fails."""
        settings = FlextCliSettings.model_validate({})
        params = m.Cli.ParamsConfig(output_format="BAD")
        result = u.Cli.params_set_format(settings, params)
        tm.fail(result)
        expected = c.Cli.CLI_PARAM_ERR_INVALID_WITH_VALID_FMT.format(
            field_label="output format",
            field_value="BAD",
            valid_values=", ".join(c.Cli.OUTPUT_FORMATS),
        )
        tm.that(result.error, eq=expected)

    # -- params_apply -------------------------------------------------------

    def test_apply_chains_all_stages_on_valid_params(self) -> None:
        """Verify that apply chains all stages on valid params."""
        settings = FlextCliSettings.model_validate({})
        params = m.Cli.ParamsConfig(
            debug=True, log_level="INFO", output_format="yaml", log_format="detailed"
        )
        result = u.Cli.params_apply(settings, params)
        tm.ok(result)
        updated = result.value
        tm.that(updated.debug, eq=True)
        tm.that(updated.cli_log_level, eq="INFO")
        tm.that(updated.cli_output_format, eq="yaml")
        tm.that(updated.cli_log_verbosity, eq="detailed")

    def test_apply_short_circuits_on_first_stage_failure(self) -> None:
        """Verify that apply short circuits on first stage failure."""
        settings = FlextCliSettings.model_validate({})
        params = m.Cli.ParamsConfig(trace=True)
        result = u.Cli.params_apply(settings, params)
        tm.fail(result)
        tm.that(result.error, eq=tc.Cli.CLI_PARAM_ERR_TRACE_REQUIRES_DEBUG)

    def test_apply_returns_result_type(self) -> None:
        """Verify that apply returns result type."""
        settings = FlextCliSettings.model_validate({})
        result = u.Cli.params_apply(settings, m.Cli.ParamsConfig())
        tm.that(result, is_=p.Result)
        tm.ok(result)


__all__: list[str] = ["TestsFlextCliParams"]
