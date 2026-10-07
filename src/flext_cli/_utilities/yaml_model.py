"""Model-only YAML egress for the CLI facade.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from pathlib import Path

from flext_cli import c, p, r, t


class FlextCliUtilitiesYamlModel:
    """Serialize one validated model at the external YAML boundary."""

    # NOTE (multi-agent, mro-j2yt.1): the validated model remains intact until
    # this external egress; no internal dump/revalidation round trip is allowed.
    @staticmethod
    def write_yaml_model(file_path: t.Cli.TextPath, model: p.Model) -> p.Result[bool]:
        """Write one protocol-backed model as YAML and propagate failures.

        Returns:
            The resulting ``p.Result[bool]``.

        """
        from flext_core import u
        try:
            return u.Yaml.yaml_dump(
                Path(file_path),
                t.Cli.JSON_MAPPING_ADAPTER.validate_python(
                    model.model_dump(mode="json"),
                ),
            )
        except c.EXC_PYDANTIC_TYPE_VALUE as exc:
            return r[bool].fail(f"YAML model write error: {exc}", exception=exc)


__all__: t.VariadicTuple[str] = ("FlextCliUtilitiesYamlModel",)
