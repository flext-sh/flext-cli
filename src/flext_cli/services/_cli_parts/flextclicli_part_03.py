"""FLEXT CLI - Unified Typer abstraction service.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from inspect import Parameter

from typer.testing import CliRunner

from flext_cli import (
    c,
    p,
    r,
    t,
    u,
)
from flext_cli.services._cli_parts.flextclicli_part_01 import (
    FlextCliCli as FlextCliCliPart01,
)
from flext_cli.services._cli_parts.flextclicli_part_02 import (
    FlextCliCli as FlextCliCliPart02,
)


class FlextCliCli(FlextCliCliPart02):
    """Implementation part for FlextCliCli."""

    @classmethod
    def model_command[M: t.Cli.ModelLike](
        cls,
        model_cls: t.Cli.ModelType[M],
        handler: p.Cli.ModelCommandHandler[M],
        settings: t.Cli.ModelLike | None = None,
    ) -> t.Cli.CliCommand:
        """Build a Typer command directly from a Pydantic request model."""
        parameters: t.MutableSequenceOf[Parameter] = []
        annotations: t.Cli.CliAnnotations = {"return": type(None)}
        fields = getattr(model_cls, "model_fields", {})
        for field_name, field_info in fields.items():
            if getattr(field_info, "exclude", None) is True:
                continue
            parameter, annotation = cls._build_model_parameter(
                field_name,
                field_info,
                settings,
            )
            parameters.append(parameter)
            annotations[field_name] = annotation
        command: FlextCliCliPart01._ModelCommand[M] = cls._ModelCommand(
            settings=settings,
            handler=handler,
            model_cls=model_cls,
            parameters=parameters,
        )
        command.__annotations__ = dict(annotations)
        return command

    @classmethod
    def derive_model[M: t.Cli.ModelLike](
        cls,
        model_cls: type[M],
        *sources: t.Cli.ModelSource,
        overrides: t.ScalarMapping | None = None,
    ) -> M:
        """Derive a target Pydantic model from ordered model/mapping sources."""
        merged: t.MutableJsonMapping = {}
        for source in sources:
            merged.update(u.Cli.model_source_data(model_cls, source))
        if overrides is not None:
            merged.update(u.Cli.model_source_data(model_cls, overrides))
        validated: M = model_cls.model_validate(merged)
        return validated

    @staticmethod
    def create_cli_runner(
        *,
        charset: str = c.Cli.ENCODING_DEFAULT,
        env: t.StrMapping | None = None,
        echo_stdin: bool = False,
    ) -> p.Result[t.Cli.TyperRunner]:
        """Create a Typer/Click test runner for real CLI execution tests."""
        if echo_stdin:
            return r[t.Cli.TyperRunner].fail(
                c.Cli.ERR_CLI_RUNNER_ECHO_STDIN_UNSUPPORTED,
            )
        runner = CliRunner(
            charset=charset,
            env=dict(env) if env is not None else None,
        )
        return r[t.Cli.TyperRunner].ok(runner)


__all__: list[str] = ["FlextCliCli"]
