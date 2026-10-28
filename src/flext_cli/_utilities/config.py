"""Universal multi-format config loader shared through ``u.Cli.config_*``.

flext-cli **amplifies** the flext-core minimal config layer (ADR-005): it reuses
``u.config_merge`` / ``u.config_env_override`` (core, stdlib) and the existing
``u.Cli.yaml_safe_load`` / ``json_read`` / ``toml_read_json`` readers, adding
multi-format dispatch, directory loading, and JSON-Schema validation. It does
**not** re-implement merge, env-expansion, or the ``m.ConfigDocument`` record.

Copyright (c) 2025 FLEXT Team. All rights reserved.
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

import os
from collections.abc import MutableSequence
from pathlib import Path
from typing import TYPE_CHECKING

from flext_core import u
from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError, ValidationError

from flext_cli import c, m, r, t
from flext_cli._utilities import FlextCliUtilitiesJson
from flext_cli._utilities._toml import FlextCliUtilitiesTomlPart06

if TYPE_CHECKING:
    from flext_cli import p


class FlextCliUtilitiesConfig:
    """Universal multi-format config load + schema validation (ADR-005)."""

    @staticmethod
    def _read_by_suffix(path: Path) -> p.Result[t.JsonMapping]:
        """Dispatch to the reader matching ``path`` suffix; reuse core cli readers.

        Returns:
            The resulting ``p.Result[t.JsonMapping]``.

        """
        suffix = path.suffix.lower()
        if suffix in {c.CONFIG_YAML_SUFFIX, ".yml"}:
            return u.Yaml.yaml_safe_load(path)
        if suffix == c.CONFIG_JSON_SUFFIX:
            return FlextCliUtilitiesJson.json_read(path)
        if suffix == c.CONFIG_TOML_SUFFIX:
            return FlextCliUtilitiesTomlPart06.toml_read_json(path)
        return r[t.JsonMapping].fail(f"{c.Cli.ERR_CONFIG_UNSUPPORTED_FORMAT}: {path}")

    @staticmethod
    def config_load(
        path: Path,
        *,
        schema_path: Path | None = None,
        expand_env: bool = True,
    ) -> p.Result[m.ConfigDocument]:
        """Load a YAML/JSON/TOML config into a validated ``m.ConfigDocument``.

        Reuses core ``u.config_env_override`` for ``${VAR}`` expansion and
        ``u.Cli.schema_validate`` for optional JSON-Schema validation.

        Returns:
            The resulting ``p.Result[m.ConfigDocument]``.

        """
        read = FlextCliUtilitiesConfig._read_by_suffix(path)
        if read.failure:
            return r[m.ConfigDocument].from_failure(read)
        data: t.JsonValue = dict(read.value)
        if expand_env:
            data = u.config_env_override(data, dict(os.environ))
        if not isinstance(data, dict):
            return r[m.ConfigDocument].fail(f"{c.ERR_CONFIG_NOT_MAPPING}: {path}")
        if schema_path is not None:
            validated = FlextCliUtilitiesConfig.schema_validate(data, schema_path)
            if validated.failure:
                return r[m.ConfigDocument].from_failure(validated)
        return r[m.ConfigDocument].ok(
            m.ConfigDocument(
                data=data,
                source_path=str(path),
                schema_ref=str(schema_path) if schema_path is not None else None,
            ),
        )

    @staticmethod
    def schema_validate(data: t.JsonMapping, schema_path: Path) -> p.Result[bool]:
        """Validate ``data`` against the JSON Schema at ``schema_path`` → ``r[bool]``.

        Returns:
            The resulting ``p.Result[bool]``.

        """
        schema_read = FlextCliUtilitiesJson.json_read(schema_path)
        if schema_read.failure:
            return r[bool].from_failure(schema_read)
        return u.try_(
            lambda: FlextCliUtilitiesConfig._run_validator(
                Draft202012Validator(dict(schema_read.value)), data
            ),
            catch=(ValidationError, SchemaError),
            op_name="schema_validate",
        )

    @staticmethod
    def _run_validator(
        validator: p.Cli.JsonSchemaValidator, data: t.JsonMapping
    ) -> bool:
        """Run a Draft 2020-12 validator; raise on first violation, else ``True``.

        Returns:
            The resulting ``bool``.

        """
        validator.validate(dict(data))
        return True


__all__: MutableSequence[str] = ["FlextCliUtilitiesConfig"]
