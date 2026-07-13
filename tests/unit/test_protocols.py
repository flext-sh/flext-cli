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
from tests.protocols import p


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
        assert isinstance(_ConformingSummary(), p.Cli.SummaryStats)

    def test_data_protocol_rejects_object_missing_required_attributes(
        self,
    ) -> None:
        """An object missing declared attributes fails the protocol check."""
        assert not isinstance(_PartialSummary(), p.Cli.SummaryStats)

    def test_method_protocol_accepts_object_exposing_method(self) -> None:
        """An object exposing ``dump`` satisfies ``YamlModule``."""
        assert isinstance(_ConformingYamlModule(), p.Cli.YamlModule)

    def test_method_protocol_rejects_object_without_method(self) -> None:
        """An object lacking ``dump`` is rejected by ``YamlModule``."""
        assert not isinstance(object(), p.Cli.YamlModule)

    def test_callable_protocol_accepts_plain_callable(self) -> None:
        """Any single-arg callable conforms to ``JsonValueProcessor``."""
        assert isinstance(lambda value: value, p.Cli.JsonValueProcessor)

    def test_property_protocol_accepts_object_exposing_properties(self) -> None:
        """An object exposing all context properties satisfies the protocol."""
        assert isinstance(_ConformingContext(), p.Cli.PipelineStageContext)

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
        assert isinstance(protocol, type)
        # A runtime-checkable protocol answers isinstance instead of raising.
        assert isinstance(object(), protocol) in {True, False}

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
    def test_top_level_protocol_is_same_object_as_cli_namespace(
        self, protocol_name: str
    ) -> None:
        """MRO exposure guarantees one shared protocol object across namespaces."""
        assert getattr(p, protocol_name) is getattr(p.Cli, protocol_name)

    def test_result_protocol_inherited_from_core_facade(self) -> None:
        """The CLI facade re-exposes the core ``Result`` protocol contract."""
        assert p.Result is not None
        assert isinstance(p.Result, type)
