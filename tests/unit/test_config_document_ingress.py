"""Native textual ingress preserves strict Python domain contracts.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests import c, m, t, tm, u

if TYPE_CHECKING:
    from pathlib import Path


class TestsFlextCliConfigDocumentIngress:
    """Exercise YAML representation decoding through the public config owner."""

    class Contract(m.ContractModel):
        """A strict domain retains enum members and fixed tuple constraints."""

        kind: t.DocumentInput[c.HandlerType] = c.DEFAULT_HANDLER_TYPE
        kinds: t.DocumentInput[tuple[t.DocumentInput[c.HandlerType], ...]] = ()
        labels: t.DocumentInput[tuple[str, str]] = ("source", "target")

    @staticmethod
    @pytest.mark.parametrize("member", c.HandlerType)
    def test_yaml_tokens_materialize_once_before_domain_validation(
        member: c.HandlerType,
    ) -> None:
        """The textual source yields actual enum members and domain tuples."""
        source: t.JsonMapping = {
            "kind": member.value,
            "kinds": [member.value],
            "labels": ["left", "right"],
        }
        parsed = tm.ok(u.Cli.yaml_parse(u.Cli.yaml_dump_str(source)))

        payload = u.Cli.config_decode(
            parsed, TestsFlextCliConfigDocumentIngress.Contract
        )

        tm.ok(payload.kind is member)
        tm.ok(payload.kinds[0] is member)
        tm.that(payload.labels, eq=("left", "right"))
        tm.ok(payload.model_dump()["kind"] is member)
        tm.that(payload.model_dump(mode="json")["kind"], eq=member.value)
        restored = type(payload).model_validate_json(payload.model_dump_json())
        tm.ok(restored.kind is member)
        tm.ok(restored.kinds[0] is member)

    @staticmethod
    def test_document_context_preserves_typed_defaults() -> None:
        """Absent enum/tuple inputs keep their validated typed defaults."""
        payload = u.Cli.config_decode({}, TestsFlextCliConfigDocumentIngress.Contract)

        tm.ok(payload.kind is c.DEFAULT_HANDLER_TYPE)
        tm.that(payload.kinds, empty=True)
        tm.that(payload.labels, eq=("source", "target"))

    @staticmethod
    @pytest.mark.parametrize(
        "source",
        [
            {"kind": None},
            {"kind": True},
            {"kind": "not-a-handler-kind"},
            {"kinds": ["not-a-handler-kind"]},
            {"labels": ["one"]},
            {"labels": "not-an-array"},
            {"labels": ["left", False]},
        ],
    )
    def test_document_grammar_keeps_native_domain_failures(
        source: t.JsonMapping,
    ) -> None:
        """Native source decoding cannot admit invalid members, items or arity."""
        parsed = tm.ok(u.Cli.yaml_parse(u.Cli.yaml_dump_str(source)))

        with pytest.raises(m.ValidationError):
            u.Cli.config_decode(parsed, TestsFlextCliConfigDocumentIngress.Contract)

    @staticmethod
    def test_python_construction_retains_its_strict_contract() -> None:
        """Ordinary Python calls do not select textual scalar/array decoding."""
        domain = TestsFlextCliConfigDocumentIngress.Contract
        valid = domain.model_validate({"kind": c.DEFAULT_HANDLER_TYPE})

        tm.ok(valid.kind is c.DEFAULT_HANDLER_TYPE)
        for source in (
            {"kind": c.DEFAULT_HANDLER_TYPE.value},
            {"kinds": [c.DEFAULT_HANDLER_TYPE]},
        ):
            with pytest.raises(m.ValidationError):
                domain.model_validate(source)

    @staticmethod
    def test_native_error_retains_the_document_source(tmp_path: Path) -> None:
        """The entry owner adds provenance without replacing the native failure."""
        source = tmp_path / "policy.yaml"

        with pytest.raises(m.ValidationError) as raised:
            u.Cli.config_decode(
                {"kind": None},
                TestsFlextCliConfigDocumentIngress.Contract,
                source_path=source,
            )

        tm.that(raised.value.__notes__, has=f"Document source: {source}")


__all__: list[str] = ["TestsFlextCliConfigDocumentIngress"]
