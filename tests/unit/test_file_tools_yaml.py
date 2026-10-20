"""Behavioral tests for typed YAML loading through the public CLI facade.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_cli import cli
from tests import m, t, tm, u

if TYPE_CHECKING:
    from pathlib import Path


class TestsFlextCliYamlModelLoading:
    """Observable contracts for model-first YAML file ingress."""

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

    @staticmethod
    def test_single_source_returns_requested_model(tmp_path: Path) -> None:
        """A successful public result contains only the requested model."""
        source = tmp_path / "consumer.yaml"
        written = u.Cli.atomic_write_text_file(
            source,
            "service:\n  host: api.internal\n  port: 8443\n"
            "features:\n  enabled: true\n",
        )
        tm.ok(written.success)

        result = cli.read_yaml_model(source, m.Tests.YamlConsumerConfig)

        tm.ok(result.success)
        tm.that(result.value, is_=m.Tests.YamlConsumerConfig)
        tm.that(result.value.service.host, eq="api.internal")
        tm.that(result.value.service.port, eq=8443)
        tm.ok(result.value.features.enabled)

    @staticmethod
    def test_chain_deep_merges_before_one_final_validation(
        tmp_path: Path,
    ) -> None:
        """Individually incomplete layers become one valid final model."""
        base_source = tmp_path / "base.yaml"
        type_source = tmp_path / "sheet.yaml"
        consumer_source = tmp_path / "consumer.yaml"
        base_written = u.Cli.atomic_write_text_file(
            base_source,
            "service:\n  host: base.internal\n",
        )
        type_written = u.Cli.atomic_write_text_file(
            type_source,
            "service:\n  port: 443\n",
        )
        consumer_written = u.Cli.atomic_write_text_file(
            consumer_source,
            "service:\n  host: consumer.internal\nfeatures:\n  enabled: true\n",
        )
        tm.ok(base_written.success)
        tm.ok(type_written.success)
        tm.ok(consumer_written.success)

        result = cli.read_yaml_model_chain(
            (base_source, type_source, consumer_source),
            m.Tests.YamlConsumerConfig,
        )

        tm.ok(result.success)
        tm.that(result.value, is_=m.Tests.YamlConsumerConfig)
        tm.that(result.value.service.host, eq="consumer.internal")
        tm.that(result.value.service.port, eq=443)
        tm.ok(result.value.features.enabled)

    @staticmethod
    def test_missing_file_fails_loud(tmp_path: Path) -> None:
        """A missing external source returns a failed public result."""
        result = cli.read_yaml_model(
            tmp_path / "missing.yaml",
            m.Tests.YamlConsumerConfig,
        )

        tm.ok(result.failure)

    @staticmethod
    def test_malformed_chain_source_fails_loud(tmp_path: Path) -> None:
        """Malformed YAML in any ordered layer returns a failed result."""
        base_source = tmp_path / "base.yaml"
        malformed_source = tmp_path / "malformed.yaml"
        base_written = u.Cli.atomic_write_text_file(
            base_source,
            "service:\n  host: api.internal\n  port: 8443\n"
            "features:\n  enabled: true\n",
        )
        malformed_written = u.Cli.atomic_write_text_file(
            malformed_source,
            "service:\n  host: [unterminated\n",
        )
        tm.ok(base_written.success)
        tm.ok(malformed_written.success)

        result = cli.read_yaml_model_chain(
            (base_source, malformed_source),
            m.Tests.YamlConsumerConfig,
        )

        tm.ok(result.failure)

    @staticmethod
    def test_strict_model_rejects_quoted_integer(tmp_path: Path) -> None:
        """External scalar coercion cannot weaken the requested model."""
        source = tmp_path / "wrong-scalar.yaml"
        written = u.Cli.atomic_write_text_file(
            source,
            'service:\n  host: api.internal\n  port: "8443"\n'
            "features:\n  enabled: true\n",
        )
        tm.ok(written.success)

        result = cli.read_yaml_model(source, m.Tests.YamlConsumerConfig)

        tm.ok(result.failure)
