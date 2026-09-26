"""Model-source helpers shared through ``u.Cli``.

Model-backed commands have one owner, ``cli.model_command``; model
derivation has one owner, ``cli.derive_model``. This module keeps only the
source-extraction primitive that ``cli.derive_model`` consumes.
"""

from __future__ import annotations

from collections.abc import Mapping

from flext_cli import t


class FlextCliUtilitiesModelCommands:
    """Model-source methods exposed directly on ``u.Cli``."""

    @staticmethod
    def model_source_data(
        model_cls: t.ModelClass[t.Cli.ModelLike], source: t.Cli.ModelSource
    ) -> t.JsonMapping:
        """Extract only target-compatible fields from a model or mapping source."""
        raw_source: t.JsonMapping | t.ScalarMapping
        if isinstance(source, Mapping):
            raw_source = source
        else:
            raw_source = source.model_dump(exclude_none=True)
        filtered_payload = {
            field_name: raw_source[field_name]
            for field_name in model_cls.model_fields
            if field_name in raw_source and raw_source[field_name] is not None
        }
        return t.Cli.JSON_MAPPING_ADAPTER.validate_python(filtered_payload)


__all__: list[str] = ["FlextCliUtilitiesModelCommands"]
