"""Behavioral tests for flext_cli.protocols.FlextCliProtocols.

The public contract of ``FlextCliProtocols`` is its ``@runtime_checkable``
structural protocols: at runtime ``isinstance(obj, Protocol)`` must accept an
object that structurally conforms and reject one that does not. These tests
exercise that observable contract through the canonical ``p`` facade only --
never protocol internals.

Modules tested: flext_cli.protocols.FlextCliProtocols

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from pathlib import Path

import pytest

from flext_cli import t
from tests import p
from flext_tests import tm


class _ConformingSummary:
    """Object structurally conforming to ``SummaryStats``."""

    verb: str = "build"
    total: int = 3
    success: int = 2
    failed: int = 1
    skipped: int = 0
    elapsed: float = 1.5


class _PartialSummary:
    """Object missing most ``SummaryStats`` attributes."""

    verb: str = "build"


class _ConformingYamlModule:
    """Object structurally conforming to ``YamlModule``."""

    def dump(self, data: object, *, default_flow_style: bool = True) -> str:
        return ""


class _ConformingContext:
    """Object structurally conforming to ``PipelineStageContext``."""

    @property
    def workspace_root(self) -> Path:
        return Path()

    @property
    def shared(self) -> t.MutableJsonMapping:
        return {}

    @property
    def settings(self) -> t.JsonMapping:
        return {}


class TestsFlextCliProtocols:
    """Behavioral contract of the FlextCliProtocols runtime protocols."""

    def test_data_protocol_accepts_structurally_conforming_object(self) -> None:
        """A fully-populated object satisfies the data-attribute protocol."""
        tm.that(_ConformingSummary(), is_=p.Cli.SummaryStats)

    def test_data_protocol_rejects_object_missing_required_attributes(self) -> None:
        """An object missing declared attributes fails the protocol check."""
        assert not isinstance(_PartialSummary(), p.Cli.SummaryStats)

    def test_method_protocol_accepts_object_exposing_method(self) -> None:
        """An object exposing ``dump`` satisfies ``YamlModule``."""
        tm.that(_ConformingYamlModule(), is_=p.Cli.YamlModule)

    def test_method_protocol_rejects_object_without_method(self) -> None:
        """An object lacking ``dump`` is rejected by ``YamlModule``."""
        assert not isinstance(object(), p.Cli.YamlModule)

    def test_callable_protocol_accepts_plain_callable(self) -> None:
        """Any single-arg callable conforms to ``JsonValueProcessor``."""
        tm.that(lambda value: value, is_=p.Cli.JsonValueProcessor)

    def test_property_protocol_accepts_object_exposing_properties(self) -> None:
        """An object exposing all context properties satisfies the protocol."""
        tm.that(_ConformingContext(), is_=p.Cli.PipelineStageContext)

    def test_property_protocol_rejects_object_missing_a_property(self) -> None:
        """Missing a single required property fails ``PipelineStageContext``."""

        class _MissingSettings:
            @property
            def workspace_root(self) -> object: ...

            @property
            def shared(self) -> object: ...

        assert not isinstance(_MissingSettings(), p.Cli.PipelineStageContext)

    @pytest.mark.parametrize(
        "protocol_name",
        [
            "CommandEntry",
            "SummaryStats",
            "ProjectFailureInfo",
            "JsonValueProcessor",
            "YamlModule",
            "PipelineStageContext",
            "PipelineExecutor",
            "PipelineService",
        ],
    )
    def test_cli_protocols_are_runtime_checkable(self, protocol_name: str) -> None:
        """Each published protocol supports runtime ``isinstance`` without error."""
        protocol = getattr(p.Cli, protocol_name)
        tm.that(protocol, is_=type)
        # A runtime-checkable protocol answers isinstance instead of raising.
        tm.that({True, False}, has=isinstance(object(), protocol))

    @pytest.mark.parametrize(
        "protocol_name",
        [
            "CommandEntry",
            "SummaryStats",
            "YamlModule",
            "JsonValueProcessor",
            "PipelineExecutor",
            "PipelineService",
        ],
    )
    def test_cli_protocol_is_stable_singleton_under_namespace(
        self, protocol_name: str
    ) -> None:
        """Each CLI protocol resolves to one shared object under ``p.Cli``."""
        assert getattr(p.Cli, protocol_name) is getattr(p.Cli, protocol_name)

    def test_result_protocol_inherited_from_core_facade(self) -> None:
        """The CLI facade re-exposes the core ``Result`` protocol contract."""
        tm.that(p.Result, none=False)
        tm.that(p.Result, is_=type)
