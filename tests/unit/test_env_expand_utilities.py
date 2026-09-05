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

from typing import TYPE_CHECKING

from flext_cli import u
from flext_tests import tm

if TYPE_CHECKING:
    from pathlib import Path


class TestsFlextCliUtilitiesEnvExpand:
    """Interpolate ${VAR} / ${VAR:-default} templates through ``u.Cli``."""

    def test_env_expand_substitutes_braced_variable(self, tmp_path: Path) -> None:
        """A ``${VAR}`` token is replaced by the injected value."""
        home = str(tmp_path / "home")
        result = u.Cli.env_expand(
            "${FLEXT_CLI_EXPAND_HOME}/.claude", {"FLEXT_CLI_EXPAND_HOME": home}
        )

        tm.that(tm.ok(result), eq=f"{home}/.claude")

    def test_env_expand_substitutes_bare_variable(self, tmp_path: Path) -> None:
        """A bare ``$VAR`` token is replaced by the injected value."""
        base = str(tmp_path / "base")
        result = u.Cli.env_expand(
            "$FLEXT_CLI_EXPAND_BARE/bin", {"FLEXT_CLI_EXPAND_BARE": base}
        )

        tm.that(tm.ok(result), eq=f"{base}/bin")

    def test_env_expand_uses_default_when_unset(self) -> None:
        """``${VAR:-default}`` falls back to the default when the var is unset."""
        result = u.Cli.env_expand("${FLEXT_CLI_EXPAND_MISSING:-20000}", {})

        tm.that(tm.ok(result), eq="20000")

    def test_env_expand_unset_without_default_is_empty(self) -> None:
        """An unset variable without a default resolves to an empty segment."""
        result = u.Cli.env_expand("prefix-${FLEXT_CLI_EXPAND_NONE}-suffix", {})

        tm.that(tm.ok(result), eq="prefix--suffix")

    def test_env_expand_template_is_data(self, tmp_path: Path) -> None:
        """The template is a plain argument, so callers pass paths as data."""
        home = str(tmp_path / "home")
        environment = {"FLEXT_CLI_EXPAND_H": home}
        for template, expected in (
            ("${FLEXT_CLI_EXPAND_H}/.codex/config.toml", f"{home}/.codex/config.toml"),
            ("${FLEXT_CLI_EXPAND_H}/.kube/config", f"{home}/.kube/config"),
        ):
            tm.that(tm.ok(u.Cli.env_expand(template, environment)), eq=expected)
