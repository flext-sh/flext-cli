"""Behavioral tests for typed YAML loading through the public CLI facade."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_cli import cli, u
from flext_tests import tm
from tests import m

if TYPE_CHECKING:
    from pathlib import Path


class TestsFlextCliYamlModelLoading:
    """Observable contracts for model-first YAML file ingress."""

    def test_single_source_returns_requested_model(self, tmp_path: Path) -> None:
        """A successful public result contains only the requested model."""
        source = tmp_path / "consumer.yaml"
        written = u.Cli.atomic_write_text_file(
            source,
            "service:\n  host: api.internal\n  port: 8443\n"
            "features:\n  enabled: true\n",
        )
        tm.that(written.success, eq=True)

        result = cli.read_yaml_model(source, m.Tests.YamlConsumerConfig)

        tm.that(result.success, eq=True)
        tm.that(result.value, is_=m.Tests.YamlConsumerConfig)
        tm.that(result.value.service.host, eq="api.internal")
        tm.that(result.value.service.port, eq=8443)
        tm.that(result.value.features.enabled, eq=True)

    def test_chain_deep_merges_before_one_final_validation(
        self, tmp_path: Path
    ) -> None:
        """Individually incomplete layers become one valid final model."""
        base_source = tmp_path / "base.yaml"
        type_source = tmp_path / "sheet.yaml"
        consumer_source = tmp_path / "consumer.yaml"
        base_written = u.Cli.atomic_write_text_file(
            base_source, "service:\n  host: base.internal\n"
        )
        type_written = u.Cli.atomic_write_text_file(
            type_source, "service:\n  port: 443\n"
        )
        consumer_written = u.Cli.atomic_write_text_file(
            consumer_source,
            "service:\n  host: consumer.internal\nfeatures:\n  enabled: true\n",
        )
        tm.that(base_written.success, eq=True)
        tm.that(type_written.success, eq=True)
        tm.that(consumer_written.success, eq=True)

        result = cli.read_yaml_model_chain(
            (base_source, type_source, consumer_source), m.Tests.YamlConsumerConfig
        )

        tm.that(result.success, eq=True)
        tm.that(result.value, is_=m.Tests.YamlConsumerConfig)
        tm.that(result.value.service.host, eq="consumer.internal")
        tm.that(result.value.service.port, eq=443)
        tm.that(result.value.features.enabled, eq=True)

    def test_missing_file_fails_loud(self, tmp_path: Path) -> None:
        """A missing external source returns a failed public result."""
        result = cli.read_yaml_model(
            tmp_path / "missing.yaml", m.Tests.YamlConsumerConfig
        )

        tm.that(result.failure, eq=True)

    def test_malformed_chain_source_fails_loud(self, tmp_path: Path) -> None:
        """Malformed YAML in any ordered layer returns a failed result."""
        base_source = tmp_path / "base.yaml"
        malformed_source = tmp_path / "malformed.yaml"
        base_written = u.Cli.atomic_write_text_file(
            base_source,
            "service:\n  host: api.internal\n  port: 8443\n"
            "features:\n  enabled: true\n",
        )
        malformed_written = u.Cli.atomic_write_text_file(
            malformed_source, "service:\n  host: [unterminated\n"
        )
        tm.that(base_written.success, eq=True)
        tm.that(malformed_written.success, eq=True)

        result = cli.read_yaml_model_chain(
            (base_source, malformed_source), m.Tests.YamlConsumerConfig
        )

        tm.that(result.failure, eq=True)

    def test_strict_model_rejects_quoted_integer(self, tmp_path: Path) -> None:
        """External scalar coercion cannot weaken the requested model."""
        source = tmp_path / "wrong-scalar.yaml"
        written = u.Cli.atomic_write_text_file(
            source,
            'service:\n  host: api.internal\n  port: "8443"\n'
            "features:\n  enabled: true\n",
        )
        tm.that(written.success, eq=True)

        result = cli.read_yaml_model(source, m.Tests.YamlConsumerConfig)

        tm.that(result.failure, eq=True)


__all__: list[str] = ["TestsFlextCliYamlModelLoading"]
