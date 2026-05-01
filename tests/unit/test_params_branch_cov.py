"""Branch coverage tests for _utilities/params.py."""

from __future__ import annotations

from flext_cli._utilities.params import FlextCliUtilitiesParams
from flext_cli.settings import FlextCliSettings
from tests import c, m


class TestsFlextCliParamsBranchCov:
    """Exercise remaining low-cost branches in params utilities."""

    def test_params_resolve_merges_model_and_kwargs(self) -> None:
        params = m.Cli.CliParamsConfig(debug=True)
        resolved = FlextCliUtilitiesParams.params_resolve(params, {"verbose": True})
        assert isinstance(resolved, m.Cli.CliParamsConfig)
        assert resolved.verbose is True
        assert resolved.debug is True

    def test_params_set_format_applies_valid_log_format(self) -> None:
        settings = FlextCliSettings()
        valid_log_format = c.Cli.CLI_VALID_LOG_FORMATS[0]
        params = m.Cli.CliParamsConfig(log_format=valid_log_format)
        result = FlextCliUtilitiesParams.params_set_format(settings, params)
        assert result.success
        assert result.value.log_verbosity == valid_log_format

    def test_params_set_format_applies_valid_output_format(self) -> None:
        settings = FlextCliSettings()
        valid_output_format = c.Cli.OUTPUT_FORMATS[0]
        params = m.Cli.CliParamsConfig(output_format=valid_output_format)
        result = FlextCliUtilitiesParams.params_set_format(settings, params)
        assert result.success
        assert result.value.output_format == valid_output_format


__all__: list[str] = ["TestsFlextCliParamsBranchCov"]
