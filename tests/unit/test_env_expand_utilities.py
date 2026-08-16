"""Behavioral tests for the ``u.Cli.env_expand`` interpolation primitive.

Exercises the observable public contract of ``FlextCliUtilitiesEnv.env_expand``
exposed through the canonical ``u.Cli`` namespace: ``${VAR}`` / ``$VAR`` and
``${VAR:-default}`` interpolation over the process environment, so callers pass
a template as data and receive the resolved absolute string.

Modules tested: flext_cli._utilities.env.FlextCliUtilitiesEnv

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import os

from flext_cli import u
from flext_tests import tm


class TestsFlextCliUtilitiesEnvExpand:
    """Interpolate ${VAR} / ${VAR:-default} templates through ``u.Cli``."""

    def test_env_expand_substitutes_braced_variable(self) -> None:
        """A ``${VAR}`` token is replaced by the process-environment value."""
        os.environ["FLEXT_CLI_EXPAND_HOME"] = "/home/tester"
        try:
            result = u.Cli.env_expand("${FLEXT_CLI_EXPAND_HOME}/.claude")
        finally:
            os.environ.pop("FLEXT_CLI_EXPAND_HOME", None)

        tm.that(tm.ok(result), eq="/home/tester/.claude")

    def test_env_expand_substitutes_bare_variable(self) -> None:
        """A bare ``$VAR`` token is replaced by the process-environment value."""
        os.environ["FLEXT_CLI_EXPAND_BARE"] = "/opt/x"
        try:
            result = u.Cli.env_expand("$FLEXT_CLI_EXPAND_BARE/bin")
        finally:
            os.environ.pop("FLEXT_CLI_EXPAND_BARE", None)

        tm.that(tm.ok(result), eq="/opt/x/bin")

    def test_env_expand_uses_default_when_unset(self) -> None:
        """``${VAR:-default}`` falls back to the default when the var is unset."""
        os.environ.pop("FLEXT_CLI_EXPAND_MISSING", None)

        result = u.Cli.env_expand("${FLEXT_CLI_EXPAND_MISSING:-20000}")

        tm.that(tm.ok(result), eq="20000")

    def test_env_expand_unset_without_default_is_empty(self) -> None:
        """An unset variable without a default resolves to an empty segment."""
        os.environ.pop("FLEXT_CLI_EXPAND_NONE", None)

        result = u.Cli.env_expand("prefix-${FLEXT_CLI_EXPAND_NONE}-suffix")

        tm.that(tm.ok(result), eq="prefix--suffix")

    def test_env_expand_template_is_data(self) -> None:
        """The template is a plain argument, so callers pass paths as data."""
        os.environ["FLEXT_CLI_EXPAND_H"] = "/home/tester"
        try:
            for template, expected in (
                (
                    "${FLEXT_CLI_EXPAND_H}/.codex/config.toml",
                    "/home/tester/.codex/config.toml",
                ),
                ("${FLEXT_CLI_EXPAND_H}/.kube/config", "/home/tester/.kube/config"),
            ):
                tm.that(tm.ok(u.Cli.env_expand(template)), eq=expected)
        finally:
            os.environ.pop("FLEXT_CLI_EXPAND_H", None)
