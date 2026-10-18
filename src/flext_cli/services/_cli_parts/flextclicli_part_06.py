"""FLEXT CLI - Unified Typer abstraction service.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from functools import partial

from flext_core import FlextRuntime

from flext_cli import m, p, t, u
from flext_cli.services._cli_parts import FlextCliCliPart05


class FlextCliCliPart06(FlextCliCliPart05):
    """Implementation part for FlextCliCliPart06."""

    @classmethod
    def service_routes[R: p.Base](
        cls,
        service_type: type[p.Service[R]],
        *,
        provide: t.Cli.NullaryOperation[p.Service[R]],
    ) -> tuple[p.Cli.ResultCommandRoute, ...]:
        """Derive one result route per operation of a core service class.

        Routes come from ``u.service_operations(service_type)``: the kebab-case
        operation name, its summary as help, and its request model or the
        shared ``m.Cli.EmptyRequest``. ``provide`` builds the service only when
        a command executes, so ``--help`` constructs no adapter. A successful
        result value is rendered; rejected input renders its cause on stdout
        and exits non-zero with the ``ValidationError`` as the failure cause.
        Any ``FlextService`` subclass conforms, including sibling service
        hierarchies that share the core contract without the CLI base.

        Args:
            service_type: Core service class whose operations become routes.
            provide: Callable building the service instance at execution time.

        Returns:
            The resulting ``tuple[p.Cli.ResultCommandRoute, ...]``.

        """
        return tuple(
            m.Cli.ResultCommandRoute(
                name=operation.name.replace("_", "-"),
                help_text=operation.summary,
                model_cls=operation.request or m.Cli.EmptyRequest,
                handler=partial(cls._execute_operation, operation, provide),
                success_formatter=cls._render_result_value,
            )
            for operation in u.service_operations(service_type)
        )

    @staticmethod
    def _execute_operation[R: p.Base](
        operation: p.ServiceOperation,
        provide: t.Cli.NullaryOperation[p.Service[R]],
        params: t.Cli.ModelLike,
    ) -> p.Result[t.Cli.ResultValue]:
        """Invoke the catalogued function without a late method-name lookup."""
        service = provide()
        return (
            operation.handler(service)
            if operation.request is None
            else operation.handler(service, params)
        )

    @staticmethod
    def _render_result_value(value: t.Cli.ResultValue) -> str:
        """Render a successful operation value as text or JSON.

        Returns:
            The resulting ``str``.

        """
        normalized = FlextRuntime.normalize_to_json_value(value)
        if isinstance(normalized, str):
            return normalized
        return u.to_json(normalized).decode()


__all__: list[str] = ["FlextCliCliPart06"]
