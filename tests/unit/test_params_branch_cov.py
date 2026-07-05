"""Behavioral contract tests for the ``u.Cli.params_*`` helpers.

Asserts observable public behavior only: returned models, ``r[T]`` success/
failure outcomes and error messages, and settings state read through the public
API. No private attributes, no internal-collaborator spying, no patching.
"""

from __future__ import annotations

import pytest

from flext_cli import c, cli, m, p, u
from tests.constants import c as tc


class TestsFlextCliParams:
    """Public contract of the CLI parameter resolution/application helpers."""

    # -- params_resolve -----------------------------------------------------

    def test_resolve_merges_model_with_kwargs(self) -> None:
        params = m.Cli.CliParamsConfig(debug=True)
        resolved = u.Cli.params_resolve(params, {"verbose": True})
        assert isinstance(resolved, m.Cli.CliParamsConfig)
        assert resolved.debug is True
        assert resolved.verbose is True

    def test_resolve_with_none_params_uses_kwargs_only(self) -> None:
        resolved = u.Cli.params_resolve(None, {"quiet": True})
        assert isinstance(resolved, m.Cli.CliParamsConfig)
        assert resolved.quiet is True

    def test_resolve_kwargs_override_model_values(self) -> None:
        params = m.Cli.CliParamsConfig(debug=True)
        resolved = u.Cli.params_resolve(params, {"debug": False})
        assert resolved.debug is False

    def test_resolve_is_idempotent_for_same_inputs(self) -> None:
        params = m.Cli.CliParamsConfig(debug=True, verbose=True)
        first = u.Cli.params_resolve(params, {})
        second = u.Cli.params_resolve(params, {})
        assert first.model_dump() == second.model_dump()

    # -- params_set_bool ----------------------------------------------------

    def test_set_bool_applies_root_and_cli_flags(self) -> None:
        settings = cli.new_settings()
        params = m.Cli.CliParamsConfig(
            debug=True,
            trace=True,
            verbose=True,
            quiet=True,
            no_color=True,
        )
        result = u.Cli.params_set_bool(settings, params)
        assert result.success
        updated = result.value
        assert updated.debug is True
        assert updated.Cli.verbose is True
        assert updated.Cli.quiet is True
        assert updated.Cli.no_color is True

    def test_set_bool_trace_without_debug_fails(self) -> None:
        settings = cli.new_settings()
        params = m.Cli.CliParamsConfig(trace=True)
        result = u.Cli.params_set_bool(settings, params)
        assert result.failure
        assert result.error == tc.Cli.CLI_PARAM_ERR_TRACE_REQUIRES_DEBUG

    def test_set_bool_no_flags_returns_settings_unchanged(self) -> None:
        settings = cli.new_settings()
        result = u.Cli.params_set_bool(settings, m.Cli.CliParamsConfig())
        assert result.success
        assert result.value.debug is settings.debug
        assert result.value.Cli.verbose is settings.Cli.verbose

    # -- params_set_log_level ----------------------------------------------

    @pytest.mark.parametrize("level", ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
    def test_set_log_level_applies_valid_level(self, level: str) -> None:
        settings = cli.new_settings()
        params = m.Cli.CliParamsConfig(log_level=level)
        result = u.Cli.params_set_log_level(settings, params)
        assert result.success
        assert result.value.Cli.cli_log_level == level

    def test_set_log_level_none_returns_settings_unchanged(self) -> None:
        settings = cli.new_settings()
        result = u.Cli.params_set_log_level(settings, m.Cli.CliParamsConfig())
        assert result.success
        assert result.value.Cli.cli_log_level == settings.Cli.cli_log_level

    def test_set_log_level_invalid_fails_with_options_message(self) -> None:
        settings = cli.new_settings()
        params = m.Cli.CliParamsConfig(log_level="BOGUS")
        result = u.Cli.params_set_log_level(settings, params)
        assert result.failure
        expected = c.Cli.CLI_PARAM_ERR_INVALID_WITH_OPTIONS_FMT.format(
            field_label="log level",
            field_value="BOGUS",
            valid_values=", ".join(c.Cli.LOG_LEVELS),
        )
        assert result.error == expected

    # -- params_set_format --------------------------------------------------

    @pytest.mark.parametrize("log_format", ["compact", "detailed", "full"])
    def test_set_format_applies_valid_log_format(self, log_format: str) -> None:
        settings = cli.new_settings()
        params = m.Cli.CliParamsConfig(log_format=log_format)
        result = u.Cli.params_set_format(settings, params)
        assert result.success
        assert result.value.Cli.log_verbosity == log_format

    @pytest.mark.parametrize(
        "output_format",
        ["json", "yaml", "csv", "table", "plain", "xml", "text"],
    )
    def test_set_format_applies_valid_output_format(self, output_format: str) -> None:
        settings = cli.new_settings()
        params = m.Cli.CliParamsConfig(output_format=output_format)
        result = u.Cli.params_set_format(settings, params)
        assert result.success
        assert result.value.Cli.output_format == output_format

    def test_set_format_none_returns_settings_unchanged(self) -> None:
        settings = cli.new_settings()
        result = u.Cli.params_set_format(settings, m.Cli.CliParamsConfig())
        assert result.success
        assert result.value.Cli.log_verbosity == settings.Cli.log_verbosity
        assert result.value.Cli.output_format == settings.Cli.output_format

    def test_set_format_invalid_log_format_fails(self) -> None:
        settings = cli.new_settings()
        params = m.Cli.CliParamsConfig(log_format="BAD")
        result = u.Cli.params_set_format(settings, params)
        assert result.failure
        expected = c.Cli.CLI_PARAM_ERR_INVALID_WITH_VALID_FMT.format(
            field_label="log format",
            field_value="BAD",
            valid_values=", ".join(c.Cli.CLI_VALID_LOG_FORMATS),
        )
        assert result.error == expected

    def test_set_format_invalid_output_format_fails(self) -> None:
        settings = cli.new_settings()
        params = m.Cli.CliParamsConfig(output_format="BAD")
        result = u.Cli.params_set_format(settings, params)
        assert result.failure
        expected = c.Cli.CLI_PARAM_ERR_INVALID_WITH_VALID_FMT.format(
            field_label="output format",
            field_value="BAD",
            valid_values=", ".join(c.Cli.OUTPUT_FORMATS),
        )
        assert result.error == expected

    # -- params_apply -------------------------------------------------------

    def test_apply_chains_all_stages_on_valid_params(self) -> None:
        settings = cli.new_settings()
        params = m.Cli.CliParamsConfig(
            debug=True,
            log_level="INFO",
            output_format="yaml",
            log_format="detailed",
        )
        result = u.Cli.params_apply(settings, params)
        assert result.success
        updated = result.value
        assert updated.debug is True
        assert updated.Cli.cli_log_level == "INFO"
        assert updated.Cli.output_format == "yaml"
        assert updated.Cli.log_verbosity == "detailed"

    def test_apply_short_circuits_on_first_stage_failure(self) -> None:
        settings = cli.new_settings()
        params = m.Cli.CliParamsConfig(trace=True)
        result = u.Cli.params_apply(settings, params)
        assert result.failure
        assert result.error == tc.Cli.CLI_PARAM_ERR_TRACE_REQUIRES_DEBUG

    def test_apply_returns_result_type(self) -> None:
        settings = cli.new_settings()
        result = u.Cli.params_apply(settings, m.Cli.CliParamsConfig())
        assert isinstance(result, p.Result)
        assert result.success


__all__: list[str] = ["TestsFlextCliParams"]
