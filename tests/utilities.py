"""Test utilities for flext-cli.

Composes ``FlextTestsUtilities + u`` via MRO. Hosts only flext-cli-specific
helpers; everything generic comes from the parent namespaces.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import (
    Iterable,
    Iterator,
    Mapping,
    MutableMapping,
    MutableSequence,
    Sequence,
)

from typing import TYPE_CHECKING

from examples import ExamplesFlextCliUtilities
from flext_tests import FlextTestsUtilities

from flext_cli import FlextCliUtilities, cli
from tests import TestsFlextCliSettings, m, p, r, tm

if TYPE_CHECKING:
    from pathlib import Path


class TestsFlextCliUtilities(
    FlextTestsUtilities,
    ExamplesFlextCliUtilities,
    FlextCliUtilities,
):
    """Test utilities for flext-cli."""

    @staticmethod
    def atomic_directory_snapshot(
        path: Path,
        *,
        required: bool = False,
    ) -> m.Cli.AtomicDirectoryState:
        """Read one authenticated empty-directory state through the facade.

        Returns:
            The resulting ``m.Cli.AtomicDirectoryState``.

        """
        result = u.Cli.atomic_read_empty_directory_state(path, required=required)
        tm.ok(result)
        return result.value

    class Tests(FlextTestsUtilities.Tests):
        """flext-cli-specific test utilities."""

        @staticmethod
        def create_test_settings() -> p.Result[p.Cli.Settings]:
            """Create test settings via Railway pattern.

            Returns:
                The resulting ``p.Result[p.Cli.Settings]``.

            """
            settings: p.Cli.Settings = TestsFlextCliSettings()
            return r[p.Cli.Settings].ok(settings)

        @staticmethod
        def create_cli_app() -> p.Result[p.Cli.Application]:
            """Create CLI app via Railway pattern.

            Returns:
                The resulting ``p.Result[p.Cli.Application]``.

            """
            return r[p.Cli.Application].ok(
                cli.create_app_with_common_params(
                    name="tests-cli",
                    help_text="Test CLI app",
                ),
            )


u = TestsFlextCliUtilities

__all__: list[str] = ["TestsFlextCliUtilities", "u"]
