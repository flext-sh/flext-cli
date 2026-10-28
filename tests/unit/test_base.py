"""Behavioral tests for the FLEXT CLI service base through the public facade.

Exercises the OBSERVABLE public contract of the ``cli`` facade
(``flext_cli.api.FlextCli``): the canonical settings singleton contract,
fresh-instance creation via ``clone``, and the public ``u.Cli`` settings
structure diagnostics and snapshot operations.

Modules tested: flext_cli.api (public ``cli`` facade)
Scope: Public base-service behavior — no private attributes, no internal spies.

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

from pathlib import Path

import pytest

from flext_cli import FlextCli, cli, settings, u
from tests import c, p, tm


class TestsFlextCliBase:
    """Verify base-service public guarantees through the CLI facade."""

    @staticmethod
    @pytest.fixture
    def facade() -> FlextCli:
        """Return a fresh instance of the public CLI facade type.

        Returns:
            A fresh instance of the public CLI facade type.

        """
        return type(cli)()

    @staticmethod
    def test_canonical_settings_satisfies_cli_protocol() -> None:
        """The canonical ``settings`` singleton satisfies the Cli settings protocol."""
        resolved_settings = tm.not_none(settings)
        tm.that(resolved_settings, is_=p.Cli.Settings)

    @staticmethod
    def test_settings_property_is_stable_within_instance(
        facade: FlextCli,
    ) -> None:
        """Repeated `settings` reads return the same singleton (idempotent access)."""
        first = facade.settings
        second = facade.settings
        tm.ok(first is second)

    @staticmethod
    def test_settings_singleton_shared_across_instances() -> None:
        """Two independent facades observe the same shared settings singleton."""
        service1 = type(cli)()
        service2 = type(cli)()
        tm.ok(service1.settings is service2.settings)

    @staticmethod
    def test_clone_returns_fresh_typed_instances() -> None:
        """``clone`` is the factory: each call yields a distinct typed instance."""
        first = settings.clone()
        second = settings.clone()
        tm.that(first, is_=p.Cli.Settings)
        tm.that(second, is_=p.Cli.Settings)
        tm.ok(first is not second)
        tm.ok(first is not settings)

    @staticmethod
    def test_settings_structure_reports_current_paths() -> None:
        """Structure diagnostics describe the configured paths as they exist."""
        base = Path.home() / c.Cli.PATH_FLEXT_DIR_NAME
        diagnostics = u.Cli.validate_settings_structure()
        symbol = (
            c.Cli.SYMBOL_SUCCESS_MARK if base.exists() else c.Cli.SYMBOL_FAILURE_MARK
        )
        state = "exists" if base.exists() else "missing"
        tm.that(diagnostics[0], eq=f"{symbol} Settings directory {state}")
        tm.that(len(diagnostics), eq=1 + len(c.Cli.STANDARD_SUBDIRS))
        for diagnostic, subdir in zip(
            diagnostics[1:],
            c.Cli.STANDARD_SUBDIRS,
            strict=True,
        ):
            exists = (base / subdir).exists()
            template = c.Cli.MSG_SUBDIR_EXISTS if exists else c.Cli.MSG_SUBDIR_MISSING
            symbol = c.Cli.SYMBOL_SUCCESS_MARK if exists else c.Cli.SYMBOL_FAILURE_MARK
            tm.that(diagnostic, eq=template.format(symbol=symbol, subdir=subdir))

    @staticmethod
    def test_settings_snapshot_exposes_public_state() -> None:
        """The public snapshot model exposes the current settings state."""
        snapshot = u.Cli.settings_snapshot_model()
        dumped = snapshot.model_dump()
        tm.that(
            set(dumped)
            >= {
                "settings_dir",
                "settings_exists",
                "settings_readable",
                "settings_writable",
                "timestamp",
            },
            eq=True,
        )
        tm.that(snapshot.settings_exists, is_=bool)
        tm.that(snapshot.settings_dir, is_=str)
        tm.that(snapshot.settings_dir, empty=False)

    @staticmethod
    def test_snapshot_directory_matches_configured_path() -> None:
        """The snapshot identifies the canonical configured settings directory."""
        snapshot = u.Cli.settings_snapshot_model()
        directory = Path.home() / c.Cli.PATH_FLEXT_DIR_NAME
        tm.that(snapshot.settings_dir, eq=str(directory))
        tm.that(snapshot.settings_exists, eq=directory.exists())
