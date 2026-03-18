"""Tests for Option Groups coverage.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_tests import tm

from flext_cli import FlextCliOptionGroup as FlextOptionGroup


def test_connection_options_defaults_are_exposed() -> None:
    options = FlextOptionGroup.connection_options()
    tm.that(len(options), eq=4)
    tm.that(options[0].default, eq="localhost")
    tm.that(options[1].default, eq=8080)
    tm.that(options[2].default, eq=30)
    tm.that(options[3].default is False, eq=True)


def test_auth_options_include_expected_env_vars() -> None:
    options = FlextOptionGroup.auth_options()
    env_vars: frozenset[str] = frozenset(
        option.envvar for option in options if isinstance(option.envvar, str)
    )
    tm.that(env_vars, eq=frozenset({"FLEXT_USERNAME", "FLEXT_PASSWORD", "FLEXT_TOKEN"}))


def test_output_options_expose_format_output_and_verbosity() -> None:
    options = FlextOptionGroup.output_options()
    tm.that(len(options), eq=3)
    tm.that(options[0].default, eq="table")
    tm.that(options[1].default is None, eq=True)
    tm.that(options[2].default is False, eq=True)
