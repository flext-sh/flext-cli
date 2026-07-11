"""Public-facade getting-started example for flext-cli.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from typing import override

from examples import c, m, p, r, s, t, u
from flext_cli import cli, settings


class ExamplesFlextCliGettingStarted(s):
    """Minimal guided tour of flext-cli through public aliases and facades."""

    def build_example_settings(self) -> p.Result[m.Examples.MyAppSettings]:
        """Build a validated application settings model through the examples facade."""
        settings_payload: t.JsonMapping = {
            "app_name": c.EXAMPLE_DEFAULT_TOOL_NAME,
            "api_key": "example-api-key",
            "max_workers": c.EXAMPLE_DEFAULT_MAX_WORKERS,
            "timeout": c.EXAMPLE_DEFAULT_TIMEOUT_SECONDS,
        }
        return r[m.Examples.MyAppSettings].ok(
            m.Examples.MyAppSettings.model_validate(settings_payload),
        )

    @staticmethod
    def persist_example_settings(
        settings: m.Examples.MyAppSettings,
    ) -> p.Result[m.Cli.LoadedConfig]:
        """Round-trip settings through the public JSON file facade."""
        wrapped_config = m.Cli.LoadedConfig(content=settings.model_dump(mode="json"))
        with TemporaryDirectory(prefix=f"{c.EXAMPLE_DEFAULT_TEMP_SUBDIR}-") as temp_dir:
            config_path = Path(temp_dir) / "settings.json"
            return cli.write_json_file(
                str(config_path),
                wrapped_config.model_dump(mode="json"),
            ).flat_map(
                lambda _: cli.read_json_model(str(config_path), m.Cli.LoadedConfig),
            )

    @override
    def execute(self) -> p.Result[t.JsonMapping]:
        """Run the public getting-started flow through typed examples aliases."""
        cli.print(
            "FLEXT CLI - Getting Started",
            style=c.Cli.MessageStyles.BOLD_BLUE,
        )
        cli.print(
            "===========================",
            style=c.Cli.MessageStyles.BOLD_BLUE,
        )

        cli.print("\n1. Setup via s/base.py", style=c.Cli.MessageStyles.BOLD_CYAN)
        runtime_snapshot: t.JsonMapping = {
            "output_format": settings.cli_output_format,
            "cli_log_level": settings.cli_log_level,
            "verbose": settings.cli_verbose,
            "quiet": settings.cli_quiet,
        }
        u.display_config_table(
            u.to_json_dict(runtime_snapshot),
            headers=c.EXAMPLE_TABLE_HEADERS_SETTING_VALUE,
        )

        settings_result = self.build_example_settings()
        if settings_result.failure:
            return r[t.JsonMapping].fail(
                settings_result.error or c.EXAMPLE_ERR_FAILED_LOAD_CONFIG,
            )

        cli.print(
            "\n2. Pydantic 2 models via m.Examples",
            style=c.Cli.MessageStyles.BOLD_CYAN,
        )
        app_settings = settings_result.value
        app_settings.display(cli)

        loaded_result = self.persist_example_settings(app_settings)
        if loaded_result.failure:
            return r[t.JsonMapping].fail(
                loaded_result.error or c.EXAMPLE_ERR_FAILED_LOAD_CONFIG,
            )

        cli.print(
            "\n3. Public cli facade round-trip",
            style=c.Cli.MessageStyles.BOLD_CYAN,
        )
        loaded_config = loaded_result.value
        roundtrip_summary = m.Cli.DisplayData(
            data={
                "loaded_keys": ", ".join(loaded_config.content.keys()),
                "api_key_present": str(bool(loaded_config.content.get("api_key"))),
                "max_workers": str(loaded_config.content.get("max_workers")),
                "timeout": str(loaded_config.content.get("timeout")),
            },
        )
        u.display_config_table(
            roundtrip_summary,
            headers=c.EXAMPLE_TABLE_HEADERS_SETTING_VALUE,
        )

        cli.print(
            "\n4. Railway result ergonomics",
            style=c.Cli.MessageStyles.BOLD_CYAN,
        )
        result_summary: t.JsonMapping = {
            "ok.success": r[str].ok(c.EXAMPLE_MSG_OPERATION_COMPLETED).success,
            "fail.failure": r[str].fail(c.EXAMPLE_MSG_ERROR_SOMETHING_FAILED).failure,
            "settings_model": type(app_settings).__name__,
            "loaded_model": type(loaded_config).__name__,
        }
        u.display_config_table(
            u.to_json_dict(result_summary),
            headers=c.EXAMPLE_TABLE_HEADERS_SETTING_VALUE,
        )

        summary: t.JsonMapping = {
            "app_name": app_settings.app_name,
            "output_format": settings.cli_output_format,
            "loaded_field_count": len(loaded_config.content),
            "result_contract": "public-r",
        }
        u.print_demo_completion(
            "Getting started",
            (
                "setup through s/base.py",
                "Pydantic 2 validation via m.Examples",
                "typed JSON round-trip through cli",
                "runtime aliases through examples",
            ),
        )
        return r[t.JsonMapping].ok(summary)
