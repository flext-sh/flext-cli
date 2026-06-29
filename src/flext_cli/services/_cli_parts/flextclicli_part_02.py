"""FLEXT CLI - Unified Typer abstraction service.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from inspect import Parameter

import typer

from flext_cli import (
    FlextCliCommonParams,
    m,
    p,
    t,
    u,
)
from flext_cli.services._cli_parts.flextclicli_part_01 import (
    FlextCliCli as FlextCliCliPart01,
)


class FlextCliCli(FlextCliCliPart01):
    """Implementation part for FlextCliCli."""

    def _apply_common_params_to_config(
        self,
        settings: p.Cli.Settings,
        *,
        params: m.Cli.CliParamsConfig,
    ) -> None:
        """Apply global CLI flags to the shared settings model."""
        resolved_log_level: str = (
            params.log_level
            if params.log_level is not None
            else str(settings.Cli.cli_log_level)
        )
        next_params = params.model_copy(
            update={"log_level": resolved_log_level},
        )
        result = FlextCliCommonParams.apply_to_config(
            settings,
            params=next_params,
        )
        if result.failure:
            u.fetch_logger(__name__).warning(
                "failed to apply cli params", error=result.error or ""
            )
            return

        updated_settings = result.value
        if updated_settings is settings or not isinstance(settings, p.Cli.Settings):
            return
        overrides: dict[str, t.JsonPayload | None] = {}
        if updated_settings.debug != settings.debug:
            overrides["debug"] = updated_settings.debug
        if updated_settings.trace != settings.trace:
            overrides["trace"] = updated_settings.trace
        if updated_settings.Cli != settings.Cli:
            overrides["Cli"] = updated_settings.Cli.model_dump(
                exclude_computed_fields=True,
            )
        if overrides:
            settings.update_global(**overrides)

    def create_app_with_common_params(
        self,
        *,
        name: str,
        help_text: str,
        settings: p.Cli.Settings | None = None,
        add_completion: bool = True,
    ) -> t.Cli.CliApp:
        """Create a Typer app with the shared global FLEXT CLI parameters."""
        app = typer.Typer(name=name, help=help_text, add_completion=add_completion)

        def apply_common_params(params: m.Cli.CliParamsConfig) -> bool:
            if settings is not None:
                self._apply_common_params_to_config(settings, params=params)
            return True

        field_names = ("debug", "trace", "verbose", "quiet", "log_level")
        parameters: t.MutableSequenceOf[Parameter] = []
        annotations: t.Cli.CliAnnotations = {"return": bool}
        for field_name in field_names:
            parameter, annotation = self._build_model_parameter(
                field_name,
                m.Cli.CliParamsConfig.model_fields[field_name],
                None,
            )
            parameters.append(parameter)
            annotations[field_name] = annotation
        global_callback: FlextCliCli._ModelCommand[m.Cli.CliParamsConfig] = (
            self._ModelCommand(
                settings=None,
                handler=apply_common_params,
                model_cls=m.Cli.CliParamsConfig,
                parameters=parameters,
            )
        )
        global_callback.__annotations__ = dict(annotations)
        app.callback()(global_callback)
        return app

    @staticmethod
    def add_group(
        app: t.Cli.CliApp,
        *,
        name: str,
        group: t.Cli.CliApp,
    ) -> None:
        """Attach a subcommand group to an application."""
        app.add_typer(group, name=name)

    @staticmethod
    def create_group(
        *,
        help_text: str,
        name: str | None = None,
    ) -> t.Cli.CliApp:
        """Create a Typer command group without re-registering global params."""
        return typer.Typer(name=name, help=help_text)


__all__: list[str] = ["FlextCliCli"]
