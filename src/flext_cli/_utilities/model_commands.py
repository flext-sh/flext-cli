"""Thin model-command adapters shared through ``u.Cli``."""

from __future__ import annotations

import inspect

from flext_core import m

from flext_cli import p, t


class FlextCliUtilitiesModelCommandBuilder[M: m.BaseModel]:
    """Thin builder for direct model-backed command callables."""

    def __init__(
        self,
        model_class: type[M],
        handler: p.Cli.ModelCommandHandler[M],
        settings: m.BaseModel | None = None,
    ) -> None:
        """Store the canonical inputs for deferred command construction."""
        super().__init__()
        self.model_class = model_class
        self.handler = handler
        self.settings = settings

    def _resolve_default(
        self,
        field_name: str,
        field_info: m.FieldInfo,
    ) -> t.Cli.CliValue | type:
        if getattr(field_info, "is_required")():
            return inspect.Parameter.empty
        if self.settings is not None and hasattr(self.settings, field_name):
            return getattr(self.settings, field_name)
        return getattr(field_info, "get_default")(call_default_factory=True)

    def build(self) -> t.Cli.CliCommand:
        """Build a direct callable with a real runtime signature."""
        model_fields = getattr(self.model_class, "model_fields", {})
        parameters = [
            inspect.Parameter(
                name=field_name,
                kind=inspect.Parameter.KEYWORD_ONLY,
                default=self._resolve_default(field_name, field_info),
                annotation=getattr(field_info, "annotation", None) or str,
            )
            for field_name, field_info in model_fields.items()
            if getattr(field_info, "exclude", None) is not True
        ]
        signature = inspect.Signature(parameters)

        def command(**kwargs: t.Cli.CliValue) -> t.JsonValue:
            if self.settings is not None:
                for field_name, field_value in kwargs.items():
                    if hasattr(self.settings, field_name):
                        setattr(self.settings, field_name, field_value)
            model = self.model_class.model_validate(kwargs)
            return self.handler(model)

        command_obj = command
        setattr(command_obj, "__signature__", signature)
        setattr(
            command_obj,
            "__annotations__",
            {parameter.name: parameter.annotation for parameter in parameters},
        )
        command.__annotations__["return"] = t.JsonValue
        return command


class FlextCliUtilitiesModelCommands:
    """Model command methods exposed directly on ``u.Cli``."""

    @staticmethod
    def model_source_data(
        model_cls: type[m.BaseModel],
        source: t.Cli.ModelSource,
    ) -> t.ScalarMapping:
        """Extract only target-compatible fields from a model or mapping source."""
        raw_source: t.ScalarMapping
        if isinstance(source, m.BaseModel):
            raw_source = source.model_dump(exclude_none=True)
        else:
            raw_source = source
        return {
            field_name: raw_source[field_name]
            for field_name in model_cls.model_fields
            if field_name in raw_source and raw_source[field_name] is not None
        }

    @classmethod
    def derive_model[M: m.BaseModel](
        cls,
        model_cls: type[M],
        *sources: t.Cli.ModelSource,
        overrides: t.ScalarMapping | None = None,
    ) -> M:
        """Derive a target model from ordered model/mapping sources."""
        merged: t.MutableScalarMapping = {}
        for source in sources:
            merged.update(cls.model_source_data(model_cls, source))
        if overrides is not None:
            merged.update(cls.model_source_data(model_cls, overrides))
        validated: M = model_cls.model_validate(merged)
        return validated

    @staticmethod
    def build_model_command[M: m.BaseModel](
        model_class: type[M],
        handler: p.Cli.ModelCommandHandler[M],
        settings: m.BaseModel | None = None,
    ) -> t.Cli.CliCommand:
        """Build a model command through the canonical CLI service."""
        return FlextCliUtilitiesModelCommandBuilder(
            model_class=model_class,
            handler=handler,
            settings=settings,
        ).build()


__all__: t.MutableSequenceOf[str] = [
    "FlextCliUtilitiesModelCommandBuilder",
    "FlextCliUtilitiesModelCommands",
]
