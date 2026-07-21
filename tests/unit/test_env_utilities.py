"""Behavioral tests for the ``u.Cli.env_read`` environment-variable primitive.

Exercises the observable public contract of ``FlextCliUtilitiesEnv.env_read``
exposed through the canonical ``u.Cli`` namespace: reading a single environment
variable by name (passed as data) and the unset-is-None contract.

Modules tested: flext_cli._utilities.env.FlextCliUtilitiesEnv

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import os

from flext_cli import u
from flext_tests import tm


class TestsFlextCliUtilitiesEnv:
    """Read a single environment variable by name through ``u.Cli``."""

    def test_env_read_returns_value_when_set(self) -> None:
        """A set environment variable is returned by name."""
        name = "FLEXT_CLI_ENV_READ_PROBE"
        os.environ[name] = "probe-value"
        try:
            result = u.Cli.env_read(name)
        finally:
            os.environ.pop(name, None)

        tm.that(tm.ok(result), eq="probe-value")

    def test_env_read_returns_empty_when_unset(self) -> None:
        """An unset environment variable resolves to an empty string, not a failure."""
        name = "FLEXT_CLI_ENV_READ_ABSENT"
        os.environ.pop(name, None)

        result = u.Cli.env_read(name)

        tm.that(tm.ok(result), eq="")

    def test_env_read_name_is_data(self) -> None:
        """The variable name is a plain argument, so callers pass it as data."""
        first = "FLEXT_CLI_ENV_READ_A"
        second = "FLEXT_CLI_ENV_READ_B"
        os.environ[first] = "value-a"
        os.environ[second] = "value-b"
        try:
            for name, expected in ((first, "value-a"), (second, "value-b")):
                tm.that(tm.ok(u.Cli.env_read(name)), eq=expected)
        finally:
            os.environ.pop(first, None)
            os.environ.pop(second, None)
