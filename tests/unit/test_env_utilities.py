"""Behavioral tests for the ``u.Cli.env_read`` environment-mapping primitive.

Exercises the observable public contract of ``FlextCliUtilitiesEnv.env_read``
exposed through the canonical ``u.Cli`` namespace: reading a single value from
an injected mapping and the unset-is-empty contract.

Modules tested: flext_cli._utilities.env.FlextCliUtilitiesEnv

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_cli import u
from flext_tests import tm
from tests import c


class TestsFlextCliUtilitiesEnv:
    """Read a single environment variable by name through ``u.Cli``."""

    def test_env_read_returns_value_when_set(self) -> None:
        """A set environment variable is returned by name."""
        result = u.Cli.env_read(
            c.Tests.ENV_READ_PROBE_NAME,
            {c.Tests.ENV_READ_PROBE_NAME: c.Tests.ENV_READ_PROBE_VALUE},
        )

        tm.that(tm.ok(result), eq=c.Tests.ENV_READ_PROBE_VALUE)

    def test_env_read_returns_empty_when_unset(self) -> None:
        """An unset environment variable resolves to an empty string, not a failure."""
        result = u.Cli.env_read(c.Tests.ENV_READ_ABSENT_NAME, {})

        tm.that(tm.ok(result), eq="")

    def test_env_read_name_is_data(self) -> None:
        """The variable name is a plain argument, so callers pass it as data."""
        for name, expected in c.Tests.ENV_READ_CASES.items():
            tm.that(
                tm.ok(u.Cli.env_read(name, c.Tests.ENV_READ_CASES)), eq=expected
            )
