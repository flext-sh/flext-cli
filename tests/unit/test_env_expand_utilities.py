"""Behavioral tests for the ``u.Cli.env_expand`` interpolation primitive.

Exercises the observable public contract of ``FlextCliUtilitiesEnv.env_expand``
exposed through the canonical ``u.Cli`` namespace: ``${VAR}`` / ``$VAR`` and
``${VAR:-default}`` interpolation over an injected mapping, so callers pass a
template and its data source and receive the resolved string.

Modules tested: flext_cli._utilities.env.FlextCliUtilitiesEnv

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_cli import u
from flext_tests import tm
from tests import c


class TestsFlextCliUtilitiesEnvExpand:
    """Interpolate ${VAR} / ${VAR:-default} templates through ``u.Cli``."""

    def test_env_expand_substitutes_braced_variable(self) -> None:
        """A ``${VAR}`` token is replaced by the injected value."""
        result = u.Cli.env_expand(
            "${FLEXT_CLI_EXPAND_HOME}/.claude",
            {"FLEXT_CLI_EXPAND_HOME": c.Tests.ENV_EXPAND_HOME_VALUE},
        )

        tm.that(tm.ok(result), eq=f"{c.Tests.ENV_EXPAND_HOME_VALUE}/.claude")

    def test_env_expand_substitutes_bare_variable(self) -> None:
        """A bare ``$VAR`` token is replaced by the injected value."""
        result = u.Cli.env_expand(
            "$FLEXT_CLI_EXPAND_BARE/bin",
            {"FLEXT_CLI_EXPAND_BARE": c.Tests.ENV_EXPAND_OPT_VALUE},
        )

        tm.that(tm.ok(result), eq=f"{c.Tests.ENV_EXPAND_OPT_VALUE}/bin")

    def test_env_expand_uses_default_when_unset(self) -> None:
        """``${VAR:-default}`` falls back to the default when the var is unset."""
        result = u.Cli.env_expand("${FLEXT_CLI_EXPAND_MISSING:-20000}", {})

        tm.that(tm.ok(result), eq="20000")

    def test_env_expand_unset_without_default_is_empty(self) -> None:
        """An unset variable without a default resolves to an empty segment."""
        result = u.Cli.env_expand("prefix-${FLEXT_CLI_EXPAND_NONE}-suffix", {})

        tm.that(tm.ok(result), eq="prefix--suffix")

    def test_env_expand_template_is_data(self) -> None:
        """The template is a plain argument, so callers pass paths as data."""
        environment = {"FLEXT_CLI_EXPAND_H": c.Tests.ENV_EXPAND_HOME_VALUE}
        for template, expected in (
            (
                "${FLEXT_CLI_EXPAND_H}/.codex/config.toml",
                f"{c.Tests.ENV_EXPAND_HOME_VALUE}/.codex/config.toml",
            ),
            (
                "${FLEXT_CLI_EXPAND_H}/.kube/config",
                f"{c.Tests.ENV_EXPAND_HOME_VALUE}/.kube/config",
            ),
        ):
            tm.that(tm.ok(u.Cli.env_expand(template, environment)), eq=expected)
