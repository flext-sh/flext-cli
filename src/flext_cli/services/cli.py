"""FLEXT CLI - Unified Typer abstraction service.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli import c, m, p, r, s, t, u
from flext_cli.services import FlextCliCommonParams
from flext_cli.services._cli import FlextCliCliPart06


class FlextCliCli(s[p.Cli.RuntimeStatus], FlextCliCliPart06):
    """Public facade for FlextCliCli."""

    def _apply_common_params_to_config(self, *, params: p.Cli.CliParamsConfig) -> None:
        """Validate optional overrides before electing this application's runtime."""
        applied = FlextCliCommonParams.apply_to_config(self.settings, params=params)
        if applied.failure:
            self._exit_failure(r[bool].from_failure(applied))
        self._apply_updated_settings(applied.value)
        u.configure_structlog(
            settings=u.logging_options(),
            runtime_settings=self.settings,
        )

    def _apply_updated_settings(self, updated_settings: p.Cli.Settings) -> None:
        """Rebind the existing DI scope without replacing settings singletons."""
        if updated_settings.model_dump() == self.settings.model_dump():
            return
        current = self._get_runtime()
        self._runtime = u.build_service_runtime(
            m.RuntimeBootstrapOptions(
                settings=updated_settings,
                container=current.container,
                context=current.context,
                dispatcher=current.dispatcher,
            ),
        )

    def create_app_with_common_params(
        self,
        *,
        name: str,
        help_text: str,
        add_completion: bool = True,
    ) -> p.Cli.Application:
        """Create a Typer app whose optional flags configure its injected runtime.

        Args:
            name: Application name shown in help output.
            help_text: Application help text.
            add_completion: Whether the completion command is registered.

        Returns:
            The resulting ``p.Cli.Application``.

        """
        app = u.Cli.framework_create_app(
            name=name,
            help_text=help_text,
            add_completion=add_completion,
        )

        def apply_common_params(params: p.Cli.CliParamsConfig) -> bool:
            self._apply_common_params_to_config(params=params)
            return True

        parameters: t.MutableSequenceOf[t.Cli.CommandParameter] = []
        annotations: t.Cli.CliAnnotations = {"return": bool}
        for field_name in c.Cli.CLI_GLOBAL_PARAM_FIELDS:
            parameter, annotation = self._build_model_parameter(
                field_name,
                m.Cli.CliParamsConfig.model_fields[field_name],
                None,
            )
            parameters.append(parameter)
            annotations[field_name] = annotation
        global_callback = self._ModelCommand(
            handler=apply_common_params,
            model_cls=m.Cli.CliParamsConfig,
            parameters=parameters,
            result_border=True,
        )
        global_callback.__annotations__ = dict(annotations)
        u.Cli.framework_register_callback(app, global_callback)
        return app


FlextCliCli = FlextCliCli

__all__: list[str] = ["FlextCliCli"]
