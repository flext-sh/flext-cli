"""FLEXT CLI - Unified Typer abstraction service.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Sequence
from inspect import cleandoc

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
                settings=settings,
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

    @classmethod
    def run_result_command[M: t.Cli.ModelLike, TResult](
        cls,
        model_cls: t.ModelClass[M],
        handler: p.Cli.ResultCommandHandler[M, TResult],
        *,
        prog_name: str,
        args: Sequence[str] | None = None,
        success_formatter: t.Cli.SuccessMessageFormatter[TResult] | None = None,
    ) -> int:
        """Run one model-backed command as the whole CLI and return its exit code.

        The application holds exactly this command and no callback, so the
        framework builds it as a single command: options follow the program
        name directly, with no subcommand token. The command is named after
        ``prog_name``; its help is the model's docstring. Without a
        ``success_formatter`` a successful run prints nothing. ``args=None``
        reads ``sys.argv[1:]``. A domain failure prints its message once on
        stderr and returns ``c.Cli.EXIT_CODE_FAILURE``; a usage error keeps
        Click's message and ``c.Cli.EXIT_CODE_USAGE``. No ``SystemExit``
        leaves this call.

        Example:
            >>> from flext_cli import c, cli, m, r
            >>> class Greeting(m.BaseModel):
            ...     \"\"\"Greet one person.\"\"\"
            ...
            ...     name: str
            >>> cli.run_result_command(
            ...     Greeting,
            ...     lambda request: r[str].ok(f"Hello, {request.name}!"),
            ...     prog_name="greet",
            ...     args=["--name", "Ada"],
            ...     success_formatter=str,
            ... ) == c.Cli.EXIT_CODE_SUCCESS
            ✅ Hello, Ada!
            True

        Args:
            model_cls: Request model whose fields become the command options.
            handler: Operation receiving the validated request.
            prog_name: Program and command name shown in help and errors.
            args: Command-line tokens; ``sys.argv[1:]`` when omitted.
            success_formatter: Renders a successful value; silent when omitted.

        Returns:
            The process exit code of the run.

        """
        # The request model documents the command; its docstring is the help.
        description = cleandoc(model_cls.__doc__ or "")
        app = cls.create_group(help_text=description, name=prog_name)
        cls.register_result_command(
            app,
            route=cls.result_route(
                metadata=m.Cli.CommandMetadata(name=prog_name, help_text=description),
                model_cls=model_cls,
                handler=handler,
                success_formatter=(
                    (lambda _value: "")
                    if success_formatter is None
                    else success_formatter
                ),
            ),
        )
        outcome = cls.execute_app(app, prog_name=prog_name, args=args)
        if outcome.success:
            return c.Cli.EXIT_CODE_SUCCESS
        # The command already rendered its domain failure when it exited;
        # finalize_result would render it a second time.
        usage_code = u.Cli.framework_report_usage_error(outcome)
        return c.Cli.EXIT_CODE_FAILURE if usage_code is None else usage_code

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
        if (usage_code := u.Cli.framework_report_usage_error(result)) is not None:
            return usage_code
        u.Cli.commands_emit_result_error(result)
        # NOTE (multi-agent): the outermost CLI owns its process contract while
        # FlextCliCliPart05 remains the single error-emission boundary.
        return failure_exit_code


__all__: list[str] = ["FlextCliCliPart05"]
