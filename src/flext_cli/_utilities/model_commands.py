"""Thin model-command adapters shared through ``u.Cli``."""

from __future__ import annotations

import inspect

from pydantic import BaseModel
from pydantic.fields import FieldInfo

from flext_cli import p, t


class FlextCliUtilitiesModelCommandBuilder[M: BaseModel]:
    """Thin builder for direct model-backed command callables."""

    def __init__(
        self,
        model_class: type[M],
        handler: p.Cli.ModelCommandHandler[M],
        config: t.Cli.ConfigModel = None,
    ) -> None:
        """Store the canonical inputs for deferred command construction."""
        super().__init__()
        self.model_class = model_class
        self.handler = handler
        self.config = config

    def _resolve_default(
        self,
        field_name: str,
        field_info: FieldInfo,
    ) -> t.Cli.CliValue | type:
        if field_info.is_required():
            return inspect.Parameter.empty
        if self.config is not None and hasattr(self.config, field_name):
            return getattr(self.config, field_name)
        return field_info.get_default(call_default_factory=True)

    def build(self) -> t.Cli.CliCommand:
        """Build a direct callable with a real runtime signature."""
        model_fields: t.Cli.FieldInfoMapping = getattr(
            self.model_class,
            "model_fields",
            {},
        )
        parameters = [
            inspect.Parameter(
                name=field_name,
                kind=inspect.Parameter.KEYWORD_ONLY,
                default=self._resolve_default(field_name, field_info),
                annotation=field_info.annotation or str,
            )
            for field_name, field_info in model_fields.items()
            if field_info.exclude is not True
        ]
        signature = inspect.Signature(parameters)

        def command(**kwargs: t.Cli.CliValue) -> t.Cli.RuntimeValue:
            if self.config is not None:
                for field_name, field_value in kwargs.items():
                    if hasattr(self.config, field_name):
                        setattr(self.config, field_name, field_value)
            model = self.model_class.model_validate(kwargs)
            return self.handler(model)

        command_obj: object = command
        setattr(command_obj, "__signature__", signature)
        setattr(
            command_obj,
            "__annotations__",
            {parameter.name: parameter.annotation for parameter in parameters},
        )
        command.__annotations__["return"] = t.Cli.RuntimeValue
        return command


class FlextCliUtilitiesModelCommands:
    """Model command methods exposed directly on ``u.Cli``."""

    @staticmethod
    def build_model_command[M: BaseModel](
        model_class: type[M],
        handler: p.Cli.ModelCommandHandler[M],
        config: t.Cli.ConfigModel = None,
    ) -> t.Cli.CliCommand:
        """Build a model command through the canonical CLI service."""
        return FlextCliUtilitiesModelCommandBuilder(
            model_class=model_class,
            handler=handler,
            config=config,
        ).build()


__all__ = [
    "FlextCliUtilitiesModelCommandBuilder",
    "FlextCliUtilitiesModelCommands",
]
