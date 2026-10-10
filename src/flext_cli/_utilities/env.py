"""Environment reading and interpolation primitives shared through ``u.Cli``.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence

from flext_cli import c, p, r, t


class FlextCliUtilitiesEnv:
    """Read and interpolate environment variables, exposed on ``u.Cli``."""

    _VAR_PATTERN = re.compile(r"\$\{([^}]+)\}|\$([A-Za-z_][A-Za-z0-9_]*)")
    _STRICT_PATTERN = re.compile(
        r"\$\{(?P<name>[A-Za-z_][A-Za-z0-9_]*)(?::-(?P<default>[^{}]*))?\}",
    )
    _ANY_PLACEHOLDER = re.compile(r"\$\{[^{}]*\}")

    @staticmethod
    def env_read(name: str, environment: t.StrMapping) -> p.Result[str]:
        """Read one environment variable by ``name`` from an injected mapping.

        Returns the variable's value, or an empty string when it is unset. Callers
        pass both the variable name and environment as data. An empty or missing
        variable is a legitimate empty-string state, not a failure; callers decide
        whether an empty value is acceptable.

        Returns:
            The resulting ``p.Result[str]``.

        """
        return r[str].ok(environment.get(name, ""))

    @staticmethod
    def env_expand(
        template: str,
        environment: t.StrMapping,
        *,
        strict: bool = False,
    ) -> p.Result[str]:
        """Interpolate environment tokens from an injected mapping.

        Substitutes every environment reference in ``template`` with the injected
        value, honouring ``${VAR:-default}`` declarations; an
        unset variable without a default resolves to an empty segment. Callers
        pass the template and environment as data and receive the resolved string.

        ``strict=True`` applies the closed braced grammar ``${NAME}`` and
        ``${NAME:-default}`` repeatedly until a fixed point, so nested defaults
        resolve. It fails when a name is neither declared nor defaulted, when any
        ``${...}`` placeholder survives expansion, or when no fixed point is
        reached within ``c.Cli.ENV_EXPAND_MAX_PASSES`` passes.

        Returns:
            The resulting ``p.Result[str]``.

        """
        if strict:
            return FlextCliUtilitiesEnv._expand_strict(template, environment)

        def _replace(match: re.Match[str]) -> str:
            token = (
                match.group(1) if match.group(1) is not None else (match.group(2) or "")
            )
            key, _, default = token.partition(":-")
            return environment.get(key, default)

        return r[str].ok(FlextCliUtilitiesEnv._VAR_PATTERN.sub(_replace, template))

    @staticmethod
    def env_expand_document(
        document: t.JsonValue,
        environment: t.StrMapping,
        *,
        skip_keys: frozenset[str] = frozenset(),
    ) -> p.Result[t.JsonValue]:
        """Strictly expand every string leaf of one JSON-compatible document.

        Every string leaf follows ``env_expand(..., strict=True)``. A mapping
        entry whose key is in ``skip_keys`` keeps its whole subtree verbatim at
        every nesting level, so a later renderer can bind its own roots. The
        first failing leaf fails the document.

        Returns:
            The resulting ``p.Result[t.JsonValue]``.

        """
        if isinstance(value := document, str):
            expanded = FlextCliUtilitiesEnv._expand_strict(value, environment)
            if expanded.failure:
                return r[t.JsonValue].from_failure(expanded)
            return r[t.JsonValue].ok(expanded.value)
        if isinstance(value, Mapping):
            return FlextCliUtilitiesEnv._expand_mapping(value, environment, skip_keys)
        if isinstance(value, Sequence):
            return FlextCliUtilitiesEnv._expand_sequence(value, environment, skip_keys)
        return r[t.JsonValue].ok(value)

    @staticmethod
    def _expand_mapping(
        value: t.JsonMapping,
        environment: t.StrMapping,
        skip_keys: frozenset[str],
    ) -> p.Result[t.JsonValue]:
        """Expand every non-skipped entry of one mapping, stopping at a failure.

        Returns:
            The expanded mapping, or the first failing entry.

        """
        mapping: dict[str, t.JsonValue] = {}
        for key, item in value.items():
            if key in skip_keys:
                mapping[key] = item
                continue
            child = FlextCliUtilitiesEnv.env_expand_document(
                item,
                environment,
                skip_keys=skip_keys,
            )
            if child.failure:
                return child
            mapping[key] = child.value
        return r[t.JsonValue].ok(mapping)

    @staticmethod
    def _expand_sequence(
        value: t.SequenceOf[t.JsonValue],
        environment: t.StrMapping,
        skip_keys: frozenset[str],
    ) -> p.Result[t.JsonValue]:
        """Expand every item of one sequence, stopping at a failure.

        Returns:
            The expanded list, or the first failing item.

        """
        items: list[t.JsonValue] = []
        for item in value:
            child = FlextCliUtilitiesEnv.env_expand_document(
                item,
                environment,
                skip_keys=skip_keys,
            )
            if child.failure:
                return child
            items.append(child.value)
        return r[t.JsonValue].ok(items)

    @staticmethod
    def _expand_strict(template: str, environment: t.StrMapping) -> p.Result[str]:
        """Expand one value to its fixed point under the closed braced grammar.

        Returns:
            The fully expanded value, or the first undeclared name, surviving
            placeholder, or missing fixed point as a failure.

        """
        current = template
        for _ in range(c.Cli.ENV_EXPAND_MAX_PASSES):
            pieces: list[str] = []
            position = 0
            for match in FlextCliUtilitiesEnv._STRICT_PATTERN.finditer(current):
                name = match.group("name")
                default = match.group("default")
                if name not in environment and default is None:
                    return r[str].fail(
                        f"undeclared placeholder ${{{name}}} without ':-default' "
                        f"in {template!r}",
                    )
                pieces.extend((
                    current[position : match.start()],
                    environment.get(name, default or ""),
                ))
                position = match.end()
            pieces.append(current[position:])
            expanded = "".join(pieces)
            if expanded == current:
                residue = FlextCliUtilitiesEnv._ANY_PLACEHOLDER.search(expanded)
                if residue is not None:
                    return r[str].fail(
                        f"placeholder {residue.group(0)!r} survives expansion "
                        f"of {template!r}",
                    )
                return r[str].ok(expanded)
            current = expanded
        return r[str].fail(
            f"no fixed point after {c.Cli.ENV_EXPAND_MAX_PASSES} expansion "
            f"passes: {template!r}",
        )


__all__: list[str] = ["FlextCliUtilitiesEnv"]
