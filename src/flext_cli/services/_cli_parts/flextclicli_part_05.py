"""FLEXT CLI - Unified Typer abstraction service.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli import c, p, r, t, u
from flext_cli.services._cli_parts.flextclicli_part_04 import (
    FlextCliCli as FlextCliCliPart04,
)


class FlextCliCli(FlextCliCliPart04):
    """Implementation part for FlextCliCli."""

    @classmethod
    def register_result_callback[M: t.Cli.ModelLike, TResult: t.Cli.ResultValue](
        cls,
        app: p.Cli.Application,
        *,
        handler: p.Cli.ResultCommandHandler[M, TResult],
        model_cls: t.ModelClass[M],
        settings: t.Cli.ModelLike | None = None,
        success_formatter: t.Cli.SuccessMessageFormatter[TResult] | None = None,
        success_message: str | None = None,
        success_type: c.Cli.MessageTypes = c.Cli.MessageTypes.SUCCESS,
    ) -> None:
        """Register one model/result handler as the application root callback."""
        execute = cls._build_result_executor(
            handler=handler,
            success_formatter=success_formatter,
            success_message=success_message,
            success_type=success_type,
        )
        cls.register_callback(
            app, command=cls.model_command(model_cls, execute, settings=settings)
        )

    @classmethod
    def register_result_command[M: t.Cli.ModelLike, TResult: t.Cli.ResultValue](
        cls,
        app: p.Cli.Application,
        *,
        handler: p.Cli.ResultCommandHandler[M, TResult],
        help_text: str,
        # mro-j47u (codex): route registration preserves the model protocol.
        model_cls: t.ModelClass[M],
        name: str,
        settings: t.Cli.ModelLike | None = None,
        success_formatter: t.Cli.SuccessMessageFormatter[TResult] | None = None,
        success_message: str | None = None,
        success_type: c.Cli.MessageTypes = c.Cli.MessageTypes.SUCCESS,
    ) -> None:
        """Register a model command that normalizes `r[...]` CLI handling."""
        execute = cls._build_result_executor(
            handler=handler,
            success_formatter=success_formatter,
            success_message=success_message,
            success_type=success_type,
        )
        cls.register_command(
            app,
            name=name,
            help_text=help_text,
            command=cls.model_command(model_cls, execute, settings=settings),
        )

    @classmethod
    def _build_result_executor[M: t.Cli.ModelLike, TResult: t.Cli.ResultValue](
        cls,
        *,
        handler: p.Cli.ResultCommandHandler[M, TResult],
        success_formatter: t.Cli.SuccessMessageFormatter[TResult] | None = None,
        success_message: str | None = None,
        success_type: c.Cli.MessageTypes = c.Cli.MessageTypes.SUCCESS,
    ) -> p.Cli.ModelCommandHandler[M]:
        """Build the shared executor used by single and batched route registration."""

        def _exit_with_failure(error: str | None) -> None:
            if error:
                u.Cli.commands_emit_error_message(error)
            cls.exit(code=1)

        def execute(params: M) -> t.JsonValue:
            result: p.Result[TResult] = handler(params)
            if result.failure:
                _exit_with_failure(result.error)
            result_value: TResult = result.value
            message = u.Cli.commands_resolve_success_message(
                result_value=result_value,
                success_message=success_message,
                success_formatter=success_formatter,
            )
            if message:
                u.Cli.commands_emit_success_message(message, success_type)
            return True

        return execute

    @classmethod
    def register_result_route(
        cls, app: p.Cli.Application, *, route: p.Cli.ResultCommandRoute
    ) -> None:
        """Register a declarative result route on a Typer app."""

        def route_execute(params: t.Cli.ModelLike) -> p.Result[t.Cli.ResultValue]:
            result = route.handler(params)
            if result.failure:
                return r[t.Cli.ResultValue].fail(result.error or "")
            return r[t.Cli.ResultValue].ok(result.value)

        cls.register_result_command(
            app,
            name=route.name,
            help_text=route.help_text,
            model_cls=route.model_cls,
            handler=route_execute,
            success_message=route.success_message,
            success_formatter=route.success_formatter,
            success_type=route.success_type,
        )

    @classmethod
    def register_result_routes(
        cls, app: p.Cli.Application, routes: t.SequenceOf[p.Cli.ResultCommandRoute]
    ) -> None:
        """Register multiple heterogeneous result routes in one call."""
        for route in routes:
            cls.register_result_route(app, route=route)


__all__: list[str] = ["FlextCliCli"]
