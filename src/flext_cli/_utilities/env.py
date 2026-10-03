"""Environment reading and interpolation primitives shared through ``u.Cli``.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import re

from flext_cli import p, r, t


class FlextCliUtilitiesEnv:
    """Read and interpolate environment variables, exposed on ``u.Cli``."""

    _VAR_PATTERN = re.compile(r"\$\{([^}]+)\}|\$([A-Za-z_][A-Za-z0-9_]*)")

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
    def env_expand(template: str, environment: t.StrMapping) -> p.Result[str]:
        """Interpolate environment tokens from an injected mapping.

        Substitutes every environment reference in ``template`` with the injected
        value, honouring ``${VAR:-default}`` declarations; an
        unset variable without a default resolves to an empty segment. Callers
        pass the template and environment as data and receive the resolved string.

        Returns:
            The resulting ``p.Result[str]``.

        """

        def _replace(match: re.Match[str]) -> str:
            token = (
                match.group(1) if match.group(1) is not None else (match.group(2) or "")
            )
            key, _, default = token.partition(":-")
            return environment.get(key, default)

        return r[str].ok(FlextCliUtilitiesEnv._VAR_PATTERN.sub(_replace, template))


__all__: list[str] = ["FlextCliUtilitiesEnv"]
