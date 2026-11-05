"""FLEXT CLI - Unified Typer abstraction service.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Sequence

from flext_cli import c, m, p, r, t, u
from flext_cli.services._cli import FlextCliCliPart04


class FlextCliCliPart05(FlextCliCliPart04):
    """Implementation part for FlextCliCliPart05."""

    @staticmethod
    def result_route[M: t.Cli.ModelLike, TResult](
        *,
        metadata: p.Cli.CommandMetadata,
        model_cls: t.ModelClass[M],
        handler: p.Cli.ResultCommandHandler[M, TResult],
        success_formatter: t.Cli.SuccessMessageFormatter[TResult],
    ) -> p.Cli.ResultCommandRoute:
        """Bind a typed operation to the existing heterogeneous CLI contract.

        The framework already validated the request. Its original instance and
        the operation's typed result reach the handler and formatter unchanged.
        Only the formatted text crosses the heterogeneous transport boundary.
        Metadata supplies only command identity and help; output fields stay flat.

        Returns:
            A result route retaining the typed handler and output formatter.

        """
        name = metadata.name

        def execute(params: t.Cli.ModelLike) -> p.Result[str]:
            if not isinstance(params, model_cls):
                message = (
                    f"Result route {name!r} requires {model_cls.__name__}, "
                    f"received {type(params).__name__}"
                )
                raise TypeError(message)
            result = handler(params)
            if result.failure:
                return r[str].from_failure(result)
            return r[str].ok(success_formatter(result.value))

        return m.Cli.ResultCommandRoute(
            name=name,
            help_text=metadata.help_text,
            model_cls=model_cls,
            handler=execute,
        )

    @classmethod
    def register_result_command(
        cls,
        app: p.Cli.Application,
        *,
        route: p.Cli.ResultCommandRoute,
        settings: t.Cli.ModelLike | None = None,
    ) -> None:
        """Register a model command that normalizes `r[...]` CLI handling.

        Args:
            app: Application receiving the command.
            route: Result route describing the model and handler.
            settings: Optional model instance supplying current field values.

        """
        execute = cls._build_route_executor(route)
        cls.register_command(
            app,
            name=route.name,
            help_text=route.help_text,
            command=cls._ModelCommand(
                handler=execute,
                model_cls=route.model_cls,
                signature=cls._model_signature(route.model_cls, settings),
                result_border=True,
            ),
        )

    @classmethod
    def register_result_route(
        cls,
        app: p.Cli.Application,
        *,
        route: p.Cli.ResultCommandRoute,
    ) -> None:
        """Register a declarative result route on a Typer app.

        Args:
            app: Application receiving the route.
            route: Result route describing the model and handler.

        """
        cls.register_result_command(app, route=route)

    @classmethod
    def _build_route_executor(
        cls,
        route: p.Cli.ResultCommandRoute,
    ) -> p.Cli.ModelCommandHandler[t.Cli.ModelLike, bool]:
        """Adapt the existing heterogeneous route contract to the result executor.

        Returns:
            A model handler retaining the route's result and success formatting.

        """

        def execute(params: t.Cli.ModelLike) -> bool:
            result = route.handler(params)
            if result.failure:
                cls._exit_failure(r[t.Cli.ResultValue].from_failure(result))
            message = u.Cli.commands_resolve_success_message(
                result_value=result.value,
                success_message=route.success_message,
                success_formatter=route.success_formatter,
            )
            if message:
                u.Cli.commands_emit_success_message(message, route.success_type)
            return True

        return execute

    @classmethod
    def register_result_routes(
        cls,
        app: p.Cli.Application,
        routes: Sequence[p.Cli.ResultCommandRoute],
    ) -> None:
        """Register multiple heterogeneous result routes in one call.

        Args:
            app: Application receiving the routes.
            routes: Ordered result routes to register.

        """
        for route in routes:
            cls.register_result_route(app, route=route)

    @staticmethod
    def finalize_result[TResult](
        result: p.Result[TResult],
        *,
        failure_exit_code: int = c.Cli.EXIT_CODE_FAILURE,
    ) -> int:
        """Finalize one public CLI Result into output/logging and an exit code.

        Args:
            result: Result whose failure renders through the error boundary.
            failure_exit_code: Exit code returned on failure.

        Returns:
            The resulting ``int``.

        """
        if result.success:
            return c.Cli.EXIT_CODE_SUCCESS
        u.Cli.commands_emit_result_error(result)
        # NOTE (multi-agent): the outermost CLI owns its process contract while
        # FlextCliCliPart05 remains the single error-emission boundary.
        return failure_exit_code


__all__: list[str] = ["FlextCliCliPart05"]
