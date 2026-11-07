"""Extracted facade class for yaml.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from flext_core import r, u

from flext_cli import c, p, t
from flext_cli._utilities import FlextCliUtilitiesConversion, FlextCliUtilitiesJson
from flext_cli._utilities._yaml import FlextCliUtilitiesYamlEditing


class FlextCliUtilitiesYaml(
    FlextCliUtilitiesYamlEditing,
):
    """Provide strict YAML reading, serialization and round-trip editing."""

    @staticmethod
    def yaml_safe_load(path: Path) -> p.Result[t.JsonMapping]:
        """Read a YAML mapping through the strict parser.

        Returns:
            The parsed mapping, or the parser's failure prefixed by ``path``.

        """
        if not path.is_file():
            return r[t.JsonMapping].fail(c.Cli.YAML_ERR_NOT_FOUND_FMT.format(path=path))
        return FlextCliUtilitiesYaml.yaml_parse(
            path.read_text(encoding=c.DEFAULT_ENCODING)
        ).map_error(lambda error: f"{path}: {error}")

    @staticmethod
    def yaml_load_documents(path: Path) -> p.Result[Sequence[t.JsonMapping]]:
        """Read every mapping of a strict YAML document stream file.

        Returns:
            The validated documents in their original order, or the parser's
            failure prefixed by ``path``.

        """
        if not path.is_file():
            return r[Sequence[t.JsonMapping]].fail(
                c.Cli.YAML_ERR_NOT_FOUND_FMT.format(path=path)
            )
        return FlextCliUtilitiesYaml.yaml_parse_documents(
            path.read_text(encoding=c.DEFAULT_ENCODING)
        ).map_error(lambda error: f"{path}: {error}")

    @staticmethod
    def yaml_parse(text: str) -> p.Result[t.JsonMapping]:
        """Parse one YAML mapping, rejecting duplicate keys.

        Returns:
            The validated mapping, or the original parsing failure.

        """
        return FlextCliUtilitiesYaml.yaml_roundtrip_load_map_text(text).map(
            lambda value: FlextCliUtilitiesConversion.YAML_DICT_ADAPTER.validate_python(
                FlextCliUtilitiesYaml.yaml_to_plain(value)
            )
        )

    @staticmethod
    def yaml_parse_documents(text: str) -> p.Result[Sequence[t.JsonMapping]]:
        """Read every mapping in a strict YAML document stream.

        Returns:
            The validated documents in their original order.

        """
        loaded = u.Yaml.unique_key_load_all(text)
        if loaded.failure:
            return r[Sequence[t.JsonMapping]].from_failure(loaded)
        try:
            documents = tuple(
                FlextCliUtilitiesConversion.YAML_DICT_ADAPTER.validate_python(value)
                for value in loaded.value
            )
        except c.ValidationError as exc:
            return r[Sequence[t.JsonMapping]].fail(
                c.Cli.YAML_ERR_VALIDATION_FMT.format(error=exc), exception=exc
            )
        return r[Sequence[t.JsonMapping]].ok(documents)

    @staticmethod
    def yaml_load_mapping(path: Path) -> t.JsonMapping:
        """Read a required mapping without replacing failures with empty data.

        Returns:
            The validated mapping.

        """
        return FlextCliUtilitiesYaml.yaml_safe_load(path).unwrap()

    @staticmethod
    def yaml_dump(
        path: Path,
        data: t.JsonMapping | t.JsonValue | t.JsonPayload,
        *,
        sort_keys: bool = False,
        indent: int = 2,
    ) -> p.Result[bool]:
        """Serialize YAML and write it to its declared destination.

        Returns:
            Success after the complete write.

        """
        serialized = FlextCliUtilitiesYaml.yaml_dump_str(
            data, sort_keys=sort_keys, indent=indent
        )
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(serialized, encoding=c.DEFAULT_ENCODING)
        return r[bool].ok(value=True)

    @staticmethod
    def yaml_dump_str(
        data: t.Cli.JsonWriteData,
        *,
        sort_keys: bool = False,
        indent: int = 2,
    ) -> str:
        """Serialize validated data through the canonical YAML owner.

        Returns:
            The serialized YAML document.

        """
        return u.Yaml.safe_dump(
            FlextCliUtilitiesJson.normalize_json_value(data),
            default_flow_style=False,
            sort_keys=sort_keys,
            allow_unicode=True,
            indent=indent,
        )


__all__: list[str] = ["FlextCliUtilitiesYaml"]
