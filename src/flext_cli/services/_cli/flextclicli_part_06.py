"""FLEXT CLI - Unified Typer abstraction service.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from functools import partial

from flext_core import FlextRuntime

from flext_cli import m, p, t, u
from flext_cli.services._cli import FlextCliCliPart05


class FlextCliCliPart06(FlextCliCliPart05):
    """Implementation part for FlextCliCliPart06."""

    @classmethod
    def service_routes[R: p.Base](
        cls,
        service_type: type[p.Service[R]],
        *,
        provide: t.Cli.NullaryOperation[p.Service[R]],
        owner: type | None = None,
        operation_prefix: str = "",
        success_formatter: t.Cli.ServiceMessageFormatter | None = None,
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
            owner: Inherited operation family, or the complete service by default.
            operation_prefix: Shared API prefix omitted from command names.
            success_formatter: Optional output formatter receiving the operation name.

        Returns:
            The resulting ``tuple[p.Cli.ResultCommandRoute, ...]``.

        """
        return tuple(
            cls.result_route(
                metadata=m.Cli.CommandMetadata(
                    name=(
                        operation.name.removeprefix(operation_prefix).replace("_", "-")
                    ),
                    help_text=operation.summary,
                ),
                model_cls=operation.request or m.Cli.EmptyRequest,
                handler=partial(cls._execute_operation, operation, provide),
                success_formatter=(
                    cls._render_result_value
                    if success_formatter is None
                    else partial(success_formatter, operation.name)
                ),
            )
            for operation in u.service_operations(service_type, owner=owner)
        )

    @staticmethod
    def _execute_operation[R: p.Base](
        operation: p.ServiceOperation,
        provide: t.Cli.NullaryOperation[p.Service[R]],
        params: t.Cli.ModelLike,
    ) -> p.Result[t.Cli.ResultValue]:
        """Invoke the catalogued function without a late method-name lookup.

        Returns:
            The resulting ``p.Result[t.Cli.ResultValue]``.

        """
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
