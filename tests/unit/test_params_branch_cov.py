"""Branch coverage tests for _utilities/params.py."""

from __future__ import annotations

from flext_cli import cli
from tests import c, m, u


class TestsFlextCliParamsBranchCov:
    """Exercise remaining low-cost branches in params utilities."""

    def test_params_resolve_merges_model_and_kwargs(self) -> None:
        params = m.Cli.CliParamsConfig(debug=True)
        resolved = u.Cli.params_resolve(params, {"verbose": True})
        assert isinstance(resolved, m.Cli.CliParamsConfig)
        assert resolved.verbose is True
        assert resolved.debug is True

    def test_params_set_format_applies_valid_log_format(self) -> None:
        settings = cli.new_settings()
        valid_log_format = c.Cli.CLI_VALID_LOG_FORMATS[0]
        params = m.Cli.CliParamsConfig(log_format=valid_log_format)
        result = u.Cli.params_set_format(settings, params)
        assert result.success
        assert result.value.Cli.log_verbosity == valid_log_format

    def test_params_set_format_applies_valid_output_format(self) -> None:
        settings = cli.new_settings()
        valid_output_format = c.Cli.OUTPUT_FORMATS[0]
        params = m.Cli.CliParamsConfig(output_format=valid_output_format)
        result = u.Cli.params_set_format(settings, params)
        assert result.success
        assert result.value.Cli.output_format == valid_output_format


__all__: list[str] = ["TestsFlextCliParamsBranchCov"]
