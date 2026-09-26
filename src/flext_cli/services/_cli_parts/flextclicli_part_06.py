"""FLEXT CLI - Unified Typer abstraction service.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli import m, p, s, t, u

from .flextclicli_part_05 import FlextCliCli as FlextCliCliPart05


class FlextCliCli(FlextCliCliPart05):
    """Implementation part for FlextCliCli."""

    @classmethod
    def service_routes[S: s[p.Base]](
        cls, service_type: type[S], *, provide: t.Cli.NullaryOperation[S]
    ) -> tuple[m.Cli.ResultCommandRoute, ...]:
        """Derive one result route per operation of a service class.

        Routes come from ``u.service_operations(service_type)``: the kebab-case
        operation name, its summary as help, and its request model or the
        shared ``m.Cli.EmptyRequest``. ``provide`` builds the service only when
        a command executes, so ``--help`` constructs no adapter. A successful
        result value is rendered; rejected input exits non-zero with the
        ``ValidationError`` as the failure cause.
        """
        return tuple(
            m.Cli.ResultCommandRoute(
                name=operation.name.replace("_", "-"),
                help_text=operation.summary,
                model_cls=operation.request or m.Cli.EmptyRequest,
                handler=cls._operation_handler(operation, provide),
                success_formatter=cls._render_result_value,
            )
            for operation in u.service_operations(service_type)
        )

    @staticmethod
    def _operation_handler[S: s[p.Base]](
        operation: m.ServiceOperation, provide: t.Cli.NullaryOperation[S]
    ) -> p.Cli.ResultRouteHandler:
        """Bind one operation to the service instance built at execution."""

        def handle(params: t.Cli.ModelLike) -> p.Result[t.Cli.ResultValue]:
            run = getattr(provide(), operation.name)
            result: p.Result[t.Cli.ResultValue] = (
                run() if operation.request is None else run(params)
            )
            return result

        return handle

    @staticmethod
    def _render_result_value(value: t.Cli.ResultValue) -> str:
        """Render a successful operation value as text or JSON."""
        normalized = u.normalize_to_json_value(value)
        if isinstance(normalized, str):
            return normalized
        return u.to_json(normalized).decode()


__all__: list[str] = ["FlextCliCli"]
