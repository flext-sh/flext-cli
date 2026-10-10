"""Higher-level CLI structural contracts.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Callable, Iterator, Mapping, MutableMapping, Sequence
from pathlib import Path
from typing import Protocol, TextIO, runtime_checkable

from flext_cli import t
from flext_cli._protocols import FlextCliProtocolsBase


class FlextCliProtocolsDomain:
    """CLI domain protocols layered on top of base callable contracts."""

    type ResultRouteHandler = Callable[..., FlextCliProtocolsBase.ErasedCommandResult]

    @runtime_checkable
    class JsonValueProcessor(Protocol):
        """Protocol for JSON-compatible value processors."""

        def __call__(self, value: t.JsonValue) -> t.JsonValue:
            """Transform one JSON-compatible value."""
            ...

    @runtime_checkable
    class YamlAnchorNode(Protocol):
        """ruamel.yaml node surface that can carry YAML anchors.

        NOTE (multi-agent): mirrors the minimal ``yaml_set_anchor`` contract of
        ruamel ``CommentedBase``. Consumed through a ``TypeGuard`` + ``hasattr``
        check (not ``isinstance``) so leaf modules never import ruamel classes.
        """

        def yaml_set_anchor(self, value: str | None) -> None:
            """Set or clear the YAML anchor on the node."""
            ...

    @runtime_checkable
    class YamlCommentSurface(Protocol):
        """ruamel.yaml ``Comment`` surface reached through ``CommentedBase.ca``.

        NOTE (multi-agent): mirrors the consumed slice of ruamel ``Comment``
        (comment payload plus the per-key/item comment slot mapping) so leaf
        modules keep fully typed access; consumed through ``cast`` because the
        ruamel property is unannotated and the module already imports ruamel.
        """

        comment: object
        items: MutableMapping[str, Sequence[object]]

    @runtime_checkable
    class YamlCommentCarrier(Protocol):
        """ruamel.yaml node exposing its comment surface through ``ca``."""

        ca: FlextCliProtocolsDomain.YamlCommentSurface

    @runtime_checkable
    class YamlBlockStyleSetter(Protocol):
        """ruamel.yaml block-style surface reached through ``CommentedBase.fa``."""

        def set_block_style(self) -> None:
            """Force block-style rendering on the node."""
            ...

    @runtime_checkable
    class YamlFlowStyleCarrier(Protocol):
        """ruamel.yaml node exposing its style surface through ``fa``."""

        fa: FlextCliProtocolsDomain.YamlBlockStyleSetter

    @runtime_checkable
    class YamlCommentKeySetter(Protocol):
        """ruamel.yaml pre/post-key comment insertion surface of ``CommentedMap``."""

        def yaml_set_comment_before_after_key(
            self,
            key: str,
            before: str | None = None,
            indent: int = 0,
            after: str | None = None,
            after_indent: int | None = None,
        ) -> None:
            """Insert one comment before or after one mapping key."""
            ...

    @runtime_checkable
    class YamlRoundtripEngine(Protocol):
        """ruamel.yaml round-trip engine surface consumed by the YAML engine.

        NOTE (multi-agent): mirrors the configured slice of ``ruamel.yaml.YAML``
        (quote preservation, width, indent policy, load/dump) so the engine's
        load/dump calls keep fully typed signatures; consumed through ``cast``.
        """

        preserve_quotes: bool
        width: int

        def indent(
            self,
            *,
            mapping: int,
            sequence: int,
            offset: int,
        ) -> None:
            """Configure block indentation for mappings and sequences."""
            ...

        def load(self, stream: TextIO | str) -> t.Cli.YamlNode:
            """Parse one YAML document from a stream or text."""
            ...

        def dump(self, data: t.Cli.YamlNode, stream: TextIO) -> None:
            """Serialize one YAML tree to a text stream."""
            ...

    @runtime_checkable
    class XlsxConditionalFormattingList(Protocol):
        """openpyxl conditional-formatting registry surface of one worksheet.

        NOTE (multi-agent): openpyxl-stubs leaves ``add`` parameters and rule
        lookups ``Incomplete``/unannotated; this pins the consumed contract.
        """

        def add(self, range_string: str, cf_rule: object) -> None:
            """Register one conditional-format rule over one cell range."""
            ...

        def __getitem__(self, key: object) -> Sequence[object]:
            """Return the rules attached to one conditional-format entry."""
            ...

        def __iter__(self) -> Iterator[object]:
            """Iterate the registered conditional-format entries."""
            ...

    @runtime_checkable
    class XlsxDataValidationSurface(Protocol):
        """openpyxl data-validation range-attachment surface."""

        def add(self, cell: str) -> None:
            """Attach the validation to one cell range reference."""
            ...

    @runtime_checkable
    class JinjaTemplateRenderer(Protocol):
        """jinja2 template render surface consumed by the template utilities."""

        def render(self, variables: Mapping[str, object]) -> str:
            """Render the template with one variable mapping."""
            ...

    @runtime_checkable
    class JsonSchemaValidator(Protocol):
        """jsonschema validator surface consumed by config validation."""

        def validate(self, instance: object) -> None:
            """Validate one instance; raise on the first violation."""
            ...

    @runtime_checkable
    class XlsxFontStyleSurface(Protocol):
        """openpyxl font style surface consumed by the style readers.

        NOTE (multi-agent): openpyxl-stubs types these members as unparameterized
        ``Alias`` descriptors (Unknown); the surface pins them as ``object`` and
        call sites narrow to the real runtime value types.
        """

        size: object
        bold: object
        italic: object
        underline: object

    @runtime_checkable
    class XlsxProtectionSurface(Protocol):
        """openpyxl cell-protection surface consumed by snapshot values."""

        locked: object
        hidden: object

    @runtime_checkable
    class XlsxRowDimensionSurface(Protocol):
        """openpyxl row-dimension surface consumed by snapshot structure."""

        height: object

    @runtime_checkable
    class DocxParagraphFormatSurface(Protocol):
        """python-docx paragraph-format surface consumed by readers and tests.

        NOTE (multi-agent): python-docx annotates these properties without
        return types (Unknown); the surface pins them as ``object`` and call
        sites narrow to the real runtime value types.
        """

        alignment: object
        keep_together: object
        keep_with_next: object
        page_break_before: object
        widow_control: object

    @runtime_checkable
    class ModelCommandHandler[TParams: t.Cli.ModelLike](Protocol):
        """Protocol for model-driven CLI command execution."""

        def __call__(self, params: TParams, /) -> t.JsonValue:
            """Execute one model-backed CLI command and return its normalized value."""
            ...

    @runtime_checkable
    class CommandEntry(Protocol):
        """Protocol for command registry entries."""

        name: str
        # mro-j47u (codex): callable behavior remains in the p facade.
        handler: FlextCliProtocolsBase.CliCommandWrapper

    @runtime_checkable
    class ResultCommandRoute(Protocol):
        """Protocol for declarative result-route registration."""

        # mro-j47u (codex): read-only properties preserve frozen-model covariance.
        @property
        def name(self) -> str:
            """The command name."""
            ...

        @property
        def help_text(self) -> str:
            """The user-facing help text."""
            ...

        @property
        def model_cls(self) -> t.ModelClass[t.Cli.ModelLike]:
            """The validated input model class."""
            ...

        @property
        def handler(self) -> FlextCliProtocolsDomain.ResultRouteHandler:
            """The type-erased result handler."""
            ...

        @property
        def success_message(self) -> str | None:
            """The static success message, when configured."""
            ...

        @property
        def success_formatter(
            self,
        ) -> t.Cli.SuccessMessageFormatter[t.Cli.ResultValue] | None:
            """The dynamic success formatter, when configured."""
            ...

        @property
        def success_type(self) -> t.Cli.MessageType:
            """The success output style."""
            ...

    @runtime_checkable
    class DeclarativeRuleType[TRule](Protocol):
        """Class contract for one settings-backed declarative rule implementation."""

        RULE_MATCHERS: t.Cli.RuleMatchers

        def __call__(self, settings: t.JsonMapping, /) -> TRule:
            """Instantiate one runtime rule from one validated rule definition."""
            ...

    @runtime_checkable
    class DeclarativeFileRuleType[TRule](Protocol):
        """Class contract for one no-arg declarative file-rule implementation."""

        RULE_MATCHERS: t.Cli.RuleMatchers

        def __call__(self) -> TRule:
            """Instantiate one file rule without extra runtime settings."""
            ...

    @runtime_checkable
    class SummaryStats(Protocol):
        """Workspace orchestration summary payload contract."""

        @property
        def verb(self) -> str:
            """Verb label for the summary block."""
            ...

        @property
        def total(self) -> int:
            """Total processed items."""
            ...

        @property
        def success(self) -> int:
            """Successful items."""
            ...

        @property
        def failed(self) -> int:
            """Failed items."""
            ...

        @property
        def skipped(self) -> int:
            """Skipped items."""
            ...

        @property
        def elapsed(self) -> float:
            """Elapsed time in seconds."""
            ...

    @runtime_checkable
    class ProjectFailureInfo(Protocol):
        """Per-project failure descriptor for verbose diagnostics."""

        @property
        def project(self) -> str:
            """Project name."""
            ...

        @property
        def elapsed(self) -> float:
            """Elapsed time in seconds."""
            ...

        @property
        def error_count(self) -> int:
            """Total project errors."""
            ...

        @property
        def log_path(self) -> Path:
            """Path to the project log."""
            ...

        @property
        def max_show(self) -> int:
            """Maximum errors to render."""
            ...

        @property
        def errors(self) -> t.SequenceOf[str]:
            """Rendered error excerpt lines."""
            ...


__all__: list[str] = ["FlextCliProtocolsDomain"]
