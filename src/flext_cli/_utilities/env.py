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
            try:
                return r[str].ok(
                    FlextCliUtilitiesEnv._expand_strict(template, environment),
                )
            except ValueError as exc:
                return r[str].fail(str(exc))

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
        every nesting level, so a later renderer can bind its own roots.

        Returns:
            The resulting ``p.Result[t.JsonValue]``.

        """
        try:
            return r[t.JsonValue].ok(
                FlextCliUtilitiesEnv._expand_tree(document, environment, skip_keys),
            )
        except ValueError as exc:
            return r[t.JsonValue].fail(str(exc))

    @staticmethod
    def _expand_tree(
        value: t.JsonValue,
        environment: t.StrMapping,
        skip_keys: frozenset[str],
    ) -> t.JsonValue:
        if isinstance(value, str):
            return FlextCliUtilitiesEnv._expand_strict(value, environment)
        if isinstance(value, Mapping):
            return {
                key: item
                if key in skip_keys
                else FlextCliUtilitiesEnv._expand_tree(item, environment, skip_keys)
                for key, item in value.items()
            }
        if isinstance(value, Sequence):
            return [
                FlextCliUtilitiesEnv._expand_tree(item, environment, skip_keys)
                for item in value
            ]
        return value

    @staticmethod
    def _expand_strict(template: str, environment: t.StrMapping) -> str:
        """Expand one value to its fixed point under the closed braced grammar.

        Returns:
            The fully expanded value.

        Raises:
            ValueError: If a name is undeclared without default, a placeholder
                survives, or no fixed point is reached.

        """

        def _replace(match: re.Match[str]) -> str:
            name = match.group("name")
            if name in environment:
                return environment[name]
            default = match.group("default")
            if default is None:
                message = (
                    f"undeclared placeholder ${{{name}}} without ':-default' "
                    f"in {template!r}"
                )
                raise ValueError(message)
            return default

        current = template
        for _ in range(c.Cli.ENV_EXPAND_MAX_PASSES):
            expanded = FlextCliUtilitiesEnv._STRICT_PATTERN.sub(_replace, current)
            if expanded == current:
                residue = FlextCliUtilitiesEnv._ANY_PLACEHOLDER.search(expanded)
                if residue is not None:
                    message = (
                        f"placeholder {residue.group(0)!r} survives expansion "
                        f"of {template!r}"
                    )
                    raise ValueError(message)
                return expanded
            current = expanded
        message = (
            f"no fixed point after {c.Cli.ENV_EXPAND_MAX_PASSES} expansion "
            f"passes: {template!r}"
        )
        raise ValueError(message)


__all__: list[str] = ["FlextCliUtilitiesEnv"]
