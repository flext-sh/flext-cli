"""Behavioral tests for the FLEXT CLI service base through the public facade.

Exercises the OBSERVABLE public contract of the ``cli`` facade
(``flext_cli.api.FlextCli``): the canonical settings singleton contract,
fresh-instance creation via ``clone``, and the ``r[T]`` outcomes of the
settings validation / snapshot operations.

Modules tested: flext_cli.api (public ``cli`` facade)
Scope: Public base-service behavior — no private attributes, no internal spies.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import pytest
from flext_tests import tm

from flext_cli import FlextCli, cli, settings
from tests import p


class TestsFlextCliBase:
    """Verify base-service public guarantees through the CLI facade."""

    @pytest.fixture
    def facade(self) -> FlextCli:
        """Return a fresh instance of the public CLI facade type."""
        return type(cli)()

    def test_canonical_settings_satisfies_cli_protocol(self) -> None:
        """The canonical ``settings`` singleton satisfies the Cli settings protocol."""
        resolved_settings = tm.not_none(settings)
        tm.that(resolved_settings, is_=p.Cli.Settings)

    def test_settings_property_is_stable_within_instance(
        self, facade: FlextCli
    ) -> None:
        """Repeated `settings` reads return the same singleton (idempotent access)."""
        first = facade.settings
        second = facade.settings
        tm.that(first is second, eq=True)

    def test_settings_singleton_shared_across_instances(self) -> None:
        """Two independent facades observe the same shared settings singleton."""
        service1 = type(cli)()
        service2 = type(cli)()
        tm.that(service1.settings is service2.settings, eq=True)

    def test_clone_returns_fresh_typed_instances(self) -> None:
        """``clone`` is the factory: each call yields a distinct typed instance."""
        first = settings.clone()
        second = settings.clone()
        tm.that(first, is_=p.Cli.Settings)
        tm.that(second, is_=p.Cli.Settings)
        tm.that(first is not second, eq=True)
        tm.that(first is not settings, eq=True)

    def test_validate_settings_reports_success_outcome(self, facade: FlextCli) -> None:
        """`validate_settings` returns a successful r[bool] carrying True."""
        result = facade.validate_settings()
        tm.ok(result)
        tm.that(result.unwrap(), eq=True)

    def test_settings_snapshot_exposes_public_state(self, facade: FlextCli) -> None:
        """`settings_snapshot` returns r[Snapshot] whose public fields are populated."""
        result = facade.settings_snapshot()
        tm.ok(result)
        snapshot = result.unwrap()
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

    def test_snapshot_map_composes_over_success(self, facade: FlextCli) -> None:
        """The r[T] snapshot value flows through `map` without losing success."""
        directory = facade.settings_snapshot().map(lambda snap: snap.settings_dir)
        tm.ok(directory)
        tm.that(directory.unwrap(), eq=facade.settings_snapshot().unwrap().settings_dir)
