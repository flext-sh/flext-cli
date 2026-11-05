"""FLEXT CLI - Unified Typer abstraction service.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Mapping, MutableSequence, Sequence
from inspect import Parameter, Signature

from flext_cli import c, p, r, t, u
from flext_cli.services._cli import FlextCliCliPart01, FlextCliCliPart02


class FlextCliCliPart03(FlextCliCliPart02):
    """Implementation part for FlextCliCliPart03."""

    @classmethod
    def model_command[M: t.Cli.ModelLike, TResult: t.JsonPayload](
        cls,
        model_cls: t.ModelClass[M],
        handler: p.Cli.ModelCommandHandler[M, TResult],
        settings: t.Cli.ModelLike | None = None,
    ) -> t.Cli.CliCommand[TResult]:
        """Build a Typer command directly from a Pydantic request model.

        A field marked ``exclude=True`` gets no option, so it must carry a
        default: a required excluded field raises ``TypeError`` at build time.
        Rejected input raises the ``ValidationError``; result routes register
        through ``register_result_command`` to exit non-zero instead.

        Args:
            model_cls: Request model whose fields declare the options.
            handler: Callable receiving the parsed request model.
            settings: Optional model instance supplying current field values.

        Returns:
            The command preserving the handler's return type.

        """
        command: FlextCliCliPart01._ModelCommand[M, TResult] = cls._ModelCommand(
            handler=handler,
            model_cls=model_cls,
            signature=cls._model_signature(model_cls, settings),
            result_border=False,
        )
        return command

    @classmethod
    def _model_signature(
        cls,
        model_cls: t.ModelClass[t.Cli.ModelLike],
        settings: t.Cli.ModelLike | None,
    ) -> Signature:
        """Declare one keyword-only option per non-excluded request field.

        Returns:
            The option signature of the request model.

        Raises:
            TypeError: If an excluded field is required.

        """
        parameters: MutableSequence[Parameter] = []
        for field_name, field_info in model_cls.model_fields.items():
            if field_info.exclude is True:
                if field_info.is_required():
                    raise TypeError(
                        c.Cli.ERR_REQUIRED_EXCLUDED_FIELD_FMT.format(
                            model=model_cls.__name__,
                            field_name=field_name,
                        ),
                    )
                continue
            parameters.append(
                cls._build_model_parameter(field_name, field_info, settings),
            )
        return Signature(parameters, return_annotation=type(None))

    @staticmethod
    def invoke_app(
        app: p.Cli.Application,
        *,
        args: Sequence[str] | None = None,
        charset: str = c.DEFAULT_ENCODING,
        env: Mapping[str, str] | None = None,
    ) -> p.Result[p.Cli.InvocationResult]:
        """Invoke an application through the private real-framework boundary.

        A foreign application or an invalid runner argument is a caller defect
        and raises; the command outcome travels in the invocation result.

        Args:
            app: Application to invoke.
            args: Optional command-line tokens passed to the application.
            charset: Encoding used to decode the command output.
            env: Optional environment mapping for the invocation.

        Returns:
            The resulting ``p.Result[p.Cli.InvocationResult]``.

        """
        return r[p.Cli.InvocationResult].ok(
            u.Cli.framework_invoke(app, args=args, charset=charset, env=env),
        )


__all__: list[str] = ["FlextCliCliPart03"]
