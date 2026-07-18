"""Generic TOML operation models with Builder DSL, flat in ``m.Cli.Toml*``.

flext-cli owns the TOML domain: these declarative operation models
(``TomlSetOp`` / ``TomlListOp`` / ``TomlRemoveOp`` / ``TomlOperation`` /
``TomlPhaseConfig``) are consumed by any project that syncs a TOML document,
paired with the ``u.Cli.toml_*`` utilities and ``t.Cli.Toml*`` types.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from itertools import chain
from typing import Annotated, Literal, Self

from flext_cli._constants.enums import FlextCliConstantsEnums as _enum
from flext_core import m, t
from collections.abc import Callable
# Pyproject "tool" table name — the default TOML root for tool configuration.
_TOOL_TABLE: str = "tool"


class FlextCliModelsToml:
    """TOML operation models exposed FLAT through ``m.Cli.Toml*``."""

    class TomlSetOp(m.ContractModel):
        """Set one TOML key to one JSON-compatible value."""

        kind: Literal[_enum.TomlOperationKind.SET] = m.Field(
            _enum.TomlOperationKind.SET,
            description="Operation kind",
            validate_default=True,
        )
        key: str = m.Field(description="TOML key name")
        value: t.JsonValue = m.Field(description="JSON-compatible value")

    class TomlListOp(m.ContractModel):
        """Set or merge one TOML string list."""

        kind: Literal[_enum.TomlOperationKind.LIST] = m.Field(
            _enum.TomlOperationKind.LIST,
            description="Operation kind",
            validate_default=True,
        )
        key: str = m.Field(description="TOML key name")
        values: t.StrSequence = m.Field(description="Expected values")
        strategy: Annotated[
            _enum.TomlMergeMode,
            m.Field(description="Merge strategy", validate_default=True),
        ] = _enum.TomlMergeMode.REPLACE
        sort: Annotated[
            bool, m.Field(description="Sort values before sync", validate_default=True)
        ] = True

    class TomlRemoveOp(m.ContractModel):
        """Remove one TOML key, optionally from a nested relative table."""

        kind: Literal[_enum.TomlOperationKind.REMOVE] = m.Field(
            _enum.TomlOperationKind.REMOVE,
            description="Operation kind",
            validate_default=True,
        )
        key: str = m.Field(description="Key to remove")
        table_path: Annotated[
            t.StrSequence,
            m.Field(description="Relative sub-table path", validate_default=True),
        ] = ()

    type TomlOperation = Annotated[
        TomlSetOp | TomlListOp | TomlRemoveOp, m.Field(discriminator="kind")
    ]

    class TomlPhaseConfig(m.ContractModel):
        """Declarative TOML phase with inline Builder DSL."""

        name: str = m.Field(description="Phase name")
        root_path: Annotated[
            t.StrSequence, m.Field(description="Root path before table_path")
        ] = (_TOOL_TABLE,)
        table_path: Annotated[
            t.StrSequence, m.Field(description="Primary table path")
        ] = ()
        operations: Annotated[
            t.SequenceOf[FlextCliModelsToml.TomlOperation],
            m.Field(description="Declarative TOML operations"),
        ] = ()
        nested_tables: Annotated[
            t.SequenceOf[FlextCliModelsToml.TomlPhaseConfig],
            m.Field(description="Nested TOML phase configs"),
        ] = ()
        custom_handler: Annotated[
            Callable[..., t.StrSequence] | None,
            m.Field(exclude=True, description="Custom handler"),
        ] = None

        class Builder(m.Builder.Identity["FlextCliModelsToml.TomlPhaseConfig"]):
            """Fluent builder for ``m.Cli.TomlPhaseConfig``."""

            def __init__(self, name: str) -> None:
                super().__init__(state=FlextCliModelsToml.TomlPhaseConfig(name=name))

            @classmethod
            def _nested_operations(
                cls,
                *,
                values: t.SequenceOf[tuple[str, t.JsonValue]] = (),
                lists: t.SequenceOf[t.StrSequencePair] = (),
                deprecated_keys: t.StrSequence = (),
            ) -> tuple[FlextCliModelsToml.TomlOperation, ...]:
                """Nested operations."""
                return tuple(
                    chain(
                        (
                            FlextCliModelsToml.TomlSetOp(key=key, value=value)
                            for key, value in values
                        ),
                        (
                            FlextCliModelsToml.TomlListOp(
                                key=key, values=tuple(entries)
                            )
                            for key, entries in lists
                        ),
                        (
                            FlextCliModelsToml.TomlRemoveOp(key=key)
                            for key in deprecated_keys
                        ),
                    )
                )

            def operation(
                self,
                operation_type: type[m.ContractModel],
                /,
                **data: t.JsonValue | t.JsonPayload | t.SequenceOf[t.JsonPayload],
            ) -> Self:
                """Operation."""
                operation_item = operation_type.model_validate(data)
                replaced: Self = self._replace(
                    self.state.model_copy(
                        update={"operations": (*self.state.operations, operation_item)}
                    )
                )
                return replaced

            def root(self, *path: str) -> Self:
                """Root."""
                result: Self = self._path("root_path", *path)
                return result

            def table(self, *path: str) -> Self:
                """Table."""
                result: Self = self._path("table_path", *path)
                return result

            def value(self, key: str, value: t.JsonValue) -> Self:
                """Value."""
                return self.operation(
                    FlextCliModelsToml.TomlSetOp, key=key, value=value
                )

            def list(
                self,
                key: str,
                values: t.StrSequence,
                *,
                strategy: _enum.TomlMergeMode = _enum.TomlMergeMode.REPLACE,
                sort: bool = True,
            ) -> Self:
                """List."""
                return self.operation(
                    FlextCliModelsToml.TomlListOp,
                    key=key,
                    values=tuple(values),
                    strategy=strategy,
                    sort=sort,
                )

            def deprecated(self, key: str, *sub_path: str) -> Self:
                """Mark a key as deprecated by scheduling its removal."""
                return self.operation(
                    FlextCliModelsToml.TomlRemoveOp, key=key, table_path=tuple(sub_path)
                )

            def nested(
                self,
                *path: str,
                values: t.SequenceOf[tuple[str, t.JsonValue]] = (),
                lists: t.SequenceOf[t.StrSequencePair] = (),
                deprecated_keys: t.StrSequence = (),
            ) -> Self:
                """Nested."""
                nested_table = FlextCliModelsToml.TomlPhaseConfig(
                    name=self.state.name,
                    root_path=(),
                    table_path=tuple(path),
                    operations=tuple(
                        self._nested_operations(
                            values=values, lists=lists, deprecated_keys=deprecated_keys
                        )
                    ),
                )
                replaced: Self = self._replace(
                    self.state.model_copy(
                        update={
                            "nested_tables": (*self.state.nested_tables, nested_table)
                        }
                    )
                )
                return replaced

            def handler(self, fn: Callable[..., t.StrSequence]) -> Self:
                """Set a custom handler function."""
                replaced: Self = self._replace(
                    self.state.model_copy(update={"custom_handler": fn})
                )
                return replaced


__all__: list[str] = ["FlextCliModelsToml"]
