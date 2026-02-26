"""Tests for Option Groups coverage.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli.option_groups import FlextCliOptionGroup as FlextOptionGroup


def test_connection_options_defaults_are_exposed() -> None:
    options = FlextOptionGroup.connection_options()

    assert len(options) == 4
    assert options[0].default == "localhost"
    assert options[1].default == 8080
    assert options[2].default == 30
    assert options[3].default is False


def test_auth_options_include_expected_env_vars() -> None:
    options = FlextOptionGroup.auth_options()

    env_vars = {option.envvar for option in options}
    assert env_vars == {"FLEXT_USERNAME", "FLEXT_PASSWORD", "FLEXT_TOKEN"}


def test_output_options_expose_format_output_and_verbosity() -> None:
    options = FlextOptionGroup.output_options()

    assert len(options) == 3
    assert options[0].default == "table"
    assert options[1].default is None
    assert options[2].default is False
