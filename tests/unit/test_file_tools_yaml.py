"""Behavioral tests for YAML writing through the public CLI facade.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import (
    Iterable,
    Iterator,
    Mapping,
    MutableMapping,
    MutableSequence,
    Sequence,
)

from typing import TYPE_CHECKING

from tests import t, tm, u

if TYPE_CHECKING:
    from pathlib import Path


class TestsFlextCliYamlModelLoading:
    """Observable contracts for YAML file egress and re-ingress."""

    @staticmethod
    def test_json_writers_preserve_null_order_and_whitespace(tmp_path: Path) -> None:
        """Both public writers retain nullable JSON metadata and ordered values."""
        payload: t.JsonDict = {
            "unset": None,
            "options": {"enabled": False, "unset": None},
            "ordered": ["zulu", " alpha ", None, 1.25],
            "records": [{"name": "second"}, {"name": "first", "value": None}],
            "spacing": "  value  ",
        }
        rendered = u.Cli.yaml_dump_str(payload, sort_keys=True)
        tm.that(tm.ok(u.Cli.yaml_parse(rendered)), eq=payload)
        destination = tmp_path / "new-directory" / "metadata.yaml"
        tm.ok(u.Cli.yaml_dump(destination, payload, sort_keys=True))
        tm.that(tm.ok(u.Cli.yaml_safe_load(destination)), eq=payload)
