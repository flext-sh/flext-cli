"""FLEXT CLI - Unified Typer abstraction service.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from inspect import Parameter
from typing import TYPE_CHECKING

from flext_cli import c, m, p, r, t, u

from .flextclicli_part_02 import FlextCliCli as FlextCliCliPart02

if TYPE_CHECKING:
    # mro-j47u (codex): the earlier MRO part is referenced only by annotation;
    # inspect.Parameter remains runtime because it constructs the CLI signature.
    from .flextclicli_part_01 import FlextCliCli as FlextCliCliPart01


class FlextCliCli(FlextCliCliPart02):
    """Implementation part for FlextCliCli."""

    @classmethod
    def model_command[M: t.Cli.ModelLike](
        cls,
        model_cls: t.ModelClass[M],
        handler: p.Cli.ModelCommandHandler[M],
        settings: t.Cli.ModelLike | None = None,
        *,
        result_border: bool = False,
    ) -> t.Cli.CliCommand:
        """Build a Typer command directly from a Pydantic request model.

        A field marked ``exclude=True`` gets no option, so it must carry a
        default: a required excluded field raises ``TypeError`` at build time.
        ``result_border`` turns rejected input into ``e.fail_validation`` with a
        non-zero exit instead of raising the ``ValidationError``.
        """
        parameters: t.MutableSequenceOf[Parameter] = []
        annotations: t.Cli.CliAnnotations = {"return": type(None)}
        fields = model_cls.model_fields
        for field_name, field_info in fields.items():
            if field_info.exclude is True:
                if field_info.is_required():
                    raise TypeError(
                        c.Cli.ERR_REQUIRED_EXCLUDED_FIELD_FMT.format(
                            model=model_cls.__name__, field_name=field_name
                        )
                    )
                continue
            parameter, annotation = cls._build_model_parameter(
                field_name, field_info, settings
            )
            parameters.append(parameter)
            annotations[field_name] = annotation
        command: FlextCliCliPart01._ModelCommand[M] = cls._ModelCommand(
            handler=handler,
            model_cls=model_cls,
            parameters=parameters,
            result_border=result_border,
        )
        command.__annotations__ = dict(annotations)
        return command

    @staticmethod
    def invoke_app(
        app: p.Cli.Application,
        *,
        args: t.StrSequence | None = None,
        charset: str = c.Cli.ENCODING_DEFAULT,
        env: t.StrMapping | None = None,
    ) -> p.Result[m.Cli.InvocationResult]:
        """Invoke an application through the private real-framework boundary.

        A foreign application or an invalid runner argument is a caller defect
        and raises; the command outcome travels in the invocation result.
        """
        return r[m.Cli.InvocationResult].ok(
            u.Cli.framework_invoke(app, args=args, charset=charset, env=env)
        )


__all__: list[str] = ["FlextCliCli"]
